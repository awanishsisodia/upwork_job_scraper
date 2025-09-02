import time
import random
import json
import csv
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from config import *

class EnhancedUpworkAIScraper:
    def __init__(self, config=None):
        """
        Initialize the Enhanced Upwork AI Job Scraper
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or self._load_default_config()
        self.base_url = "https://www.upwork.com"
        self.jobs = []
        self.driver = None
        self.ua = UserAgent()
        self.setup_logging()
        self.setup_output_directory()
        
    def _load_default_config(self):
        """Load default configuration from config.py"""
        return {
            'search_queries': SEARCH_QUERIES,
            'max_pages_per_query': MAX_PAGES_PER_QUERY,
            'headless_mode': HEADLESS_MODE,
            'output_formats': OUTPUT_FORMATS,
            'output_directory': OUTPUT_DIRECTORY,
            'filename_prefix': FILENAME_PREFIX
        }
    
    def setup_logging(self):
        """Set up logging configuration"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, LOG_FILE)
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.config['output_directory']):
            os.makedirs(self.config['output_directory'])
            self.logger.info(f"Created output directory: {self.config['output_directory']}")
    
    def setup_driver(self):
        """Set up Chrome WebDriver with enhanced anti-detection"""
        try:
            chrome_options = Options()
            
            if self.config['headless_mode']:
                chrome_options.add_argument("--headless")
            
            # Enhanced anti-detection options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # Set user agent
            if USER_AGENT_ROTATION:
                chrome_options.add_argument(f'--user-agent={self.ua.random}')
            
            # Set window size
            chrome_options.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            self.logger.info("Enhanced WebDriver setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def random_delay(self, delay_range):
        """Add random delay within specified range"""
        if RANDOM_DELAYS:
            delay = random.uniform(delay_range[0], delay_range[1])
            time.sleep(delay)
    
    def search_jobs(self, query, max_pages=None):
        """Search for jobs using a specific query"""
        if max_pages is None:
            max_pages = self.config['max_pages_per_query']
            
        search_url = f"{self.base_url}/search/jobs/?q={query.replace(' ', '+')}"
        self.logger.info(f"Searching for jobs with query: {query}")
        
        try:
            self.driver.get(search_url)
            self.random_delay(DELAY_BETWEEN_QUERIES)
            
            page = 1
            jobs_found = 0
            
            while page <= max_pages:
                self.logger.info(f"Scraping page {page} for query: {query}")
                
                # Wait for jobs to load
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='job-tile']"))
                    )
                except:
                    self.logger.warning(f"No job cards found on page {page} for query: {query}")
                    break
                
                # Parse the page
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all("div", {"data-test": "job-tile"})
                
                if not job_cards:
                    self.logger.warning(f"No job cards found on page {page} for query: {query}")
                    break
                
                self.logger.info(f"Found {len(job_cards)} jobs on page {page} for query: {query}")
                
                for job_card in job_cards:
                    try:
                        job_data = self.extract_job_card_data(job_card, query)
                        if job_data and self.filter_job(job_data):
                            # Get detailed job information if enabled
                            if EXTRACT_DETAILED_INFO and job_data.get('url'):
                                detailed_info = self.scrape_job_details(job_data['url'])
                                job_data.update(detailed_info)
                            
                            self.jobs.append(job_data)
                            jobs_found += 1
                            self.logger.info(f"Scraped job: {job_data.get('title', 'Unknown')}")
                            
                            # Random delay between jobs
                            self.random_delay(DELAY_BETWEEN_JOBS)
                    
                    except Exception as e:
                        self.logger.error(f"Error processing job card: {e}")
                        continue
                
                # Try to go to next page
                if page < max_pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='pagination-next']")
                        if next_button and next_button.is_enabled():
                            next_button.click()
                            self.random_delay(DELAY_BETWEEN_PAGES)
                            page += 1
                        else:
                            self.logger.info(f"No more pages available for query: {query}")
                            break
                    except:
                        self.logger.info(f"No next page button found for query: {query}")
                        break
                else:
                    break
            
            self.logger.info(f"Query '{query}' completed. Jobs found: {jobs_found}")
            return jobs_found
            
        except Exception as e:
            self.logger.error(f"Error searching jobs for query '{query}': {e}")
            return 0
    
    def filter_job(self, job_data):
        """Filter jobs based on configuration criteria"""
        # Filter by budget
        if MIN_BUDGET > 0 or MAX_BUDGET:
            budget = job_data.get('budget', '')
            if budget:
                try:
                    # Extract numeric value from budget string
                    import re
                    budget_match = re.search(r'\$?(\d+)', budget)
                    if budget_match:
                        budget_value = int(budget_match.group(1))
                        if MIN_BUDGET > 0 and budget_value < MIN_BUDGET:
                            return False
                        if MAX_BUDGET and budget_value > MAX_BUDGET:
                            return False
                except:
                    pass
        
        # Filter by job type
        if job_data.get('job_type') not in JOB_TYPES:
            return False
        
        # Filter by experience level
        if job_data.get('experience_level') not in EXPERIENCE_LEVELS:
            return False
        
        return True
    
    def extract_job_card_data(self, job_card, query):
        """Extract data from a job card element with query context"""
        try:
            job_data = {
                'search_query': query,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract job title
            title_elem = job_card.find('h4', {'data-test': 'job-title'})
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
            
            # Extract job URL
            link_elem = job_card.find('a', {'data-test': 'job-title'})
            if link_elem and link_elem.get('href'):
                job_data['url'] = self.base_url + link_elem['href']
            
            # Extract budget
            budget_elem = job_card.find('span', {'data-test': 'budget'})
            if budget_elem:
                job_data['budget'] = budget_elem.get_text(strip=True)
            
            # Extract job type
            type_elem = job_card.find('span', {'data-test': 'job-type'})
            if type_elem:
                job_data['job_type'] = type_elem.get_text(strip=True)
            
            # Extract experience level
            exp_elem = job_card.find('span', {'data-test': 'experience-level'})
            if exp_elem:
                job_data['experience_level'] = exp_elem.get_text(strip=True)
            
            # Extract duration
            duration_elem = job_card.find('span', {'data-test': 'duration'})
            if duration_elem:
                job_data['duration'] = duration_elem.get_text(strip=True)
            
            # Extract skills if enabled
            if EXTRACT_SKILLS:
                skills = []
                skills_elem = job_card.find_all('span', {'data-test': 'skill'})
                for skill in skills_elem:
                    skills.append(skill.get_text(strip=True))
                job_data['skills'] = skills
            
            # Extract client info if enabled
            if EXTRACT_CLIENT_INFO:
                client_elem = job_card.find('div', {'data-test': 'client-info'})
                if client_elem:
                    job_data['client_info'] = client_elem.get_text(strip=True)
            
            # Extract posted time if enabled
            if EXTRACT_POSTING_DATE:
                time_elem = job_card.find('time')
                if time_elem:
                    job_data['posted_time'] = time_elem.get('datetime') or time_elem.get_text(strip=True)
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting job card data: {e}")
            return {}
    
    def scrape_job_details(self, job_url):
        """Scrape detailed information from a specific job posting"""
        try:
            self.driver.get(job_url)
            self.random_delay((3, 6))
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            job_details = {}
            
            # Extract job description
            desc_elem = soup.find('div', {'data-test': 'job-description'})
            if desc_elem:
                job_details['description'] = desc_elem.get_text(strip=True)
            
            # Extract additional skills
            if EXTRACT_SKILLS:
                skills = []
                skills_elem = soup.find_all('span', class_='skill')
                for skill in skills_elem:
                    skills.append(skill.get_text(strip=True))
                if skills:
                    job_details['detailed_skills'] = skills
            
            # Extract client details
            if EXTRACT_CLIENT_INFO:
                client_elem = soup.find('div', {'data-test': 'client-info'})
                if client_elem:
                    job_details['detailed_client_info'] = client_elem.get_text(strip=True)
            
            # Extract posting date
            if EXTRACT_POSTING_DATE:
                date_elem = soup.find('time')
                if date_elem:
                    job_details['detailed_posting_date'] = date_elem.get('datetime') or date_elem.get_text(strip=True)
            
            return job_details
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {job_url}: {e}")
            return {}
    
    def save_data(self):
        """Save scraped data in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for format_type in self.config['output_formats']:
            try:
                if format_type == 'json':
                    filename = f"{self.config['filename_prefix']}_{timestamp}.json"
                    filepath = os.path.join(self.config['output_directory'], filename)
                    self.save_to_json(filepath)
                
                elif format_type == 'csv':
                    filename = f"{self.config['filename_prefix']}_{timestamp}.csv"
                    filepath = os.path.join(self.config['output_directory'], filename)
                    self.save_to_csv(filepath)
                
                elif format_type == 'excel':
                    filename = f"{self.config['filename_prefix']}_{timestamp}.xlsx"
                    filepath = os.path.join(self.config['output_directory'], filename)
                    self.save_to_excel(filepath)
                    
            except Exception as e:
                self.logger.error(f"Error saving data in {format_type} format: {e}")
    
    def save_to_json(self, filepath):
        """Save scraped data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
    
    def save_to_csv(self, filepath):
        """Save scraped data to CSV file"""
        try:
            if self.jobs:
                df = pd.DataFrame(self.jobs)
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.logger.info(f"Data saved to {filepath}")
            else:
                self.logger.warning("No data to save")
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
    
    def save_to_excel(self, filepath):
        """Save scraped data to Excel file"""
        try:
            if self.jobs:
                df = pd.DataFrame(self.jobs)
                df.to_excel(filepath, index=False, engine='openpyxl')
                self.logger.info(f"Data saved to {filepath}")
            else:
                self.logger.warning("No data to save")
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")
    
    def run(self):
        """Main method to run the enhanced scraper"""
        try:
            self.logger.info("Starting Enhanced Upwork AI Jobs Scraper")
            self.setup_driver()
            
            total_jobs = 0
            for query in self.config['search_queries']:
                jobs_found = self.search_jobs(query)
                total_jobs += jobs_found
                
                # Delay between queries
                if query != self.config['search_queries'][-1]:  # Not the last query
                    self.random_delay(DELAY_BETWEEN_QUERIES)
            
            # Save data in multiple formats
            self.save_data()
            
            self.logger.info(f"Scraping completed successfully! Total jobs: {total_jobs}")
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed")
    
    def get_jobs_count(self):
        """Return the total number of scraped jobs"""
        return len(self.jobs)
    
    def get_jobs_summary(self):
        """Return a comprehensive summary of scraped jobs"""
        if not self.jobs:
            return "No jobs scraped yet"
        
        summary = {
            'total_jobs': len(self.jobs),
            'search_queries': {},
            'job_types': {},
            'experience_levels': {},
            'budget_ranges': {},
            'scraping_timeline': {}
        }
        
        for job in self.jobs:
            # Count by search query
            query = job.get('search_query', 'Unknown')
            summary['search_queries'][query] = summary['search_queries'].get(query, 0) + 1
            
            # Count job types
            job_type = job.get('job_type', 'Unknown')
            summary['job_types'][job_type] = summary['job_types'].get(job_type, 0) + 1
            
            # Count experience levels
            exp_level = job.get('experience_level', 'Unknown')
            summary['experience_levels'][exp_level] = summary['experience_levels'].get(exp_level, 0) + 1
            
            # Count budget ranges
            budget = job.get('budget', 'Unknown')
            summary['budget_ranges'][budget] = summary['budget_ranges'].get(budget, 0) + 1
            
            # Count by scraping time
            scraped_at = job.get('scraped_at', 'Unknown')
            if scraped_at != 'Unknown':
                date = scraped_at.split('T')[0]
                summary['scraping_timeline'][date] = summary['scraping_timeline'].get(date, 0) + 1
        
        return summary

if __name__ == "__main__":
    # Create enhanced scraper instance
    scraper = EnhancedUpworkAIScraper()
    
    # Run the scraper
    scraper.run()
    
    # Print comprehensive summary
    print("\n" + "="*60)
    print("ENHANCED SCRAPING SUMMARY")
    print("="*60)
    print(f"Total jobs scraped: {scraper.get_jobs_count()}")
    
    summary = scraper.get_jobs_summary()
    print(f"\nJobs by Search Query: {summary['search_queries']}")
    print(f"Job Types: {summary['job_types']}")
    print(f"Experience Levels: {summary['experience_levels']}")
    print(f"Budget Ranges: {summary['budget_ranges']}")
    print(f"Scraping Timeline: {summary['scraping_timeline']}")
    print("="*60)
