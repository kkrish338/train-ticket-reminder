#!/bin/bash
# Automated APK Build Script for Train Ticket Reminder App
# This script handles all dependencies and builds the APK automatically

set -e  # Exit on any error

echo "========================================="
echo "🚂 Train Ticket Reminder - APK Builder"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    print_error "This script must run in WSL (Windows Subsystem for Linux)"
    exit 1
fi

print_success "Running in WSL environment"

# Step 1: Update package list
print_info "Updating package list..."
sudo apt update -qq
print_success "Package list updated"

# Step 2: Check and install Java
print_info "Checking Java installation..."
if ! command -v java &> /dev/null; then
    print_info "Installing Java 17 JDK..."
    sudo apt install -y openjdk-17-jdk > /dev/null 2>&1
    print_success "Java 17 JDK installed"
else
    print_success "Java already installed: $(java -version 2>&1 | head -n 1)"
fi

# Step 3: Install build dependencies
print_info "Installing build tools and dependencies..."
sudo apt install -y \
    build-essential \
    git \
    zip \
    unzip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    python3 \
    python3-pip \
    python3-dev > /dev/null 2>&1
print_success "Build tools installed"

# Step 4: Upgrade pip
print_info "Upgrading pip..."
pip3 install --upgrade pip -q
print_success "Pip upgraded"

# Step 5: Install Buildozer and Cython
print_info "Installing Buildozer and Cython..."
if ! command -v buildozer &> /dev/null; then
    pip3 install buildozer cython -q
    print_success "Buildozer and Cython installed"
else
    print_success "Buildozer already installed"
fi

# Add local bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$PATH:$HOME/.local/bin"
    echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
    print_success "Added ~/.local/bin to PATH"
fi

# Step 6: Verify buildozer is accessible
print_info "Verifying Buildozer installation..."
if ! command -v buildozer &> /dev/null; then
    print_error "Buildozer not found in PATH. Try: source ~/.bashrc"
    exit 1
fi
print_success "Buildozer is ready"

# Step 7: Check if we're in the correct directory
if [ ! -f "main.py" ] || [ ! -f "buildozer.spec" ]; then
    print_error "Cannot find main.py or buildozer.spec in current directory"
    print_info "Please run this script from: /mnt/c/workspace/train_book"
    exit 1
fi
print_success "Found project files"

# Step 8: Clean previous build (optional)
if [ -d ".buildozer" ]; then
    print_info "Previous build found. Cleaning..."
    buildozer android clean > /dev/null 2>&1 || true
    print_success "Build directory cleaned"
fi

# Step 9: Start building APK
echo ""
print_info "========================================="
print_info "🔨 Starting APK Build Process..."
print_info "========================================="
print_info "This will take 20-30 minutes on first build"
print_info "(Downloading Android SDK, NDK, and dependencies)"
echo ""

# Build with verbose output
buildozer -v android debug

# Step 10: Check if build was successful
if [ -d "bin" ] && [ -f "bin/trainbook-1.0.0-arm64-v8a-debug.apk" ]; then
    echo ""
    print_success "========================================="
    print_success "🎉 APK BUILD SUCCESSFUL!"
    print_success "========================================="
    echo ""
    print_success "APK Location:"
    echo "  Linux:   $(pwd)/bin/trainbook-1.0.0-arm64-v8a-debug.apk"
    echo "  Windows: c:\\workspace\\train_book\\bin\\trainbook-1.0.0-arm64-v8a-debug.apk"
    echo ""
    print_success "APK Size: $(ls -lh bin/trainbook-1.0.0-arm64-v8a-debug.apk | awk '{print $5}')"
    echo ""
    print_info "Next Steps:"
    echo "  1. Copy APK to your Android phone"
    echo "  2. Install the APK (allow 'Unknown Sources')"
    echo "  3. Grant Notifications & Alarms permissions"
    echo "  4. Disable battery optimization for the app"
    echo ""
    print_info "See BUILD_APK_GUIDE.md for detailed installation instructions"
else
    echo ""
    print_error "========================================="
    print_error "❌ BUILD FAILED"
    print_error "========================================="
    echo ""
    print_error "APK file was not created"
    print_info "Check the build log above for errors"
    print_info "Common issues:"
    echo "  - Insufficient disk space (need ~5GB)"
    echo "  - Network issues during SDK download"
    echo "  - Missing dependencies"
    echo ""
    print_info "Try running: buildozer android clean"
    print_info "Then run this script again"
    exit 1
fi
