# Configuration file for Upwork AI Jobs Scraper

# Search Configuration
SEARCH_QUERIES = [
    "AI",
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Data Science",
    "Neural Networks",
    "ChatGPT",
    "OpenAI",
    "Generative AI",
    "AI Development",
    "AI Integration",
    "AI Consulting"
]

# Scraping Configuration
MAX_PAGES_PER_QUERY = 5
DELAY_BETWEEN_PAGES = (3, 6)  # (min, max) seconds
DELAY_BETWEEN_JOBS = (1, 3)   # (min, max) seconds
DELAY_BETWEEN_QUERIES = (5, 10)  # (min, max) seconds

# Browser Configuration
HEADLESS_MODE = True
WINDOW_SIZE = (1920, 1080)
USER_AGENT_ROTATION = True

# Data Extraction Configuration
EXTRACT_DETAILED_INFO = True
EXTRACT_SKILLS = True
EXTRACT_CLIENT_INFO = True
EXTRACT_BUDGET_INFO = True
EXTRACT_POSTING_DATE = True

# Output Configuration
OUTPUT_FORMATS = ['json', 'csv', 'excel']
OUTPUT_DIRECTORY = 'output'
FILENAME_PREFIX = 'upwork_ai_jobs'

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Anti-Detection Configuration
USE_PROXY = False
PROXY_LIST = []
ROTATE_USER_AGENTS = True
RANDOM_DELAYS = True

# Job Filtering Configuration
MIN_BUDGET = 0
MAX_BUDGET = None
JOB_TYPES = ['Fixed', 'Hourly', 'Unknown']
EXPERIENCE_LEVELS = ['Entry', 'Intermediate', 'Expert', 'Unknown']

# Database Configuration (Optional)
USE_DATABASE = False
DATABASE_TYPE = 'sqlite'  # 'sqlite', 'postgresql', 'mysql'
DATABASE_CONFIG = {
    'sqlite': {
        'database': 'upwork_jobs.db'
    },
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'upwork_jobs',
        'user': 'username',
        'password': 'password'
    }
}
