import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the 'aimodel' directory to the system path to allow importing translate_me
sys.path.append(os.path.join(os.path.dirname(__file__), 'aimodel'))

from translate_me import MedVerseLLM

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize the AI model
med_model = MedVerseLLM()

@app.route('/translate_result', methods=['POST'])
def translate_result():
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)