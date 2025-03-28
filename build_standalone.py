"""
Build script to create a standalone executable of the Instagram AI Bot.
This script uses PyInstaller to package the application with all dependencies.
"""

import os
import sys
import subprocess
import shutil
import platform

# Set the output directory to D: drive by default, fallback to current directory/dist
if platform.system() == "Windows" and os.path.exists("D:/"):
    OUTPUT_DIR = "D:/InstagramAIBot"
else:
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def install_dependencies():
    """Install all required dependencies."""
    print("Installing required dependencies...")
    dependencies = [
        "opencv-python",
        "pillow",
        "numpy",
        "requests",
        "python-dotenv",
        "flask",
        "instagrapi",
        "matplotlib"
    ]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)

def create_spec_file():
    """Create a PyInstaller spec file for the application."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/web_interface/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/web_interface/templates', 'src/web_interface/templates'),
        ('src/web_interface/static', 'src/web_interface/static'),
        ('.env.example', '.'),
        ('src/browser_tools', 'src/browser_tools'),
    ],
    hiddenimports=[
        'instagrapi',
        'flask',
        'matplotlib',
        'numpy',
        'cv2',
        'PIL',
        'requests',
        'dotenv',
        'json',
        'os',
        'sys',
        'datetime',
        'random',
        'time',
        're',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='InstagramAIBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InstagramAIBot',
)
"""
    with open("instagram_bot.spec", "w") as f:
        f.write(spec_content)
    print("Created PyInstaller spec file.")

def create_launcher_script():
    """Create a launcher script for the standalone application."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if platform.system() == "Windows":
        launcher_content = """@echo off
echo Starting Instagram AI Bot...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed or not in PATH. Please install Node.js.
    pause
    exit /b 1
)

REM Start the browser tools server in the background
echo Starting Browser Tools Server...
start /b cmd /c "node src/browser_tools/mcp_server.js"

REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul

REM Start the web interface
echo Starting Instagram Bot Web Interface...
echo.
echo The application will open in your default browser shortly...
echo.
echo DO NOT CLOSE THIS WINDOW while using the application!
echo.

REM Start the web interface and open the browser
start http://localhost:5000
InstagramAIBot\InstagramAIBot.exe

echo.
echo Instagram AI Bot has been shut down.
pause
"""
        with open(os.path.join(OUTPUT_DIR, "run_instagram_bot.bat"), "w") as f:
            f.write(launcher_content)
    else:
        launcher_content = """#!/bin/bash
echo "Starting Instagram AI Bot..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js."
    read -p "Press Enter to exit..."
    exit 1
fi

# Start the browser tools server in the background
echo "Starting Browser Tools Server..."
node src/browser_tools/mcp_server.js &

# Wait a moment for the server to start
sleep 2

# Start the web interface
echo "Starting Instagram Bot Web Interface..."
echo
echo "The application will open in your default browser shortly..."
echo
echo "DO NOT CLOSE THIS WINDOW while using the application!"
echo

# Start the web interface and open the browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000
elif command -v open &> /dev/null; then
    open http://localhost:5000
fi

./InstagramAIBot/InstagramAIBot

echo
echo "Instagram AI Bot has been shut down."
read -p "Press Enter to exit..."
"""
        with open(os.path.join(OUTPUT_DIR, "run_instagram_bot.sh"), "w") as f:
            f.write(launcher_content)
        os.chmod(os.path.join(OUTPUT_DIR, "run_instagram_bot.sh"), 0o755)
    
    print("Created launcher script in", OUTPUT_DIR)

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "instagram_bot.spec", "--distpath", OUTPUT_DIR])
    print("Executable built successfully to", OUTPUT_DIR)

def copy_node_files():
    """Copy Node.js files to the distribution directory."""
    print("Copying Node.js files...")
    os.makedirs(os.path.join(OUTPUT_DIR, "src/browser_tools"), exist_ok=True)
    
    # Copy all files from src/browser_tools to dist/src/browser_tools
    for file in os.listdir("src/browser_tools"):
        src_path = os.path.join("src/browser_tools", file)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, os.path.join(OUTPUT_DIR, "src/browser_tools", file))
    
    print("Node.js files copied successfully to", OUTPUT_DIR)

def create_readme():
    """Create a README file for the standalone application."""
    readme_content = """# Instagram AI Bot - Standalone Version

## Requirements
- Node.js must be installed on your system

## How to Use
1. Extract all files to a directory of your choice (can be on a USB drive)
2. Run the launcher script:
   - On Windows: Double-click `run_instagram_bot.bat`
   - On macOS/Linux: Double-click `run_instagram_bot.sh` or run it from terminal

3. The application will start and open in your default web browser
4. Log in to your Instagram account
5. Use the interface to generate and post content

## Important Notes
- DO NOT close the command prompt/terminal window while using the application
- The first time you run the application, you'll need to set up your API keys in the .env file
- All generated images and data will be stored in the application directory

## Troubleshooting
- If the application doesn't start, make sure Node.js is installed
- If you encounter any errors, check the logs in the command prompt/terminal window
"""
    with open(os.path.join(OUTPUT_DIR, "README.txt"), "w") as f:
        f.write(readme_content)
    print("Created README file in", OUTPUT_DIR)

def create_env_file():
    """Create an example .env file for the distribution."""
    env_content = """# Instagram credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# API keys
OPENAI_API_KEY=your_openai_api_key
MIDJOURNEY_API_KEY=your_midjourney_api_key

# Web interface settings
PORT=5000
DEBUG=False

# Optional proxy configuration
# PROXY=http://username:password@proxy-server:port
"""
    with open(os.path.join(OUTPUT_DIR, ".env.example"), "w") as f:
        f.write(env_content)
    print("Created .env.example file in", OUTPUT_DIR)

def build_standalone():
    """Build the standalone application."""
    print("Building standalone Instagram AI Bot...")
    print("Output directory:", OUTPUT_DIR)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Install required packages
    install_pyinstaller()
    install_dependencies()
    
    # Create PyInstaller spec file
    create_spec_file()
    
    # Build executable
    build_executable()
    
    # Copy Node.js files
    copy_node_files()
    
    # Create launcher script
    create_launcher_script()
    
    # Create README file
    create_readme()
    
    # Create example .env file
    create_env_file()
    
    print("")
    print("====================================")
    print("Standalone build completed successfully!")
    print("====================================")
    print(f"The standalone application is available in: {OUTPUT_DIR}")
    print("To run the application:")
    if platform.system() == "Windows":
        print(f"1. Navigate to {OUTPUT_DIR}")
        print("2. Double-click run_instagram_bot.bat")
    else:
        print(f"1. Navigate to {OUTPUT_DIR}")
        print("2. Run ./run_instagram_bot.sh")
    print("====================================")

if __name__ == "__main__":
    build_standalone()