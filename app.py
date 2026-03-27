import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from aimodel.translate_me import MedVerseLLM
from aimodel.document_processor import DocumentProcessor
from aimodel.health_analyzer import HealthAnalyzer


app = Flask(__name__)
# Auto-configure tesseract if available
try:
    from tesseract_config import *
except ImportError:
    pass
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the AI model
try:
    med_model = MedVerseLLM()
    print("MedVerse AI Model loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load AI Model. {e}")
    med_model = None

# Initialize document processor and health analyzer
try:
    doc_processor = DocumentProcessor()
    health_analyzer = HealthAnalyzer()
    print("Document Processor and Health Analyzer initialized successfully.")
except Exception as e:
    print(f"Warning: Could not initialize processors: {e}")
    doc_processor = None
    health_analyzer = None

# Initialize database
def init_db():
    """Initialize SQLite database for storing user data and reports"""
    conn = sqlite3.connect('medverse.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        analysis_result TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()


def _model_unavailable_response():
    return jsonify({
        "error": (
            "Backend is running, but AI model initialization failed. "
            "Check server logs and Google credentials setup."
        )
    }), 503


@app.route('/', methods=['GET'])
def root_status():
    return jsonify({
        "service": "MedVerse AI Backend",
        "status": "running",
        "model_loaded": med_model is not None,
    })


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "ok": True,
        "model_loaded": med_model is not None,
    })


@app.route('/languages', methods=['GET'])
def get_languages():
    if med_model is None:
        return _model_unavailable_response()

    language_names = sorted(med_model.translator_engine.indian_lan_codes.keys())
    return jsonify({
        "default": "english",
        "supported_languages": language_names,
    })

@app.route('/translate_result', methods=['POST'])
def translate_result():
    if med_model is None:
        return _model_unavailable_response()

    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'english')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Return original text if English is requested
        if target_lang.lower() == 'english':
             return jsonify({"translated_text": text})

        # Perform Translation
        # We use translate_text directly here because we are translating a report,
        # not asking the RAG model a question.
        result = med_model.translator_engine.translate_text(text, target_lang)
        
        # Handle potential error strings from the translator
        if isinstance(result, str) and result.startswith("Error"):
             return jsonify({"error": result}), 400

        translated_text = result['translated'] if isinstance(result, dict) else result
        
        return jsonify({"translated_text": translated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translate_batch', methods=['POST'])
def translate_batch():
    if med_model is None:
        return _model_unavailable_response()

    try:
        data = request.json or {}
        texts = data.get('texts', [])
        target_lang = data.get('target_lang', 'english')

        if not isinstance(texts, list) or not texts:
            return jsonify({"error": "No texts provided"}), 400

        if target_lang.lower() == 'english':
            return jsonify({"translated_texts": texts})

        translated_texts = []
        for item in texts:
            text = str(item)
            result = med_model.translator_engine.translate_text(text, target_lang)
            if isinstance(result, str) and result.startswith("Error"):
                return jsonify({"error": result}), 400

            translated_value = result['translated'] if isinstance(result, dict) else result
            translated_texts.append(translated_value)

        return jsonify({"translated_texts": translated_texts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat_bot', methods=['POST'])
def chat_bot():
    if med_model is None:
        return _model_unavailable_response()

    try:
        data = request.json
        user_query = data.get('query', '')
        target_lang = data.get('target_lang', 'english')
        
        if not user_query:
             return jsonify({"error": "No query provided"}), 400
        
        # This calls the method that translates Input -> English -> RAG -> Target Lang
        response = med_model.process_query(user_query, target_lang)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================= Authentication Endpoints =========================

@app.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', 'User').strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        conn = sqlite3.connect('medverse.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', 
                         (email, password, name))
            conn.commit()
            user_id = cursor.lastrowid
            
            return jsonify({
                "success": True,
                "user_id": user_id,
                "message": f"Welcome {name}! Account created successfully."
            }), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 409
        finally:
            conn.close()
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        conn = sqlite3.connect('medverse.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM users WHERE email = ? AND password = ?', 
                      (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                "success": True,
                "user_id": user[0],
                "name": user[1],
                "message": f"Welcome back, {user[1]}!"
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================= File Upload Endpoints =========================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload medical document endpoint"""
    if doc_processor is None or health_analyzer is None:
        return jsonify({"error": "Document processing service unavailable"}), 503
    
    try:
        # Check if file is in request
        if 'report_file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['report_file']
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Use PDF or Image (JPG, PNG, etc.)"}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "File too large. Max size is 50MB"}), 413
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(filepath)
        
        # Process document
        doc_result = doc_processor.process_document(filepath)
        
        if not doc_result["success"]:
            return jsonify({"error": f"Failed to process document: {doc_result['error']}"}), 400
        
        # Extract biomarkers
        biomarkers = doc_processor.extract_biomarkers(doc_result["extracted_text"])
        
        # Analyze health
        analysis = health_analyzer.generate_report_data(
            doc_result["extracted_text"],
            biomarkers,
            filename
        )
        
        # Store in database
        conn = sqlite3.connect('medverse.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reports (user_id, file_name, file_path, analysis_result) VALUES (?, ?, ?, ?)',
                      (user_id, filename, filepath, json.dumps(analysis)))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "file_name": filename,
            "message": "Report uploaded and analyzed successfully",
            "analysis": analysis
        }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


# ========================= Report Analysis Endpoints =========================

@app.route('/analyze', methods=['POST'])
def analyze_report():
    """Analyze medical report endpoint"""
    if health_analyzer is None:
        return jsonify({"error": "Analysis service unavailable"}), 503
    
    try:
        data = request.json
        report_text = data.get('text', '')
        file_name = data.get('file_name', 'unknown')
        
        if not report_text:
            return jsonify({"error": "No text provided for analysis"}), 400
        
        # Extract biomarkers
        biomarkers = doc_processor.extract_biomarkers(report_text) if doc_processor else {}
        
        # Analyze
        analysis = health_analyzer.generate_report_data(report_text, biomarkers, file_name)
        
        return jsonify(analysis), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    """Get user's medical report history"""
    try:
        conn = sqlite3.connect('medverse.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, file_name, upload_date, analysis_result FROM reports WHERE user_id = ? ORDER BY upload_date DESC',
                      (user_id,))
        reports = cursor.fetchall()
        conn.close()
        
        reports_list = []
        for report in reports:
            analysis = json.loads(report['analysis_result']) if report['analysis_result'] else {}
            reports_list.append({
                "id": report['id'],
                "file_name": report['file_name'],
                "upload_date": report['upload_date'],
                "risk_level": analysis.get('risk_level', 'N/A'),
                "summary": analysis.get('summary', 'No summary available')
            })
        
        return jsonify(reports_list), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get detailed medical report"""
    try:
        conn = sqlite3.connect('medverse.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_name, analysis_result, upload_date FROM reports WHERE id = ?',
                      (report_id,))
        report = cursor.fetchone()
        conn.close()
        
        if not report:
            return jsonify({"error": "Report not found"}), 404
        
        analysis = json.loads(report['analysis_result']) if report['analysis_result'] else {}
        
        return jsonify({
            "file_name": report['file_name'],
            "upload_date": report['upload_date'],
            "analysis": analysis
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)