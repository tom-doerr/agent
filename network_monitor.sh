#!/bin/bash
# Network monitoring script
# Logs network status, interface changes, and connectivity issues

LOG_FILE="/home/tom/git/agent/network_monitor.log"
INTERVAL=10  # Check every 10 seconds
WIFI_IF="wlxcc641af139a6"

echo "=== Network Monitor Started at $(date) ===" | tee -a "$LOG_FILE"

# Get initial state
prev_ip=$(ip addr show $WIFI_IF 2>/dev/null | grep "inet " | awk '{print $2}')
prev_state=$(ip link show $WIFI_IF 2>/dev/null | grep -oP '(?<=state )\w+')

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Check WiFi interface status
    curr_state=$(ip link show $WIFI_IF 2>/dev/null | grep -oP '(?<=state )\w+')
    curr_ip=$(ip addr show $WIFI_IF 2>/dev/null | grep "inet " | awk '{print $2}')

    # Detect state changes
    if [ "$curr_state" != "$prev_state" ]; then
        echo "[$timestamp] INTERFACE STATE CHANGE: $prev_state -> $curr_state" | tee -a "$LOG_FILE"
        prev_state=$curr_state
    fi

    if [ "$curr_ip" != "$prev_ip" ]; then
        echo "[$timestamp] IP ADDRESS CHANGE: $prev_ip -> $curr_ip" | tee -a "$LOG_FILE"
        prev_ip=$curr_ip
    fi

    # Check connectivity
    if ! ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        echo "[$timestamp] CONNECTIVITY LOST: Ping to 8.8.8.8 failed" | tee -a "$LOG_FILE"
    fi

    # Check DNS
    if ! host -W 2 google.com >/dev/null 2>&1; then
        echo "[$timestamp] DNS FAILURE: Cannot resolve google.com" | tee -a "$LOG_FILE"
    fi

    # Check API connectivity
    api_result=$(curl -s -m 3 -I https://openrouter.ai 2>&1 | head -1)
    if ! echo "$api_result" | grep -q "200\|301\|302"; then
        echo "[$timestamp] API ISSUE: OpenRouter - $api_result" | tee -a "$LOG_FILE"
    fi

    # Periodic status (every minute)
    if [ $(($(date +%s) % 60)) -lt $INTERVAL ]; then
        rtt=$(ping -c 1 8.8.8.8 2>/dev/null | grep "time=" | awk -F'time=' '{print $2}' | awk '{print $1}')
        echo "[$timestamp] OK: $curr_state, IP: $curr_ip, RTT: ${rtt}ms" >> "$LOG_FILE"
    fi

    sleep $INTERVAL
done
