# MedVerse AI - Medical Document Processing & Analysis

## Overview

This document explains the two new Python modules and the updated Flask endpoints for medical document processing and disease identification.

---

## 1. Document Processor Module (`aimodel/document_processor.py`)

### Purpose
Handles reading and extracting text from medical PDFs and images using Google Cloud Vision API with fallback to local OCR.

### Key Classes & Methods

#### `DocumentProcessor` Class

**`__init__()`**
- Initializes Google Cloud Vision API client
- Gracefully handles initialization failures with fallback mode

**`extract_text_from_image(image_path)`**
- Extracts text from image files using Google Cloud Vision API
- Falls back to local OCR if Vision API unavailable
- Supports: JPG, PNG, BMP, GIF, TIFF formats
- Returns: Extracted text as string

**`extract_text_from_pdf(pdf_path)`**
- Extracts text from PDF files using PyPDF2
- Processes all pages in the PDF
- Returns: Complete text content from all pages

**`process_document(file_path)`**
- Main method to process any medical document
- Auto-detects file type (PDF or Image)
- Returns Dictionary with:
  - `success`: Boolean indicating if processing succeeded
  - `file_name`: Original filename
  - `file_type`: Type of document (pdf/image)
  - `extracted_text`: Extracted text content
  - `error`: Error message if failed

**`extract_biomarkers(text)`**
- Scans medical text for common biomarkers
- Identifies: Cholesterol, Blood Sugar, Blood Pressure, WBC, Hemoglobin, etc.
- Returns: Dictionary of detected biomarkers

### Usage Example
```python
from aimodel.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_document('/path/to/medical_report.pdf')

if result['success']:
    print(result['extracted_text'])
    biomarkers = processor.extract_biomarkers(result['extracted_text'])
    print(biomarkers)
```

---

## 2. Health Analyzer Module (`aimodel/health_analyzer.py`)

### Purpose
Analyzes medical data to identify diseases, assess risk levels, and generate recommendations.

### Key Classes & Methods

#### `HealthAnalyzer` Class

**`__init__()`**
- Loads disease profiles and risk factor thresholds
- Initializes 8 disease profiles: Hypertension, High Cholesterol, Diabetes, Anemia, Infection, Kidney Disease, Electrolyte Imbalance, Cardiovascular Risk

**`analyze_report(report_text, biomarkers=None)`**
- Analyzes medical report text against disease profiles
- Uses keyword matching and biomarker detection
- Returns Dictionary with:
  - `identified_diseases`: List of detected diseases with confidence scores
  - `risk_level`: Overall risk level (Low/Moderate/High)
  - `risk_score`: Numeric risk score (0-3)
  - `recommendations`: Personalized health recommendations
  - `summary`: Human-readable analysis summary
  - `doctor_questions`: Top 3 questions for healthcare provider

**`generate_report_data(report_text, biomarkers=None, file_name="")`**
- Generates complete report ready for frontend display
- Returns Dictionary formatted for result.html display
- Includes all analysis data plus metadata

**`_generate_summary(diseases, risk_level)`**
- Creates human-readable summary of findings
- Includes primary/secondary diagnoses and risk level

**`_generate_doctor_questions(diseases)`**
- Generates targeted questions based on identified conditions
- Helps patients prepare for doctor visits

### Disease Profiles

Each disease has:
- **Keywords**: Terms that indicate the disease is present
- **Biomarkers**: Medical measurements associated with disease
- **Risk Level**: 1-3 scale for severity
- **Recommendations**: Specific medical recommendations

Example: Hypertension
```json
{
  "keywords": ["blood pressure", "bp", "160", "150", "140", "130"],
  "risk_level": 3,
  "recommendations": [
    "Reduce sodium intake",
    "Maintain regular exercise",
    "Monitor blood pressure daily",
    "Consult cardiologist"
  ]
}
```

### Usage Example
```python
from aimodel.health_analyzer import HealthAnalyzer

analyzer = HealthAnalyzer()
report_text = "Patient has elevated blood pressure 160/90 and high cholesterol 240"
analysis = analyzer.analyze_report(report_text)

print(analysis['risk_level'])  # 🔴 High Risk
print(analysis['identified_diseases'])  # [Hypertension, High Cholesterol]
print(analysis['recommendations'])  # [Reduce sodium, ...]
```

---

## 3. Updated Flask Endpoints (`app.py`)

### New Dependencies
- `google-cloud-vision`: Image text extraction
- `PyPDF2`: PDF text extraction
- `Pillow`: Image processing
- `pytesseract`: Local OCR fallback
- `werkzeug`: File handling
- `sqlite3`: Database (built-in)

### Authentication Endpoints

#### `POST /signup`
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```
**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "message": "Welcome John Doe! Account created successfully."
}
```

#### `POST /login`
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "John Doe",
  "message": "Welcome back, John Doe!"
}
```

### File Upload & Analysis Endpoints

#### `POST /upload`
**Description:** Upload and analyze medical document

**Request (multipart/form-data):**
- `report_file`: PDF or Image file (required)
- `user_id`: User ID (required)

**Response:**
```json
{
  "success": true,
  "file_name": "20260327_120530_report.pdf",
  "analysis": {
    "summary": "Risk Assessment: 🔴 High Risk. Primary finding: Hypertension...",
    "risk_level": "🔴 High Risk",
    "risk_score": 2.75,
    "identified_diseases": [
      {
        "name": "Hypertension",
        "confidence": 0.95
      },
      {
        "name": "High Cholesterol",
        "confidence": 0.75
      }
    ],
    "recommendations": [
      "Reduce sodium intake...",
      "Maintain regular exercise...",
      "Monitor blood pressure daily..."
    ],
    "doctor_questions": [
      "What is my current risk level?",
      "Should I take medications?",
      "What lifestyle changes should I make?"
    ]
  }
}
```

#### `POST /analyze`
**Description:** Analyze plain text medical data

**Request:**
```json
{
  "text": "Patient blood pressure: 160/90, Cholesterol: 250",
  "file_name": "manual_report"
}
```
**Response:** Same as /upload analysis object

### Report History Endpoints

#### `GET /history/<user_id>`
**Description:** Get user's report history

**Response:**
```json
[
  {
    "id": 1,
    "file_name": "20260327_120530_report.pdf",
    "upload_date": "2026-03-27 12:05:30",
    "risk_level": "🔴 High Risk",
    "summary": "Risk Assessment: High Risk..."
  },
  {
    "id": 2,
    "file_name": "20260326_150215_scan.jpg",
    "upload_date": "2026-03-26 15:02:15",
    "risk_level": "🟢 Low Risk",
    "summary": "Your medical report shows normal..."
  }
]
```

#### `GET /report/<report_id>`
**Description:** Get detailed view of specific report

**Response:**
```json
{
  "file_name": "report.pdf",
  "upload_date": "2026-03-27 12:05:30",
  "analysis": {
    "summary": "...",
    "risk_level": "...",
    "identified_diseases": [...],
    ...
  }
}
```

---

## 4. Database Schema (`medverse.db`)

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Reports Table
```sql
CREATE TABLE reports (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id INTEGER NOT NULL,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  analysis_result TEXT,  -- JSON string
  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
)
```

---

## 5. Integration with Frontend

### How result.html displays data:

The analysis results are automatically populated in [result.html](result.html):

- **Summary Text** → `typingText` element (animated out)
- **Risk Level** → `riskLabel` element (color-coded)
- **Doctor Questions** → `q1`, `q2`, `q3` elements
- **Recommendations** → Available via script for display

### JavaScript Integration:

The upload function in script.js now:
1. Calls `/upload` endpoint with file and user_id
2. Receives complete analysis
3. Stores in localStorage
4. Triggers animation on result.html

Example JavaScript:
```javascript
const response = await fetch('http://127.0.0.1:5000/upload', {
    method: 'POST',
    body: formData  // Contains file + user_id
});
const result = await response.json();
// result.analysis contains risk_level, summary, recommendations
```

---

## 6. Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Google Cloud Vision (Optional)
If using Vision API for OCR:
```bash
# Install Tesseract OCR (required for pytesseract)
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

### Step 3: Setup Google Cloud Credentials
```bash
# Set environment variable for Google credentials
# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\credentials.json"

# Or Linux/Mac:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Step 4: Run Flask App
```bash
python app.py
```

---

## 7. Risk Assessment Logic

### Risk Score Calculation:
- **0-1.5**: 🟢 Low Risk
- **1.5-2.5**: 🟡 Moderate Risk  
- **2.5+**: 🔴 High Risk

### Confidence Scoring:
- Keyword match: +0.2 per keyword found
- Biomarker match: +0.4 per biomarker found
- Maximum: 1.0 (100%)

---

## 8. Supported Medical Biomarkers

- Cholesterol (Total, LDL, HDL)
- Blood Sugar (Glucose, Fasting, HbA1c)
- Blood Pressure (Systolic, Diastolic)
- White Blood Cells (WBC, Leukocytes)
- Hemoglobin (Hb, HbG)
- Triglycerides
- Creatinine
- Sodium
- Potassium

---

## 9. Error Handling

All endpoints return appropriate HTTP status codes:
- **200**: Successful request
- **201**: Resource created (signup)
- **400**: Bad request (missing fields)
- **401**: Unauthorized (wrong credentials)
- **404**: Resource not found
- **409**: Conflict (email exists)
- **413**: Payload too large (file > 50MB)
- **503**: Service unavailable

---

## 10. Security Notes

⚠️ **Current Version**: Uses plain-text password storage for simplicity. 

**For Production:**
- Use `bcrypt` or `argon2` for password hashing
- Implement JWT tokens instead of user_id
- Add HTTPS/SSL support
- Implement rate limiting
- Add input validation/sanitization
- Use environment variables for sensitive data

---

## Support & Troubleshooting

### Issue: Google Vision API not working
**Solution**: Ensure credentials are set. Falls back to local pytesseract.

### Issue: Tesseract not found
**Solution**: Install Tesseract OCR from GitHub (Windows) or apt/brew (Linux/Mac)

### Issue: File upload fails
**Solution**: Check file size (< 50MB), format (PDF/Image), and permissions

---

**Created**: March 2026
**Framework**: Flask 2.0+
**Python**: 3.8+
