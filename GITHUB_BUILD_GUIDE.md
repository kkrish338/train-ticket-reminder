# GitHub Actions - APK Build Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Create GitHub Account
If you don't have one, sign up at: https://github.com/signup

### Step 2: Create New Repository
1. Go to: https://github.com/new
2. Repository name: `train-ticket-reminder`
3. Description: `Android app for train ticket booking reminders`
4. Choose: **Public** (for free unlimited builds)
5. Click "Create repository"

### Step 3: Upload Your Project

**Option A: Using GitHub Desktop (Easiest)**
1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in
3. File → Add Local Repository → Select `c:\workspace\train_book`
4. Publish repository

**Option B: Using Git Command Line**
```powershell
cd c:\workspace\train_book
git init
git add .
git commit -m "Initial commit - Train Ticket Reminder App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/train-ticket-reminder.git
git push -u origin main
```

**Option C: Using GitHub Web Interface (No Git needed)**
1. Open your new repository on GitHub
2. Click "uploading an existing file"
3. Drag and drop ALL files from `c:\workspace\train_book`
4. Click "Commit changes"

### Step 4: Watch the Build
1. Go to your repository on GitHub
2. Click "Actions" tab
3. You'll see the build running automatically
4. Wait 15-25 minutes for first build

### Step 5: Download Your APK
1. When build is complete (green checkmark ✓)
2. Click on the workflow run
3. Scroll down to "Artifacts"
4. Download `train-ticket-reminder-apk`
5. Extract the ZIP file
6. Your APK is inside!

---

## 🎯 What I've Set Up For You

✅ **GitHub Actions Workflow** (`.github/workflows/build-apk.yml`)
   - Automatically builds APK on every code push
   - Uses Ubuntu latest (fast build environment)
   - Installs all dependencies automatically
   - Uploads APK as downloadable artifact

✅ **Automatic Triggers:**
   - Every push to `main` or `master` branch
   - Every pull request
   - Manual trigger from Actions tab
   - Automatic releases on version tags

✅ **Build Process:**
   - Sets up Python 3.10
   - Installs Java 17
   - Configures Android SDK
   - Installs Buildozer & dependencies
   - Builds APK
   - Uploads as artifact

---

## 📥 Getting Your APK After Each Build

### Method 1: Download from Actions
1. Go to: `https://github.com/YOUR_USERNAME/train-ticket-reminder/actions`
2. Click latest successful workflow run (green ✓)
3. Scroll to "Artifacts" section
4. Click "train-ticket-reminder-apk" to download ZIP
5. Extract and install APK on your phone

### Method 2: Create a Release (One-time setup)
1. Create a version tag:
   ```powershell
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. GitHub automatically creates a Release with APK attached
3. Anyone can download from Releases page

---

## 🔄 Making Changes and Rebuilding

Every time you want to update your app:

1. **Make changes** to your code locally
2. **Test on desktop** with: `python main.py`
3. **Upload to GitHub:**
   ```powershell
   git add .
   git commit -m "Updated feature X"
   git push
   ```
4. **GitHub Actions automatically builds new APK**
5. **Download** from Actions tab

---

## ⚙️ Build Settings

The workflow is configured in `.github/workflows/build-apk.yml`

**Build Time:** ~15-25 minutes (first build), ~10-15 minutes (subsequent)

**Free Limits:**
- Public repos: Unlimited builds
- Private repos: 2,000 minutes/month (≈80-120 builds)

**Build Status:** See badge at top of your README on GitHub

---

## 🐛 Troubleshooting

### Build Failed?
1. Check the Actions tab
2. Click the failed workflow
3. Read error messages in logs
4. Common fixes:
   - Missing files: Make sure all files uploaded
   - buildozer.spec errors: Check syntax
   - Dependency issues: Usually auto-fixed on retry

### Can't Download APK?
- Make sure build finished successfully (green ✓)
- Artifacts expire after 90 days (rebuild to get new one)
- Check you're logged into GitHub

### Want Faster Builds?
- Builds run in parallel if you push multiple times
- Use branch protection to build only on merge
- Cache dependencies (advanced)

---

## 🎓 Pro Tips

### Add Build Badge to README
```markdown
![Build Status](https://github.com/YOUR_USERNAME/train-ticket-reminder/workflows/Build%20Android%20APK/badge.svg)
```

### Manual Build Trigger
1. Go to Actions tab
2. Select "Build Android APK" workflow
3. Click "Run workflow"
4. Select branch and click "Run"

### Auto-deploy to Beta Testers
Set up Google Play Console integration (requires Play Store account)

### Build Different Versions
Create different branches (dev, staging, production) for different APK versions

---

## 📊 What Happens During Build

```
1. ✓ Check out your code
2. ✓ Set up Python 3.10
3. ✓ Install Java 17 JDK
4. ✓ Configure Android SDK
5. ✓ Install build tools (gcc, git, etc.)
6. ✓ Install Buildozer & Cython
7. ✓ Download Android NDK (~1GB, cached after first build)
8. ✓ Build APK with python-for-android
9. ✓ Upload APK as artifact
10. ✓ Done! 🎉
```

---

## 🆓 Cost

**FREE Forever** for public repositories!

GitHub Actions is 100% free for open-source projects with unlimited builds.

---

## 🚀 Next Steps

1. Create GitHub account
2. Create new repository
3. Upload your project files
4. Watch the magic happen!
5. Download your APK in 15-25 minutes

No Linux, no WSL, no local setup needed! ✨

---

**Need Help?** Check GitHub Actions documentation or the error logs in the Actions tab.
