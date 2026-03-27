#!/usr/bin/env python
"""
Test Script for MedVerse AI Medical Processing
Run this script to verify all components are working correctly.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("Testing Imports...")
    print("=" * 60)
    
    modules = {
        'flask': 'Flask Framework',
        'flask_cors': 'CORS Support',
        'werkzeug': 'File Handling',
        'PyPDF2': 'PDF Processing',
        'PIL': 'Image Processing',
        'google.cloud': 'Google Cloud Libraries',
    }
    
    failed = []
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✓ {module:20} - {description}")
        except ImportError as e:
            print(f"✗ {module:20} - {description} [MISSING]")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  Missing modules: {', '.join(failed)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All imports successful!\n")
    return True

def test_document_processor():
    """Test DocumentProcessor initialization"""
    print("=" * 60)
    print("Testing DocumentProcessor...")
    print("=" * 60)
    
    try:
        from aimodel.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        if processor:
            print("✓ DocumentProcessor initialized")
            print(f"  - Vision API: {'Enabled' if processor.vision_client else 'Disabled (fallback mode)'}")
            print()
            return True
    except Exception as e:
        print(f"✗ Error initializing DocumentProcessor: {e}")
        print()
        return False

def test_health_analyzer():
    """Test HealthAnalyzer initialization"""
    print("=" * 60)
    print("Testing HealthAnalyzer...")
    print("=" * 60)
    
    try:
        from aimodel.health_analyzer import HealthAnalyzer
        analyzer = HealthAnalyzer()
        
        if analyzer:
            print("✓ HealthAnalyzer initialized")
            print(f"  - Disease profiles loaded: {len(analyzer.disease_profiles)}")
            print(f"  - Risk factors configured: {len(analyzer.risk_factors)}")
            
            # List diseases
            print("\n  Diseases recognized:")
            for disease in list(analyzer.disease_profiles.keys())[:4]:
                print(f"    • {disease}")
            print()
            return True
    except Exception as e:
        print(f"✗ Error initializing HealthAnalyzer: {e}")
        print()
        return False

def test_sample_analysis():
    """Test a sample medical analysis"""
    print("=" * 60)
    print("Testing Sample Analysis...")
    print("=" * 60)
    
    try:
        from aimodel.health_analyzer import HealthAnalyzer
        
        analyzer = HealthAnalyzer()
        
        # Sample medical text
        medical_text = """
        Patient Lab Results (Date: 2026-03-27):
        - Blood Pressure: 165/95 mmHg (elevated)
        - Total Cholesterol: 270 mg/dL 
        - LDL Cholesterol: 180 mg/dL (high)
        - HDL Cholesterol: 35 mg/dL (low)
        - Triglycerides: 280 mg/dL
        - Blood Sugar (Fasting): 140 mg/dL
        - White Blood Cells: 12,000/µL
        - Hemoglobin: 14.5 g/dL
        Notes: Patient reports fatigue and occasional chest tightness.
        """
        
        analysis = analyzer.analyze_report(medical_text)
        
        print("✓ Analysis completed successfully")
        print(f"  - Risk Level: {analysis['risk_level']}")
        print(f"  - Risk Score: {analysis['risk_score']}")
        print(f"  - Diseases Identified: {len(analysis['identified_diseases'])}")
        
        if analysis['identified_diseases']:
            print("\n  Top Identified Diseases:")
            for disease in analysis['identified_diseases'][:3]:
                print(f"    • {disease['disease']} (Confidence: {disease['confidence']*100:.0f}%)")
        
        print(f"\n  Recommendations:")
        for rec in analysis['recommendations'][:3]:
            print(f"    • {rec}")
        
        print(f"\n  Doctor Questions:")
        for q in analysis['doctor_questions']:
            print(f"    • {q}")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        print()
        return False

def test_database():
    """Test database initialization"""
    print("=" * 60)
    print("Testing Database...")
    print("=" * 60)
    
    try:
        import sqlite3
        
        # Check if we can connect
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test basic table creation
        cursor.execute('''
        CREATE TABLE test (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        ''')
        
        cursor.execute('INSERT INTO test (name) VALUES (?)', ('test_user',))
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print("✓ Database operations working")
            print(f"  - Test record created and retrieved")
            print(f"  - Check 'medverse.db' file will be created on first run")
            print()
            return True
    
    except Exception as e:
        print(f"✗ Database error: {e}")
        print()
        return False

def test_file_system():
    """Test file system permissions"""
    print("=" * 60)
    print("Testing File System...")
    print("=" * 60)
    
    try:
        upload_dir = 'uploads'
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            print(f"✓ Created '{upload_dir}' directory")
        
        # Test write permissions
        test_file = os.path.join(upload_dir, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print(f"✓ Write permissions verified")
        print(f"  - Upload directory: {os.path.abspath(upload_dir)}")
        print()
        return True
    
    except Exception as e:
        print(f"✗ File system error: {e}")
        print()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " MedVerse AI - System Test Suite ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = {
        "Imports": test_imports(),
        "DocumentProcessor": test_document_processor(),
        "HealthAnalyzer": test_health_analyzer(),
        "Sample Analysis": test_sample_analysis(),
        "Database": test_database(),
        "File System": test_file_system(),
    }
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All systems operational! Ready to run MedVerse AI")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Visit: http://127.0.0.1:5000/")
        print("3. Upload a medical document from index.html")
        print("4. Check results on result.html")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("• Install missing modules: pip install -r requirements.txt")
        print("• Check Google Cloud credentials for Vision API")
        print("• Verify file permissions on the project directory")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
