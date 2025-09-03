import time
import random
import json
import csv
import pandas as pd
import platform
import shutil
import subprocess
import urllib.request
import zipfile
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpworkAIScraper:
    def __init__(self, headless=True):
        """
        Initialize the Upwork AI Job Scraper
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.base_url = "https://www.upwork.com"
        self.search_url = "https://www.upwork.com/nx/search/jobs/?nbs=1&q=AI"
        self.jobs = []
        self.driver = None
        self.headless = headless
        self.ua = UserAgent()
        
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Add various options to avoid detection
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set user agent
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            
            # Set window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize driver with proper architecture detection
            try:
                # For Mac ARM64, we need to handle the architecture mismatch
                import platform
                if platform.system() == "Darwin" and platform.machine() == "arm64":
                    # Clear any cached drivers that might be wrong architecture
                    import shutil
                    cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
                    if os.path.exists(cache_dir):
                        try:
                            shutil.rmtree(cache_dir)
                            logger.info("Cleared ChromeDriver cache for fresh download")
                        except Exception as e:
                            logger.warning(f"Could not clear cache: {e}")
                    
                    # Force download of mac-arm64 version
                    try:
                        from webdriver_manager.chrome import ChromeDriverManager
                        from webdriver_manager.core.os_manager import ChromeType
                        
                        # Try to get the correct driver path
                        driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
                        
                        # Verify the driver is executable
                        if not os.access(driver_path, os.X_OK):
                            os.chmod(driver_path, 0o755)
                        
                        service = Service(driver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        
                    except Exception as e:
                        logger.warning(f"ChromeDriverManager failed, trying alternative approach: {e}")
                        # Fallback: try to find and use the correct driver manually
                        self._setup_driver_manual_fallback(chrome_options)
                else:
                    # For non-Mac ARM64 systems, use standard approach
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e:
                logger.error(f"Error setting up WebDriver: {e}")
                raise
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("WebDriver setup completed successfully")
    
    def _setup_driver_manual_fallback(self, chrome_options):
        """Manual fallback for Mac ARM64 ChromeDriver setup"""
        try:
            # Try to find the correct driver in the cache
            cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
            if os.path.exists(cache_dir):
                # Look for the actual chromedriver executable
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        if file == "chromedriver" and not file.endswith(".chromedriver"):
                            driver_path = os.path.join(root, file)
                            try:
                                # Make it executable
                                os.chmod(driver_path, 0o755)
                                
                                # Test if it's the right architecture
                                import subprocess
                                result = subprocess.run([driver_path, "--version"], 
                                                      capture_output=True, text=True, timeout=10)
                                
                                if result.returncode == 0:
                                    logger.info(f"Found working ChromeDriver: {driver_path}")
                                    service = Service(driver_path)
                                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                                    return
                                    
                            except Exception as e:
                                logger.warning(f"Driver {driver_path} failed: {e}")
                                continue
            
            # If we get here, try to download manually
            logger.info("Attempting manual ChromeDriver download...")
            import urllib.request
            import zipfile
            
            # Download the correct mac-arm64 version
            url = "https://storage.googleapis.com/chrome-for-testing-public/139.0.7258.154/mac-arm64/chromedriver-mac-arm64.zip"
            zip_path = os.path.expanduser("~/chromedriver-mac-arm64.zip")
            
            logger.info(f"Downloading ChromeDriver from {url}")
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract the zip file
            extract_dir = os.path.expanduser("~/chromedriver-mac-arm64")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the chromedriver executable
            driver_path = os.path.join(extract_dir, "chromedriver-mac-arm64", "chromedriver")
            os.chmod(driver_path, 0o755)
            
            # Clean up
            os.remove(zip_path)
            
            logger.info(f"Manual download successful: {driver_path}")
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            logger.error(f"Manual fallback failed: {e}")
            raise Exception(f"All ChromeDriver setup methods failed: {e}")
    
    def random_delay(self, min_delay=2, max_delay=5):
        """Add random delay to avoid detection"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scrape_job_details(self, job_url):
        """Scrape detailed information from a specific job posting"""
        try:
            self.driver.get(job_url)
            self.random_delay(3, 6)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            job_details = {}
            
            # Extract job title
            title_elem = soup.find('h1')
            if title_elem:
                job_details['title'] = title_elem.get_text(strip=True)
            
            # Extract job description
            desc_elem = soup.find('div', {'data-test': 'job-description'})
            if desc_elem:
                job_details['description'] = desc_elem.get_text(strip=True)
            
            # Extract budget information
            budget_elem = soup.find('span', string=lambda text: text and ('$' in text or 'Fixed' in text or 'Hourly' in text))
            if budget_elem:
                job_details['budget'] = budget_elem.get_text(strip=True)
            
            # Extract skills
            skills = []
            skills_elem = soup.find_all('span', class_='skill')
            for skill in skills_elem:
                skills.append(skill.get_text(strip=True))
            job_details['skills'] = skills
            
            # Extract client info
            client_elem = soup.find('div', {'data-test': 'client-info'})
            if client_elem:
                job_details['client_info'] = client_elem.get_text(strip=True)
            
            # Extract posted date
            date_elem = soup.find('time')
            if date_elem:
                job_details['posted_date'] = date_elem.get('datetime') or date_elem.get_text(strip=True)
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error scraping job details from {job_url}: {e}")
            return {}
    
    def scrape_jobs_list(self, max_pages=5):
        """Scrape jobs from the search results page"""
        try:
            self.driver.get(self.search_url)
            self.random_delay(3, 6)
            
            page = 1
            while page <= max_pages:
                logger.info(f"Scraping page {page}")
                
                # Wait for jobs to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='job-tile']"))
                )
                
                # Parse the page
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all("div", {"data-test": "job-tile"})
                
                if not job_cards:
                    logger.warning(f"No job cards found on page {page}")
                    break
                
                logger.info(f"Found {len(job_cards)} jobs on page {page}")
                
                for job_card in job_cards:
                    try:
                        job_data = self.extract_job_card_data(job_card)
                        if job_data:
                            # Get detailed job information
                            if job_data.get('url'):
                                detailed_info = self.scrape_job_details(job_data['url'])
                                job_data.update(detailed_info)
                            
                            self.jobs.append(job_data)
                            logger.info(f"Scraped job: {job_data.get('title', 'Unknown')}")
                            
                            # Random delay between jobs
                            self.random_delay(1, 3)
                    
                    except Exception as e:
                        logger.error(f"Error processing job card: {e}")
                        continue
                
                # Try to go to next page
                if page < max_pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='pagination-next']")
                        if next_button and next_button.is_enabled():
                            next_button.click()
                            self.random_delay(3, 6)
                            page += 1
                        else:
                            logger.info("No more pages available")
                            break
                    except:
                        logger.info("No next page button found")
                        break
                else:
                    break
            
            logger.info(f"Total jobs scraped: {len(self.jobs)}")
            
        except Exception as e:
            logger.error(f"Error scraping jobs list: {e}")
    
    def extract_job_card_data(self, job_card):
        """Extract data from a job card element"""
        try:
            job_data = {}
            
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
            
            # Extract skills
            skills = []
            skills_elem = job_card.find_all('span', {'data-test': 'skill'})
            for skill in skills_elem:
                skills.append(skill.get_text(strip=True))
            job_data['skills'] = skills
            
            # Extract client info
            client_elem = job_card.find('div', {'data-test': 'client-info'})
            if client_elem:
                job_data['client_info'] = client_elem.get_text(strip=True)
            
            # Extract posted time
            time_elem = job_card.find('time')
            if time_elem:
                job_data['posted_time'] = time_elem.get('datetime') or time_elem.get_text(strip=True)
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job card data: {e}")
            return {}
    
    def save_to_json(self, filename='ai_jobs.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_csv(self, filename='ai_jobs.csv'):
        """Save scraped data to CSV file"""
        try:
            if self.jobs:
                df = pd.DataFrame(self.jobs)
                df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Data saved to {filename}")
            else:
                logger.warning("No data to save")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def save_to_excel(self, filename='ai_jobs.xlsx'):
        """Save scraped data to Excel file"""
        try:
            if self.jobs:
                df = pd.DataFrame(self.jobs)
                df.to_excel(filename, index=False, engine='openpyxl')
                logger.info(f"Data saved to {filename}")
            else:
                logger.warning("No data to save")
        except Exception as e:
            logger.error(f"Error saving to Excel: {e}")
    
    def run(self, max_pages=5):
        """Main method to run the scraper"""
        try:
            logger.info("Starting Upwork AI Jobs Scraper")
            self.setup_driver()
            self.scrape_jobs_list(max_pages)
            
            # Save data in multiple formats
            self.save_to_json()
            self.save_to_csv()
            self.save_to_excel()
            
            logger.info("Scraping completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
    
    def get_jobs_count(self):
        """Return the total number of scraped jobs"""
        return len(self.jobs)
    
    def get_jobs_summary(self):
        """Return a summary of scraped jobs"""
        if not self.jobs:
            return "No jobs scraped yet"
        
        summary = {
            'total_jobs': len(self.jobs),
            'job_types': {},
            'experience_levels': {},
            'budget_ranges': {}
        }
        
        for job in self.jobs:
            # Count job types
            job_type = job.get('job_type', 'Unknown')
            summary['job_types'][job_type] = summary['job_types'].get(job_type, 0) + 1
            
            # Count experience levels
            exp_level = job.get('experience_level', 'Unknown')
            summary['experience_levels'][exp_level] = summary['experience_levels'].get(exp_level, 0) + 1
            
            # Count budget ranges
            budget = job.get('budget', 'Unknown')
            summary['budget_ranges'][budget] = summary['budget_ranges'].get(budget, 0) + 1
        
        return summary

if __name__ == "__main__":
    # Create scraper instance
    scraper = UpworkAIScraper(headless=True)
    
    # Run the scraper
    scraper.run(max_pages=3)
    
    # Print summary
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    print(f"Total jobs scraped: {scraper.get_jobs_count()}")
    
    summary = scraper.get_jobs_summary()
    print(f"\nJob Types: {summary['job_types']}")
    print(f"Experience Levels: {summary['experience_levels']}")
    print(f"Budget Ranges: {summary['budget_ranges']}")
    print("="*50)
