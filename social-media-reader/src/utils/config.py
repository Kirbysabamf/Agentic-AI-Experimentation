import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json


class Config:
    """
    Configuration manager for the Social Media Reader application.
    Loads settings from environment variables with sensible defaults.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file and os.path.exists(env_file):
            self._load_env_file(env_file)
        
        self._setup_logging()
        
    def _load_env_file(self, env_file: str):
        """Load environment variables from file."""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not load env file {env_file}: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_file_path = Path(self.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    # OpenAI Configuration
    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    @property
    def OPENAI_MODEL(self) -> str:
        return os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # LinkedIn Configuration
    @property
    def LINKEDIN_EMAIL(self) -> str:
        return os.getenv('LINKEDIN_EMAIL', '')
    
    @property
    def LINKEDIN_PASSWORD(self) -> str:
        return os.getenv('LINKEDIN_PASSWORD', '')
    
    @property
    def LINKEDIN_PROFILE_URL(self) -> str:
        return os.getenv('LINKEDIN_PROFILE_URL', '')
    
    # Reddit Configuration
    @property
    def REDDIT_CLIENT_ID(self) -> str:
        return os.getenv('REDDIT_CLIENT_ID', '')
    
    @property
    def REDDIT_CLIENT_SECRET(self) -> str:
        return os.getenv('REDDIT_CLIENT_SECRET', '')
    
    @property
    def REDDIT_USER_AGENT(self) -> str:
        return os.getenv('REDDIT_USER_AGENT', 'SocialMediaReader/1.0')
    
    # Application Configuration
    @property
    def USE_MOCK_DATA(self) -> bool:
        return os.getenv('USE_MOCK_DATA', 'false').lower() in ('true', '1', 'yes')
    
    @property
    def MAX_LINKEDIN_POSTS(self) -> int:
        try:
            return int(os.getenv('MAX_LINKEDIN_POSTS', '50'))
        except ValueError:
            return 50
    
    @property
    def MAX_REDDIT_POSTS(self) -> int:
        try:
            return int(os.getenv('MAX_REDDIT_POSTS', '100'))
        except ValueError:
            return 100
    
    @property
    def OUTPUT_DIR(self) -> str:
        return os.getenv('OUTPUT_DIR', './results')
    
    @property
    def DATA_DIR(self) -> str:
        return os.getenv('DATA_DIR', './data')
    
    # Logging Configuration
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def LOG_FILE(self) -> str:
        return os.getenv('LOG_FILE', './data/application.log')
    
    # Chrome/Selenium Configuration
    @property
    def CHROME_HEADLESS(self) -> bool:
        return os.getenv('CHROME_HEADLESS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def CHROME_TIMEOUT(self) -> int:
        try:
            return int(os.getenv('CHROME_TIMEOUT', '30'))
        except ValueError:
            return 30
    
    @property
    def SELENIUM_IMPLICIT_WAIT(self) -> int:
        try:
            return int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10'))
        except ValueError:
            return 10
    
    # Content Generation Settings
    @property
    def DEFAULT_POST_TYPE(self) -> str:
        return os.getenv('DEFAULT_POST_TYPE', 'standard')
    
    @property
    def GENERATE_VARIATIONS(self) -> bool:
        return os.getenv('GENERATE_VARIATIONS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def CONTENT_CALENDAR_DAYS(self) -> int:
        try:
            return int(os.getenv('CONTENT_CALENDAR_DAYS', '7'))
        except ValueError:
            return 7
    
    # LinkedIn Post Configuration
    @property
    def POST_MIN_WORDS(self) -> int:
        try:
            return int(os.getenv('POST_MIN_WORDS', '100'))
        except ValueError:
            return 100
    
    @property
    def POST_MAX_WORDS(self) -> int:
        try:
            return int(os.getenv('POST_MAX_WORDS', '300'))
        except ValueError:
            return 300
    
    @property
    def INCLUDE_HASHTAGS(self) -> bool:
        return os.getenv('INCLUDE_HASHTAGS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def INCLUDE_EMOJIS(self) -> bool:
        return os.getenv('INCLUDE_EMOJIS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def MAX_HASHTAGS(self) -> int:
        try:
            return int(os.getenv('MAX_HASHTAGS', '5'))
        except ValueError:
            return 5
    
    # Reddit Scraping Configuration
    @property
    def REDDIT_TIME_FILTER(self) -> str:
        return os.getenv('REDDIT_TIME_FILTER', 'week')
    
    @property
    def REDDIT_SORT_METHOD(self) -> str:
        return os.getenv('REDDIT_SORT_METHOD', 'hot')
    
    @property
    def MIN_POST_SCORE(self) -> int:
        try:
            return int(os.getenv('MIN_POST_SCORE', '50'))
        except ValueError:
            return 50
    
    @property
    def MIN_POST_COMMENTS(self) -> int:
        try:
            return int(os.getenv('MIN_POST_COMMENTS', '10'))
        except ValueError:
            return 10
    
    # Development Settings
    @property
    def DEBUG(self) -> bool:
        return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    @property
    def ENABLE_CACHE(self) -> bool:
        return os.getenv('ENABLE_CACHE', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def CACHE_DURATION_HOURS(self) -> int:
        try:
            return int(os.getenv('CACHE_DURATION_HOURS', '24'))
        except ValueError:
            return 24
    
    # Feature Flags
    @property
    def ENABLE_VIDEO_SCRIPTS(self) -> bool:
        return os.getenv('ENABLE_VIDEO_SCRIPTS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def ENABLE_CAROUSEL_POSTS(self) -> bool:
        return os.getenv('ENABLE_CAROUSEL_POSTS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def ENABLE_POLLS(self) -> bool:
        return os.getenv('ENABLE_POLLS', 'true').lower() in ('true', '1', 'yes')
    
    @property
    def ENABLE_ANALYTICS(self) -> bool:
        return os.getenv('ENABLE_ANALYTICS', 'true').lower() in ('true', '1', 'yes')
    
    # Validation Methods
    def validate_openai_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.USE_MOCK_DATA and not self.OPENAI_API_KEY:
            logging.error("OpenAI API key is required when not using mock data")
            return False
        return True
    
    def validate_linkedin_config(self) -> bool:
        """Validate LinkedIn configuration."""
        if not self.USE_MOCK_DATA:
            if not self.LINKEDIN_EMAIL or not self.LINKEDIN_PASSWORD:
                logging.warning("LinkedIn credentials not provided - will use mock data")
                return False
        return True
    
    def validate_reddit_config(self) -> bool:
        """Validate Reddit configuration."""
        if not self.USE_MOCK_DATA:
            if not self.REDDIT_CLIENT_ID or not self.REDDIT_CLIENT_SECRET:
                logging.warning("Reddit API credentials not provided - will use mock data")
                return False
        return True
    
    def validate_all(self) -> Dict[str, bool]:
        """Validate all configurations and return status."""
        return {
            'openai': self.validate_openai_config(),
            'linkedin': self.validate_linkedin_config(),
            'reddit': self.validate_reddit_config()
        }
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [self.OUTPUT_DIR, self.DATA_DIR]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logging.info(f"Created/verified directory: {directory}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration (excluding sensitive data)."""
        return {
            'openai_model': self.OPENAI_MODEL,
            'use_mock_data': self.USE_MOCK_DATA,
            'max_linkedin_posts': self.MAX_LINKEDIN_POSTS,
            'max_reddit_posts': self.MAX_REDDIT_POSTS,
            'output_dir': self.OUTPUT_DIR,
            'data_dir': self.DATA_DIR,
            'log_level': self.LOG_LEVEL,
            'chrome_headless': self.CHROME_HEADLESS,
            'default_post_type': self.DEFAULT_POST_TYPE,
            'generate_variations': self.GENERATE_VARIATIONS,
            'reddit_time_filter': self.REDDIT_TIME_FILTER,
            'reddit_sort_method': self.REDDIT_SORT_METHOD,
            'feature_flags': {
                'video_scripts': self.ENABLE_VIDEO_SCRIPTS,
                'carousel_posts': self.ENABLE_CAROUSEL_POSTS,
                'polls': self.ENABLE_POLLS,
                'analytics': self.ENABLE_ANALYTICS
            }
        }
    
    def save_config(self, filename: str = "config_summary.json"):
        """Save current configuration to file."""
        config_path = Path(self.DATA_DIR) / filename
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.get_config_summary(), f, indent=2)
            logging.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def load_config(env_file: str = '.env') -> Config:
    """Load configuration from environment file."""
    global config
    config = Config(env_file)
    return config