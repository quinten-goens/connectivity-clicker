FROM python:3.11-slim

# Install Chromium + its driver, plus git (needed to pip-install pocketlogpy
# from its git repo). We use Debian's chromium packages rather than Google
# Chrome's .deb because Google only ships an amd64 build, whereas Dokploy may
# run on arm64 hosts; chromium has native packages for both architectures and
# apt pulls in the right shared-library dependencies automatically.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        chromium \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Tell Selenium where the Chromium binary lives so it doesn't look for "chrome".
ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /app

# Install Python dependencies first to leverage Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY click_summary.py click_runner.py ./

# Outcome logging goes to PocketLog (https://github.com/euctrl-pru/pocketlogpy)
# under the manually-registered flow "connectivity_clicker". Provide credentials
# at runtime via Dokploy env vars (do NOT bake them into the image):
#   POCKETLOG_URL, POCKETLOG_EMAIL, POCKETLOG_PASSWORD
# If they are absent, the click still runs; only the logging is skipped.

# click_summary.py falls back to system Chrome/Chromium when the portable
# Windows paths are absent, which is exactly what we want inside the container.
#
# The container stays running idle so that a Dokploy schedule can `docker exec`
# the click into it on an interval (recommended: every 4 minutes), e.g.:
#   docker exec <container> python /app/click_summary.py --headless
# Each exec performs one click and returns its exit status to the scheduler.
CMD ["sleep", "infinity"]
