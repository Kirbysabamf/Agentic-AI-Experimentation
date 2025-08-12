import openai
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LinkedInPostGenerator:
    """
    Generate LinkedIn posts with various styles and formats,
    optimized for engagement and professional presentation.
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the LinkedIn post generator.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use for generation
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
    def generate_post_from_summary(self, summary_data: Dict, 
                                  style_profile: Dict, 
                                  post_type: str = "standard") -> Dict:
        """
        Generate a LinkedIn post from Reddit summary data.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            post_type: Type of post to generate ("standard", "carousel", "video_script", "poll")
            
        Returns:
            Dictionary containing the generated post and metadata
        """
        if post_type == "standard":
            return self._generate_standard_post(summary_data, style_profile)
        elif post_type == "carousel":
            return self._generate_carousel_post(summary_data, style_profile)
        elif post_type == "video_script":
            return self._generate_video_script(summary_data, style_profile)
        elif post_type == "poll":
            return self._generate_poll_post(summary_data, style_profile)
        else:
            logger.warning(f"Unknown post type: {post_type}, defaulting to standard")
            return self._generate_standard_post(summary_data, style_profile)
    
    def _generate_standard_post(self, summary_data: Dict, style_profile: Dict) -> Dict:
        """
        Generate a standard LinkedIn text post.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            
        Returns:
            Dictionary with generated post data
        """
        try:
            # Extract key information
            summary_text = summary_data.get('summary', '')
            insights = summary_data.get('insights', {})
            metadata = summary_data.get('metadata', {})
            
            # Create enhanced prompt
            prompt = self._create_standard_post_prompt(summary_text, insights, style_profile)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn content creator specializing in data science and technology content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            post_content = response.choices[0].message.content.strip()
            
            # Extract hashtags and mentions
            hashtags = self._extract_hashtags(post_content)
            mentions = self._extract_mentions(post_content)
            
            return {
                'post_type': 'standard',
                'content': post_content,
                'hashtags': hashtags,
                'mentions': mentions,
                'estimated_engagement': self._estimate_engagement(post_content, style_profile),
                'character_count': len(post_content),
                'word_count': len(post_content.split()),
                'generation_timestamp': datetime.now().isoformat(),
                'metadata': {
                    'source_posts_analyzed': metadata.get('posts_analyzed', 0),
                    'categories_covered': list(metadata.get('categories', {}).keys()),
                    'style_applied': True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate standard post: {str(e)}")
            return self._generate_fallback_post(summary_data)
    
    def _generate_carousel_post(self, summary_data: Dict, style_profile: Dict) -> Dict:
        """
        Generate a LinkedIn carousel post with multiple slides.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            
        Returns:
            Dictionary with carousel post data
        """
        try:
            insights = summary_data.get('insights', {})
            categorized_content = summary_data.get('categorized_content', {})
            
            # Create carousel structure
            slides = []
            
            # Title slide
            title_slide = {
                'slide_number': 1,
                'title': '🔍 Data Visualization Trends',
                'content': 'Latest insights from r/dataisbeautiful',
                'type': 'title'
            }
            slides.append(title_slide)
            
            # Insight slides
            trending_keywords = insights.get('trending_keywords', [])[:5]
            if trending_keywords:
                trend_slide = {
                    'slide_number': 2,
                    'title': '📈 Trending Topics',
                    'content': '\n'.join([f"• {keyword[0].title()}" for keyword in trending_keywords]),
                    'type': 'content'
                }
                slides.append(trend_slide)
            
            # Tools slide
            top_tools = insights.get('top_tools', [])[:5]
            if top_tools:
                tools_slide = {
                    'slide_number': 3,
                    'title': '🛠️ Popular Tools',
                    'content': '\n'.join([f"• {tool[0].title()}: {tool[1]} mentions" for tool in top_tools]),
                    'type': 'content'
                }
                slides.append(tools_slide)
            
            # Themes slide
            content_themes = insights.get('content_themes', [])[:4]
            if content_themes:
                themes_slide = {
                    'slide_number': 4,
                    'title': '🎯 Content Themes',
                    'content': '\n'.join([f"• {theme['theme']}: {theme['post_count']} posts" for theme in content_themes]),
                    'type': 'content'
                }
                slides.append(themes_slide)
            
            # CTA slide
            cta_slide = {
                'slide_number': len(slides) + 1,
                'title': '💬 What\'s Your Take?',
                'content': 'Which data story caught your attention?\n\nShare your thoughts in the comments!',
                'type': 'cta'
            }
            slides.append(cta_slide)
            
            # Generate main post text
            main_post_prompt = f"""
            Create a LinkedIn post to introduce this carousel about data visualization trends.
            
            Style guidelines: {self._get_style_summary(style_profile)}
            
            Carousel covers:
            - Trending topics: {', '.join([kw[0] for kw in trending_keywords[:3]])}
            - Popular tools: {', '.join([tool[0] for tool in top_tools[:3]])}
            - Content themes: {', '.join([theme['theme'] for theme in content_themes[:3]])}
            
            Write an engaging introduction (100-150 words) that encourages people to swipe through.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging LinkedIn carousel introductions."},
                    {"role": "user", "content": main_post_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            main_content = response.choices[0].message.content.strip()
            
            return {
                'post_type': 'carousel',
                'main_content': main_content,
                'slides': slides,
                'total_slides': len(slides),
                'estimated_engagement': self._estimate_engagement(main_content, style_profile, boost=1.3),
                'generation_timestamp': datetime.now().isoformat(),
                'instructions': [
                    "Create slides using your preferred design tool",
                    "Use consistent branding across all slides",
                    "Keep text readable on mobile devices",
                    "Include your logo/watermark on each slide"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate carousel post: {str(e)}")
            return self._generate_fallback_post(summary_data, post_type='carousel')
    
    def _generate_video_script(self, summary_data: Dict, style_profile: Dict) -> Dict:
        """
        Generate a video script for LinkedIn video content.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            
        Returns:
            Dictionary with video script data
        """
        try:
            insights = summary_data.get('insights', {})
            
            script_prompt = f"""
            Create a 60-90 second video script about data visualization trends from r/dataisbeautiful.
            
            Key insights to cover:
            {json.dumps(insights, indent=2)}
            
            Style guidelines: {self._get_style_summary(style_profile)}
            
            Format the script with:
            - Hook (first 3 seconds)
            - Main content (3 key points)
            - Call to action
            
            Include timing cues and visual suggestions.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging social media video scripts."},
                    {"role": "user", "content": script_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            script_content = response.choices[0].message.content.strip()
            
            # Parse script into sections
            sections = self._parse_video_script(script_content)
            
            return {
                'post_type': 'video_script',
                'full_script': script_content,
                'sections': sections,
                'estimated_duration': '60-90 seconds',
                'video_type': 'talking_head_with_graphics',
                'estimated_engagement': self._estimate_engagement(script_content, style_profile, boost=1.5),
                'generation_timestamp': datetime.now().isoformat(),
                'production_notes': [
                    "Use engaging visuals for data points",
                    "Keep text overlays simple and readable",
                    "Include captions for accessibility",
                    "End with a clear call-to-action"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate video script: {str(e)}")
            return self._generate_fallback_post(summary_data, post_type='video_script')
    
    def _generate_poll_post(self, summary_data: Dict, style_profile: Dict) -> Dict:
        """
        Generate a LinkedIn poll post.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            
        Returns:
            Dictionary with poll post data
        """
        try:
            insights = summary_data.get('insights', {})
            top_tools = insights.get('top_tools', [])
            content_themes = insights.get('content_themes', [])
            
            poll_prompt = f"""
            Create a LinkedIn poll about data visualization preferences based on these trends:
            
            Top tools: {', '.join([tool[0] for tool in top_tools[:4]])}
            Top themes: {', '.join([theme['theme'] for theme in content_themes[:4]])}
            
            Style guidelines: {self._get_style_summary(style_profile)}
            
            Create:
            1. An engaging question for the poll
            2. 2-4 poll options
            3. Context text (100-150 words) explaining why you're asking
            4. A call-to-action encouraging comments
            
            Make it relevant to the data science/visualization community.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging LinkedIn polls for data science professionals."},
                    {"role": "user", "content": poll_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            poll_content = response.choices[0].message.content.strip()
            
            # Extract poll components
            poll_components = self._parse_poll_content(poll_content)
            
            return {
                'post_type': 'poll',
                'content': poll_content,
                'poll_question': poll_components.get('question', 'What\'s your preferred data visualization tool?'),
                'poll_options': poll_components.get('options', ['Python', 'R', 'Tableau', 'Other']),
                'context_text': poll_components.get('context', ''),
                'estimated_engagement': self._estimate_engagement(poll_content, style_profile, boost=1.4),
                'generation_timestamp': datetime.now().isoformat(),
                'poll_duration': '1 week',
                'engagement_tips': [
                    "Respond to comments to boost engagement",
                    "Share results in a follow-up post",
                    "Thank participants for voting"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate poll post: {str(e)}")
            return self._generate_fallback_post(summary_data, post_type='poll')
    
    def _create_standard_post_prompt(self, summary_text: str, insights: Dict, style_profile: Dict) -> str:
        """Create a detailed prompt for standard post generation."""
        style_summary = self._get_style_summary(style_profile)
        
        prompt = f"""
        Create an engaging LinkedIn post about data visualization trends from r/dataisbeautiful.
        
        Content Summary:
        {summary_text}
        
        Key Insights:
        - Trending keywords: {', '.join([kw[0] for kw in insights.get('trending_keywords', [])[:5]])}
        - Popular tools: {', '.join([tool[0] for tool in insights.get('top_tools', [])[:3]])}
        - Engagement stats: {insights.get('engagement_stats', {})}
        
        Writing Style Guidelines:
        {style_summary}
        
        Requirements:
        1. Make it engaging and professional
        2. Include specific data points or trends
        3. Add value for data science professionals
        4. Keep it between 150-300 words
        5. End with an engaging question or insight
        6. Use appropriate emojis and hashtags if they match the style
        
        Write the LinkedIn post now:
        """
        
        return prompt
    
    def _get_style_summary(self, style_profile: Dict) -> str:
        """Extract a concise style summary for prompts."""
        ai_profile = style_profile.get('ai_style_profile', {})
        linguistic = style_profile.get('linguistic_patterns', {})
        structural = style_profile.get('structural_patterns', {})
        
        style_elements = []
        
        if ai_profile.get('tone'):
            style_elements.append(f"Tone: {ai_profile['tone']}")
        
        if ai_profile.get('voice_characteristics'):
            style_elements.append(f"Voice: {', '.join(ai_profile['voice_characteristics'])}")
        
        avg_words = linguistic.get('avg_words_per_post', 0)
        if avg_words > 0:
            style_elements.append(f"Length: ~{int(avg_words)} words")
        
        if structural.get('uses_lists_pct', 0) > 30:
            style_elements.append("Often uses lists")
        
        if structural.get('call_to_action_pct', 0) > 50:
            style_elements.append("Includes call-to-action")
        
        if linguistic.get('punctuation_usage', {}).get('emojis', 0) > 0:
            style_elements.append("Uses emojis")
        
        return '; '.join(style_elements) if style_elements else "Professional, engaging style"
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from post content."""
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @ mentions from post content."""
        import re
        mentions = re.findall(r'@\w+', content)
        return mentions
    
    def _estimate_engagement(self, content: str, style_profile: Dict, boost: float = 1.0) -> Dict:
        """
        Estimate potential engagement based on content and style.
        
        Args:
            content: Post content
            style_profile: User's writing style profile
            boost: Multiplier for certain post types
            
        Returns:
            Dictionary with engagement estimates
        """
        base_score = 100  # Base engagement score
        
        # Content factors
        word_count = len(content.split())
        if 100 <= word_count <= 300:
            base_score += 20  # Optimal length bonus
        
        if '?' in content:
            base_score += 15  # Question bonus
        
        hashtag_count = content.count('#')
        if 1 <= hashtag_count <= 5:
            base_score += 10  # Optimal hashtag bonus
        
        emoji_count = len([c for c in content if ord(c) > 127])  # Simple emoji detection
        if emoji_count > 0:
            base_score += 10
        
        # Style profile factors
        historical_engagement = style_profile.get('engagement_patterns', {})
        avg_likes = historical_engagement.get('avg_likes', 50)
        
        # Apply boost for special post types
        base_score = int(base_score * boost)
        
        return {
            'estimated_likes': max(int(avg_likes * (base_score / 100)), 10),
            'estimated_comments': max(int(avg_likes * 0.1 * (base_score / 100)), 2),
            'estimated_shares': max(int(avg_likes * 0.05 * (base_score / 100)), 1),
            'engagement_score': base_score,
            'confidence': 'medium'
        }
    
    def _parse_video_script(self, script: str) -> List[Dict]:
        """Parse video script into structured sections."""
        sections = []
        lines = script.split('\n')
        
        current_section = {'type': 'intro', 'content': '', 'timing': '0-3s'}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Simple parsing logic
            if 'hook' in line.lower() or 'intro' in line.lower():
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'type': 'intro', 'content': line, 'timing': '0-3s'}
            elif 'point' in line.lower() or 'main' in line.lower():
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'type': 'main', 'content': line, 'timing': '3-45s'}
            elif 'call' in line.lower() or 'cta' in line.lower():
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'type': 'cta', 'content': line, 'timing': '45-60s'}
            else:
                current_section['content'] += f" {line}"
        
        if current_section['content']:
            sections.append(current_section)
        
        return sections
    
    def _parse_poll_content(self, content: str) -> Dict:
        """Parse poll content to extract question and options."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        question = ""
        options = []
        context = ""
        
        in_options = False
        
        for line in lines:
            if '?' in line and not question:
                question = line
            elif line.startswith(('A)', 'B)', 'C)', 'D)', '1.', '2.', '3.', '4.', '-', '•')):
                in_options = True
                option = line.split(')', 1)[-1].split('.', 1)[-1].strip(' -•')
                options.append(option)
            elif not in_options and not question:
                context += f" {line}"
        
        return {
            'question': question or "What's your preferred approach?",
            'options': options[:4] if options else ['Option A', 'Option B', 'Option C', 'Option D'],
            'context': context.strip()
        }
    
    def _generate_fallback_post(self, summary_data: Dict, post_type: str = 'standard') -> Dict:
        """Generate a basic fallback post if AI generation fails."""
        fallback_content = """🔍 Latest insights from the data visualization community:

📈 Trending topics include climate data, tech salaries, and personal analytics
🛠️ Python and R continue to dominate as preferred tools
📊 Original content (OC) posts are getting the most engagement

The r/dataisbeautiful community never ceases to amaze with creative data storytelling!

What's your favorite data visualization from this week?

#DataScience #DataVisualization #Analytics #DataStorytelling"""
        
        return {
            'post_type': post_type,
            'content': fallback_content,
            'hashtags': ['#DataScience', '#DataVisualization', '#Analytics', '#DataStorytelling'],
            'mentions': [],
            'estimated_engagement': {
                'estimated_likes': 50,
                'estimated_comments': 8,
                'estimated_shares': 3,
                'engagement_score': 85,
                'confidence': 'low'
            },
            'character_count': len(fallback_content),
            'word_count': len(fallback_content.split()),
            'generation_timestamp': datetime.now().isoformat(),
            'is_fallback': True
        }
    
    def generate_content_calendar(self, summary_data: Dict, 
                                 style_profile: Dict, 
                                 days: int = 7) -> List[Dict]:
        """
        Generate a content calendar with multiple post variations.
        
        Args:
            summary_data: Summary data from ContentSummarizer
            style_profile: User's writing style profile
            days: Number of days to generate content for
            
        Returns:
            List of scheduled post suggestions
        """
        calendar = []
        post_types = ['standard', 'poll', 'carousel', 'video_script']
        
        for day in range(days):
            post_type = post_types[day % len(post_types)]
            
            post = self.generate_post_from_summary(summary_data, style_profile, post_type)
            
            calendar_entry = {
                'day': day + 1,
                'suggested_post_time': '9:00 AM' if day % 2 == 0 else '2:00 PM',
                'post_type': post_type,
                'post_data': post,
                'notes': self._get_scheduling_notes(post_type),
                'priority': 'high' if post_type in ['standard', 'poll'] else 'medium'
            }
            
            calendar.append(calendar_entry)
        
        return calendar
    
    def _get_scheduling_notes(self, post_type: str) -> List[str]:
        """Get scheduling and optimization notes for different post types."""
        notes = {
            'standard': [
                "Best posted on weekdays between 8-10 AM",
                "Engage with comments within first 2 hours",
                "Consider boosting if engagement is high"
            ],
            'poll': [
                "Post early in the week for maximum participation",
                "Share results in a follow-up post",
                "Encourage discussion in comments"
            ],
            'carousel': [
                "Design slides before posting",
                "Test readability on mobile devices",
                "Include swipe prompt in caption"
            ],
            'video_script': [
                "Record video with good lighting and audio",
                "Add captions for accessibility",
                "Upload natively to LinkedIn for best reach"
            ]
        }
        
        return notes.get(post_type, ["Post during peak engagement hours"])
    
    def save_generated_content(self, content: Dict, filename: str = "linkedin_post.json"):
        """Save generated content to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            logger.info(f"Generated content saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save generated content: {str(e)}")