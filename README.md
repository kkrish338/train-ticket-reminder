# Train Ticket Reminder - Android App

[![Build Status](https://github.com/YOUR_USERNAME/train-ticket-reminder/workflows/Build%20Android%20APK/badge.svg)](https://github.com/YOUR_USERNAME/train-ticket-reminder/actions)

A Python-based Android application that helps users schedule reminders to book train tickets 60 days in advance.

## 📥 Download APK

### Latest Release
Download the latest APK from [Releases](https://github.com/YOUR_USERNAME/train-ticket-reminder/releases/latest)

### Build from GitHub Actions
1. Go to [Actions](https://github.com/YOUR_USERNAME/train-ticket-reminder/actions)
2. Click latest successful workflow (green ✓)
3. Download APK from "Artifacts" section

## Features

- 📅 **Calendar Interface**: Select future journey dates with an intuitive calendar widget
- ⏰ **Automatic Alarms**: Get loud alarms 60 days before your journey at 7:45 AM
- 🔊 **Cannot Miss**: Full-screen alarm with sound, vibration, and LED lights
- 📝 **Notes**: Add custom notes for each reminder (e.g., route, number of tickets)
- 🔔 **Persistent Alarms**: Reminders survive app closure and device reboots
- 💾 **Local Storage**: All data stored securely in SQLite database

## Technology Stack

- **Framework**: Kivy (Python UI framework for Android)
- **Database**: SQLite3
- **Build Tool**: Buildozer with python-for-android
- **Android APIs**: AlarmManager, NotificationManager (via pyjnius)

## Project Structure

```
train_book/
├── main.py                          # Main application entry point
├── database/
│   ├── __init__.py
│   └── db_manager.py               # SQLite database operations
├── widgets/
│   ├── __init__.py
│   └── calendar_widget.py          # Custom calendar UI
├── services/
│   ├── __init__.py
│   ├── alarm_scheduler.py          # AlarmManager integration
│   ├── notification_service.py     # Notification display
│   ├── boot_receiver.py            # Boot completion handler
│   └── alarm_receiver.py           # Alarm trigger handler
├── utils/
│   ├── __init__.py
│   └── date_utils.py               # Date calculation utilities
├── assets/                          # App icons and images
├── buildozer.spec                   # Build configuration
└── README.md                        # This file
```

## Development Setup

### Prerequisites

- **Anaconda Python 3.10+** (installed at `C:\Program Files\Anaconda3`)
- **WSL2** (Windows Subsystem for Linux) - Required for building APK on Windows
- **Android Device/Emulator** - For testing

### Install Dependencies (Windows - Desktop Testing)

```powershell
# Activate Anaconda environment
& "C:\Program Files\Anaconda3\Scripts\activate"

# Install Kivy
pip install kivy[base]
```

### Run on Desktop (for development/testing)

```powershell
# Navigate to project directory
cd c:\workspace\train_book

# Run the app
& "C:\Program Files\Anaconda3\python.exe" main.py
```

**Note**: On desktop, alarms won't actually schedule but will print debug messages.

## Building APK

### Step 1: Set up WSL2

```powershell
# Install WSL2 with Ubuntu
wsl --install -d Ubuntu-22.04
```

### Step 2: Install Build Dependencies (inside WSL2)

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip build-essential git zip unzip \
    openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 cmake \
    libffi-dev libssl-dev

# Install Buildozer and Cython
pip3 install buildozer cython
```

### Step 3: Build APK

```bash
# Navigate to project (in WSL2)
cd /mnt/c/workspace/train_book

# First build (downloads SDK/NDK - may take 20-30 minutes)
buildozer android debug

# Output APK will be in: bin/trainbook-1.0.0-arm64-v8a-debug.apk
```

### Step 4: Install on Android Device

```bash
# Connect device via USB (enable USB debugging)
adb devices

# Install APK
adb install bin/trainbook-1.0.0-arm64-v8a-debug.apk
```

## Android Permissions

The app requires the following permissions:

- `SCHEDULE_EXACT_ALARM` - Schedule precise alarm times (7:45 AM)
- `POST_NOTIFICATIONS` - Display notifications (Android 13+)
- `USE_EXACT_ALARM` - Alternative for exact alarms
- `RECEIVE_BOOT_COMPLETED` - Restore alarms after reboot
- `WAKE_LOCK` - Wake device for alarm
- `VIBRATE` - Vibrate phone when alarm triggers
- `USE_FULL_SCREEN_INTENT` - Show full-screen alarm even when locked
- `SYSTEM_ALERT_WINDOW` - Display alarm over other apps
- `INTERNET` - (Reserved for future features)

**Important**: On Android 12+, users must manually grant "Alarms & reminders" permission from Settings.

## How It Works

1. **User selects date**: Opens calendar and picks journey date (must be 60+ days in future)
2. **Add note**: Enters reminder details (e.g., "Mumbai to Delhi, 2 tickets")
3. **Save**: App calculates reminder date (event_date - 60 days) and schedules alarm for 7:45 AM
4. **Alarm triggers**: At 7:45 AM on reminder date, full-screen alarm appears with sound and vibration
5. **Reboot handling**: After device restart, all pending alarms are automatically rescheduled

### Alarm Features:
- **Full-screen display**: Shows even when phone is locked
- **Alarm sound**: Uses system alarm sound (loud and attention-grabbing)
- **Vibration pattern**: Multiple vibrations to ensure you notice
- **LED lights**: Red blinking light (if device supports it)
- **Cannot dismiss accidentally**: Requires intentional interaction

## Database Schema

```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_date TEXT NOT NULL,           -- Journey date (YYYY-MM-DD)
    reminder_date TEXT NOT NULL,         -- Notification date (60 days before)
    reminder_time TEXT DEFAULT '07:45', -- Notification time
    note TEXT,                           -- User's note
    alarm_id INTEGER UNIQUE,             -- Android AlarmManager ID
    is_triggered INTEGER DEFAULT 0,      -- Has notification been sent?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Desktop Testing

- **Import errors (kivy, jnius)**: Normal on Windows. Install `kivy` for desktop testing: `pip install kivy[base]`
- **Alarms not scheduling**: Expected - AlarmManager only works on Android

### Build Issues

- **Buildozer not found**: Must run in WSL2, not Windows PowerShell
- **SDK download fails**: Check internet connection, may need to retry
- **Build errors**: Run `buildozer android clean` then rebuild

### Android Issues

- **Notification not appearing**: Check if "Alarms & reminders" permission is granted in Settings
- **Alarm not triggering**: Ensure battery optimization is disabled for the app
- **After reboot, alarms missing**: Check `RECEIVE_BOOT_COMPLETED` permission

## Future Enhancements

- [ ] Direct link to train booking websites
- [ ] Multiple reminder times (e.g., 30 days, 15 days before)
- [ ] Recurring reminders (weekly/monthly trains)
- [ ] Export/import reminders
- [ ] Cloud sync

## License

MIT License - Free to use and modify

## Contact

For issues or questions, please refer to the project documentation.
