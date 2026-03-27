"""
Tesseract OCR Installation Helper for Windows
Run this script to install Tesseract and configure it properly
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path


def check_tesseract_installed():
    """Check if tesseract is already installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Tesseract is already installed!")
            print(result.stdout.split('\n')[0])
            return True
    except FileNotFoundError:
        pass
    return False


def find_tesseract_path():
    """Find tesseract installation path"""
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\%s\AppData\Local\Tesseract-OCR\tesseract.exe' % os.getenv('USERNAME'),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Check registry
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r'SOFTWARE\Tesseract-OCR')
        path, _ = winreg.QueryValueEx(key, 'InstallationDirectory')
        tesseract_path = os.path.join(path, 'tesseract.exe')
        if os.path.exists(tesseract_path):
            return tesseract_path
    except:
        pass
    
    return None


def configure_tesseract():
    """Configure pytesseract to use tesseract"""
    tesseract_path = find_tesseract_path()
    
    if not tesseract_path:
        print("✗ Tesseract not found in standard locations")
        return False
    
    # Create configuration file
    config_code = f"""
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'{tesseract_path}'
"""
    
    config_file = os.path.join(os.path.dirname(__file__), 'tesseract_config.py')
    
    with open(config_file, 'w') as f:
        f.write(config_code)
    
    print(f"✓ Tesseract configured at: {tesseract_path}")
    print(f"✓ Configuration file created: {config_file}")
    return True


def main():
    print("\n" + "=" * 60)
    print("Tesseract OCR Installation Helper")
    print("=" * 60 + "\n")
    
    # Check if already installed
    if check_tesseract_installed():
        print("\nConfiguring pytesseract...")
        if configure_tesseract():
            print("\n✓ Tesseract is ready to use!")
            return 0
        else:
            print("\n⚠️  Could not configure tesseract")
            return 1
    
    print("Tesseract is not installed.")
    print("\n" + "=" * 60)
    print("INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    print("""
1. Download Tesseract Installer:
   https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe

2. Run the installer:
   - Double-click tesseract-ocr-w64-setup-v5.4.1.exe
   - During installation:
     * Accept the default installation path: C:\\Program Files\\Tesseract-OCR
     * Install all language packs (especially if processing non-English documents)
     * Complete the installation

3. After Installation:
   - Restart this Python script to confirm installation
   - Or restart your Flask server: python app.py

4. Alternative - Use Docker:
   If installation is problematic, consider using Docker:
   - Docker image with Tesseract pre-installed
   - No system dependencies to manage
   
5. Alternative - Use Cloud OCR Only:
   - Set up Google Cloud Vision API credentials
   - System will use Vision API instead of Tesseract
   - Set: export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
    """.strip())
    
    print("\n" + "=" * 60)
    print("Quick Installation via Command Line (Requires Admin)")
    print("=" * 60)
    print("""
Windows PowerShell (Run as Administrator):
    $url = 'https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe'
    $output = 'C:\\tesseract-install.exe'
    (New-Object System.Net.WebClient).DownloadFile($url, $output)
    & $output
    """.strip())
    
    print("\n" + "=" * 60)
    print("Verify Installation")
    print("=" * 60)
    print("""
After installing, verify it works:
    python -c "import pytesseract; from PIL import Image; print(pytesseract.image_to_string(Image.open('test.png')))"
    """.strip())
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
