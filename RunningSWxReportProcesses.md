Checking Running Processes

# Check if launchd service is running
launchctl list | grep spaceweather

# Check for running Python scheduler processes
ps aux | grep -E "(scheduler|space_weather)" | grep -v grep

# View recent log activity
tail -20 space_weather_automation.log
Stopping Processes
1. Stop launchd Service (Background Daemon)

# Stop and unload the service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist

# Verify it's stopped
launchctl list | grep spaceweather
2. Stop Foreground Schedulers
If running scheduler.py or flare_scheduler.py in a terminal:
Press Ctrl+C to stop
3. Kill Any Remaining Processes

# Find and kill any lingering processes
pkill -f space_weather_automation.py
pkill -f scheduler.py
pkill -f flare_scheduler.py
Restarting Later

# Reload launchd service
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Or run foreground scheduler
python3 scheduler.py