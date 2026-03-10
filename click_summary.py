"""
Connectivity Clicker - Automates clicking the Summary button on the Connectivity App
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import zipfile
import requests
import json
from pathlib import Path


def setup_chrome(install_dir="C:/Users/qgoens/dev/chrome-portable"):
    """
    Downloads and sets up a portable Chrome for Testing and ChromeDriver.

    Args:
        install_dir (str): Directory where Chrome will be installed.
                          Default is C:/Users/qgoens/dev/chrome-portable

    Returns:
        tuple: (chrome_binary_path, chromedriver_path) or (None, None) if failed
    """
    install_path = Path(install_dir)
    install_path.mkdir(parents=True, exist_ok=True)

    chrome_dir = install_path / "chrome-win64"
    chromedriver_dir = install_path / "chromedriver-win64"

    chrome_binary = chrome_dir / "chrome.exe"
    chromedriver_binary = chromedriver_dir / "chromedriver.exe"

    # Check if already installed
    if chrome_binary.exists() and chromedriver_binary.exists():
        print(f"✓ Chrome already installed at {chrome_binary}")
        print(f"✓ ChromeDriver already installed at {chromedriver_binary}")
        return str(chrome_binary), str(chromedriver_binary)

    try:
        # Get the latest Chrome for Testing version
        print("Fetching latest Chrome for Testing version...")
        version_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
        response = requests.get(version_url)
        response.raise_for_status()
        version_data = response.json()
        version = version_data['channels']['Stable']['version']

        print(f"Latest stable version: {version}")

        # Download URLs
        chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chrome-win64.zip"
        chromedriver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip"

        # Download Chrome
        if not chrome_binary.exists():
            print(f"Downloading Chrome to {install_path}...")
            chrome_zip = install_path / "chrome.zip"
            response = requests.get(chrome_url, stream=True)
            response.raise_for_status()

            with open(chrome_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("Extracting Chrome...")
            with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
                zip_ref.extractall(install_path)

            chrome_zip.unlink()  # Delete zip file
            print(f"✓ Chrome installed at {chrome_binary}")

        # Download ChromeDriver
        if not chromedriver_binary.exists():
            print(f"Downloading ChromeDriver to {install_path}...")
            driver_zip = install_path / "chromedriver.zip"
            response = requests.get(chromedriver_url, stream=True)
            response.raise_for_status()

            with open(driver_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("Extracting ChromeDriver...")
            with zipfile.ZipFile(driver_zip, 'r') as zip_ref:
                zip_ref.extractall(install_path)

            driver_zip.unlink()  # Delete zip file
            print(f"✓ ChromeDriver installed at {chromedriver_binary}")

        return str(chrome_binary), str(chromedriver_binary)

    except Exception as e:
        print(f"✗ Error setting up Chrome: {str(e)}")
        return None, None


def click_summary_button(headless=True, wait_time=20, chrome_binary=None, chromedriver_path=None):
    """
    Clicks the Summary button in the Connectivity App iframe.

    Args:
        headless (bool): If True, runs browser in headless mode (no GUI).
                        If False, shows the browser window. Default is True.
        wait_time (int): Maximum time to wait for elements to load (seconds). Default is 20.
        chrome_binary (str): Path to Chrome executable. If None, uses system Chrome.
        chromedriver_path (str): Path to ChromeDriver executable. If None, uses system ChromeDriver.

    Returns:
        bool: True if successful, False otherwise.
    """
    driver = None
    try:
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

        # Additional options for stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        # Use custom Chrome binary if provided
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            print(f"Using Chrome at: {chrome_binary}")

        # Initialize the driver
        print("Initializing Chrome driver...")
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the main page
        url = "https://ansperformance.eu/traffic/connectivity/"
        print(f"Navigating to {url}")
        driver.get(url)

        # Wait for the iframe to be present
        print("Waiting for iframe to load...")
        wait = WebDriverWait(driver, wait_time)
        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src*="ConnectivityApp"]'))
        )

        # Switch to the iframe
        print("Switching to iframe...")
        driver.switch_to.frame(iframe)

        # Wait a bit for the Shiny app to load
        time.sleep(3)

        # Try multiple strategies to find and click the Summary button
        clicked = False

        # Strategy 1: Find by text containing "Summary"
        try:
            print("Attempting to find Summary button by text...")
            summary_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Summary')]"))
            )
            summary_button.click()
            clicked = True
            print("✓ Successfully clicked Summary button using text search")
        except (TimeoutException, NoSuchElementException):
            print("Strategy 1 failed, trying alternative method...")

        # Strategy 2: Find by SVG with specific class
        if not clicked:
            try:
                print("Attempting to find Summary button by SVG...")
                svg_element = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg.bi-layout-sidebar'))
                )
                # Click the parent div instead of SVG
                parent = svg_element.find_element(By.XPATH, './..')
                parent.click()
                clicked = True
                print("✓ Successfully clicked Summary button using SVG search")
            except (TimeoutException, NoSuchElementException):
                print("Strategy 2 failed, trying alternative method...")

        # Strategy 3: Find any element with both SVG and "Summary" text
        if not clicked:
            try:
                print("Attempting to find Summary button by combined search...")
                elements = driver.find_elements(By.XPATH, "//*[contains(., 'Summary')]")
                for element in elements:
                    if element.find_elements(By.TAG_NAME, 'svg'):
                        element.click()
                        clicked = True
                        print("✓ Successfully clicked Summary button using combined search")
                        break
            except Exception as e:
                print(f"Strategy 3 failed: {e}")

        if clicked:
            print("\n✓ Summary button clicked successfully!")
            # Wait a moment to see the result (especially useful in non-headless mode)
            time.sleep(2)
            return True
        else:
            print("\n✗ Failed to click Summary button after all strategies")
            return False

    except TimeoutException:
        print(f"\n✗ Timeout: Element not found within {wait_time} seconds")
        return False
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        return False
    finally:
        # Clean up
        if driver:
            print("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Click the Summary button on Connectivity App')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run in headless mode (default: True)')
    parser.add_argument('--show-browser', action='store_true',
                        help='Show the browser window (sets headless to False)')
    parser.add_argument('--wait-time', type=int, default=20,
                        help='Maximum wait time in seconds (default: 20)')
    parser.add_argument('--setup', action='store_true',
                        help='Download and setup portable Chrome (run this first)')
    parser.add_argument('--chrome-dir', type=str, default="C:/Users/qgoens/dev/chrome-portable",
                        help='Directory for portable Chrome installation')

    args = parser.parse_args()

    # If --setup is specified, download Chrome and exit
    if args.setup:
        print("Setting up portable Chrome...")
        chrome_bin, driver_path = setup_chrome(install_dir=args.chrome_dir)
        if chrome_bin and driver_path:
            print("\n✓ Setup complete!")
            print(f"Chrome: {chrome_bin}")
            print(f"ChromeDriver: {driver_path}")
            print("\nYou can now run: python click_summary.py --show-browser")
            exit(0)
        else:
            print("\n✗ Setup failed!")
            exit(1)

    # Normal operation - use portable Chrome
    chrome_binary = Path(args.chrome_dir) / "chrome-win64" / "chrome.exe"
    chromedriver_path = Path(args.chrome_dir) / "chromedriver-win64" / "chromedriver.exe"

    # Check if portable Chrome exists
    if not chrome_binary.exists() or not chromedriver_path.exists():
        print("⚠ Portable Chrome not found. Run setup first:")
        print("  python click_summary.py --setup")
        print("\nAttempting to use system Chrome instead...")
        chrome_binary = None
        chromedriver_path = None

    # If --show-browser is specified, override headless
    headless = not args.show_browser if args.show_browser else args.headless

    success = click_summary_button(
        headless=headless,
        wait_time=args.wait_time,
        chrome_binary=str(chrome_binary) if chrome_binary else None,
        chromedriver_path=str(chromedriver_path) if chromedriver_path else None
    )
    exit(0 if success else 1)
