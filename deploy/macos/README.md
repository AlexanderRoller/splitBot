# splitBot (macOS) launchd deployment

This repo includes a LaunchAgent plist:

- `deploy/macos/com.lex.splitbot.plist`

## Install / Update

```bash
mkdir -p ~/Library/LaunchAgents
cp deploy/macos/com.lex.splitbot.plist ~/Library/LaunchAgents/com.lex.splitbot.plist

# restart
launchctl unload ~/Library/LaunchAgents/com.lex.splitbot.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.lex.splitbot.plist
```

## Logs

- `logs/splitbot.out.log`
- `logs/splitbot.err.log`

## Python runtime

The service uses Python 3.12 by default (Homebrew):

- `/opt/homebrew/bin/python3.12`

Override by setting `PYTHON_BIN` in the plist or environment.
