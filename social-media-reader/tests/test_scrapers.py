import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from pathlib import Path

from src.scrapers.linkedin_scraper import LinkedInScraper, MockLinkedInScraper
from src.scrapers.reddit_scraper import RedditScraper, MockRedditScraper


class TestLinkedInScraper:
    """Test cases for LinkedIn scraper."""
    
    def test_init(self):
        """Test LinkedIn scraper initialization."""
        scraper = LinkedInScraper(headless=True, timeout=10)
        assert scraper.headless == True
        assert scraper.timeout == 10
        assert scraper.driver is None
    
    @patch('src.scrapers.linkedin_scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome):
        """Test Chrome WebDriver setup."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        scraper = LinkedInScraper(headless=True)
        driver = scraper.setup_driver()
        
        assert driver == mock_driver
        assert scraper.driver == mock_driver
        mock_chrome.assert_called_once()
    
    @patch('src.scrapers.linkedin_scraper.webdriver.Chrome')
    @patch('src.scrapers.linkedin_scraper.WebDriverWait')
    @patch('src.scrapers.linkedin_scraper.EC')
    def test_login_success(self, mock_ec, mock_wait, mock_chrome):
        """Test successful LinkedIn login."""
        # Setup mocks
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait.return_value.until.return_value = True
        
        mock_email_input = Mock()
        mock_password_input = Mock()
        mock_login_button = Mock()
        
        mock_driver.find_element.side_effect = [mock_email_input, mock_password_input, mock_login_button]
        
        scraper = LinkedInScraper()
        result = scraper.login("test@example.com", "password123")
        
        assert result == True
        mock_email_input.send_keys.assert_called_once_with("test@example.com")
        mock_password_input.send_keys.assert_called_once_with("password123")
        mock_login_button.click.assert_called_once()
    
    def test_parse_count(self):
        """Test engagement count parsing."""
        scraper = LinkedInScraper()
        
        assert scraper._parse_count("123") == 123
        assert scraper._parse_count("1.5K") == 1500
        assert scraper._parse_count("2.3M") == 2300000
        assert scraper._parse_count("") == 0
        assert scraper._parse_count("invalid") == 0
    
    def test_save_posts(self, temp_dir):
        """Test saving posts to JSON file."""
        scraper = LinkedInScraper()
        test_posts = [
            {"text": "Test post 1", "likes": 10},
            {"text": "Test post 2", "likes": 20}
        ]
        
        filename = Path(temp_dir) / "test_posts.json"
        scraper.save_posts(test_posts, str(filename))
        
        assert filename.exists()
        
        with open(filename, 'r') as f:
            saved_posts = json.load(f)
        
        assert len(saved_posts) == 2
        assert saved_posts[0]["text"] == "Test post 1"


class TestMockLinkedInScraper:
    """Test cases for Mock LinkedIn scraper."""
    
    def test_init(self):
        """Test mock scraper initialization."""
        scraper = MockLinkedInScraper()
        assert len(scraper.sample_posts) > 0
        assert all('text' in post for post in scraper.sample_posts)
    
    def test_login_always_succeeds(self):
        """Test that mock login always succeeds."""
        scraper = MockLinkedInScraper()
        result = scraper.login("any@email.com", "anypassword")
        assert result == True
    
    def test_get_user_posts(self):
        """Test getting sample posts from mock scraper."""
        scraper = MockLinkedInScraper()
        posts = scraper.get_user_posts("https://linkedin.com/in/test", max_posts=2)
        
        assert len(posts) == 2
        assert all('text' in post for post in posts)
        assert all('likes' in post for post in posts)
        assert all('timestamp' in post for post in posts)
    
    def test_post_structure(self):
        """Test that mock posts have expected structure."""
        scraper = MockLinkedInScraper()
        posts = scraper.get_user_posts("test_url", max_posts=1)
        
        post = posts[0]
        required_fields = ['text', 'timestamp', 'likes', 'comments', 'shares', 'post_type']
        
        for field in required_fields:
            assert field in post, f"Missing field: {field}"


class TestRedditScraper:
    """Test cases for Reddit scraper."""
    
    def test_init(self):
        """Test Reddit scraper initialization."""
        scraper = RedditScraper("client_id", "client_secret", "user_agent")
        assert scraper.client_id == "client_id"
        assert scraper.client_secret == "client_secret"
        assert scraper.user_agent == "user_agent"
        assert scraper.reddit is None
    
    @patch('src.scrapers.reddit_scraper.praw.Reddit')
    def test_setup_reddit_client(self, mock_reddit):
        """Test Reddit client setup."""
        mock_reddit_instance = Mock()
        mock_reddit.return_value = mock_reddit_instance
        mock_reddit_instance.user.me.return_value = None
        
        scraper = RedditScraper("client_id", "client_secret", "user_agent")
        result = scraper.setup_reddit_client()
        
        assert result == True
        assert scraper.reddit == mock_reddit_instance
        mock_reddit.assert_called_once_with(
            client_id="client_id",
            client_secret="client_secret",
            user_agent="user_agent"
        )
    
    def test_filter_high_quality_posts(self):
        """Test filtering posts by quality metrics."""
        scraper = RedditScraper("client_id", "client_secret", "user_agent")
        
        test_posts = [
            {"score": 100, "num_comments": 20, "over_18": False, "spoiler": False},
            {"score": 30, "num_comments": 5, "over_18": False, "spoiler": False},  # Low quality
            {"score": 150, "num_comments": 50, "over_18": True, "spoiler": False},  # NSFW
            {"score": 200, "num_comments": 30, "over_18": False, "spoiler": False}
        ]
        
        filtered_posts = scraper.filter_high_quality_posts(
            test_posts, min_score=50, min_comments=10
        )
        
        assert len(filtered_posts) == 2  # First and last posts should pass
        assert all(post["score"] >= 50 for post in filtered_posts)
        assert all(post["num_comments"] >= 10 for post in filtered_posts)
        assert all(not post["over_18"] for post in filtered_posts)
    
    def test_categorize_posts(self):
        """Test post categorization."""
        scraper = RedditScraper("client_id", "client_secret", "user_agent")
        
        test_posts = [
            {"title": "Amazing visualization of climate data", "selftext": "Created with Python"},
            {"title": "New dataset available for download", "selftext": "CSV format"},
            {"title": "Tutorial: How to create charts", "selftext": "Step by step guide"},
            {"title": "Analysis of stock market trends", "selftext": "Research findings"}
        ]
        
        categories = scraper.categorize_posts(test_posts)
        
        assert len(categories) == 6  # All category types
        assert len(categories['visualization']) >= 1
        assert len(categories['dataset']) >= 1
        assert len(categories['tutorial']) >= 1
        assert len(categories['analysis']) >= 1
    
    def test_get_trending_topics(self):
        """Test trending topic extraction."""
        scraper = RedditScraper("client_id", "client_secret", "user_agent")
        
        test_posts = [
            {"title": "Python visualization tutorial", "selftext": "Using matplotlib", "score": 100},
            {"title": "Python data analysis guide", "selftext": "With pandas", "score": 200},
            {"title": "R programming tutorial", "selftext": "Statistical analysis", "score": 150}
        ]
        
        topics = scraper.get_trending_topics(test_posts, top_n=5)
        
        assert len(topics) <= 5
        assert all('topic' in topic for topic in topics)
        assert all('score' in topic for topic in topics)
        assert all('post_count' in topic for topic in topics)
        
        # Python should be a top topic (appears in 2 posts)
        topic_words = [topic['topic'] for topic in topics]
        assert 'python' in topic_words


class TestMockRedditScraper:
    """Test cases for Mock Reddit scraper."""
    
    def test_init(self):
        """Test mock Reddit scraper initialization."""
        scraper = MockRedditScraper()
        assert len(scraper.sample_posts) > 0
        assert all('title' in post for post in scraper.sample_posts)
    
    def test_setup_reddit_client_always_succeeds(self):
        """Test that mock client setup always succeeds."""
        scraper = MockRedditScraper()
        result = scraper.setup_reddit_client()
        assert result == True
    
    def test_get_dataisbeautiful_posts(self):
        """Test getting sample Reddit posts."""
        scraper = MockRedditScraper()
        posts = scraper.get_dataisbeautiful_posts(limit=2)
        
        assert len(posts) == 2
        assert all('title' in post for post in posts)
        assert all('score' in post for post in posts)
        assert all('num_comments' in post for post in posts)
        assert all(post['subreddit'] == 'dataisbeautiful' for post in posts)
    
    def test_post_structure(self):
        """Test that mock Reddit posts have expected structure."""
        scraper = MockRedditScraper()
        posts = scraper.get_dataisbeautiful_posts(limit=1)
        
        post = posts[0]
        required_fields = [
            'id', 'title', 'selftext', 'url', 'score', 'upvote_ratio', 
            'num_comments', 'created_utc', 'author', 'subreddit'
        ]
        
        for field in required_fields:
            assert field in post, f"Missing field: {field}"
        
        # Check comments structure
        if post.get('top_comments'):
            comment = post['top_comments'][0]
            comment_fields = ['id', 'body', 'score', 'author', 'created_utc']
            for field in comment_fields:
                assert field in comment, f"Missing comment field: {field}"


class TestScraperIntegration:
    """Integration tests for scrapers."""
    
    def test_linkedin_to_file_workflow(self, temp_dir):
        """Test complete LinkedIn scraping workflow."""
        scraper = MockLinkedInScraper()
        
        # Login
        assert scraper.login("test@example.com", "password")
        
        # Get posts
        posts = scraper.get_user_posts("https://linkedin.com/in/test", max_posts=3)
        assert len(posts) == 3
        
        # Save posts
        output_file = Path(temp_dir) / "linkedin_output.json"
        scraper.save_posts(posts, str(output_file))
        
        # Verify file
        assert output_file.exists()
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        assert len(saved_data) == 3
    
    def test_reddit_to_file_workflow(self, temp_dir):
        """Test complete Reddit scraping workflow."""
        scraper = MockRedditScraper()
        
        # Setup client
        assert scraper.setup_reddit_client()
        
        # Get posts
        posts = scraper.get_dataisbeautiful_posts(limit=5)
        assert len(posts) <= 5
        
        # Filter high quality posts
        filtered_posts = scraper.filter_high_quality_posts(posts, min_score=1000)
        assert len(filtered_posts) <= len(posts)
        
        # Categorize posts
        categories = scraper.categorize_posts(filtered_posts)
        assert isinstance(categories, dict)
        
        # Get trending topics
        topics = scraper.get_trending_topics(filtered_posts)
        assert isinstance(topics, list)
        
        # Save posts
        output_file = Path(temp_dir) / "reddit_output.json"
        scraper.save_posts(filtered_posts, str(output_file))
        
        # Verify file
        assert output_file.exists()
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        assert len(saved_data) == len(filtered_posts)
    
    def test_error_handling(self):
        """Test error handling in scrapers."""
        # Test LinkedIn scraper with invalid driver
        linkedin_scraper = LinkedInScraper()
        posts = linkedin_scraper.get_user_posts("invalid_url", max_posts=10)
        assert len(posts) == 0  # Should return empty list on error
        
        # Test Reddit scraper without proper setup
        reddit_scraper = RedditScraper("invalid", "invalid", "invalid")
        posts = reddit_scraper.get_dataisbeautiful_posts(limit=10)
        assert len(posts) == 0  # Should return empty list on error
    
    def test_data_consistency(self):
        """Test that scraped data is consistent."""
        # LinkedIn data consistency
        linkedin_scraper = MockLinkedInScraper()
        linkedin_posts = linkedin_scraper.get_user_posts("test_url", max_posts=5)
        
        for post in linkedin_posts:
            assert isinstance(post['text'], str)
            assert isinstance(post['likes'], int)
            assert isinstance(post['comments'], int)
            assert post['likes'] >= 0
            assert post['comments'] >= 0
        
        # Reddit data consistency
        reddit_scraper = MockRedditScraper()
        reddit_posts = reddit_scraper.get_dataisbeautiful_posts(limit=5)
        
        for post in reddit_posts:
            assert isinstance(post['title'], str)
            assert isinstance(post['score'], int)
            assert isinstance(post['num_comments'], int)
            assert post['score'] >= 0
            assert post['num_comments'] >= 0
            assert post['subreddit'] == 'dataisbeautiful'