"""
Medical Document Processor
Handles reading and extracting text from medical PDFs and images
"""

import os
import io
from typing import Dict, List, Optional
from google.cloud import vision
import PyPDF2
from PIL import Image
import base64


class DocumentProcessor:
    """Process medical documents (PDF/Image) and extract text"""
    
    def __init__(self):
        """Initialize the Vision API client"""
        self._configure_local_tesseract()
        try:
            self.vision_client = vision.ImageAnnotatorClient()
            self.initialized = True
        except Exception as e:
            print(f"Warning: Google Cloud Vision API not initialized: {e}")
            self.vision_client = None
            self.initialized = False

    def _configure_local_tesseract(self) -> None:
        """Try to configure pytesseract path on Windows when tesseract is installed but not in PATH."""
        try:
            import pytesseract
        except Exception:
            return

        common_paths = [
            r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        ]

        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using Google Cloud Vision API
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text from the image
        """
        if not self.vision_client:
            return self._extract_text_locally(image_path)
        
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.vision_client.document_text_detection(image=image)
            
            # Extract full text from response
            full_text = ""
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            for symbol in word.symbols:
                                full_text += symbol.text
                            full_text += " "
                        full_text += "\n"
                    full_text += "\n"
            
            return full_text.strip()
        
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return self._extract_text_locally(image_path)
    
    def _extract_text_locally(self, image_path: str) -> str:
        """
        Fallback method to extract text locally using PIL and OCR
        
        Args:
            image_path: Path to the image
            
        Returns:
            Extracted text or placeholder if tesseract unavailable
        """
        try:
            from pytesseract import pytesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text if text.strip() else self._get_image_placeholder(image_path)
        except ImportError:
            print("⚠️  Tesseract OCR not installed. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("Windows installer: https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe")
            return self._get_image_placeholder(image_path)
        except Exception as e:
            print(f"⚠️  Local OCR error: {e}")
            return self._get_image_placeholder(image_path)
    
    def _get_image_placeholder(self, image_path: str) -> str:
        """
        Get placeholder text when OCR is not available.
        Includes image metadata and installation instructions.
        """
        try:
            image = Image.open(image_path)
            width, height = image.size
            filename = os.path.basename(image_path)
            
            placeholder = (
                f"[MEDICAL IMAGE DOCUMENT]\n"
                f"File: {filename}\n"
                f"Dimensions: {width}x{height} pixels\n"
                f"Format: {image.format}\n\n"
                f"Note: Text extraction requires Tesseract OCR.\n"
                f"Install from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                f"Your document has been received for analysis."
            )
            
            return placeholder
        except Exception as e:
            return f"[Image file received: {os.path.basename(image_path)}]"
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return "Unable to extract text from PDF"
    
    def process_document(self, file_path: str) -> Dict:
        """
        Process any medical document (PDF or Image)
        
        Args:
            file_path: Path to the medical document
            
        Returns:
            Dictionary with extracted information
        """
        result = {
            "success": False,
            "file_name": os.path.basename(file_path),
            "file_type": self._get_file_type(file_path),
            "extracted_text": "",
            "error": None
        }
        
        if not os.path.exists(file_path):
            result["error"] = "File not found"
            return result
        
        try:
            if result["file_type"] == "pdf":
                result["extracted_text"] = self.extract_text_from_pdf(file_path)
            elif result["file_type"] == "image":
                result["extracted_text"] = self.extract_text_from_image(file_path)
            else:
                result["error"] = "Unsupported file type"
                return result
            
            result["success"] = bool(result["extracted_text"])
            
            if not result["success"]:
                result["error"] = "No text could be extracted from document"
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _get_file_type(self, file_path: str) -> Optional[str]:
        """Determine file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return "pdf"
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
            return "image"
        
        return None
    
    def extract_biomarkers(self, text: str) -> Dict[str, str]:
        """
        Extract common biomarkers and values from medical text
        
        Args:
            text: Medical report text
            
        Returns:
            Dictionary of extracted biomarkers
        """
        biomarkers = {}
        keywords = {
            "cholesterol": ["cholesterol", "total cholesterol", "ldl", "hdl"],
            "blood_sugar": ["glucose", "blood sugar", "fasting glucose", "hba1c"],
            "blood_pressure": ["bp", "blood pressure", "systolic", "diastolic"],
            "white_blood_cells": ["wbc", "white blood cells", "leukocytes"],
            "hemoglobin": ["hemoglobin", "hb", "hgb"],
            "triglycerides": ["triglycerides", "trg"],
            "creatinine": ["creatinine"],
            "sodium": ["sodium", "na"],
            "potassium": ["potassium", "k"],
        }
        
        text_lower = text.lower()
        
        for biomarker, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in text_lower:
                    biomarkers[biomarker] = "Present"
                    break
        
        return biomarkers
