"""
Medical Health Analyzer
Analyzes medical reports to identify diseases and assess risk
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime


class HealthAnalyzer:
    """Analyze medical data and provide disease identification and risk assessment"""
    
    def __init__(self):
        """Initialize with disease-symptom mappings"""
        self.disease_profiles = self._load_disease_profiles()
        self.risk_factors = self._load_risk_factors()
    
    def _load_disease_profiles(self) -> Dict:
        """Load disease profiles with symptoms and indicators"""
        return {
            "Hypertension": {
                "keywords": ["blood pressure", "bp", "160", "150", "140", "130", "systolic", "diastolic"],
                "biomarkers": ["blood_pressure"],
                "risk_level": 3,
                "recommendations": [
                    "Reduce sodium intake (less than 2,300mg/day)",
                    "Maintain regular exercise (150 min/week)",
                    "Monitor blood pressure daily",
                    "Consult cardiologist for medication management"
                ]
            },
            "High Cholesterol": {
                "keywords": ["cholesterol", "ldl", "hdl", "lipid profile", "200", "240", "fatty"],
                "biomarkers": ["cholesterol"],
                "risk_level": 2,
                "recommendations": [
                    "Reduce saturated fat intake",
                    "Add soluble fiber (oats, beans, fruits)",
                    "Take statins if prescribed",
                    "Exercise 30 minutes daily",
                    "Recheck lipid profile in 3 months"
                ]
            },
            "Diabetes": {
                "keywords": ["diabetes", "glucose", "sugar", "blood sugar", "126", "200", "fasting", "hba1c", "insulin"],
                "biomarkers": ["blood_sugar"],
                "risk_level": 3,
                "recommendations": [
                    "Monitor blood sugar regularly",
                    "Follow a low glycemic index diet",
                    "Maintain regular physical activity",
                    "Take prescribed medications",
                    "Consult endocrinologist quarterly"
                ]
            },
            "Anemia": {
                "keywords": ["hemoglobin", "hb", "anemia", "low hemoglobin", "7", "8", "9", "red blood cells", "rbc"],
                "biomarkers": ["hemoglobin"],
                "risk_level": 2,
                "recommendations": [
                    "Increase iron-rich foods (spinach, beans, lean meat)",
                    "Take iron supplements as prescribed",
                    "Eat vitamin C with iron sources",
                    "Recheck hemoglobin in 4 weeks",
                    "Investigate underlying cause"
                ]
            },
            "Infection": {
                "keywords": ["white blood cells", "wbc", "infection", "fever", "bacterial", "viral", "antibiotic"],
                "biomarkers": ["white_blood_cells"],
                "risk_level": 2,
                "recommendations": [
                    "Rest and hydration",
                    "Take prescribed antibiotics if bacterial",
                    "Monitor temperature",
                    "Seek immediate care if severe symptoms",
                    "Follow-up blood test after 1 week"
                ]
            },
            "Kidney Disease": {
                "keywords": ["creatinine", "kidney", "gfr", "renal", "proteinuria", "albumin"],
                "biomarkers": ["creatinine"],
                "risk_level": 3,
                "recommendations": [
                    "Limit protein intake",
                    "Control blood pressure",
                    "Reduce sodium intake",
                    "Consult nephrologist",
                    "Regular kidney function tests"
                ]
            },
            "Electrolyte Imbalance": {
                "keywords": ["sodium", "potassium", "na", "k", "electrolyte", "imbalance", "hyponatremia", "hyperkalemia"],
                "biomarkers": ["sodium", "potassium"],
                "risk_level": 2,
                "recommendations": [
                    "Monitor fluid intake",
                    "Adjust diet as per recommendations",
                    "Take supplements if prescribed",
                    "Recheck electrolytes in 1 week",
                    "Avoid diuretics if not prescribed"
                ]
            },
            "Cardiovascular Risk": {
                "keywords": ["heart", "cardiac", "chest pain", "arrhythmia", "triglycerides", "tachycardia"],
                "biomarkers": ["cholesterol", "blood_pressure", "triglycerides"],
                "risk_level": 3,
                "recommendations": [
                    "Avoid strenuous activity without medical clearance",
                    "Take prescribed cardiovascular medications",
                    "Follow a heart-healthy diet",
                    "Consult cardiologist immediately",
                    "Consider stress management and yoga"
                ]
            }
        }
    
    def _load_risk_factors(self) -> Dict:
        """Load risk factor thresholds"""
        return {
            "blood_pressure": {
                "normal": (120, 80),
                "elevated": (130, 139, 85, 89),
                "high": (140, 90)
            },
            "cholesterol": {
                "desirable": 200,
                "borderline": 200,
                "high": 240
            },
            "blood_sugar": {
                "normal": 100,
                "prediabetic": 126,
                "diabetic": 126
            },
            "hemoglobin_male": {
                "normal": (13.5, 17.5),
                "low": 13.5
            },
            "hemoglobin_female": {
                "normal": (12.0, 15.5),
                "low": 12.0
            }
        }
    
    def analyze_report(self, report_text: str, biomarkers: Dict = None) -> Dict:
        """
        Analyze medical report and identify diseases
        
        Args:
            report_text: Extracted medical report text
            biomarkers: Extracted biomarkers dictionary
            
        Returns:
            Analysis result with identified diseases and risk assessment
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "identified_diseases": [],
            "risk_level": "Low Risk",
            "risk_score": 0,
            "recommendations": [],
            "summary": "",
            "doctor_questions": [],
            "biomarkers_detected": biomarkers or {}
        }
        
        if not report_text:
            analysis["summary"] = "No medical data available for analysis"
            return analysis
        
        # Convert to lowercase for analysis
        text_lower = report_text.lower()
        
        # Identify diseases
        diseases_found = []
        total_risk = 0
        
        for disease, profile in self.disease_profiles.items():
            # Check if disease keywords match
            match_score = 0
            for keyword in profile["keywords"]:
                if keyword in text_lower:
                    match_score += 1
            
            # Check if biomarkers match
            if biomarkers:
                for biomarker in profile["biomarkers"]:
                    if biomarker in biomarkers:
                        match_score += 2
            
            if match_score > 0:
                diseases_found.append({
                    "disease": disease,
                    "confidence": min(match_score * 0.2, 1.0),  # Convert to percentage
                    "risk_level": profile["risk_level"],
                    "recommendations": profile["recommendations"]
                })
        
        # Sort by confidence
        diseases_found.sort(key=lambda x: x["confidence"], reverse=True)
        analysis["identified_diseases"] = diseases_found[:3]  # Top 3 diseases
        
        # Calculate overall risk
        if diseases_found:
            total_risk = sum(d["risk_level"] * d["confidence"] for d in diseases_found) / len(diseases_found)
            
            if total_risk >= 3:
                analysis["risk_level"] = "🔴 High Risk"
            elif total_risk >= 2:
                analysis["risk_level"] = "🟡 Moderate Risk"
            else:
                analysis["risk_level"] = "🟢 Low Risk"
        
        analysis["risk_score"] = round(total_risk, 2)
        
        # Compile recommendations
        all_recommendations = []
        for disease in diseases_found:
            all_recommendations.extend(disease["recommendations"])
        analysis["recommendations"] = list(set(all_recommendations))[:5]  # Top 5 unique recommendations
        
        # Generate summary
        analysis["summary"] = self._generate_summary(diseases_found, analysis["risk_level"])
        
        # Generate doctor questions
        analysis["doctor_questions"] = self._generate_doctor_questions(diseases_found)
        
        return analysis
    
    def _generate_summary(self, diseases: List, risk_level: str) -> str:
        """Generate human-readable summary of analysis"""
        if not diseases:
            return "Your medical report shows normal parameters. No critical findings detected. Continue with regular checkups."
        
        summary = f"Risk Assessment: {risk_level}. "
        
        if len(diseases) > 0:
            main_disease = diseases[0]["disease"]
            confidence = int(diseases[0]["confidence"] * 100)
            summary += f"Primary finding: {main_disease} (confidence: {confidence}%). "
        
        if len(diseases) > 1:
            secondary_diseases = [d["disease"] for d in diseases[1:]]
            summary += f"Secondary findings: {', '.join(secondary_diseases)}. "
        
        summary += "Schedule an appointment with your healthcare provider for detailed evaluation and personalized treatment plan."
        
        return summary
    
    def _generate_doctor_questions(self, diseases: List) -> List[str]:
        """Generate doctor-ready questions based on identified diseases"""
        questions = [
            "What is my current risk level and prognosis?",
            "What lifestyle changes should I make?",
            "Do I need any medications or supplements?"
        ]
        
        for disease in diseases[:2]:
            disease_name = disease["disease"]
            if disease_name == "Hypertension":
                questions.extend([
                    "Should I monitor my blood pressure at home?",
                    "What are the side effects of my BP medication?"
                ])
            elif disease_name == "Diabetes":
                questions.extend([
                    "What is my target blood sugar range?",
                    "How often should I get HbA1c tested?"
                ])
            elif disease_name == "High Cholesterol":
                questions.extend([
                    "Should I start statin therapy?",
                    "What diet changes are most important?"
                ])
        
        return questions[:3]  # Return top 3 questions
    
    def generate_report_data(self, report_text: str, biomarkers: Dict = None, file_name: str = "") -> Dict:
        """
        Generate complete report data for frontend display
        
        Args:
            report_text: Medical report text
            biomarkers: Extracted biomarkers
            file_name: Name of uploaded file
            
        Returns:
            Complete report data ready for result.html
        """
        analysis = self.analyze_report(report_text, biomarkers)
        
        report_data = {
            "success": True,
            "file_name": file_name,
            "analysis_date": datetime.now().isoformat(),
            "summary": analysis["summary"],
            "risk_level": analysis["risk_level"],
            "risk_score": analysis["risk_score"],
            "identified_diseases": [
                {
                    "name": d["disease"],
                    "confidence": d["confidence"]
                }
                for d in analysis["identified_diseases"]
            ],
            "recommendations": analysis["recommendations"],
            "doctor_questions": analysis["doctor_questions"],
            "biomarkers": analysis["biomarkers_detected"]
        }
        
        return report_data
