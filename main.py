#!/usr/bin/env python3
"""Main entry point for voiceblend-tui."""

import bootstrap  # noqa: F401 - Must be imported first to setup path

from voiceblend_tui.app import VoiceBlendApp

if __name__ == "__main__":
    app = VoiceBlendApp()
    app.run()

