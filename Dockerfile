FROM python:3.11-slim

# Install Google Chrome (stable). Selenium 4.6+ ships Selenium Manager, which
# automatically downloads a matching ChromeDriver at runtime, so we only need
# the browser itself plus its shared-library dependencies here.
# Install Google Chrome (stable) plus git (needed to pip-install pocketlogpy
# from its git repo). We let apt resolve Chrome's shared-library dependencies
# from its own .deb metadata rather than hand-listing them, which keeps this
# working across Debian releases (package names like libasound2 vs libasound2t64
# differ between versions).
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        git \
        ca-certificates \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && rm -f /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first to leverage Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY click_summary.py click_runner.py ./

# Outcome logging goes to PocketLog (https://github.com/euctrl-pru/pocketlogpy)
# under the manually-registered flow "connectivity_clicker". Provide credentials
# at runtime, e.g. `docker run -e POCKETLOG_URL=... -e POCKETLOG_EMAIL=... \
# -e POCKETLOG_PASSWORD=... <image>`. If they are absent, the click still runs;
# only the logging is skipped (with a warning).
ENV POCKETLOG_URL="" \
    POCKETLOG_EMAIL="" \
    POCKETLOG_PASSWORD=""

# click_summary.py falls back to system Chrome when the portable Windows paths
# are absent, which is exactly what we want inside the container.
#
# Each container run performs a single click and exits. Schedule the run in
# Dokploy (recommended: every 4 minutes, matching the existing GitHub Actions
# cadence). To instead self-loop within one long-lived run, override CMD with
# e.g. `python click_runner.py --interval 4 --duration 60`.
CMD ["python", "click_summary.py", "--headless"]
