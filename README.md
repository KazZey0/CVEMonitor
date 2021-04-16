# CVEMonitor
Monitor for latest exploits. Docker + sqlite + telegram bot

### Configuration
Edit telemonitor.py to configure telegram bot:
```
self.userid = "Telegram ID"
self.bot = telebot.TeleBot("TOKEN")
```
### Deployment
Deploy with docker:
```
docker pull python:alpine
bash build.sh
bash start.sh
```

### Current version

POC source:
+ github

Push message:
+ telegram

