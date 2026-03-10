# Connectivity Clicker

A Python application that automates clicking the "Summary" button in the iframe on the [ANS Performance Connectivity page](https://ansperformance.eu/traffic/connectivity/).

## Features

- Automates clicking the Summary button in the Shiny app iframe
- Supports both headless and visible browser modes
- Multiple fallback strategies to locate the button
- Configurable wait times
- Command-line interface

## Installation

1. Create a virtual environment (recommended):

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

To deactivate the virtual environment later, simply run:
```bash
deactivate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Setup portable Chrome (recommended for corporate environments):
```bash
python click_summary.py --setup
```

This will automatically download Chrome for Testing and ChromeDriver to `C:\Users\qgoens\dev\chrome-portable\` (bypasses group policy restrictions).

**Alternative:** If you have Chrome installed system-wide and it's not blocked, you can skip the setup and use the system Chrome (the script will attempt this automatically).

## Usage

### As a Python module:

```python
from click_summary import click_summary_button, setup_chrome

# First time: setup portable Chrome
chrome_bin, driver_path = setup_chrome()

# Run in headless mode (default) with portable Chrome
click_summary_button(headless=True, chrome_binary=chrome_bin, chromedriver_path=driver_path)

# Run with visible browser
click_summary_button(headless=False, chrome_binary=chrome_bin, chromedriver_path=driver_path)

# Custom wait time
click_summary_button(headless=True, wait_time=30, chrome_binary=chrome_bin, chromedriver_path=driver_path)

# Use system Chrome (if not blocked)
click_summary_button(headless=True)
```

### From command line:

```bash
# First time: setup portable Chrome
python click_summary.py --setup

# Run in headless mode (default) - uses portable Chrome if available
python click_summary.py

# Show the browser window
python click_summary.py --show-browser

# Custom wait time
python click_summary.py --wait-time 30

# Use custom Chrome installation directory
python click_summary.py --setup --chrome-dir "C:/custom/path"
python click_summary.py --show-browser --chrome-dir "C:/custom/path"
```

## Function Parameters

### click_summary_button()
- `headless` (bool): If True, runs browser in headless mode (no GUI). Default is True.
- `wait_time` (int): Maximum time to wait for elements to load in seconds. Default is 20.
- `chrome_binary` (str): Path to Chrome executable. If None, uses system Chrome.
- `chromedriver_path` (str): Path to ChromeDriver executable. If None, uses system ChromeDriver.

### setup_chrome()
- `install_dir` (str): Directory where Chrome will be installed. Default is `C:/Users/qgoens/dev/chrome-portable`.

## Returns

- `True` if the button was clicked successfully
- `False` if an error occurred

## GitHub Actions Automation

The repository includes a GitHub Actions workflow that automatically runs the clicker every hour, with clicks every 4 minutes within that hour.

### Setup

1. Push the repository to GitHub
2. The workflow will automatically run every hour (at minute 0)
3. You can also manually trigger it from the Actions tab

### Workflow Details

- **Schedule**: Runs every hour (`0 * * * *`)
- **Interval**: Clicks every 4 minutes
- **Duration**: Runs for 60 minutes
- **Clicks per hour**: ~15 clicks

### Manual Triggering

You can manually trigger the workflow from GitHub:
1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "Connectivity Clicker" workflow
4. Click "Run workflow"

### Local Testing

You can test the runner locally:
```bash
# Run every 4 minutes for 1 hour
python click_runner.py

# Custom interval and duration
python click_runner.py --interval 5 --duration 30
```

## Troubleshooting

**Chrome blocked by group policy:**
If you see an error like "This program is blocked by group policy", the portable Chrome setup will bypass this:
```bash
python click_summary.py --setup
python click_summary.py --show-browser
```

The portable Chrome is downloaded to your user directory (`C:\Users\qgoens\dev\`), which typically isn't restricted by group policy.

## Requirements

- Python 3.7+
- Selenium 4.0+
- Requests library (for downloading Chrome)
- Chrome browser + ChromeDriver (automatically downloaded by `--setup`)
