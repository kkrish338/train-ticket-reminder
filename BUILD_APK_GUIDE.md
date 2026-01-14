# 📱 Build APK File - Complete Guide

## Quick Overview
Building an Android APK from Python requires Linux. We'll use WSL2 (Windows Subsystem for Linux) on your Windows machine.

**Time Required:** 30-45 minutes (first time setup + build)

---

## 🚀 Method 1: Automated Setup (Recommended)

I've created an automated script that will handle everything for you.

### Step 1: Install WSL2 Ubuntu
Open PowerShell as **Administrator** and run:
```powershell
wsl --install -d Ubuntu-22.04
```

**What happens:**
- Downloads Ubuntu 22.04 (~500MB)
- Installs WSL2 feature
- **You'll need to restart your computer**

After restart:
- Ubuntu will open automatically
- Create a username (e.g., `dev`)
- Create a password (type it - won't show on screen)

### Step 2: Run the Automated Build Script
Once Ubuntu is ready, run this **ONE COMMAND** in PowerShell:

```powershell
wsl bash -c "cd /mnt/c/workspace/train_book && bash build_apk.sh"
```

**What it does automatically:**
1. ✅ Updates Ubuntu packages
2. ✅ Installs Java 17 JDK
3. ✅ Installs build tools (git, zip, unzip, etc.)
4. ✅ Installs Python 3 and pip
5. ✅ Installs Buildozer and Cython
6. ✅ Builds your APK file

**Time:** 25-35 minutes on first run

### Step 3: Get Your APK
After successful build, your APK will be in:
```
c:\workspace\train_book\bin\trainbook-1.0.0-arm64-v8a-debug.apk
```

Copy it to your phone via:
- USB cable
- Email it to yourself
- Upload to Google Drive
- WhatsApp to yourself

---

## 🔧 Method 2: Manual Step-by-Step

If the automated script has issues, follow these manual steps:

### Step 1: Install WSL2 Ubuntu
```powershell
# Run as Administrator
wsl --install -d Ubuntu-22.04
```
Restart computer, create Ubuntu username/password.

### Step 2: Enter WSL2
```powershell
wsl
```

### Step 3: Navigate to Project
```bash
cd /mnt/c/workspace/train_book
```

### Step 4: Install Dependencies
```bash
# Update package list
sudo apt update

# Install Java 17
sudo apt install -y openjdk-17-jdk

# Install build tools
sudo apt install -y build-essential git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev \
    libssl-dev python3 python3-pip python3-dev

# Install Buildozer
pip3 install --upgrade pip
pip3 install buildozer cython
```

### Step 5: Initialize Buildozer (First Time Only)
```bash
buildozer init
# This creates buildozer.spec (we already have it, so skip or overwrite)
```

### Step 6: Build APK
```bash
buildozer android debug
```

**First build takes 20-30 minutes** because it downloads:
- Android SDK (~200MB)
- Android NDK (~1GB)
- Python-for-Android
- All dependencies

**Subsequent builds:** 2-5 minutes

### Step 7: Find Your APK
```bash
ls -lh bin/
```

Your APK: `trainbook-1.0.0-arm64-v8a-debug.apk`

---

## 📥 Installing APK on Android Phone

### Option A: USB Cable
1. Connect phone to computer
2. Copy APK from `c:\workspace\train_book\bin\` to phone
3. On phone: Open file manager → Downloads
4. Tap the APK file
5. Allow "Install from Unknown Sources" if prompted
6. Tap Install

### Option B: Google Drive / Cloud
1. Upload APK to Google Drive
2. On phone: Open Drive app
3. Download the APK
4. Install from Downloads folder

### Option C: Direct Download
1. Email APK to yourself
2. Open email on phone
3. Download attachment
4. Install APK

---

## ⚙️ Android Permissions Setup

After installing, you MUST grant these permissions:

### 1. Enable Notifications
Settings → Apps → Train Ticket Reminder → Notifications → **ON**

### 2. Enable Alarms & Reminders
Settings → Apps → Train Ticket Reminder → Alarms & reminders → **Allow**

### 3. Disable Battery Optimization
Settings → Apps → Train Ticket Reminder → Battery → **Unrestricted**

**Why?** So alarms work even when phone is sleeping.

---

## 🐛 Troubleshooting

### "buildozer: command not found"
```bash
# Add to PATH
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### "Permission denied" errors
```bash
# Make build script executable
chmod +x build_apk.sh
```

### Build fails with "Java not found"
```bash
# Check Java version
java -version

# If not installed:
sudo apt install -y openjdk-17-jdk
```

### Out of disk space
```bash
# Check available space
df -h

# WSL needs ~5GB free for first build
```

### "Recipe not found" errors
```bash
# Clean and rebuild
buildozer android clean
buildozer android debug
```

---

## 📊 Build Status Indicators

During build, you'll see:
- `[INFO]` - Normal progress messages
- `[WARNING]` - Non-critical issues (usually okay)
- `[ERROR]` - Build failed (need to fix)

**Success message:**
```
# Android packaging done!
# APK trainbook-1.0.0-arm64-v8a-debug.apk available in the bin directory
```

---

## 🎯 Quick Command Reference

```bash
# Enter WSL
wsl

# Navigate to project
cd /mnt/c/workspace/train_book

# Build APK
buildozer android debug

# Clean build (if errors)
buildozer android clean

# Build for release (signed)
buildozer android release

# Check logs
cat .buildozer/android/platform/build-arm64-v8a/build.log
```

---

## 🚀 Next Steps After Build

1. **Test on Android device** - Install and verify all features work
2. **Test alarms** - Create a test reminder for near future
3. **Grant all permissions** - Especially alarms and notifications
4. **Share with others** - APK can be installed on any Android phone
5. **Consider Play Store** - For release build with signing key

---

## 📦 Release Build (For Distribution)

To create a signed release APK for Play Store:

```bash
# Generate signing key
keytool -genkey -v -keystore train-ticket-key.keystore -alias trainbook \
    -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
buildozer android release

# APK will be: bin/trainbook-1.0.0-arm64-v8a-release-unsigned.apk
```

Then sign it with your keystore before uploading to Play Store.

---

## ✅ Success Checklist

- [ ] WSL2 Ubuntu installed
- [ ] Dependencies installed (Java, build tools, Python)
- [ ] Buildozer installed
- [ ] APK built successfully
- [ ] APK copied to phone
- [ ] APK installed on phone
- [ ] All permissions granted
- [ ] Test alarm created and verified

---

**Need Help?** Check the error messages in the build log or the troubleshooting section above.
