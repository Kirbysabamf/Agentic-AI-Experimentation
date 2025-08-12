# Social Media Reader

> A generative AI solution that analyzes your LinkedIn writing style and creates engaging LinkedIn posts summarizing the latest trends from r/dataisbeautiful

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](#testing)

## 🚀 Features

- **🤖 AI Writing Style Analysis**: Learn your unique LinkedIn writing patterns using GPT-4
- **📊 Reddit Content Scraping**: Automatically gathers trending posts from r/dataisbeautiful
- **✍️ Personalized Content Generation**: Creates LinkedIn posts in your voice and style
- **📅 Content Calendar**: Generates multi-day posting schedules with variety
- **🎨 Multiple Post Types**: Standard posts, carousels, polls, and video scripts
- **🔍 Smart Content Filtering**: Focuses on high-engagement, quality content
- **🐳 Docker Ready**: Fully containerized for easy deployment
- **🧪 Comprehensive Testing**: Full test suite with 90%+ coverage

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Setup](#-api-setup)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [Examples](#-examples)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## 🛠 Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key (required)
- LinkedIn account (optional - can use mock data)
- Reddit API credentials (optional - can use mock data)
- Chrome browser (for LinkedIn scraping)

### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd social-media-reader
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### Quick Start with Mock Data

```bash
python main.py --mock-data --linkedin-profile https://linkedin.com/in/sample
```

## ⚙ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Required: OpenAI API
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Optional: LinkedIn Credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
LINKEDIN_PROFILE_URL=https://linkedin.com/in/your-profile

# Optional: Reddit API
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=SocialMediaReader/1.0 by YourUsername

# Application Settings
USE_MOCK_DATA=false
MAX_LINKEDIN_POSTS=50
MAX_REDDIT_POSTS=100
OUTPUT_DIR=./results
LOG_LEVEL=INFO

# Feature Flags
ENABLE_CAROUSEL_POSTS=true
ENABLE_POLLS=true
ENABLE_VIDEO_SCRIPTS=true
CONTENT_CALENDAR_DAYS=7
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `USE_MOCK_DATA` | `false` | Use sample data instead of real APIs |
| `MAX_LINKEDIN_POSTS` | `50` | Maximum LinkedIn posts to analyze |
| `MAX_REDDIT_POSTS` | `100` | Maximum Reddit posts to process |
| `CHROME_HEADLESS` | `true` | Run Chrome in headless mode |
| `REDDIT_TIME_FILTER` | `week` | Reddit time filter (hour/day/week/month) |
| `POST_MIN_WORDS` | `100` | Minimum words in generated posts |
| `POST_MAX_WORDS` | `300` | Maximum words in generated posts |

## 🎯 Usage

### Basic Usage

```bash
# Analyze your LinkedIn profile and generate content
python main.py --linkedin-profile https://linkedin.com/in/yourprofile

# Use mock data for testing
python main.py --mock-data

# Custom output directory
python main.py --mock-data --output-dir ./custom_results

# Generate specific post types
python main.py --mock-data --post-types standard carousel poll

# Generate 14-day content calendar
python main.py --mock-data --calendar-days 14
```

### Advanced Usage

```bash
# Use custom configuration file
python main.py --config production.env --linkedin-profile https://linkedin.com/in/yourprofile

# Debug mode with verbose logging
python main.py --mock-data --log-level DEBUG

# Generate only standard posts
python main.py --mock-data --post-types standard
```

### Command Line Options

```
--linkedin-profile URL    LinkedIn profile URL to analyze
--mock-data              Use mock data instead of real API calls
--config FILE            Configuration file path (default: .env)
--output-dir DIR         Output directory for results
--data-dir DIR           Data directory for intermediate files
--log-level LEVEL        Logging level (DEBUG/INFO/WARNING/ERROR)
--post-types TYPES       Post types to generate (standard/carousel/poll/video_script)
--calendar-days N        Number of days for content calendar
--version                Show version information
--help                   Show help message
```

## 🔑 API Setup

### OpenAI API (Required)

1. Create account at [OpenAI](https://platform.openai.com)
2. Generate API key in API settings
3. Add to `.env` file: `OPENAI_API_KEY=your-key-here`

### Reddit API (Optional)

1. Create Reddit app at [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Choose "script" type application
3. Note the client ID and secret
4. Add to `.env` file:
```bash
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=SocialMediaReader/1.0 by YourUsername
```

### LinkedIn (Optional)

LinkedIn credentials are optional. The application can use mock data if credentials are not provided.

⚠️ **Note**: LinkedIn scraping should comply with their Terms of Service. Consider using their official API for production use.

## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f social-media-reader
```

### Development Mode

```bash
# Run with development profile
docker-compose --profile development up

# Run tests
docker-compose run social-media-reader-dev

# Start Jupyter notebook
docker-compose --profile development up jupyter
```

### Production Deployment

```bash
# Build production image
docker build -t social-media-reader:latest .

# Run with environment file
docker run --env-file .env -v $(pwd)/results:/app/results social-media-reader:latest
```

### Docker Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Required for Docker
OPENAI_API_KEY=your-key
USE_MOCK_DATA=true  # Set to false when APIs are configured
```

## 📁 Project Structure

```
social-media-reader/
├── src/                          # Source code
│   ├── scrapers/                 # Web scrapers
│   │   ├── linkedin_scraper.py   # LinkedIn post scraper
│   │   └── reddit_scraper.py     # Reddit post scraper
│   ├── analyzers/                # AI analyzers
│   │   ├── style_analyzer.py     # Writing style analysis
│   │   └── content_summarizer.py # Content summarization
│   ├── generators/               # Content generators
│   │   └── linkedin_post_generator.py # LinkedIn post creation
│   └── utils/                    # Utilities
│       ├── config.py             # Configuration management
│       └── logger.py             # Logging utilities
├── tests/                        # Test suite
│   ├── test_scrapers.py
│   ├── test_analyzers.py
│   ├── test_generators.py
│   └── test_utils.py
├── config/                       # Configuration files
├── data/                         # Data storage
├── results/                      # Output files
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── docker-compose.yml            # Multi-service setup
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 📊 Examples

### Sample Output

The application generates various types of LinkedIn content:

#### Standard Post
```
🔍 Latest insights from the data visualization community:

📈 Trending topics: Climate data analysis showing unprecedented warming patterns
🛠️ Python and R continue to dominate as preferred tools
📊 Original content (OC) posts are generating 3x more engagement

Key takeaways from this week's r/dataisbeautiful:
1) Interactive dashboards are driving higher engagement
2) Climate visualizations are resonating with audiences  
3) Salary analysis posts consistently perform well

The creativity in data storytelling never ceases to amaze! 

What's your favorite visualization technique for complex datasets?

#DataScience #DataVisualization #Analytics
```

#### Content Calendar Entry
```json
{
  "day": 1,
  "suggested_post_time": "9:00 AM",
  "post_type": "standard",
  "priority": "high",
  "notes": [
    "Best posted on weekdays between 8-10 AM",
    "Engage with comments within first 2 hours",
    "Consider boosting if engagement is high"
  ]
}
```

### Generated Files

The application creates several output files:

- `linkedin_posts_YYYYMMDD_HHMMSS.json` - LinkedIn posts data
- `reddit_posts_YYYYMMDD_HHMMSS.json` - Reddit posts data  
- `style_profile_YYYYMMDD_HHMMSS.json` - Writing style analysis
- `content_summary_YYYYMMDD_HHMMSS.json` - Content summary
- `pipeline_results_YYYYMMDD_HHMMSS.json` - Complete pipeline results

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scrapers.py

# Run with verbose output
pytest -v

# Run in Docker
docker-compose run social-media-reader-dev
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Mock Tests**: Test with sample data (no API calls)
- **End-to-End Tests**: Test complete workflows

### Coverage Report

The test suite maintains 90%+ code coverage:

```bash
# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View detailed coverage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run type checking
mypy src/

# Run linting
flake8 src/ tests/
```

### Code Style

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking
- **Conventional Commits** for commit messages

## 🐛 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Error
```
Error: OpenAI API key is required but not provided
```
**Solution**: Add your OpenAI API key to the `.env` file or use `--mock-data` flag.

#### 2. LinkedIn Login Failed
```
ERROR: LinkedIn login failed
```
**Solution**: 
- Check LinkedIn credentials in `.env`
- Try using `--mock-data` for testing
- Ensure Chrome/ChromeDriver is properly installed

#### 3. Reddit API Connection Error
```
ERROR: Failed to connect to Reddit API
```
**Solution**:
- Verify Reddit API credentials
- Check Reddit app configuration
- Use `--mock-data` as fallback

#### 4. Chrome/Selenium Issues
```
ERROR: Chrome WebDriver setup failed
```
**Solution**:
- Install Chrome browser
- Verify ChromeDriver is in PATH
- Use Docker for consistent environment

#### 5. Permission Errors
```
ERROR: Permission denied writing to directory
```
**Solution**:
- Check directory permissions
- Use `--output-dir` to specify writable directory
- Run with appropriate user permissions

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python main.py --mock-data --log-level DEBUG
```

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review logs in `./data/application.log`
- Use `--mock-data` to isolate API issues
- Run tests to verify installation: `pytest`

## 📈 Performance Tips

- **Use Mock Data**: For development and testing, use `--mock-data` to avoid API limits
- **Limit Post Counts**: Reduce `MAX_LINKEDIN_POSTS` and `MAX_REDDIT_POSTS` for faster execution
- **Enable Caching**: Set `ENABLE_CACHE=true` to cache API responses
- **Parallel Processing**: The application automatically optimizes API calls

## 🔐 Security

- **Environment Variables**: Never commit API keys to version control
- **Docker Security**: Application runs as non-root user in container
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Built-in rate limiting prevents API abuse
- **Secure Storage**: Credentials are encrypted in memory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) for GPT-4 API
- [Reddit](https://reddit.com) for the vibrant r/dataisbeautiful community
- [PRAW](https://praw.readthedocs.io) for Reddit API access
- [Selenium](https://selenium.dev) for web scraping capabilities
- Contributors and the open source community

---

**Made with ❤️ for the data science community**

For questions, suggestions, or issues, please open a [GitHub Issue](https://github.com/your-repo/issues).