#!/usr/bin/env python3
"""
Quick test script to scrape a few AI jobs from Upwork
This is useful for testing the setup without running a full scrape
"""

import sys
from enhanced_scraper import EnhancedUpworkAIScraper

def quick_test():
    """Run a quick test with minimal scraping"""
    print("="*60)
    print("QUICK TEST - UPWORK AI JOBS SCRAPER")
    print("="*60)
    print("This will scrape just 1-2 pages with basic AI queries")
    print("to verify everything is working correctly.")
    print("="*60)
    
    try:
        # Create a minimal configuration for testing
        test_config = {
            'search_queries': ['AI', 'Machine Learning'],  # Just 2 queries
            'max_pages_per_query': 1,  # Just 1 page per query
            'headless_mode': False,  # Visible browser for testing (better for Cloudflare bypass)
            'output_formats': ['json'],  # Just JSON output
            'output_directory': 'output',
            'filename_prefix': 'quick_test'
        }
        
        print("Configuration:")
        print(f"  Search queries: {test_config['search_queries']}")
        print(f"  Pages per query: {test_config['max_pages_per_query']}")
        print(f"  Headless mode: {test_config['headless_mode']}")
        print(f"  Output format: {test_config['output_formats']}")
        print()
        
        # Create scraper with test config
        scraper = EnhancedUpworkAIScraper(test_config)
        
        print("Starting quick test...")
        print("(This may take a few minutes)")
        print()
        
        # Run the scraper
        scraper.run()
        
        # Print results
        print("\n" + "="*60)
        print("QUICK TEST RESULTS")
        print("="*60)
        print(f"Total jobs scraped: {scraper.get_jobs_count()}")
        
        if scraper.get_jobs_count() > 0:
            print("\nSample jobs:")
            for i, job in enumerate(scraper.jobs[:3]):  # Show first 3 jobs
                print(f"\n{i+1}. {job.get('title', 'No title')}")
                print(f"   Budget: {job.get('budget', 'No budget')}")
                print(f"   Type: {job.get('job_type', 'No type')}")
                print(f"   Experience: {job.get('experience_level', 'No level')}")
                if job.get('skills'):
                    print(f"   Skills: {', '.join(job.get('skills', []))}")
            
            print(f"\n✅ Quick test successful! Scraped {scraper.get_jobs_count()} jobs.")
            print("Check the 'output' directory for the results file.")
            
        else:
            print("\n⚠️  No jobs were scraped. This might indicate:")
            print("   - Upwork's HTML structure has changed")
            print("   - Network connectivity issues")
            print("   - Rate limiting or blocking")
            print("\nTry running with --verbose for more details.")
        
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Quick test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Run 'python test_setup.py' to check your setup")
        print("2. Ensure Google Chrome is installed")
        print("3. Check your internet connection")
        print("4. Try running with verbose logging")
        sys.exit(1)

if __name__ == "__main__":
    quick_test()
