#!/usr/bin/env python3
"""
Simple command-line interface for the Upwork AI Jobs Scraper
"""

import argparse
import sys
from enhanced_scraper import EnhancedUpworkAIScraper
from config import *

def main():
    parser = argparse.ArgumentParser(
        description="Upwork AI Jobs Scraper - Scrape AI-related jobs from Upwork",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py                    # Run with default settings
  python run_scraper.py --queries "AI" "ML"  # Run with specific queries
  python run_scraper.py --pages 10         # Scrape 10 pages per query
  python run_scraper.py --no-headless      # Run with visible browser
  python run_scraper.py --output csv       # Save only in CSV format
        """
    )
    
    parser.add_argument(
        '--queries', 
        nargs='+', 
        default=SEARCH_QUERIES,
        help='Search queries to use (default: all AI-related queries)'
    )
    
    parser.add_argument(
        '--pages', 
        type=int, 
        default=MAX_PAGES_PER_QUERY,
        help=f'Maximum pages to scrape per query (default: {MAX_PAGES_PER_QUERY})'
    )
    
    parser.add_argument(
        '--no-headless', 
        action='store_true',
        help='Run browser in visible mode (default: headless)'
    )
    
    parser.add_argument(
        '--output', 
        nargs='+', 
        choices=['json', 'csv', 'excel'],
        default=OUTPUT_FORMATS,
        help='Output formats to save data (default: all formats)'
    )
    
    parser.add_argument(
        '--prefix', 
        type=str, 
        default=FILENAME_PREFIX,
        help=f'Filename prefix for output files (default: {FILENAME_PREFIX})'
    )
    
    parser.add_argument(
        '--min-budget', 
        type=int, 
        default=MIN_BUDGET,
        help=f'Minimum budget filter (default: {MIN_BUDGET})'
    )
    
    parser.add_argument(
        '--max-budget', 
        type=int, 
        default=MAX_BUDGET,
        help=f'Maximum budget filter (default: {MAX_BUDGET})'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Update configuration based on command line arguments
    scraper_config = {
        'search_queries': args.queries,
        'max_pages_per_query': args.pages,
        'headless_mode': not args.no_headless,
        'output_formats': args.output,
        'output_directory': OUTPUT_DIRECTORY,
        'filename_prefix': args.prefix
    }
    
    # Update global config for filtering
    import config as config_module
    config_module.MIN_BUDGET = args.min_budget
    config_module.MAX_BUDGET = args.max_budget
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("="*60)
    print("UPWORK AI JOBS SCRAPER")
    print("="*60)
    print(f"Search Queries: {', '.join(scraper_config['search_queries'])}")
    print(f"Max Pages per Query: {scraper_config['max_pages_per_query']}")
    print(f"Headless Mode: {scraper_config['headless_mode']}")
    print(f"Output Formats: {', '.join(scraper_config['output_formats'])}")
    print(f"Min Budget: ${config_module.MIN_BUDGET if config_module.MIN_BUDGET > 0 else 'No limit'}")
    print(f"Max Budget: ${config_module.MAX_BUDGET if config_module.MAX_BUDGET else 'No limit'}")
    print("="*60)
    
    try:
        # Create and run scraper
        scraper = EnhancedUpworkAIScraper(scraper_config)
        scraper.run()
        
        # Print summary
        print("\n" + "="*60)
        print("SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Total jobs scraped: {scraper.get_jobs_count()}")
        
        summary = scraper.get_jobs_summary()
        print(f"\nJobs by Search Query:")
        for query, count in summary['search_queries'].items():
            print(f"  {query}: {count}")
        
        print(f"\nJob Types:")
        for job_type, count in summary['job_types'].items():
            print(f"  {job_type}: {count}")
        
        print(f"\nExperience Levels:")
        for exp_level, count in summary['experience_levels'].items():
            print(f"  {exp_level}: {count}")
        
        print(f"\nBudget Ranges:")
        for budget, count in summary['budget_ranges'].items():
            print(f"  {budget}: {count}")
        
        print("="*60)
        print("Data saved to 'output' directory")
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
