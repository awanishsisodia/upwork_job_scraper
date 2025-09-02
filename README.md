# Upwork AI Jobs Scraper

A powerful Python web scraper designed to extract AI-related job postings from Upwork. This tool uses Selenium WebDriver with advanced anti-detection techniques to scrape comprehensive job information including titles, descriptions, budgets, skills, and client details.

## Features

- **Multi-Query Search**: Scrape jobs using multiple AI-related search terms
- **Comprehensive Data Extraction**: Extract job titles, descriptions, budgets, skills, experience levels, and client information
- **Multiple Output Formats**: Save data in JSON, CSV, and Excel formats
- **Anti-Detection**: Advanced techniques to avoid being blocked by Upwork
- **Configurable**: Easy-to-modify configuration file for customizing scraping behavior
- **Detailed Logging**: Comprehensive logging for monitoring and debugging
- **Job Filtering**: Filter jobs by budget, job type, and experience level
- **Command Line Interface**: Easy-to-use CLI for different scraping scenarios

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver (automatically managed by webdriver-manager)**

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python run_scraper.py
```

### Advanced Usage

**Custom search queries:**
```bash
python run_scraper.py --queries "AI" "Machine Learning" "Deep Learning"
```

**Scrape more pages per query:**
```bash
python run_scraper.py --pages 10
```

**Run with visible browser (for debugging):**
```bash
python run_scraper.py --no-headless
```

**Save only in specific format:**
```bash
python run_scraper.py --output csv
```

**Set budget filters:**
```bash
python run_scraper.py --min-budget 100 --max-budget 5000
```

**Enable verbose logging:**
```bash
python run_scraper.py --verbose
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--queries` | Search queries to use | All AI-related queries |
| `--pages` | Max pages per query | 5 |
| `--no-headless` | Run with visible browser | False |
| `--output` | Output formats (json/csv/excel) | All formats |
| `--prefix` | Filename prefix | upwork_ai_jobs |
| `--min-budget` | Minimum budget filter | 0 |
| `--max-budget` | Maximum budget filter | No limit |
| `--verbose` | Enable verbose logging | False |

## Configuration

The scraper uses `config.py` for all configuration settings. Key configurations include:

### Search Queries
```python
SEARCH_QUERIES = [
    "AI", "Artificial Intelligence", "Machine Learning",
    "Deep Learning", "Natural Language Processing",
    "Computer Vision", "Data Science", "Neural Networks"
]
```

### Scraping Settings
```python
MAX_PAGES_PER_QUERY = 5
DELAY_BETWEEN_PAGES = (3, 6)  # Random delays
DELAY_BETWEEN_JOBS = (1, 3)
```

### Output Settings
```python
OUTPUT_FORMATS = ['json', 'csv', 'excel']
OUTPUT_DIRECTORY = 'output'
```

## Project Structure

```
├── upwork_scraper.py          # Basic scraper implementation
├── enhanced_scraper.py        # Enhanced scraper with configuration
├── run_scraper.py            # Command-line interface
├── config.py                 # Configuration file
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── output/                  # Output directory (created automatically)
└── logs/                    # Log files (created automatically)
```

## Data Structure

Each scraped job contains the following information:

```json
{
  "search_query": "AI",
  "scraped_at": "2024-01-15T10:30:00",
  "title": "AI Developer Needed for Chatbot Project",
  "url": "https://www.upwork.com/jobs/~0123456789",
  "budget": "$500-1000",
  "job_type": "Fixed",
  "experience_level": "Intermediate",
  "duration": "1-3 months",
  "skills": ["Python", "Machine Learning", "NLP"],
  "client_info": "Client Info",
  "posted_time": "2 hours ago",
  "description": "Detailed job description...",
  "detailed_skills": ["Additional skills..."],
  "detailed_client_info": "Detailed client information...",
  "detailed_posting_date": "2024-01-15"
}
```

## Anti-Detection Features

The scraper includes several techniques to avoid detection:

- **User Agent Rotation**: Random user agents for each session
- **Random Delays**: Variable delays between actions
- **Browser Fingerprinting**: Removes automation indicators
- **Headless Mode**: Runs without visible browser (configurable)
- **Request Throttling**: Limits request frequency

## Output Files

The scraper automatically creates:

- **JSON files**: Structured data for programmatic use
- **CSV files**: Spreadsheet-compatible format
- **Excel files**: Multi-sheet Excel workbooks
- **Log files**: Detailed scraping logs

All files are timestamped and saved in the `output/` directory.

## Troubleshooting

### Common Issues

1. **Chrome WebDriver Issues**
   - Ensure Google Chrome is installed
   - The scraper automatically downloads the correct WebDriver version

2. **No Jobs Found**
   - Check if Upwork's HTML structure has changed
   - Verify search queries are valid
   - Try running with `--no-headless` for debugging

3. **Rate Limiting**
   - Increase delays in `config.py`
   - Reduce the number of pages per query
   - Use proxy rotation (advanced)

### Debug Mode

Run with visible browser and verbose logging:
```bash
python run_scraper.py --no-headless --verbose
```

## Legal and Ethical Considerations

- **Respect robots.txt**: The scraper respects website terms
- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Terms of Service**: Ensure compliance with Upwork's terms
- **Data Usage**: Use scraped data responsibly and ethically

## Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with applicable laws and website terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Run with `--verbose` for detailed output
4. Ensure all dependencies are properly installed

## Performance Tips

- **Headless Mode**: Use for production (faster, less resource-intensive)
- **Page Limits**: Start with fewer pages to test
- **Query Selection**: Focus on specific, relevant search terms
- **Regular Updates**: Keep dependencies updated for best performance

## Future Enhancements

- Database integration (PostgreSQL, MySQL)
- Proxy rotation support
- Advanced filtering options
- Scheduled scraping
- Email notifications
- Web dashboard for results
