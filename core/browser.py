"""
Bridge penghubung antara Core Engine / AI Command dengan Browser Launcher.
"""

from browser.launcher import BrowserLauncher
from core.config import ConfigManager


class BrowserBridge:
    def __init__(self, config: ConfigManager) -> None:
        self.config = config
        self.launcher = BrowserLauncher()

    def launch(self, target: str) -> dict:
        prefer_chrome = bool(self.config.get("prefer_chrome", True))
        return self.launcher.open_url(target, prefer_chrome=prefer_chrome)

    def open_menu(self) -> None:
        self.launcher.interactive_menu(prefer_chrome=bool(self.config.get("prefer_chrome", True)))
