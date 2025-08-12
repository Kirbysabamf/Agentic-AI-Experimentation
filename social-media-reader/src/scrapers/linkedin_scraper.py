import requests
import time
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """
    LinkedIn scraper to extract user's posts and writing style.
    Uses Selenium for dynamic content loading.
    """
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn with credentials.
        Returns True if successful, False otherwise.
        """
        if not self.driver:
            self.setup_driver()
            
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form
            email_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Enter credentials
            email_input.send_keys(email)
            password_input.send_keys(password)
            login_button.click()
            
            # Wait for successful login (check for feed or profile)
            WebDriverWait(self.driver, self.timeout).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "feed-container")),
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
                )
            )
            
            logger.info("Successfully logged into LinkedIn")
            return True
            
        except TimeoutException:
            logger.error("Login timeout - check credentials or network")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def get_user_posts(self, profile_url: str, max_posts: int = 50) -> List[Dict]:
        """
        Scrape user's recent posts from their LinkedIn profile.
        
        Args:
            profile_url: LinkedIn profile URL
            max_posts: Maximum number of posts to scrape
            
        Returns:
            List of dictionaries containing post data
        """
        if not self.driver:
            logger.error("Driver not initialized. Call login() first.")
            return []
            
        posts = []
        
        try:
            # Navigate to activity page
            activity_url = f"{profile_url.rstrip('/')}/recent-activity/all/"
            self.driver.get(activity_url)
            
            # Wait for posts to load
            time.sleep(3)
            
            # Scroll to load more posts
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 10
            
            while len(posts) < max_posts and scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                
                # Extract posts from current page
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".feed-shared-update-v2")
                
                for post_element in post_elements[len(posts):]:
                    if len(posts) >= max_posts:
                        break
                        
                    post_data = self._extract_post_data(post_element)
                    if post_data:
                        posts.append(post_data)
            
            logger.info(f"Scraped {len(posts)} posts from LinkedIn profile")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to scrape posts: {str(e)}")
            return posts
    
    def _extract_post_data(self, post_element) -> Optional[Dict]:
        """
        Extract relevant data from a single post element.
        
        Args:
            post_element: Selenium WebElement of the post
            
        Returns:
            Dictionary with post data or None if extraction fails
        """
        try:
            post_data = {
                'text': '',
                'timestamp': '',
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'post_type': 'text'
            }
            
            # Extract post text
            try:
                text_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-text")
                post_data['text'] = text_element.text.strip()
            except NoSuchElementException:
                # Try alternative selector
                try:
                    text_element = post_element.find_element(By.CSS_SELECTOR, ".update-components-text")
                    post_data['text'] = text_element.text.strip()
                except NoSuchElementException:
                    pass
            
            # Extract timestamp
            try:
                time_element = post_element.find_element(By.CSS_SELECTOR, "time")
                post_data['timestamp'] = time_element.get_attribute("datetime")
            except NoSuchElementException:
                pass
            
            # Extract engagement metrics
            try:
                # Likes
                likes_element = post_element.find_element(By.CSS_SELECTOR, ".social-counts-reactions__count")
                post_data['likes'] = self._parse_count(likes_element.text)
            except NoSuchElementException:
                pass
            
            try:
                # Comments
                comments_element = post_element.find_element(By.CSS_SELECTOR, ".social-counts-comments")
                post_data['comments'] = self._parse_count(comments_element.text)
            except NoSuchElementException:
                pass
            
            # Only return posts with actual text content
            if post_data['text']:
                return post_data
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract post data: {str(e)}")
            return None
    
    def _parse_count(self, count_text: str) -> int:
        """Parse engagement count text to integer."""
        if not count_text:
            return 0
            
        count_text = count_text.replace(',', '').strip()
        
        # Handle abbreviated numbers (1K, 1M, etc.)
        if count_text.endswith('K'):
            return int(float(count_text[:-1]) * 1000)
        elif count_text.endswith('M'):
            return int(float(count_text[:-1]) * 1000000)
        
        try:
            return int(count_text)
        except ValueError:
            return 0
    
    def save_posts(self, posts: List[Dict], filename: str = "linkedin_posts.json"):
        """Save scraped posts to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(posts)} posts to {filename}")
        except Exception as e:
            logger.error(f"Failed to save posts: {str(e)}")
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None


class MockLinkedInScraper(LinkedInScraper):
    """
    Mock scraper for testing and development when LinkedIn access is restricted.
    Returns sample data that mimics real LinkedIn post structure.
    """
    
    def __init__(self):
        super().__init__()
        self.sample_posts = [
            {
                "text": "Just launched a new data visualization project using Python and D3.js! The insights from customer behavior data were incredible. Key takeaways: 1) Mobile usage peaked at 3pm daily, 2) Weekend engagement was 40% higher than weekdays, 3) Visual content drove 3x more shares. Data storytelling at its finest! 📊 #DataScience #Visualization",
                "timestamp": "2024-01-15T10:30:00Z",
                "likes": 127,
                "comments": 23,
                "shares": 15,
                "post_type": "text"
            },
            {
                "text": "Reflecting on my journey in tech... Started as a curious analyst, now leading data initiatives that impact millions of users. The biggest lesson? Never stop learning. Whether it's a new ML algorithm, visualization technique, or industry trend - staying curious is what separates good data scientists from great ones. What's keeping you curious today? 🤔",
                "timestamp": "2024-01-12T08:15:00Z",
                "likes": 89,
                "comments": 31,
                "shares": 8,
                "post_type": "text"
            },
            {
                "text": "Hot take: The most underrated skill in data science isn't coding or statistics - it's communication. I've seen brilliant models fail because they couldn't be explained to stakeholders, and simple analyses drive massive business impact because they were presented clearly. Invest in your storytelling skills! 🗣️ #DataScience #Communication",
                "timestamp": "2024-01-08T14:45:00Z",
                "likes": 203,
                "comments": 45,
                "shares": 27,
                "post_type": "text"
            }
        ]
    
    def login(self, email: str, password: str) -> bool:
        """Mock login always succeeds."""
        logger.info("Using mock LinkedIn scraper - login bypassed")
        return True
    
    def get_user_posts(self, profile_url: str, max_posts: int = 50) -> List[Dict]:
        """Return sample posts instead of scraping."""
        logger.info(f"Returning {len(self.sample_posts)} mock LinkedIn posts")
        return self.sample_posts[:max_posts]