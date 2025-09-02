#!/usr/bin/env python3
"""
Test script to verify the Upwork AI Jobs Scraper setup
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'selenium',
        'beautifulsoup4',
        'pandas',
        'lxml',
        'fake_useragent',
        'webdriver_manager'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required modules imported successfully!")
        return True

def test_config():
    """Test if configuration file can be loaded"""
    try:
        from config import SEARCH_QUERIES, MAX_PAGES_PER_QUERY
        print(f"✅ Configuration loaded successfully!")
        print(f"   Search queries: {len(SEARCH_QUERIES)} configured")
        print(f"   Max pages per query: {MAX_PAGES_PER_QUERY}")
        return True
    except ImportError as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

def test_scraper_initialization():
    """Test if scraper can be initialized"""
    try:
        from enhanced_scraper import EnhancedUpworkAIScraper
        scraper = EnhancedUpworkAIScraper()
        print("✅ Scraper initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return False

def test_chrome_driver():
    """Test if Chrome WebDriver can be set up"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Testing Chrome WebDriver setup...")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Chrome WebDriver working! Tested with: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver test failed: {e}")
        print("Please ensure Google Chrome is installed")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("UPWORK AI JOBS SCRAPER - SETUP TEST")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Scraper Initialization", test_scraper_initialization),
        ("Chrome WebDriver", test_chrome_driver)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nYou can now run the scraper with:")
        print("  python run_scraper.py")
        print("\nOr for help:")
        print("  python run_scraper.py --help")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Ensure Google Chrome is installed")
        print("3. Check your Python version (3.7+ required)")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
