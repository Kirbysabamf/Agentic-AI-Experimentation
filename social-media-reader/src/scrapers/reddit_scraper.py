import praw
import requests
import time
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RedditScraper:
    """
    Reddit scraper to extract posts from r/dataisbeautiful subreddit.
    Uses PRAW (Python Reddit API Wrapper) for efficient and respectful scraping.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit scraper with API credentials.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.reddit = None
        
    def setup_reddit_client(self) -> bool:
        """
        Initialize Reddit API client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # Test the connection
            self.reddit.user.me()
            logger.info("Successfully connected to Reddit API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {str(e)}")
            return False
    
    def get_dataisbeautiful_posts(self, 
                                  time_filter: str = "week", 
                                  limit: int = 100,
                                  sort: str = "hot") -> List[Dict]:
        """
        Scrape posts from r/dataisbeautiful subreddit.
        
        Args:
            time_filter: Time period to filter posts ("hour", "day", "week", "month", "year", "all")
            limit: Maximum number of posts to retrieve
            sort: Sorting method ("hot", "new", "top", "rising")
            
        Returns:
            List of dictionaries containing post data
        """
        if not self.reddit:
            if not self.setup_reddit_client():
                return []
        
        posts = []
        
        try:
            subreddit = self.reddit.subreddit("dataisbeautiful")
            
            # Get posts based on sort method
            if sort == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort == "new":
                submissions = subreddit.new(limit=limit)
            elif sort == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                post_data = self._extract_post_data(submission)
                if post_data:
                    posts.append(post_data)
                    
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Scraped {len(posts)} posts from r/dataisbeautiful")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to scrape Reddit posts: {str(e)}")
            return posts
    
    def _extract_post_data(self, submission) -> Optional[Dict]:
        """
        Extract relevant data from a Reddit submission.
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            Dictionary with post data or None if extraction fails
        """
        try:
            # Get post creation time
            created_utc = datetime.utcfromtimestamp(submission.created_utc)
            
            post_data = {
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext,
                'url': submission.url,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'created_utc': created_utc.isoformat(),
                'author': str(submission.author) if submission.author else '[deleted]',
                'subreddit': str(submission.subreddit),
                'is_self': submission.is_self,
                'post_hint': getattr(submission, 'post_hint', None),
                'domain': submission.domain,
                'permalink': submission.permalink,
                'thumbnail': submission.thumbnail if hasattr(submission, 'thumbnail') else None,
                'flair_text': submission.link_flair_text,
                'gilded': submission.gilded,
                'stickied': submission.stickied,
                'locked': submission.locked,
                'spoiler': submission.spoiler,
                'over_18': submission.over_18
            }
            
            # Get top comments for additional context
            post_data['top_comments'] = self._get_top_comments(submission, max_comments=5)
            
            return post_data
            
        except Exception as e:
            logger.warning(f"Failed to extract post data for submission {submission.id}: {str(e)}")
            return None
    
    def _get_top_comments(self, submission, max_comments: int = 5) -> List[Dict]:
        """
        Extract top comments from a submission.
        
        Args:
            submission: PRAW Submission object
            max_comments: Maximum number of comments to extract
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        try:
            # Expand comment tree
            submission.comments.replace_more(limit=0)
            
            # Get top-level comments sorted by score
            top_comments = sorted(submission.comments, key=lambda x: x.score, reverse=True)
            
            for comment in top_comments[:max_comments]:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'score': comment.score,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'created_utc': datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                        'is_submitter': comment.is_submitter,
                        'gilded': comment.gilded
                    }
                    comments.append(comment_data)
            
        except Exception as e:
            logger.warning(f"Failed to extract comments: {str(e)}")
        
        return comments
    
    def filter_high_quality_posts(self, posts: List[Dict], 
                                  min_score: int = 50, 
                                  min_comments: int = 10) -> List[Dict]:
        """
        Filter posts based on engagement metrics to get high-quality content.
        
        Args:
            posts: List of post dictionaries
            min_score: Minimum score threshold
            min_comments: Minimum number of comments
            
        Returns:
            Filtered list of high-quality posts
        """
        filtered_posts = []
        
        for post in posts:
            if (post['score'] >= min_score and 
                post['num_comments'] >= min_comments and 
                not post['over_18'] and 
                not post['spoiler']):
                filtered_posts.append(post)
        
        logger.info(f"Filtered {len(filtered_posts)} high-quality posts from {len(posts)} total posts")
        return filtered_posts
    
    def categorize_posts(self, posts: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize posts based on content type and topic.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Dictionary with categorized posts
        """
        categories = {
            'visualization': [],
            'dataset': [],
            'tutorial': [],
            'analysis': [],
            'tool': [],
            'other': []
        }
        
        # Keywords for categorization
        viz_keywords = ['chart', 'graph', 'plot', 'visualization', 'viz', 'infographic', 'dashboard']
        dataset_keywords = ['dataset', 'data', 'database', 'collection', 'survey', 'census']
        tutorial_keywords = ['tutorial', 'how to', 'guide', 'learn', 'course', 'teaching']
        analysis_keywords = ['analysis', 'research', 'study', 'findings', 'insights', 'report']
        tool_keywords = ['tool', 'library', 'package', 'software', 'app', 'platform']
        
        for post in posts:
            title_lower = post['title'].lower()
            text_lower = post['selftext'].lower()
            combined_text = f"{title_lower} {text_lower}"
            
            # Categorize based on keywords
            if any(keyword in combined_text for keyword in viz_keywords):
                categories['visualization'].append(post)
            elif any(keyword in combined_text for keyword in dataset_keywords):
                categories['dataset'].append(post)
            elif any(keyword in combined_text for keyword in tutorial_keywords):
                categories['tutorial'].append(post)
            elif any(keyword in combined_text for keyword in analysis_keywords):
                categories['analysis'].append(post)
            elif any(keyword in combined_text for keyword in tool_keywords):
                categories['tool'].append(post)
            else:
                categories['other'].append(post)
        
        # Log category distribution
        for category, category_posts in categories.items():
            logger.info(f"{category.capitalize()}: {len(category_posts)} posts")
        
        return categories
    
    def get_trending_topics(self, posts: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Extract trending topics and themes from post titles and content.
        
        Args:
            posts: List of post dictionaries
            top_n: Number of top topics to return
            
        Returns:
            List of trending topic dictionaries
        """
        from collections import Counter
        import re
        
        # Extract words from titles and text
        all_words = []
        topic_scores = Counter()
        
        # Common stop words to filter out
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                     'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        for post in posts:
            # Combine title and text
            text = f"{post['title']} {post['selftext']}".lower()
            
            # Extract meaningful words (3+ characters, alphanumeric)
            words = re.findall(r'\b[a-z]{3,}\b', text)
            
            # Filter out stop words and add to collection
            meaningful_words = [word for word in words if word not in stop_words]
            
            # Weight by post engagement
            weight = min(post['score'] / 100, 5)  # Cap weight at 5x
            
            for word in meaningful_words:
                topic_scores[word] += weight
        
        # Get top topics
        top_topics = []
        for word, score in topic_scores.most_common(top_n):
            # Count posts containing this topic
            post_count = sum(1 for post in posts if word in f"{post['title']} {post['selftext']}".lower())
            
            top_topics.append({
                'topic': word,
                'score': round(score, 2),
                'post_count': post_count,
                'relevance': round(score / len(posts), 2)
            })
        
        logger.info(f"Identified {len(top_topics)} trending topics")
        return top_topics
    
    def save_posts(self, posts: List[Dict], filename: str = "reddit_posts.json"):
        """Save scraped posts to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(posts)} posts to {filename}")
        except Exception as e:
            logger.error(f"Failed to save posts: {str(e)}")


class MockRedditScraper(RedditScraper):
    """
    Mock scraper for testing and development when Reddit API access is not available.
    Returns sample data that mimics real r/dataisbeautiful posts.
    """
    
    def __init__(self):
        super().__init__("mock_id", "mock_secret", "mock_agent")
        self.sample_posts = [
            {
                "id": "sample1",
                "title": "[OC] Global Temperature Anomalies 1880-2023: A Century of Climate Data",
                "selftext": "Created this visualization using NASA temperature data and Python (matplotlib, seaborn). Shows clear warming trend especially after 1980. Data source: NASA GISS. Code available on GitHub.",
                "url": "https://i.redd.it/sample1.png",
                "score": 4521,
                "upvote_ratio": 0.94,
                "num_comments": 387,
                "created_utc": "2024-01-15T12:30:00",
                "author": "climate_viz_person",
                "subreddit": "dataisbeautiful",
                "is_self": False,
                "post_hint": "image",
                "domain": "i.redd.it",
                "permalink": "/r/dataisbeautiful/comments/sample1/",
                "thumbnail": "https://preview.redd.it/sample1_thumb.png",
                "flair_text": "OC",
                "gilded": 2,
                "stickied": False,
                "locked": False,
                "spoiler": False,
                "over_18": False,
                "top_comments": [
                    {
                        "id": "comment1",
                        "body": "This is excellent work! The trend is undeniable when you see it visualized like this.",
                        "score": 156,
                        "author": "data_enthusiast",
                        "created_utc": "2024-01-15T13:15:00",
                        "is_submitter": False,
                        "gilded": 0
                    }
                ]
            },
            {
                "id": "sample2", 
                "title": "[OC] Tech Salary Distribution Across US Cities - Software Engineers 2023",
                "selftext": "Analyzed 50K+ salary data points from levels.fyi. Used R and ggplot2 for visualization. SF still leads but Austin and Seattle showing strong growth.",
                "url": "https://i.redd.it/sample2.png",
                "score": 3247,
                "upvote_ratio": 0.91,
                "num_comments": 428,
                "created_utc": "2024-01-14T09:45:00",
                "author": "salary_analyst",
                "subreddit": "dataisbeautiful",
                "is_self": False,
                "post_hint": "image", 
                "domain": "i.redd.it",
                "permalink": "/r/dataisbeautiful/comments/sample2/",
                "thumbnail": "https://preview.redd.it/sample2_thumb.png",
                "flair_text": "OC",
                "gilded": 1,
                "stickied": False,
                "locked": False,
                "spoiler": False,
                "over_18": False,
                "top_comments": [
                    {
                        "id": "comment2",
                        "body": "Great analysis! Would love to see this broken down by experience level too.",
                        "score": 203,
                        "author": "tech_worker",
                        "created_utc": "2024-01-14T10:30:00",
                        "is_submitter": False,
                        "gilded": 0
                    }
                ]
            },
            {
                "id": "sample3",
                "title": "[OC] My Personal Screen Time Data for 2023 - What 8760 Hours Looks Like",
                "selftext": "Tracked every hour of screen time across devices using RescueTime API. Built interactive dashboard with D3.js. Some surprising patterns emerged!",
                "url": "https://i.redd.it/sample3.png", 
                "score": 1987,
                "upvote_ratio": 0.88,
                "num_comments": 245,
                "created_utc": "2024-01-13T16:20:00",
                "author": "quantified_self",
                "subreddit": "dataisbeautiful",
                "is_self": False,
                "post_hint": "image",
                "domain": "i.redd.it", 
                "permalink": "/r/dataisbeautiful/comments/sample3/",
                "thumbnail": "https://preview.redd.it/sample3_thumb.png",
                "flair_text": "OC",
                "gilded": 0,
                "stickied": False,
                "locked": False,
                "spoiler": False,
                "over_18": False,
                "top_comments": [
                    {
                        "id": "comment3",
                        "body": "This is both fascinating and terrifying. Thanks for sharing the methodology!",
                        "score": 89,
                        "author": "productivity_nerd",
                        "created_utc": "2024-01-13T17:05:00", 
                        "is_submitter": False,
                        "gilded": 0
                    }
                ]
            }
        ]
    
    def setup_reddit_client(self) -> bool:
        """Mock setup always succeeds."""
        logger.info("Using mock Reddit scraper - API connection bypassed")
        return True
    
    def get_dataisbeautiful_posts(self, time_filter: str = "week", limit: int = 100, sort: str = "hot") -> List[Dict]:
        """Return sample posts instead of scraping."""
        logger.info(f"Returning {len(self.sample_posts)} mock Reddit posts")
        return self.sample_posts[:limit]