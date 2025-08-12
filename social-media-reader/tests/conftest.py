import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config = Config()
    
    # Override directories to use temp directory
    with patch.object(config, 'DATA_DIR', temp_dir):
        with patch.object(config, 'OUTPUT_DIR', temp_dir):
            with patch.object(config, 'USE_MOCK_DATA', True):
                yield config


@pytest.fixture
def sample_linkedin_posts():
    """Sample LinkedIn posts for testing."""
    return [
        {
            "text": "Just launched a new data visualization project! 📊 The insights we discovered were incredible. Key takeaways: 1) Mobile usage peaked at 3pm, 2) Weekend engagement was 40% higher, 3) Visual content drove 3x more shares. #DataScience #Visualization",
            "timestamp": "2024-01-15T10:30:00Z",
            "likes": 127,
            "comments": 23,
            "shares": 15,
            "post_type": "text"
        },
        {
            "text": "Reflecting on my tech journey... The biggest lesson? Never stop learning. Whether it's a new algorithm or visualization technique, staying curious is what separates good data scientists from great ones. What keeps you motivated? 🤔",
            "timestamp": "2024-01-12T08:15:00Z",
            "likes": 89,
            "comments": 31,
            "shares": 8,
            "post_type": "text"
        },
        {
            "text": "Hot take: Communication skills matter more than coding skills in data science. I've seen brilliant models fail because they couldn't be explained clearly. Invest in your storytelling! 🗣️ #DataScience #Communication",
            "timestamp": "2024-01-08T14:45:00Z",
            "likes": 203,
            "comments": 45,
            "shares": 27,
            "post_type": "text"
        }
    ]


@pytest.fixture
def sample_reddit_posts():
    """Sample Reddit posts for testing."""
    return [
        {
            "id": "test1",
            "title": "[OC] Global Temperature Anomalies 1880-2023: Visualization of Climate Data",
            "selftext": "Created using NASA data and Python matplotlib. Shows clear warming trend.",
            "url": "https://i.redd.it/test1.png",
            "score": 4521,
            "upvote_ratio": 0.94,
            "num_comments": 387,
            "created_utc": "2024-01-15T12:30:00",
            "author": "climate_viz",
            "subreddit": "dataisbeautiful",
            "is_self": False,
            "post_hint": "image",
            "domain": "i.redd.it",
            "permalink": "/r/dataisbeautiful/comments/test1/",
            "flair_text": "OC",
            "gilded": 2,
            "top_comments": [
                {
                    "id": "comment1",
                    "body": "Excellent visualization! The trend is clear.",
                    "score": 156,
                    "author": "data_fan"
                }
            ]
        },
        {
            "id": "test2",
            "title": "[OC] Tech Salary Distribution Across US Cities 2023",
            "selftext": "Analyzed 50K+ data points from salary surveys using R and ggplot2.",
            "url": "https://i.redd.it/test2.png",
            "score": 3247,
            "upvote_ratio": 0.91,
            "num_comments": 428,
            "created_utc": "2024-01-14T09:45:00",
            "author": "salary_analyst",
            "subreddit": "dataisbeautiful",
            "is_self": False,
            "post_hint": "image",
            "domain": "i.redd.it",
            "permalink": "/r/dataisbeautiful/comments/test2/",
            "flair_text": "OC",
            "gilded": 1,
            "top_comments": [
                {
                    "id": "comment2",
                    "body": "Great analysis! Would love breakdown by experience level.",
                    "score": 203,
                    "author": "tech_worker"
                }
            ]
        }
    ]


@pytest.fixture
def sample_style_profile():
    """Sample writing style profile for testing."""
    return {
        'linguistic_patterns': {
            'avg_words_per_post': 85.5,
            'avg_sentences_per_post': 4.2,
            'vocabulary_diversity': 0.67,
            'most_common_words': [('data', 15), ('visualization', 12), ('analysis', 8)],
            'readability': {
                'avg_flesch_reading_ease': 65.2,
                'avg_flesch_kincaid_grade': 8.5
            },
            'punctuation_usage': {
                'exclamation_marks': 5,
                'question_marks': 3,
                'emojis': 8,
                'hashtags': 12
            }
        },
        'structural_patterns': {
            'uses_lists_pct': 45.0,
            'uses_bullet_points_pct': 20.0,
            'call_to_action_pct': 60.0,
            'opening_patterns': ["Just launched", "Reflecting on"],
            'closing_patterns': ["What do you think?", "Thoughts?"]
        },
        'content_themes': {
            'theme_scores': {
                'technology': 25,
                'learning': 18,
                'career': 15,
                'insights': 12
            },
            'dominant_themes': [('technology', 25), ('learning', 18)],
            'emotional_tone': {
                'positive_score': 20,
                'negative_score': 3,
                'overall_tone': 'positive'
            }
        },
        'ai_style_profile': {
            'tone': 'professional yet approachable',
            'voice_characteristics': ['analytical', 'enthusiastic', 'questioning'],
            'common_phrases': ['key takeaways', 'what keeps you', 'hot take'],
            'storytelling_style': 'data-driven with personal insights',
            'engagement_techniques': ['questions', 'numbered lists', 'emojis'],
            'typical_post_structure': 'hook, insight, call-to-action'
        }
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a test AI response for LinkedIn post generation."
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_selenium_driver():
    """Mock Selenium WebDriver for testing."""
    mock_driver = Mock()
    mock_element = Mock()
    
    # Configure mock behavior
    mock_driver.find_element.return_value = mock_element
    mock_driver.find_elements.return_value = [mock_element, mock_element]
    mock_element.text = "Sample post content"
    mock_element.get_attribute.return_value = "2024-01-15T10:30:00Z"
    
    return mock_driver


@pytest.fixture
def mock_reddit_client():
    """Mock Reddit PRAW client for testing."""
    mock_reddit = Mock()
    mock_subreddit = Mock()
    mock_submission = Mock()
    
    # Configure mock Reddit API responses
    mock_reddit.subreddit.return_value = mock_subreddit
    mock_subreddit.hot.return_value = [mock_submission]
    mock_subreddit.top.return_value = [mock_submission]
    
    # Configure mock submission
    mock_submission.id = "test123"
    mock_submission.title = "[OC] Test Data Visualization"
    mock_submission.selftext = "Test description"
    mock_submission.score = 1500
    mock_submission.num_comments = 150
    mock_submission.created_utc = 1642234567.0
    mock_submission.author = "test_user"
    mock_submission.url = "https://test.com/image.png"
    
    return mock_reddit


@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir):
    """Setup test environment variables."""
    test_env_vars = {
        'USE_MOCK_DATA': 'true',
        'OPENAI_API_KEY': 'test-api-key',
        'LOG_LEVEL': 'DEBUG',
        'DATA_DIR': temp_dir,
        'OUTPUT_DIR': temp_dir
    }
    
    # Store original values
    original_values = {}
    for key, value in test_env_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_summary_data():
    """Sample content summary data for testing."""
    return {
        'summary': 'Latest data visualization trends show increased interest in climate data and salary analysis.',
        'metadata': {
            'posts_analyzed': 20,
            'total_posts_available': 50,
            'categories': {
                'data_visualizations': 12,
                'datasets_and_tools': 5,
                'analysis_and_insights': 3
            },
            'generation_timestamp': '2024-01-15T12:00:00Z'
        },
        'insights': {
            'trending_keywords': [('climate', 15), ('salary', 12), ('python', 10)],
            'top_tools': [('python', 8), ('r', 5), ('tableau', 3)],
            'content_themes': [
                {'theme': 'Climate Data', 'post_count': 8, 'avg_engagement': 2500},
                {'theme': 'Tech Salaries', 'post_count': 6, 'avg_engagement': 1800}
            ]
        }
    }


class TestDataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def create_linkedin_post(text: str = "Test post", likes: int = 50, comments: int = 10):
        """Create a test LinkedIn post."""
        return {
            "text": text,
            "timestamp": "2024-01-15T10:30:00Z",
            "likes": likes,
            "comments": comments,
            "shares": 5,
            "post_type": "text"
        }
    
    @staticmethod
    def create_reddit_post(title: str = "Test Post", score: int = 1000):
        """Create a test Reddit post."""
        return {
            "id": "test123",
            "title": title,
            "selftext": "Test description",
            "score": score,
            "num_comments": 100,
            "created_utc": "2024-01-15T12:30:00",
            "author": "test_user",
            "subreddit": "dataisbeautiful",
            "url": "https://test.com/image.png",
            "flair_text": "OC",
            "top_comments": []
        }


# Make test data generator available as fixture
@pytest.fixture
def test_data_generator():
    """Test data generator utility."""
    return TestDataGenerator()