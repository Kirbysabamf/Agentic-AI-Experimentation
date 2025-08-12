#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting Social Media Reader application..."

# Wait for dependencies if needed
if [ "$WAIT_FOR_REDIS" = "true" ]; then
    log "Waiting for Redis to be ready..."
    while ! redis-cli -h redis ping > /dev/null 2>&1; do
        sleep 1
    done
    log "Redis is ready!"
fi

# Create necessary directories
mkdir -p /app/data /app/results

# Set permissions
chmod 755 /app/data /app/results

# Check if required environment variables are set
check_env_var() {
    if [ -z "${!1}" ]; then
        log "WARNING: $1 environment variable is not set"
        if [ "$2" = "required" ]; then
            log "ERROR: $1 is required but not set. Exiting."
            exit 1
        fi
    else
        log "$1 is configured"
    fi
}

# Check critical environment variables
if [ "$USE_MOCK_DATA" != "true" ]; then
    check_env_var "OPENAI_API_KEY" "required"
    check_env_var "LINKEDIN_EMAIL" "optional"
    check_env_var "LINKEDIN_PASSWORD" "optional"
    check_env_var "REDDIT_CLIENT_ID" "optional"
    check_env_var "REDDIT_CLIENT_SECRET" "optional"
else
    log "Using mock data - skipping API credential checks"
fi

# Display Chrome/ChromeDriver versions
log "Chrome version: $(google-chrome --version)"
log "ChromeDriver version: $(chromedriver --version)"

# Set up X virtual framebuffer for headless Chrome
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
XVFB_PID=$!
log "Started Xvfb with PID $XVFB_PID"

# Function to cleanup on exit
cleanup() {
    log "Shutting down..."
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID > /dev/null 2>&1 || true
        log "Stopped Xvfb"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Run the main application
log "Starting main application with args: $@"

# Execute the command
exec "$@"