# 🚀 Quick Start - Build APK in 3 Steps

## Prerequisites
- Windows 10/11 (64-bit)
- ~5GB free disk space
- Internet connection

---

## Step 1: Install WSL2 Ubuntu

**Open PowerShell as Administrator** (Right-click → Run as Administrator)

```powershell
wsl --install -d Ubuntu-22.04
```

**Then:**
1. Wait for download to complete (~500MB)
2. Restart your computer when prompted
3. Ubuntu will open automatically after restart
4. Create username (e.g., `dev`)
5. Create password (won't show when typing - this is normal)

---

## Step 2: Build the APK

**Option A: Automated (Easiest)**

Open PowerShell (normal, not admin) in `c:\workspace\train_book`:

```powershell
.\BuildAPK.ps1
```

Select option `1` and wait 20-35 minutes.

**Option B: One Command**

```powershell
wsl bash -c "cd /mnt/c/workspace/train_book && chmod +x build_apk.sh && ./build_apk.sh"
```

---

## Step 3: Install on Phone

**Your APK location:**
```
c:\workspace\train_book\bin\trainbook-1.0.0-arm64-v8a-debug.apk
```

**Methods to transfer:**
- USB cable → Copy to phone → Install
- Email to yourself → Download on phone → Install
- WhatsApp to yourself → Download → Install
- Google Drive → Upload → Download on phone → Install

**On phone:**
1. Open the APK file
2. Allow "Install from Unknown Sources" if asked
3. Tap Install
4. Open app
5. Grant Notifications & Alarms permissions

---

## ✅ That's It!

Your app is now installed and ready to use!

**Remember to:**
- Grant all permissions (Notifications, Alarms)
- Disable battery optimization for the app
- Create a test reminder to verify alarms work

---

## 🆘 Having Issues?

See `BUILD_APK_GUIDE.md` for detailed troubleshooting.

**Common fixes:**
- If buildozer not found: `source ~/.bashrc` in WSL
- If build fails: `buildozer android clean` then rebuild
- If out of space: Free up 5GB disk space

---

## 📁 File Overview

- `BuildAPK.ps1` - Windows PowerShell helper script
- `build_apk.sh` - Linux automated build script
- `BUILD_APK_GUIDE.md` - Detailed instructions
- `buildozer.spec` - Android build configuration
- `main.py` - Your app code

---

**Need Help?** Check error messages or see BUILD_APK_GUIDE.md
