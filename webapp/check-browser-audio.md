# Browser Audio Troubleshooting

Your system audio is working correctly. You have:
- ✅ Multiple audio capture devices (ALC1220 and BKD-11 Pro)
- ✅ User in audio group
- ✅ Capture enabled at 100% volume

## The Issue

The browser is showing "0 devices" which means it's not getting access to your microphones. This is a browser permission/security issue, not a system audio issue.

## Solutions to Try:

### 1. Browser Permissions
Check your browser's microphone permissions:
- **Chrome/Chromium**: 
  - Go to `chrome://settings/content/microphone`
  - Make sure "Sites can ask to use your microphone" is enabled
  - Check if localhost:3000 is in the blocked list

- **Firefox**:
  - Go to `about:preferences#privacy`
  - Find "Microphone" under Permissions
  - Check Settings

### 2. Try Different Access Methods

Option A - Direct file access (bypasses some security):
```bash
cd /home/tom/git/agent/webapp
python3 -m http.server 8080
```
Then visit: http://localhost:8080/test-microphone.html

Option B - Use Firefox (often more permissive):
```bash
firefox http://localhost:3000
```

Option C - Use Chrome with flags:
```bash
google-chrome --use-fake-ui-for-media-stream http://localhost:3000
```

### 3. System-wide Audio Permissions

Check if your browser has system-level permissions:
```bash
# For systems using systemd
systemctl --user status pulseaudio

# Check if browser can access audio
ps aux | grep -E "chrome|firefox" | head -5
```

### 4. Test with Simple HTML

Try the test page directly:
```bash
firefox /home/tom/git/agent/webapp/test-microphone.html
```

This will show exactly what's happening with permissions.

### 5. Docker Audio Passthrough (Advanced)

If you need audio to work specifically through Docker, you might need to add audio device mapping to docker-compose.yml:

```yaml
services:
  frontend:
    devices:
      - /dev/snd:/dev/snd
    group_add:
      - audio
```

But this is usually not necessary for web apps using getUserMedia.

## Most Likely Issue

The browser is probably:
1. Blocking microphone access for security reasons
2. Has denied permission previously (check site settings)
3. Requires HTTPS for microphone access (though localhost should work)

Try opening Chrome DevTools (F12) → Console, and see if there are any security errors when you click the microphone button.