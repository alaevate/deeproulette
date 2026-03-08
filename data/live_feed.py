"""
data/live_feed.py
=================
Live WebSocket feed — connects to a Pragmatic Play live roulette table
and streams real spin results in real time.

Handles:
  - Initial subscription handshake
  - Periodic keepalive pings
  - Automatic reconnection on drops
  - Two message formats (Pragmatic Play delta & legacy)
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime

from config.settings import RECONNECT_DELAY
from utils.constants import PING_INTERVAL


class LiveFeed:
    """
    Async WebSocket client.
    Register a callback with  on_number(async_fn)  — it will be called with
    every new roulette result as a plain integer (0–36).
    """

    def __init__(self, ws_url: str, casino_id: str, table_id: str,
                 currency: str = "USD"):
        self.ws_url    = ws_url
        self.casino_id = casino_id
        self.table_id  = table_id
        self.currency  = currency

        self.connected  = False
        self._ws        = None
        self._callbacks = []
        self._log       = logging.getLogger("LiveFeed")

    # ── Public API ────────────────────────────────────────────────────────────

    def on_number(self, callback):
        """Register an async function to receive each new spin number."""
        self._callbacks.append(callback)

    async def listen(self):
        """
        Main loop — connects, listens, and reconnects automatically if the
        connection drops.  Runs indefinitely until cancelled.
        """
        while True:
            if not self.connected:
                if not await self._connect():
                    self._log.warning(
                        f"Could not connect. Retrying in {RECONNECT_DELAY}s..."
                    )
                    await asyncio.sleep(RECONNECT_DELAY)
                    continue

            try:
                async for raw_message in self._ws:
                    await self._handle_message(raw_message)
            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                self._log.warning("Connection dropped — reconnecting...")
                await asyncio.sleep(RECONNECT_DELAY)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.connected = False
                self._log.error(f"Unexpected feed error: {e}")
                await asyncio.sleep(RECONNECT_DELAY)

    async def disconnect(self):
        """Gracefully close the WebSocket connection."""
        self.connected = False
        if self._ws:
            await self._ws.close()

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _connect(self) -> bool:
        """Open the WebSocket, subscribe, and start the keepalive loop."""
        try:
            self._ws       = await websockets.connect(
                self.ws_url, ping_interval=None
            )
            self.connected = True
            await self._subscribe()
            asyncio.create_task(self._keepalive())
            self._log.info("Connected to live roulette feed.")
            return True
        except Exception as e:
            self._log.error(f"Connection error: {e}")
            return False

    async def _subscribe(self):
        """Send the subscription message required by Pragmatic Play."""
        msg = {
            "type":           "subscribe",
            "isDeltaEnabled": True,
            "casinoId":       self.casino_id,
            "key":            [self.table_id],
            "currency":       self.currency,
        }
        await self._ws.send(json.dumps(msg))

    async def _keepalive(self):
        """Send a ping every PING_INTERVAL seconds to prevent timeout."""
        while self.connected:
            try:
                await self._ws.send(json.dumps({
                    "type":     "ping",
                    "pingTime": int(datetime.now().timestamp() * 1000),
                }))
                await asyncio.sleep(PING_INTERVAL)
            except Exception:
                self.connected = False
                break

    async def _handle_message(self, raw: str):
        """Parse a raw JSON message and fire callbacks if a number is found."""
        try:
            data   = json.loads(raw)
            number = self._extract_number(data)
            if number is not None:
                for cb in self._callbacks:
                    await cb(number)
        except json.JSONDecodeError:
            self._log.debug("Received non-JSON message (ignored).")
        except Exception as e:
            self._log.debug(f"Message handling error: {e}")

    @staticmethod
    def _extract_number(data: dict):
        """
        Try to extract a roulette number from a parsed JSON message.

        Supports two formats:
          Format A (Pragmatic Play delta):
            {"tableId": "236", "last20Results": [{"result": "16", ...}, ...]}

          Format B (legacy):
            {"result": {"number": "16"}}
        """
        # Format A
        if "tableId" in data and "last20Results" in data:
            results = data.get("last20Results", [])
            if results:
                try:
                    return int(results[0]["result"])
                except (KeyError, ValueError, TypeError):
                    pass

        # Format B
        if "result" in data and isinstance(data["result"], dict):
            try:
                return int(data["result"]["number"])
            except (KeyError, ValueError, TypeError):
                pass

        return None
