# 🚄 Taiwan High Speed Rail (THSR) Booking Assistant

> ⚠️ **For Academic Research Only**

Automated booking system for Taiwan High Speed Rail using Python + Playwright.

## ⚠️ Disclaimer

This project is intended for **academic research and educational purposes only**. Users are responsible for all risks and legal consequences of using this program. The author is not liable for any direct or indirect damages.

**Do not use for commercial purposes or activities that violate THSR's terms of service.**

## Features

- ✅ **Two Modes**: CLI (all platforms) and GUI (Windows only)
- ✅ Auto-fill booking form (stations, date, time, ticket count)
- ✅ Automatic CAPTCHA recognition (using ddddocr)
- ✅ Auto-retry on CAPTCHA failure (up to 5 attempts)
- ✅ Automatically select first available train
- ✅ Auto-fill passenger information
- ✅ Complete booking automatically
- ✅ Modern GUI with real-time status updates (Windows)

## Installation

```bash
# Using uv (recommended)
uv sync

# Install Playwright browsers
uv run playwright install chromium

# For GUI on Windows: Install additional Flet dependencies
uv pip install "flet[all]"

# For Linux/macOS/WSL: Install Chromium system dependencies
uv run playwright install-deps chromium
```

## Configuration

Copy `.env.example` to `.env` and fill in your details:

```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Edit `.env`:

```env
# Station codes: 1=Nangang, 2=Taipei, 3=Banqiao, 4=Taoyuan, 5=Hsinchu, 6=Miaoli
#               7=Taichung, 8=Changhua, 9=Yunlin, 10=Chiayi, 11=Tainan, 12=Zuoying
START_STATION=2
END_STATION=12

TRAVEL_DATE=2026/01/25
TRAVEL_TIME=08:00
ADULT_COUNT=1

# Required
PASSENGER_ID=A123456789
PASSENGER_EMAIL=your@email.com

# Optional
PASSENGER_PHONE=0912345678
```

## Usage

### CLI Mode (All Platforms)

Reads configuration from `.env` file.

```bash
# Linux/macOS/WSL
uv run python -m src.main

# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; uv run python -m src.main

# Windows CMD
set PYTHONIOENCODING=utf-8 && uv run python -m src.main
```

### GUI Mode (Windows Only)

No `.env` file needed - configure directly in the GUI.

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; uv run python -m src.gui

# Windows CMD
set PYTHONIOENCODING=utf-8 && uv run python -m src.gui
```

## Project Structure

```
src/
├── main.py      # CLI entry point
├── gui.py       # GUI entry point (Windows only)
├── config.py    # Configuration & selectors
├── booking.py   # Core booking logic
└── captcha.py   # CAPTCHA handling
```

## Tech Stack

- Python 3.12+
- Playwright (browser automation)
- ddddocr (CAPTCHA recognition)
- python-dotenv (environment management)
- Flet (GUI framework for Windows)

## License

MIT License - See [LICENSE](LICENSE)

---

**This project is for academic research only. Please comply with all applicable laws and regulations.**
