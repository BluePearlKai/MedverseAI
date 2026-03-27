import html
import json
import os

from google.cloud import translate_v2 as translate

try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None


class IndianLanguageTranslator:
    def __init__(self):
        self.translator = None
        self.fallback_translator = None
        self.init_error = None
        try:
            self.translator = translate.Client()
        except Exception as e:
            self.init_error = str(e)
            if GoogleTranslator is not None:
                self.fallback_translator = True
        # 22 Scheduled Languages of India + English default.
        self.indian_lan_codes = {
            "assamese": "as",
            "bengali": "bn",
            "spanish": "es",
            "dogri": "doi",
            "gujarati": "gu",
            "hindi": "hi",
            "kannada": "kn",
            "kashmiri": "ks",
            "konkani": "kok",
            "maithili": "mai",
            "malayalam": "ml",
            "manipuri": "mni",
            "marathi": "mr",
            "nepali": "ne",
            "odia": "or",
            "punjabi": "pa",
            "sanskrit": "sa",
            "santali": "sat",
            "sindhi": "sd",
            "tamil": "ta",
            "telugu": "te",
            "urdu": "ur",
            "english": "en",
        }

        # Common aliases that map to the official language keys above.
        self.language_aliases = {
            "eng": "english",
            "en": "english",
            "oriya": "odia",
            "panjabi": "punjabi",
            "meitei": "manipuri",
            "meiteilon": "manipuri",
            "kashmiri (arabic)": "kashmiri",
        }

    def normalize_language(self, lang_name: str) -> str:
        if not lang_name:
            return "english"
        cleaned = lang_name.strip().lower()
        return self.language_aliases.get(cleaned, cleaned)

    def get_language_code(self, lang_name: str) -> str:
        normalized = self.normalize_language(lang_name)
        return self.indian_lan_codes.get(normalized, "en")

    def translate_text(self, text, target_lang="english", source_lang=None):
        """Translate text using Google Cloud Translate.

        English is the default target if target_lang is missing/invalid.
        """
        if self.translator is None and self.fallback_translator is None:
            return (
                "Error: Google Translate client is not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS and ensure your service account has "
                f"Cloud Translation access. Details: {self.init_error}"
            )

        target_lang_normalized = self.normalize_language(target_lang)
        if target_lang_normalized not in self.indian_lan_codes:
            return f"Error: {target_lang} is not in the supported language list."

        source_code = None
        if source_lang:
            source_lang_normalized = self.normalize_language(source_lang)
            if source_lang_normalized in self.indian_lan_codes:
                source_code = self.indian_lan_codes[source_lang_normalized]

        try:
            if self.translator is None and self.fallback_translator is not None:
                fallback_result = GoogleTranslator(
                    source="auto",
                    target=self.indian_lan_codes[target_lang_normalized],
                ).translate(text)
                return {
                    "original": text,
                    "translated": fallback_result,
                    "language": target_lang_normalized.capitalize(),
                    "source_language": None,
                    "pronunciation": None,
                }

            translate_kwargs = {
                "target_language": self.indian_lan_codes[target_lang_normalized],
                "format_": "text",
            }
            if source_code:
                translate_kwargs["source_language"] = source_code

            result = self.translator.translate(text, **translate_kwargs)

            translated_text = html.unescape(result.get("translatedText", ""))
            detected_source = result.get("detectedSourceLanguage")

            return {
                "original": text,
                "translated": translated_text,
                "language": target_lang_normalized.capitalize(),
                "source_language": detected_source,
                "pronunciation": None,
            }
        except Exception as e:
            return f"Error: {str(e)}"

class MedVerseLLM:
    """
    A wrapper model that reads data from Google Translate, processes it 
    (simulating an LLM), and outputs in 22 Indian languages.
    """
    def __init__(self):
        self.translator_engine = IndianLanguageTranslator()
        self.knowledge_base = self._load_rag_data()

    def process_query(self, user_text, target_lang="english"):
        """
        1. Translates input (Indian Lang) -> English
        2. Feeds to LLM
        3. Translates output (English) -> Target (Indian Lang)
        """
        try:
            if (
                self.translator_engine.translator is None
                and self.translator_engine.fallback_translator is None
            ):
                return {
                    "error": (
                        "Google Translate client is not configured. "
                        "Set GOOGLE_APPLICATION_CREDENTIALS to use multilingual translation."
                    )
                }

            # Step 1: Translate Input to English for the Model to understand
            # 'target_language="en"' ensures the LLM receives English text regardless of source.
            if self.translator_engine.translator is not None:
                trans_obj = self.translator_engine.translator.translate(
                    user_text,
                    target_language="en",
                    format_="text",
                )
                english_input = html.unescape(trans_obj.get("translatedText", ""))
            else:
                english_input = GoogleTranslator(source="auto", target="en").translate(user_text)
            
            # Step 2: Get Response from LLM (Simulated)
            llm_response_en = self._rag_inference(english_input)

            # Step 3: Translate Response to User's Target Language
            normalized_target_lang = self.translator_engine.normalize_language(target_lang)
            if normalized_target_lang == "english":
                return {
                    "original_query": user_text,
                    "translated_response": llm_response_en,
                    "language": "English"
                }
            
            final_result = self.translator_engine.translate_text(
                llm_response_en,
                normalized_target_lang,
                source_lang="english",
            )
            return {
                "original_query": user_text,
                "translated_response": final_result['translated'] if isinstance(final_result, dict) else final_result,
                "language": normalized_target_lang.capitalize(),
                "pronunciation": final_result.get('pronunciation') if isinstance(final_result, dict) else None
            }

        except Exception as e:
            return f"Model Processing Error: {str(e)}"

    def _load_rag_data(self):
        """
        Loads the medical knowledge base from the JSON file.
        """
        try:
            # medical_data.json is in the project root, one level above aimodel/.
            file_path = os.path.join(os.path.dirname(__file__), "..", "medical_data.json")
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _rag_inference(self, text):
        """
        Retrieval-Augmented Generation (RAG) Logic:
        Searches the JSON knowledge base for the best matching answer based on keywords.
        """
        text_lower = text.lower()
        best_match = None
        max_score = 0

        # Simple keyword matching algorithm
        for entry in self.knowledge_base:
            score = 0
            for keyword in entry.get('keywords', []):
                if keyword in text_lower:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = entry

        if best_match and max_score > 0:
            return best_match['answer']
        
        return "I am unable to find specific medical advice for that query in my database. Please consult a doctor or try rephrasing."
