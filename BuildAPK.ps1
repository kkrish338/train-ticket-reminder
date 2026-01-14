# Train Ticket Reminder - APK Builder (Windows PowerShell)
# Quick start script for building Android APK

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Train Ticket Reminder - APK Builder" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if WSL is installed
Write-Host ">> Checking WSL installation..." -ForegroundColor Yellow
$wslCheck = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "X WSL is not installed or not enabled" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install WSL2 with Ubuntu, run PowerShell as Administrator and execute:" -ForegroundColor Yellow
    Write-Host "  wsl --install -d Ubuntu-22.04" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation:" -ForegroundColor Yellow
    Write-Host "  1. Restart your computer" -ForegroundColor White
    Write-Host "  2. Ubuntu will open - create username and password" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "OK WSL is installed" -ForegroundColor Green

# Check if Ubuntu is installed
Write-Host ">> Checking Ubuntu distribution..." -ForegroundColor Yellow
$ubuntuCheck = wsl -l -v 2>&1 | Select-String "Ubuntu"
if (-not $ubuntuCheck) {
    Write-Host "X Ubuntu distribution not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Ubuntu 22.04 with:" -ForegroundColor Yellow
    Write-Host "  wsl --install -d Ubuntu-22.04" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "OK Ubuntu is installed" -ForegroundColor Green

# Check if project files exist
$projectPath = "c:\workspace\train_book"
if (-not (Test-Path "$projectPath\main.py")) {
    Write-Host "X Project files not found at $projectPath" -ForegroundColor Red
    exit 1
}

Write-Host "OK Project files found" -ForegroundColor Green
Write-Host ""

# Offer build options
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Choose an option:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "1. Auto-build APK (Recommended - Installs everything)" -ForegroundColor White
Write-Host "2. Manual build (If auto-build had issues)" -ForegroundColor White
Write-Host "3. Clean and rebuild (If previous build failed)" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "Starting Automated APK Build" -ForegroundColor Cyan
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "This will take 20-35 minutes on first build" -ForegroundColor Yellow
        Write-Host "Please be patient..." -ForegroundColor Yellow
        Write-Host ""
        
        # Make script executable and run
        wsl bash -c "cd /mnt/c/workspace/train_book && chmod +x build_apk.sh && ./build_apk.sh"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=========================================" -ForegroundColor Green
            Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
            Write-Host "=========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your APK is ready at:" -ForegroundColor Green
            Write-Host "  $projectPath\bin\trainbook-1.0.0-arm64-v8a-debug.apk" -ForegroundColor White
            Write-Host ""
            Write-Host "Next: Transfer this APK to your Android phone and install it" -ForegroundColor Yellow
            Write-Host ""
            
            # Offer to open folder
            $openFolder = Read-Host "Open APK folder? (Y/N)"
            if ($openFolder -eq "Y" -or $openFolder -eq "y") {
                explorer "$projectPath\bin"
            }
        } else {
            Write-Host ""
            Write-Host "X Build failed. Check the error messages above." -ForegroundColor Red
            Write-Host ""
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Opening WSL in project directory..." -ForegroundColor Yellow
        Write-Host "Run these commands:" -ForegroundColor Yellow
        Write-Host "  buildozer android debug" -ForegroundColor White
        Write-Host ""
        wsl -d Ubuntu --cd /mnt/c/workspace/train_book
    }
    
    "3" {
        Write-Host ""
        Write-Host "Cleaning previous build..." -ForegroundColor Yellow
        wsl bash -c "cd /mnt/c/workspace/train_book && buildozer android clean"
        Write-Host "OK Cleaned. Now run option 1 to rebuild" -ForegroundColor Green
        Write-Host ""
    }
    
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
