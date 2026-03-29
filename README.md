🩺 MedVerse AI

Intelligent Medical Report Analysis Made Simple

<p align="center"> <img src="docs/logo-placeholder.png" alt="MedVerse AI Logo" width="180"/> </p> <p align="center"> <b>Transform complex medical reports into clear, actionable health insights.</b><br> OCR • Risk Analysis • Multi-language Support • Patient Empowerment </p>
📘 Introduction

Medical reports are often complex, technical, and difficult for patients to interpret. Many individuals struggle to understand key biomarkers, risk indicators, and medical terminology — especially when reports are written in English or filled with dense medical jargon.

MedVerse AI bridges this gap by transforming medical reports into clear, understandable health insights.

Using OCR, rule-based analysis, and multi-language translation, MedVerse AI helps patients:

Understand their medical data
Identify potential health risks
Prepare informed questions for doctors
Access insights in their native language

MedVerse AI is designed as a patient-support tool, not a diagnostic replacement.
✨ Features
🔍 Automated OCR Processing
Extracts text from:
PDF medical reports
Scanned lab reports
Medical images
Uses:
Google Cloud Vision API
Pytesseract OCR Engine
🧠 Health Risk Assessment
Identifies key biomarkers
Evaluates risk levels:
🟢 Low Risk
🟡 Moderate Risk
🔴 High Risk
Generates:
Confidence scores
Condition-specific insights
Preventive recommendations

Supported Disease Profiles:

Hypertension
Diabetes
Anemia
Thyroid Disorders
Liver Conditions
Kidney Disorders
Cardiovascular Risk
General Wellness Indicators
🩺 Doctor-Ready Question Generator

Automatically generates personalized questions such as:

"Should I monitor my blood pressure more frequently?"
"Are dietary changes recommended for my glucose levels?"
"Do I need further diagnostic tests?"

This helps patients have more productive medical consultations.

🌐 Multi-Language Support (22 Indian Languages)
Translates medical explanations into regional languages
Powered by Google Cloud Translation API
Makes healthcare insights accessible to diverse populations

Supported Examples:

Hindi
Tamil
Bengali
Marathi
Telugu
Gujarati
Kannada
Malayalam
Punjabi
Odia
And more...
🔐 Secure Health History Dashboard

Users can:

Track previous reports
Compare health trends
Revisit analysis results
Maintain structured health records
🏗️ Tech Stack
Backend
Python (Flask)
Frontend
HTML5
CSS3 (Glassmorphism UI Design)
Vanilla JavaScript
Databases
MySQL
User authentication
Profile management
SQLite
Medical report metadata
Analysis history
AI / ML Components
Google Cloud Vision API (OCR)
Pytesseract OCR
Google Cloud Translation API
Custom RAG Engine
JSON-based knowledge base (medical_data.json)
Rule-Based Health Analyzer
📂 Project Structure
MedVerse-AI/
│
├── app.py
│   Flask application entry point
│   Handles routes for:
│   - Authentication
│   - Uploads
│   - History
│   - Chat Interface
│
├── aimodel/
│   Core AI processing package
│
│   ├── document_processor.py
│   │   Handles OCR and text extraction
│   │
│   ├── health_analyzer.py
│   │   Maps biomarkers to:
│   │   - Disease risks
│   │   - Recommendations
│   │
│   ├── translate_me.py
│       Multi-language translation pipeline
│
├── assets/
│   Frontend resources
│   - CSS
│   - JavaScript
│
├── uploads/
│   Temporary storage for uploaded reports
│
├── medical_data.json
│   Knowledge base used by RAG engine
│
├── requirements.txt
│   Python dependencies
│
└── README.md
🚀 Getting Started
📌 Prerequisites

Ensure the following are installed:

Python 3.9+
MySQL Server
Tesseract OCR
Google Cloud Account
pip (Python Package Manager)
🔧 Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/MedVerse-AI.git

cd MedVerse-AI
2️⃣ Create Virtual Environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Install Tesseract OCR
Windows:

Download from:
https://github.com/tesseract-ocr/tesseract

Linux:
sudo apt install tesseract-ocr
macOS:
brew install tesseract
5️⃣ Configure Google Cloud APIs

Enable:

Vision API
Translation API

Set credentials:

export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
6️⃣ Setup MySQL Database

Create database:

CREATE DATABASE medverse_users;

Update credentials in:

app.py
7️⃣ Run Application
python app.py

Access:

http://127.0.0.1:5000
🧪 Usage
Step-by-Step Workflow
Register a new user account
Login to dashboard
Upload medical report (PDF/Image)
System extracts report text
Health risks are analyzed
Results are translated (optional)
Insights saved to history
Example Upload Types

Supported Formats:

.pdf
.png
.jpg
.jpeg
🧠 Architecture & Data Flow
User Upload
     │
     ▼
Document Processor
(OCR Engine)
     │
     ▼
Text Extraction
     │
     ▼
Health Analyzer
(Rule-Based Engine)
     │
     ▼
Risk Assessment
     │
     ▼
RAG Knowledge Engine
(JSON-based)
     │
     ▼
Translation Layer
(Google API)
     │
     ▼
User Dashboard Output
🔄 Core Processing Pipeline
1️⃣ Upload Stage

User uploads a medical report.

2️⃣ OCR Stage

document_processor.py extracts readable text.

3️⃣ Analysis Stage

health_analyzer.py:

Identifies biomarkers
Maps thresholds
Determines risk levels
4️⃣ Knowledge Retrieval

RAG engine retrieves relevant medical explanations.

5️⃣ Translation

translate_me.py converts content to selected language.

6️⃣ Visualization

Frontend renders:

Risk levels
Insights
Doctor questions
🔐 Security Considerations

MedVerse AI includes:

User authentication via MySQL
Secure session handling
Isolated medical metadata storage
Temporary file upload handling
User-based history access

Recommended Enhancements:

HTTPS deployment
File encryption
Rate limiting
JWT-based authentication
Role-based access control
⚠️ Medical Disclaimer

MedVerse AI is NOT a medical diagnosis tool.

This system:

Provides informational insights
Highlights possible risk indicators
Suggests discussion points

This system DOES NOT:

Diagnose diseases
Replace doctors
Provide treatment plans

Always consult a licensed medical professional for:

Diagnosis
Treatment
Medical decisions
📈 Future Enhancements

Planned roadmap:

📊 Trend Visualization Charts
🧬 Advanced ML Risk Prediction
🩻 Medical Image Classification
🔔 Health Alerts & Notifications
📱 Mobile App Version
☁️ Cloud Deployment (Docker + Kubernetes)
🤝 Contributing

Contributions are welcome!

Steps:
fork → clone → branch → commit → push → pull request

Example:

git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
🧾 License

This project is licensed under the:

MIT License

See:

LICENSE

for details.

👨‍💻 Maintainer

Project Name: MedVerse AI
Role: Open Source Medical Intelligence Platform

Maintained with ❤️ by contributors dedicated to improving health literacy through technology.

⭐ Support the Project

If you find this project useful:

⭐ Star the repository
🍴 Fork it
📢 Share it

Together, we can make healthcare understanding accessible to everyone.
