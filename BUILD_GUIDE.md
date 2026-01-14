# Build and Deployment Guide

## Complete Step-by-Step Guide for Building APK

### Phase 1: Desktop Development & Testing (Windows)

#### 1. Verify Python Installation
```powershell
& "C:\Program Files\Anaconda3\python.exe" --version
# Should show Python 3.12.x or later
```

#### 2. Install Kivy for Desktop Testing
```powershell
cd c:\workspace\train_book
& "C:\Program Files\Anaconda3\python.exe" -m pip install kivy
```

#### 3. Test Application on Desktop
```powershell
# Run the app
& "C:\Program Files\Anaconda3\python.exe" main.py
```

**What to test on desktop:**
- ✅ Calendar opens and displays correctly
- ✅ Date selection works
- ✅ Can add reminder with note
- ✅ Reminders list shows saved items
- ✅ Delete functionality works
- ⚠️ Alarms won't actually trigger (Android-only feature)

---

### Phase 2: WSL2 Setup (Required for APK Building)

#### 1. Install WSL2

```powershell
# Check if WSL2 is already installed
wsl --list

# If not installed, install Ubuntu
wsl --install -d Ubuntu-22.04

# Restart computer if prompted
```

#### 2. Configure WSL2 Ubuntu

```bash
# Start WSL2
wsl

# Update system
sudo apt update && sudo apt upgrade -y

# Install build dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    build-essential \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev

# Verify Java installation
java -version
# Should show Java 17.x
```

#### 3. Install Buildozer

```bash
# Install Buildozer and Cython
pip3 install --upgrade buildozer cython

# Verify installation
buildozer --version
```

---

### Phase 3: Build APK

#### 1. Navigate to Project in WSL2

```bash
# Access Windows files from WSL2
cd /mnt/c/workspace/train_book

# Verify files
ls -la
# Should see main.py, buildozer.spec, database/, services/, etc.
```

#### 2. First Build (Downloads SDK/NDK)

```bash
# Clean any previous builds
buildozer android clean

# Start first build (takes 20-30 minutes)
buildozer android debug

# The first build will:
# 1. Download Android SDK (~400 MB)
# 2. Download Android NDK (~1 GB)
# 3. Download Python 3.10 for Android
# 4. Compile all dependencies
# 5. Create APK file
```

**Expected Output Location:**
```
bin/trainbook-1.0.0-arm64-v8a-debug.apk
```

#### 3. Subsequent Builds (Much Faster)

```bash
# After first build, subsequent builds take 5-10 minutes
buildozer android debug

# Force rebuild if needed
buildozer android clean
buildozer android debug
```

---

### Phase 4: Deploy to Android Device

#### 1. Enable USB Debugging on Android

1. Go to **Settings** → **About Phone**
2. Tap **Build Number** 7 times (enables Developer Mode)
3. Go to **Settings** → **Developer Options**
4. Enable **USB Debugging**

#### 2. Connect Device and Install APK

```bash
# In WSL2, check if device is connected
adb devices
# Should show: List of devices attached
#              ABC123456789    device

# If "adb: command not found", install it:
sudo apt install android-tools-adb

# Install APK
adb install bin/trainbook-1.0.0-arm64-v8a-debug.apk

# If already installed, reinstall
adb install -r bin/trainbook-1.0.0-arm64-v8a-debug.apk
```

#### 3. Copy APK to Windows for Sharing

```bash
# Copy from WSL2 to Windows Desktop
cp bin/trainbook-1.0.0-arm64-v8a-debug.apk /mnt/c/Users/YOUR_USERNAME/Desktop/

# Or copy to project directory (accessible from Windows)
cp bin/trainbook-1.0.0-arm64-v8a-debug.apk .
```

---

### Phase 5: Post-Installation Setup (Android)

#### 1. Grant Required Permissions

After installing the app, you need to manually grant permissions:

1. **Open App** (may crash first time - this is normal)
2. Go to **Android Settings** → **Apps** → **Train Ticket Reminder**
3. Tap **Permissions**
4. Enable:
   - ✅ **Notifications** (required for reminders)
   - ✅ **Alarms & Reminders** (Android 12+)

#### 2. Disable Battery Optimization (Critical!)

To ensure alarms trigger even when phone is idle:

1. Go to **Settings** → **Apps** → **Train Ticket Reminder**
2. Tap **Battery** or **Battery Usage**
3. Select **Unrestricted** or **Don't Optimize**

#### 3. Test the App

1. Open app
2. Tap "+ Add Reminder"
3. Select a date (must be 60+ days in future)
4. Add a note (e.g., "Test reminder")
5. Save
6. Check if reminder appears in list

---

### Phase 6: Testing Notifications

Since you can't wait 60 days to test, here's how to test manually:

#### Option A: Modify Reminder Date (for testing only)

Edit `utils/date_utils.py` and change line:
```python
reminder_dt = event_dt - timedelta(days=60)
# Change to:
reminder_dt = event_dt - timedelta(minutes=2)  # Test in 2 minutes
```

Then rebuild and test.

#### Option B: Use ADB to View Scheduled Alarms

```bash
# View all scheduled alarms
adb shell dumpsys alarm | grep trainbook

# View app logs
adb logcat | grep python
```

---

## Build Configuration Reference

### buildozer.spec Key Settings

```ini
# App metadata
title = Train Ticket Reminder
package.name = trainbook
package.domain = org.trainbook
version = 1.0.0

# Python requirements
requirements = python3,kivy,pyjnius,android,sqlite3

# Android settings
android.api = 33          # Target Android 13
android.minapi = 21       # Minimum Android 5.0
android.archs = arm64-v8a,armeabi-v7a  # Supports most devices

# Permissions
android.permissions = INTERNET,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,
    SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM
```

---

## Troubleshooting

### Build Issues

#### Error: "buildozer: command not found"
```bash
# Install buildozer in WSL2
pip3 install --upgrade buildozer
```

#### Error: "SDK download failed"
```bash
# Check internet connection
ping google.com

# Try manual SDK download
buildozer android clean
buildozer android debug
```

#### Error: "Java not found"
```bash
# Install Java 17
sudo apt install openjdk-17-jdk

# Verify
java -version
```

#### Error: "Permission denied" on buildozer
```bash
# Fix permissions
chmod +x ~/.buildozer -R
```

### Runtime Issues

#### App crashes on startup
- **Solution**: Grant permissions in Settings → Apps → Train Ticket Reminder

#### Notifications not appearing
- **Solution**: Check notification permission in app settings
- **Solution**: Disable battery optimization for the app

#### Alarms not triggering
- **Solution**: Grant "Alarms & Reminders" permission (Settings → Apps)
- **Solution**: Ensure battery optimization is disabled

#### After reboot, alarms missing
- **Solution**: Check RECEIVE_BOOT_COMPLETED permission is granted

### Testing Issues

#### Can't test 60-day delay
- **Solution**: Modify `timedelta(days=60)` to `timedelta(minutes=2)` for testing
- **Remember**: Change back to 60 days for production!

#### Want to view logs
```bash
# View real-time logs
adb logcat | grep python

# Save logs to file
adb logcat > app_logs.txt
```

---

## Building Release APK (for Play Store)

### 1. Generate Signing Key

```bash
# Create keystore
keytool -genkey -v -keystore trainbook.keystore -alias trainbook \
    -keyalg RSA -keysize 2048 -validity 10000

# Remember the password!
```

### 2. Configure buildozer.spec

```ini
# Add to buildozer.spec
[app]
android.release_artifact = apk

# Sign configuration
android.sign.key = trainbook.keystore
android.sign.alias = trainbook
```

### 3. Build Release APK

```bash
# Build release
buildozer android release

# Output: bin/trainbook-1.0.0-arm64-v8a-release.apk
```

---

## File Size Information

- **APK Size**: ~20-30 MB (single architecture)
- **Installed Size**: ~50-70 MB
- **Database Size**: <1 MB (grows with reminders)

---

## Version Management

To update version:

1. Edit `buildozer.spec`:
   ```ini
   version = 1.0.1
   ```

2. Rebuild:
   ```bash
   buildozer android clean
   buildozer android debug
   ```

---

## Quick Reference Commands

```bash
# Development
& "C:\Program Files\Anaconda3\python.exe" main.py  # Test on Windows

# Building (in WSL2)
cd /mnt/c/workspace/train_book
buildozer android clean                             # Clean build
buildozer android debug                             # Build debug APK

# Deployment
adb devices                                         # Check device
adb install -r bin/*.apk                            # Install APK
adb logcat | grep python                            # View logs
```

---

## Support

For issues or questions:
1. Check the main README.md
2. Review this build guide
3. Check buildozer logs in `.buildozer/`
4. Review Android logcat output
