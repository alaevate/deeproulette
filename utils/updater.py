"""Checks GitHub Releases for a newer version of DeepRoulette."""

import urllib.request
import urllib.error
import json
import webbrowser

from rich.console import Console
from rich.panel   import Panel

console = Console()

_VERSION = "2.0.0"
_REPO = "alaevate/deeproulette"
_API_URL = f"https://api.github.com/repos/{_REPO}/releases/latest"
_RELEASES_URL = f"https://github.com/{_REPO}/releases/latest"

def _parse_version(tag: str) -> tuple:
    """Convert 'v2.1.0' or '2.1.0' to (2, 1, 0) for comparison."""
    tag = tag.lstrip("v").strip()
    try:
        return tuple(int(x) for x in tag.split("."))
    except ValueError:
        return (0, 0, 0)


def check_for_updates() -> None:
    """Query GitHub Releases API for a newer version; prompt to open download page."""
    try:
        req = urllib.request.Request(
            _API_URL,
            headers={"User-Agent": f"DeepRoulette/{_VERSION}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        latest_tag  = data.get("tag_name", "")
        latest_name = data.get("name", latest_tag)

        if not latest_tag:
            return

        if _parse_version(latest_tag) <= _parse_version(_VERSION):
            # Already up to date — show a small green notice
            console.print(
                f"  [dim green]✔  DeepRoulette v{_VERSION} is up to date.[/dim green]\n"
            )
            return
        console.print(Panel(
            f"  [bold yellow]🚀  New version available![/bold yellow]\n\n"
            f"  Installed : [dim]v{_VERSION}[/dim]\n"
            f"  Latest    : [bold green]{latest_name}[/bold green]\n\n"
            f"  [dim]Download → {_RELEASES_URL}[/dim]",
            title="[bold cyan]Update Available[/bold cyan]",
            border_style="yellow",
            padding=(0, 2),
        ))

        answer = console.input(
            "  Open the download page now? [bold]\\[y/N][/bold] "
        ).strip().lower()

        if answer == "y":
            webbrowser.open(_RELEASES_URL)
            console.print("  [dim]Browser opened — press Enter after downloading.[/dim]")
            console.input()

        console.print()

    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        # No internet / timeout / bad response — skip silently
        pass
    except Exception:
        pass
