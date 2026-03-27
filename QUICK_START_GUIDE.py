"""
QUICK START GUIDE - MedVerse AI Medical Processing
===================================================

This file provides quick reference examples for using the new medical processing features.
"""

# ========================= SETUP INSTRUCTIONS =========================

"""
1. Install Dependencies:
   pip install -r requirements.txt

2. Set Google Cloud Credentials (Optional, needed for Vision API):
   Windows: $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\credentials.json"
   Linux/Mac: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

3. Create uploads folder (automatically created by Flask):
   - The app will create 'uploads' folder on first run
   - Make sure Flask has write permissions

4. Run the Flask app:
   python app.py
   
   The server will start at http://127.0.0.1:5000
"""

# ========================= API USAGE EXAMPLES =========================

"""
1. USER REGISTRATION
   POST http://127.0.0.1:5000/signup
   
   Request Body:
   {
     "email": "patient@example.com",
     "password": "secure_password",
     "name": "John Patient"
   }
   
   Response:
   {
     "success": true,
     "user_id": 1,
     "message": "Welcome John Patient! Account created successfully."
   }
"""

"""
2. USER LOGIN
   POST http://127.0.0.1:5000/login
   
   Request Body:
   {
     "email": "patient@example.com",
     "password": "secure_password"
   }
   
   Response:
   {
     "success": true,
     "user_id": 1,
     "name": "John Patient",
     "message": "Welcome back, John Patient!"
   }
"""

"""
3. UPLOAD MEDICAL DOCUMENT & ANALYZE
   POST http://127.0.0.1:5000/upload
   Content-Type: multipart/form-data
   
   Parameters:
   - report_file: [PDF or Image file]
   - user_id: 1
   
   Response:
   {
     "success": true,
     "file_name": "20260327_120530_blood_test.pdf",
     "analysis": {
       "summary": "Risk Assessment: 🔴 High Risk. Primary finding: Hypertension...",
       "risk_level": "🔴 High Risk",
       "risk_score": 2.8,
       "identified_diseases": [
         {"name": "Hypertension", "confidence": 0.95},
         {"name": "High Cholesterol", "confidence": 0.75}
       ],
       "recommendations": [
         "Reduce sodium intake (< 2,300mg/day)",
         "Maintain regular exercise (150 min/week)",
         "Monitor blood pressure daily"
       ],
       "doctor_questions": [
         "What is my current risk level?",
         "Do I need medications?",
         "What lifestyle changes are important?"
       ],
       "biomarkers": {
         "blood_pressure": "Present",
         "cholesterol": "Present"
       }
     }
   }
"""

"""
4. ANALYZE PLAIN TEXT REPORT
   POST http://127.0.0.1:5000/analyze
   Content-Type: application/json
   
   Request Body:
   {
     "text": "Blood pressure: 160/90 mmHg, Total Cholesterol: 280 mg/dL, HDL: 35 mg/dL",
     "file_name": "manual_entry"
   }
   
   Response: Same as upload response
"""

"""
5. GET USER REPORT HISTORY
   GET http://127.0.0.1:5000/history/1
   (Replace 1 with actual user_id)
   
   Response:
   [
     {
       "id": 1,
       "file_name": "20260327_120530_report.pdf",
       "upload_date": "2026-03-27 12:05:30",
       "risk_level": "🔴 High Risk",
       "summary": "Risk Assessment: High Risk. Primary finding: Hypertension..."
     },
     {
       "id": 2,
       "file_name": "20260326_150215_checkup.jpg",
       "upload_date": "2026-03-26 15:02:15",
       "risk_level": "🟢 Low Risk",
       "summary": "Your medical report shows normal parameters..."
     }
   ]
"""

"""
6. GET DETAILED REPORT
   GET http://127.0.0.1:5000/report/1
   (Replace 1 with actual report_id)
   
   Response:
   {
     "file_name": "blood_test.pdf",
     "upload_date": "2026-03-27 12:05:30",
     "analysis": {
       "summary": "...",
       "risk_level": "...",
       "identified_diseases": [...],
       "recommendations": [...],
       "doctor_questions": [...]
     }
   }
"""

# ========================= PYTHON CODE EXAMPLES =========================

# Example 1: Direct Document Processing
from aimodel.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Process an image
image_result = processor.process_document('path/to/medical_scan.jpg')
if image_result['success']:
    print(f"Extracted text from {image_result['file_name']}")
    print(image_result['extracted_text'][:200])  # First 200 chars
    
    # Extract biomarkers
    biomarkers = processor.extract_biomarkers(image_result['extracted_text'])
    print(f"Biomarkers found: {biomarkers}")

# Process a PDF
pdf_result = processor.process_document('path/to/lab_report.pdf')
if pdf_result['success']:
    print(f"Successfully read PDF: {pdf_result['file_type']}")

# Example 2: Health Analysis
from aimodel.health_analyzer import HealthAnalyzer

analyzer = HealthAnalyzer()

medical_text = """
Patient Lab Results:
- Blood Pressure: 165/95 mmHg
- Total Cholesterol: 270 mg/dL
- LDL Cholesterol: 180 mg/dL
- Blood Sugar (Fasting): 140 mg/dL
- White Blood Cells: 11,500/µL
- Hemoglobin: 14.5 g/dL
"""

analysis = analyzer.analyze_report(medical_text)

print(f"Risk Level: {analysis['risk_level']}")
print(f"Risk Score: {analysis['risk_score']}")
print(f"Identified Diseases: {[d['disease'] for d in analysis['identified_diseases']]}")
print(f"Summary: {analysis['summary']}")
print(f"Top Recommendations:")
for rec in analysis['recommendations'][:3]:
    print(f"  - {rec}")
print(f"Questions for Doctor:")
for q in analysis['doctor_questions']:
    print(f"  - {q}")

# Example 3: Full Pipeline
def process_and_analyze_medical_document(file_path):
    """Complete pipeline: extract text and analyze"""
    
    # Step 1: Extract text from document
    processor = DocumentProcessor()
    doc_result = processor.process_document(file_path)
    
    if not doc_result['success']:
        print(f"Error: {doc_result['error']}")
        return None
    
    # Step 2: Extract biomarkers
    text = doc_result['extracted_text']
    biomarkers = processor.extract_biomarkers(text)
    
    # Step 3: Analyze health
    analyzer = HealthAnalyzer()
    analysis = analyzer.generate_report_data(text, biomarkers, doc_result['file_name'])
    
    return analysis

# Usage
result = process_and_analyze_medical_document('path/to/blood_test.pdf')
if result:
    print("Analysis Complete!")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Summary: {result['summary']}")

# ========================= FRONTEND INTEGRATION =========================

"""
The JavaScript frontend has been updated to:

1. Send files to /upload endpoint:
   - Calls fakeUpload() on click
   - Sends file + user_id to backend
   - Receives analysis results

2. Display results on result.html:
   - Shows summary in animated typing effect
   - Displays risk level with color coding
   - Shows doctor questions
   - Enables translation to other languages

3. Store reports in database:
   - Saves file and analysis in SQLite
   - Users can view history on reports.html
   - Can retrieve any previous report

Example script.js integration (already implemented):
- login() sends credentials to /login
- fakeUpload() sends file to /upload
- loadReports() fetches /history/{user_id}
"""

# ========================= DISEASE IDENTIFICATION MATRIX =========================

"""
The system identifies the following diseases:

1. HYPERTENSION (High Blood Pressure)
   Keywords: blood pressure, bp, 160, 150, 140, 130
   Risk Level: 🔴 High (3/3)
   Recommendations: Reduce sodium, exercise, monitor BP

2. HIGH CHOLESTEROL
   Keywords: cholesterol, ldl, hdl, lipid, 240
   Risk Level: 🟡 Moderate (2/3)
   Recommendations: Reduce fat, add fiber, statins if needed

3. DIABETES
   Keywords: glucose, blood sugar, 126, 200, insulin, hba1c
   Risk Level: 🔴 High (3/3)
   Recommendations: Monitor glucose, low GI diet, medications

4. ANEMIA
   Keywords: hemoglobin, hb, 7, 8, 9, red blood cells
   Risk Level: 🟡 Moderate (2/3)
   Recommendations: Iron supplements, iron-rich foods

5. INFECTION
   Keywords: white blood cells, wbc, fever, bacterial
   Risk Level: 🟡 Moderate (2/3)
   Recommendations: Rest, hydration, antibiotics

6. KIDNEY DISEASE
   Keywords: creatinine, kidney, gfr, proteinuria
   Risk Level: 🔴 High (3/3)
   Recommendations: Limit protein, control BP, consult nephrologist

7. ELECTROLYTE IMBALANCE
   Keywords: sodium, potassium, na, k, imbalance
   Risk Level: 🟡 Moderate (2/3)
   Recommendations: Monitor fluids, supplements, dietary changes

8. CARDIOVASCULAR RISK
   Keywords: heart, cardiac, chest pain, triglycerides
   Risk Level: 🔴 High (3/3)
   Recommendations: Avoid strenuous activity, cardiac meds
"""

# ========================= FILE UPLOAD SPECIFICATIONS =========================

"""
SUPPORTED FILE FORMATS:
- PDF: *.pdf (any size up to 50MB)
- Images: *.jpg, *.jpeg, *.png, *.bmp, *.gif, *.tiff

TEXT EXTRACTION METHOD:
- PDFs: PyPDF2 (Python native)
- Images: Google Cloud Vision API (with pytesseract fallback)

FILE SIZE LIMITS:
- Maximum: 50 MB per file
- Server returns 413 error if exceeded
- Recommended: Keep under 10 MB for faster processing

PROCESSING TIME:
- PDFs: 1-3 seconds
- Images: 2-5 seconds (with Vision API)
- Analysis: < 1 second
"""

# ========================= TROUBLESHOOTING =========================

"""
COMMON ISSUES & SOLUTIONS:

1. "Module not found: DocumentProcessor"
   Solution: Make sure aimodel/document_processor.py exists
   Check: ls aimodel/ or dir aimodel\

2. "Google Vision API not initialized"
   Solution: This is normal - the system uses pytesseract fallback
   To enable Vision API:
   - Set up Google Cloud credentials
   - Run: pip install google-cloud-vision

3. "File upload returns 413 error"
   Solution: File is too large (> 50MB)
   Fix: Compress or split your document

4. "No text could be extracted"
   Reasons: 
   - Low quality document image
   - Handwritten text (Vision API struggles)
   - Scanned document without OCR layer
   Solution: Use higher quality scans or printed documents

5. "Port 5000 already in use"
   Solution: 
   - Kill process: lsof -ti:5000 | xargs kill -9 (Linux/Mac)
   - Or change port: app.run(port=5001)

6. "database is locked"
   Solution: 
   - Close other database connections
   - Delete medverse.db-journal if exists
   - Restart Flask app
"""

# ========================= PERFORMANCE TIPS =========================

"""
OPTIMIZATION SUGGESTIONS:

1. DATABASE INDEXING:
   Add indexes for faster queries:
   CREATE INDEX idx_user_id ON reports(user_id);
   CREATE INDEX idx_upload_date ON reports(upload_date);

2. CACHING:
   Cache frequently accessed analysis:
   - Use Redis for session data
   - Cache biomarker patterns
   - Store common disease profiles in memory

3. PREPROCESS DOCUMENTS:
   - Convert to high contrast before OCR
   - Split large PDFs into pages
   - Use compression for image uploads

4. ASYNC PROCESSING:
   For production, use async jobs:
   - Celery for background processing
   - Queue long-running analysis tasks
"""

print("MedVerse AI - Medical Processing Setup Complete!")
print("Refer to MEDICAL_PROCESSING_DOCS.md for detailed documentation")
