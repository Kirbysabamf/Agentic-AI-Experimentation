#!/usr/bin/env python3
"""
Social Media Reader - Main Application Entry Point

A generative AI solution that reads LinkedIn posts to learn writing style
and summarizes Reddit r/dataisbeautiful content in your personal style.

Usage:
    python main.py --help
    python main.py --linkedin-profile https://linkedin.com/in/yourprofile
    python main.py --mock-data --output-dir ./results
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config import load_config, get_config
from src.utils.logger import setup_logger, get_app_logger
from src.scrapers.linkedin_scraper import LinkedInScraper, MockLinkedInScraper
from src.scrapers.reddit_scraper import RedditScraper, MockRedditScraper
from src.analyzers.style_analyzer import WritingStyleAnalyzer
from src.analyzers.content_summarizer import ContentSummarizer
from src.generators.linkedin_post_generator import LinkedInPostGenerator


class SocialMediaReaderApp:
    """Main application class for Social Media Reader."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        # Load configuration
        if config_file:
            self.config = load_config(config_file)
        else:
            self.config = get_config()
        
        # Setup logging
        self.logger = setup_logger(
            name='social-media-reader',
            log_file=self.config.LOG_FILE,
            log_level=self.config.LOG_LEVEL
        )
        
        # Create output directories
        self.config.create_directories()
        
        # Initialize components
        self.linkedin_scraper = None
        self.reddit_scraper = None
        self.style_analyzer = None
        self.content_summarizer = None
        self.post_generator = None
        
        self.logger.info("Social Media Reader application initialized")
    
    def initialize_components(self):
        """Initialize all application components."""
        try:
            # Initialize scrapers
            if self.config.USE_MOCK_DATA:
                self.linkedin_scraper = MockLinkedInScraper()
                self.reddit_scraper = MockRedditScraper()
                self.logger.info("Initialized with mock data scrapers")
            else:
                # LinkedIn scraper
                if self.config.LINKEDIN_EMAIL and self.config.LINKEDIN_PASSWORD:
                    self.linkedin_scraper = LinkedInScraper(
                        headless=self.config.CHROME_HEADLESS,
                        timeout=self.config.CHROME_TIMEOUT
                    )
                else:
                    self.linkedin_scraper = MockLinkedInScraper()
                    self.logger.warning("LinkedIn credentials not provided, using mock data")
                
                # Reddit scraper
                if self.config.REDDIT_CLIENT_ID and self.config.REDDIT_CLIENT_SECRET:
                    self.reddit_scraper = RedditScraper(
                        client_id=self.config.REDDIT_CLIENT_ID,
                        client_secret=self.config.REDDIT_CLIENT_SECRET,
                        user_agent=self.config.REDDIT_USER_AGENT
                    )
                else:
                    self.reddit_scraper = MockRedditScraper()
                    self.logger.warning("Reddit credentials not provided, using mock data")
            
            # Initialize analyzers and generators
            if self.config.OPENAI_API_KEY:
                self.style_analyzer = WritingStyleAnalyzer(
                    openai_api_key=self.config.OPENAI_API_KEY,
                    model=self.config.OPENAI_MODEL
                )
                self.content_summarizer = ContentSummarizer(
                    openai_api_key=self.config.OPENAI_API_KEY,
                    model=self.config.OPENAI_MODEL
                )
                self.post_generator = LinkedInPostGenerator(
                    openai_api_key=self.config.OPENAI_API_KEY,
                    model=self.config.OPENAI_MODEL
                )
                self.logger.info("Initialized AI components with OpenAI API")
            else:
                raise ValueError("OpenAI API key is required but not provided")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    def scrape_linkedin_posts(self, profile_url: str) -> List[Dict]:
        """
        Scrape LinkedIn posts for style analysis.
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            List of LinkedIn posts
        """
        self.logger.info(f"Starting LinkedIn post scraping for: {profile_url}")
        
        try:
            # Login if real scraper
            if not isinstance(self.linkedin_scraper, MockLinkedInScraper):
                login_success = self.linkedin_scraper.login(
                    self.config.LINKEDIN_EMAIL,
                    self.config.LINKEDIN_PASSWORD
                )
                if not login_success:
                    raise Exception("LinkedIn login failed")
            
            # Scrape posts
            posts = self.linkedin_scraper.get_user_posts(
                profile_url,
                max_posts=self.config.MAX_LINKEDIN_POSTS
            )
            
            self.logger.info(f"Successfully scraped {len(posts)} LinkedIn posts")
            
            # Save posts
            output_file = Path(self.config.DATA_DIR) / f"linkedin_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.linkedin_scraper.save_posts(posts, str(output_file))
            
            return posts
            
        except Exception as e:
            self.logger.error(f"LinkedIn scraping failed: {str(e)}")
            raise
        finally:
            # Cleanup
            if hasattr(self.linkedin_scraper, 'close'):
                self.linkedin_scraper.close()
    
    def scrape_reddit_posts(self) -> List[Dict]:
        """
        Scrape Reddit r/dataisbeautiful posts.
        
        Returns:
            List of Reddit posts
        """
        self.logger.info("Starting Reddit post scraping from r/dataisbeautiful")
        
        try:
            # Setup Reddit client if needed
            if not isinstance(self.reddit_scraper, MockRedditScraper):
                setup_success = self.reddit_scraper.setup_reddit_client()
                if not setup_success:
                    raise Exception("Reddit client setup failed")
            
            # Scrape posts
            posts = self.reddit_scraper.get_dataisbeautiful_posts(
                time_filter=self.config.REDDIT_TIME_FILTER,
                limit=self.config.MAX_REDDIT_POSTS,
                sort=self.config.REDDIT_SORT_METHOD
            )
            
            # Filter for high quality posts
            filtered_posts = self.reddit_scraper.filter_high_quality_posts(
                posts,
                min_score=self.config.MIN_POST_SCORE,
                min_comments=self.config.MIN_POST_COMMENTS
            )
            
            self.logger.info(f"Scraped {len(posts)} Reddit posts, {len(filtered_posts)} high quality")
            
            # Save posts
            output_file = Path(self.config.DATA_DIR) / f"reddit_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.reddit_scraper.save_posts(filtered_posts, str(output_file))
            
            return filtered_posts
            
        except Exception as e:
            self.logger.error(f"Reddit scraping failed: {str(e)}")
            raise
    
    def analyze_writing_style(self, linkedin_posts: List[Dict]) -> Dict:
        """
        Analyze writing style from LinkedIn posts.
        
        Args:
            linkedin_posts: List of LinkedIn posts
            
        Returns:
            Style analysis profile
        """
        self.logger.info("Starting writing style analysis")
        
        try:
            style_profile = self.style_analyzer.analyze_posts(linkedin_posts)
            
            # Generate style summary
            style_summary = self.style_analyzer.generate_style_summary()
            self.logger.info(f"Style analysis completed: {style_summary}")
            
            # Save style profile
            output_file = Path(self.config.DATA_DIR) / f"style_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.style_analyzer.save_style_profile(str(output_file))
            
            return style_profile
            
        except Exception as e:
            self.logger.error(f"Style analysis failed: {str(e)}")
            raise
    
    def generate_content_summary(self, reddit_posts: List[Dict], style_profile: Dict) -> Dict:
        """
        Generate content summary of Reddit posts in user's style.
        
        Args:
            reddit_posts: List of Reddit posts
            style_profile: User's writing style profile
            
        Returns:
            Content summary data
        """
        self.logger.info("Starting content summarization")
        
        try:
            summary_data = self.content_summarizer.summarize_reddit_content(
                reddit_posts,
                style_profile,
                max_posts_to_analyze=20
            )
            
            self.logger.info("Content summarization completed")
            
            # Save summary
            output_file = Path(self.config.OUTPUT_DIR) / f"content_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.content_summarizer.save_summary(summary_data, str(output_file))
            
            return summary_data
            
        except Exception as e:
            self.logger.error(f"Content summarization failed: {str(e)}")
            raise
    
    def generate_linkedin_posts(self, summary_data: Dict, style_profile: Dict) -> Dict:
        """
        Generate LinkedIn posts from summary data.
        
        Args:
            summary_data: Content summary data
            style_profile: User's writing style profile
            
        Returns:
            Generated posts data
        """
        self.logger.info("Starting LinkedIn post generation")
        
        try:
            generated_posts = {}
            
            # Generate different post types
            post_types = ['standard']
            
            if self.config.ENABLE_CAROUSEL_POSTS:
                post_types.append('carousel')
            if self.config.ENABLE_POLLS:
                post_types.append('poll')
            if self.config.ENABLE_VIDEO_SCRIPTS:
                post_types.append('video_script')
            
            for post_type in post_types:
                post = self.post_generator.generate_post_from_summary(
                    summary_data,
                    style_profile,
                    post_type=post_type
                )
                generated_posts[post_type] = post
                
                self.logger.info(f"Generated {post_type} post")
            
            # Generate content calendar if enabled
            if self.config.CONTENT_CALENDAR_DAYS > 0:
                calendar = self.post_generator.generate_content_calendar(
                    summary_data,
                    style_profile,
                    days=self.config.CONTENT_CALENDAR_DAYS
                )
                generated_posts['content_calendar'] = calendar
                self.logger.info(f"Generated {self.config.CONTENT_CALENDAR_DAYS}-day content calendar")
            
            # Save generated posts
            output_file = Path(self.config.OUTPUT_DIR) / f"linkedin_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.post_generator.save_generated_content(generated_posts, str(output_file))
            
            return generated_posts
            
        except Exception as e:
            self.logger.error(f"LinkedIn post generation failed: {str(e)}")
            raise
    
    def run_full_pipeline(self, linkedin_profile_url: str) -> Dict:
        """
        Run the complete pipeline from scraping to post generation.
        
        Args:
            linkedin_profile_url: LinkedIn profile URL
            
        Returns:
            Complete pipeline results
        """
        start_time = time.time()
        self.logger.info("Starting full Social Media Reader pipeline")
        
        try:
            # Step 1: Initialize components
            self.initialize_components()
            
            # Step 2: Scrape LinkedIn posts
            linkedin_posts = self.scrape_linkedin_posts(linkedin_profile_url)
            
            # Step 3: Scrape Reddit posts
            reddit_posts = self.scrape_reddit_posts()
            
            # Step 4: Analyze writing style
            style_profile = self.analyze_writing_style(linkedin_posts)
            
            # Step 5: Generate content summary
            summary_data = self.generate_content_summary(reddit_posts, style_profile)
            
            # Step 6: Generate LinkedIn posts
            generated_posts = self.generate_linkedin_posts(summary_data, style_profile)
            
            # Compile results
            pipeline_results = {
                'execution_timestamp': datetime.now().isoformat(),
                'execution_time_seconds': round(time.time() - start_time, 2),
                'config_summary': self.config.get_config_summary(),
                'data_summary': {
                    'linkedin_posts_scraped': len(linkedin_posts),
                    'reddit_posts_scraped': len(reddit_posts),
                    'style_profile_generated': bool(style_profile),
                    'content_summary_generated': bool(summary_data),
                    'posts_generated': list(generated_posts.keys())
                },
                'linkedin_posts': linkedin_posts,
                'reddit_posts': reddit_posts,
                'style_profile': style_profile,
                'content_summary': summary_data,
                'generated_posts': generated_posts
            }
            
            # Save complete results
            results_file = Path(self.config.OUTPUT_DIR) / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Pipeline completed successfully in {pipeline_results['execution_time_seconds']} seconds")
            self.logger.info(f"Results saved to: {results_file}")
            
            return pipeline_results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def display_results_summary(self, results: Dict):
        """
        Display a summary of pipeline results.
        
        Args:
            results: Pipeline results dictionary
        """
        print("\n" + "="*60)
        print("           SOCIAL MEDIA READER RESULTS")
        print("="*60)
        
        data_summary = results.get('data_summary', {})
        
        print(f"📊 Execution Time: {results.get('execution_time_seconds', 0)} seconds")
        print(f"📱 LinkedIn Posts Analyzed: {data_summary.get('linkedin_posts_scraped', 0)}")
        print(f"🔍 Reddit Posts Processed: {data_summary.get('reddit_posts_scraped', 0)}")
        print(f"✍️  Posts Generated: {', '.join(data_summary.get('posts_generated', []))}")
        
        # Display generated posts
        generated_posts = results.get('generated_posts', {})
        
        if 'standard' in generated_posts:
            standard_post = generated_posts['standard']
            print(f"\n📝 GENERATED LINKEDIN POST:")
            print("-" * 40)
            print(standard_post.get('content', ''))
            print("-" * 40)
            
            engagement = standard_post.get('estimated_engagement', {})
            print(f"📈 Estimated Engagement:")
            print(f"   Likes: {engagement.get('estimated_likes', 0)}")
            print(f"   Comments: {engagement.get('estimated_comments', 0)}")
            print(f"   Shares: {engagement.get('estimated_shares', 0)}")
        
        if 'content_calendar' in generated_posts:
            calendar = generated_posts['content_calendar']
            print(f"\n📅 CONTENT CALENDAR ({len(calendar)} days):")
            for entry in calendar[:3]:  # Show first 3 days
                print(f"   Day {entry['day']}: {entry['post_type']} post at {entry['suggested_post_time']}")
            if len(calendar) > 3:
                print(f"   ... and {len(calendar) - 3} more days")
        
        print(f"\n💾 Full results saved to: {self.config.OUTPUT_DIR}")
        print("="*60)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Social Media Reader - AI-powered LinkedIn content generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --linkedin-profile https://linkedin.com/in/yourprofile
  python main.py --mock-data --output-dir ./custom_results
  python main.py --config custom.env --linkedin-profile https://linkedin.com/in/yourprofile
        """
    )
    
    parser.add_argument(
        '--linkedin-profile',
        type=str,
        help='LinkedIn profile URL to analyze writing style'
    )
    
    parser.add_argument(
        '--mock-data',
        action='store_true',
        help='Use mock data instead of real API calls'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='.env',
        help='Configuration file path (default: .env)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Data directory for intermediate files'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    parser.add_argument(
        '--post-types',
        nargs='+',
        choices=['standard', 'carousel', 'poll', 'video_script'],
        default=['standard'],
        help='Types of posts to generate'
    )
    
    parser.add_argument(
        '--calendar-days',
        type=int,
        help='Number of days for content calendar'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Social Media Reader v1.0.0'
    )
    
    return parser


def main():
    """Main application entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        app = SocialMediaReaderApp(args.config if Path(args.config).exists() else None)
        
        # Override config with command line arguments
        if args.mock_data:
            app.config.USE_MOCK_DATA = True
        if args.output_dir:
            app.config.OUTPUT_DIR = args.output_dir
        if args.data_dir:
            app.config.DATA_DIR = args.data_dir
        if args.log_level:
            app.config.LOG_LEVEL = args.log_level
        if args.calendar_days:
            app.config.CONTENT_CALENDAR_DAYS = args.calendar_days
        
        # Ensure directories exist
        app.config.create_directories()
        
        # Determine LinkedIn profile URL
        linkedin_profile = args.linkedin_profile or app.config.LINKEDIN_PROFILE_URL
        if not linkedin_profile and not app.config.USE_MOCK_DATA:
            print("Error: LinkedIn profile URL is required unless using mock data")
            print("Use --linkedin-profile URL or set LINKEDIN_PROFILE_URL in config")
            sys.exit(1)
        
        # Validate configuration
        validation_results = app.config.validate_all()
        if not all(validation_results.values()) and not app.config.USE_MOCK_DATA:
            print("Warning: Some configurations are invalid. Using mock data where needed.")
            app.config.USE_MOCK_DATA = True
        
        # Display startup info
        print("Social Media Reader v1.0.0")
        print(f"Configuration: {args.config}")
        print(f"Mode: {'Mock Data' if app.config.USE_MOCK_DATA else 'Live APIs'}")
        print(f"Output Directory: {app.config.OUTPUT_DIR}")
        print(f"LinkedIn Profile: {linkedin_profile or 'Mock Profile'}")
        print("-" * 60)
        
        # Run pipeline
        results = app.run_full_pipeline(linkedin_profile or "mock_profile")
        
        # Display results
        app.display_results_summary(results)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        if args.log_level == 'DEBUG':
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())