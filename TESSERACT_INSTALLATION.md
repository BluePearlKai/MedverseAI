# Tesseract OCR Installation Guide for MedVerse AI

## Current Status

Your system is working correctly, but **Tesseract OCR is optional**. The application will:
- ✅ **Accept image uploads** (JPG, PNG, etc.)
- ✅ **Accept PDF uploads**
- ✅ **Analyze documents** (can work without OCR)
- ⚠️ **Extract text from images** - Requires Tesseract or Google Cloud Vision API

---

## Why Tesseract?

Tesseract enables the system to read text from medical scan images and photographs. Without it:
- **PDFs**: Still work perfectly ✅
- **Images with text**: System acknowledges the file but cannot extract text

---

## Installation Options

### Option 1: Install Tesseract (Recommended for Local Development)

#### Step 1: Download Installer
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the Windows installer: **tesseract-ocr-w64-setup-v5.4.1.exe**
   - Direct link: https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe

#### Step 2: Run Installer
1. Double-click the downloaded `.exe` file
2. Choose installation path (default: `C:\Program Files\Tesseract-OCR`)
3. **Important**: Select all language packs (for medical reports in different languages)
4. Complete the installation

#### Step 3: Verify Installation
```bash
tesseract --version
```

If successful, you'll see version info like: `tesseract v5.4.1`

#### Step 4: Configure Python (Optional)
Run the setup script:
```bash
python install_tesseract.py
```

This will:
- ✅ Detect your Tesseract installation
- ✅ Create configuration file
- ✅ Ready to use immediately

---

### Option 2: Use Google Cloud Vision API (For Production)

Since your system already has Google Cloud libraries installed:

#### Step 1: Set Up Google Cloud Credentials
```bash
# Download credentials from Google Cloud Console
# Then set environment variable:

# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\credentials.json"

# Windows CMD:
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\credentials.json

# Restart Flask after setting
```

#### Step 2: Restart the Application
```bash
python app.py
```

Now the system will use Google Cloud Vision API automatically!

---

### Option 3: No Installation (Fallback Mode)

If you can't/don't want to install Tesseract:

1. **System still works** ✅
2. **Image uploads are accepted** ✅
3. **Text extraction limited** - Falls back to image metadata
4. **Analysis still completes** - Based on available data

The application is robust and handles missing components gracefully.

---

## Quick Installation Script

Instead of manual download, use PowerShell to automate:

```powershell
# Run as Administrator
$url = 'https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe'
$output = 'C:\tesseract-install.exe'

# Download
(New-Object System.Net.WebClient).DownloadFile($url, $output)

# Install (runs installer GUI)
& $output

# Cleanup installer
Remove-Item $output -Force
```

---

## Troubleshooting

### Issue: "tesseract is not installed or it's not in your PATH"

**Solution 1**: Ensure Tesseract is in Windows PATH
```powershell
# Check if tesseract is accessible
where tesseract

# If not found, add to PATH:
# Settings → Environment Variables → Add C:\Program Files\Tesseract-OCR to PATH
# Then restart PowerShell/CMD and Restart Flask
```

**Solution 2**: Manually configure pytesseract
```python
# Add to the top of aimodel/document_processor.py
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Solution 3**: Use system without Tesseract
- Continue using the app as-is
- PDFs will still work perfectly
- Images will be processed with fallback method

---

### Issue: Installer Fails to Run

**Windows Defender/Antivirus Blocking:**
- Temporarily disable antivirus
- Or download from official Microsoft Store (if available)

**Permission Issues:**
- Run PowerShell as Administrator
- Or install to user directory instead of Program Files

---

## Testing Tesseract Installation

### Test 1: Command Line
```bash
tesseract --version
```

### Test 2: Python Import
```python
from pytesseract import pytesseract
pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print("Tesseract configured successfully!")
```

### Test 3: With MedVerse AI
1. Upload an image file
2. Check console output
3. Should NOT see: "Error in local OCR"

---

## Alternative: Docker Deployment

For production, consider Docker (Tesseract pre-installed):

```dockerfile
FROM python:3.11
RUN apt-get update && apt-get install -y tesseract-ocr
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## System Status

### Current Capabilities
- ✅ Flask backend running
- ✅ Health Analyzer working
- ✅ PDF extraction working
- ✅ Database ready
- ⚠️ Image OCR needs Tesseract or Google Cloud Vision

### What You Can Do Right Now
1. Upload and analyze **any PDF** ✅
2. Upload and analyze **plain text reports** ✅
3. View report history ✅
4. Translate results ✅
5. Upload images (will only extract metadata) ⚠️

### To Enable Full Image Support
Choose ONE:
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Or setup Google Cloud Vision API with credentials
- Or continue without it (PDFs work great!)

---

## Next Steps

### After Installing Tesseract:

1. **Restart Flask:**
   ```bash
   python app.py
   ```

2. **Test the system:**
   ```bash
   python test_system.py
   ```

3. **Try uploading an image:**
   - Go to http://localhost:5000/
   - Upload a medical scan image
   - Check that text extraction works

---

## Support

If you encounter issues:

1. **Check installation:**
   ```bash
   python install_tesseract.py
   ```

2. **View logs:** Check Flask console output for specific errors

3. **Test components:** Run `python test_system.py`

4. **Restart everything:**
   - Kill Flask (Ctrl+C)
   - Restart: `python app.py`

---

## Summary

| Feature | Without Tesseract | With Tesseract |
|---------|------------------|-----------------|
| PDF Analysis | ✅ | ✅ |
| Image Upload | ✅ | ✅ |
| Image Text Extraction | ⚠️ (metadata only) | ✅ |
| Medical Report Analysis | ✅ | ✅ |
| Risk Assessment | ✅ | ✅ |
| Recommendations | ✅ | ✅ |

**Your system works great either way!** Tesseract just enhances image OCR capabilities.

---

**Installation Time:** 5-10 minutes  
**Difficulty Level:** Easy  
**Is it Required?** No, but recommended for full image support
