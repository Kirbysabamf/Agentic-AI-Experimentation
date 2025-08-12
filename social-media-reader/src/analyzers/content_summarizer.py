import openai
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContentSummarizer:
    """
    AI-powered content summarizer that processes Reddit posts from r/dataisbeautiful
    and creates summaries in the user's writing style.
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the content summarizer.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use for summarization
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
    def summarize_reddit_content(self, reddit_posts: List[Dict], 
                                style_profile: Dict, 
                                max_posts_to_analyze: int = 20) -> Dict:
        """
        Create a comprehensive summary of Reddit content in the user's writing style.
        
        Args:
            reddit_posts: List of Reddit post dictionaries
            style_profile: User's writing style profile
            max_posts_to_analyze: Maximum number of posts to analyze
            
        Returns:
            Dictionary containing the summary and metadata
        """
        if not reddit_posts:
            logger.warning("No Reddit posts provided for summarization")
            return {}
        
        logger.info(f"Summarizing {len(reddit_posts)} Reddit posts")
        
        # Select top posts for analysis
        top_posts = self._select_top_posts(reddit_posts, max_posts_to_analyze)
        
        # Categorize content
        categorized_content = self._categorize_content(top_posts)
        
        # Generate insights and trends
        insights = self._extract_insights(top_posts)
        
        # Create styled summary
        summary = self._generate_styled_summary(categorized_content, insights, style_profile)
        
        return {
            'summary': summary,
            'metadata': {
                'posts_analyzed': len(top_posts),
                'total_posts_available': len(reddit_posts),
                'categories': {cat: len(posts) for cat, posts in categorized_content.items()},
                'generation_timestamp': datetime.now().isoformat(),
                'style_applied': True
            },
            'insights': insights,
            'categorized_content': categorized_content
        }
    
    def _select_top_posts(self, posts: List[Dict], max_posts: int) -> List[Dict]:
        """
        Select the most relevant and high-quality posts for analysis.
        
        Args:
            posts: List of Reddit posts
            max_posts: Maximum number of posts to select
            
        Returns:
            List of selected posts
        """
        # Sort by engagement score (combination of score, comments, and recency)
        def calculate_engagement_score(post):
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)
            
            # Boost score based on engagement
            engagement_score = score + (comments * 2)  # Comments weighted more heavily
            
            # Boost OC (Original Content)
            if post.get('flair_text') == 'OC':
                engagement_score *= 1.5
            
            # Penalize deleted/removed content
            if post.get('author') in ['[deleted]', '[removed]']:
                engagement_score *= 0.1
            
            return engagement_score
        
        sorted_posts = sorted(posts, key=calculate_engagement_score, reverse=True)
        return sorted_posts[:max_posts]
    
    def _categorize_content(self, posts: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize Reddit posts by content type and theme.
        
        Args:
            posts: List of Reddit posts
            
        Returns:
            Dictionary with categorized posts
        """
        categories = {
            'data_visualizations': [],
            'datasets_and_tools': [],
            'analysis_and_insights': [],
            'tutorials_and_guides': [],
            'trends_and_patterns': [],
            'personal_projects': []
        }
        
        for post in posts:
            title = post.get('title', '').lower()
            selftext = post.get('selftext', '').lower()
            combined_text = f"{title} {selftext}"
            
            # Categorization logic
            if any(keyword in combined_text for keyword in ['visualization', 'chart', 'graph', 'plot', '[oc]']):
                categories['data_visualizations'].append(post)
            elif any(keyword in combined_text for keyword in ['dataset', 'data source', 'api', 'tool', 'library']):
                categories['datasets_and_tools'].append(post)
            elif any(keyword in combined_text for keyword in ['analysis', 'research', 'study', 'findings']):
                categories['analysis_and_insights'].append(post)
            elif any(keyword in combined_text for keyword in ['tutorial', 'how to', 'guide', 'learn']):
                categories['tutorials_and_guides'].append(post)
            elif any(keyword in combined_text for keyword in ['trend', 'pattern', 'over time', 'years']):
                categories['trends_and_patterns'].append(post)
            else:
                categories['personal_projects'].append(post)
        
        return categories
    
    def _extract_insights(self, posts: List[Dict]) -> Dict:
        """
        Extract key insights and trending topics from Reddit posts.
        
        Args:
            posts: List of Reddit posts
            
        Returns:
            Dictionary with insights and trends
        """
        from collections import Counter
        import re
        
        # Extract trending topics
        all_titles = ' '.join([post.get('title', '') for post in posts]).lower()
        
        # Data science/visualization keywords
        keywords = [
            'python', 'r', 'javascript', 'tableau', 'matplotlib', 'seaborn', 'plotly',
            'covid', 'climate', 'temperature', 'salary', 'income', 'population',
            'election', 'sports', 'netflix', 'spotify', 'uber', 'tesla',
            'machine learning', 'ai', 'neural network', 'algorithm'
        ]
        
        keyword_mentions = {}
        for keyword in keywords:
            count = all_titles.count(keyword)
            if count > 0:
                keyword_mentions[keyword] = count
        
        # Top tools/technologies mentioned
        tool_patterns = re.findall(r'\b(python|r|javascript|d3|tableau|excel|sql|pandas|numpy)\b', all_titles)
        top_tools = Counter(tool_patterns).most_common(5)
        
        # Popular data sources
        source_patterns = re.findall(r'\b(nasa|census|who|world bank|github|kaggle|netflix|spotify)\b', all_titles)
        popular_sources = Counter(source_patterns).most_common(5)
        
        # Calculate average engagement
        avg_score = sum(post.get('score', 0) for post in posts) / len(posts) if posts else 0
        avg_comments = sum(post.get('num_comments', 0) for post in posts) / len(posts) if posts else 0
        
        return {
            'trending_keywords': sorted(keyword_mentions.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_tools': top_tools,
            'popular_data_sources': popular_sources,
            'engagement_stats': {
                'avg_score': round(avg_score, 1),
                'avg_comments': round(avg_comments, 1),
                'total_posts_analyzed': len(posts)
            },
            'content_themes': self._identify_content_themes(posts)
        }
    
    def _identify_content_themes(self, posts: List[Dict]) -> List[Dict]:
        """
        Identify major content themes from the posts.
        
        Args:
            posts: List of Reddit posts
            
        Returns:
            List of theme dictionaries
        """
        themes = []
        
        # Common themes in r/dataisbeautiful
        theme_keywords = {
            'Climate & Environment': ['climate', 'temperature', 'carbon', 'emission', 'weather', 'global warming'],
            'Technology & AI': ['ai', 'machine learning', 'algorithm', 'tech', 'software', 'coding'],
            'Economics & Finance': ['salary', 'income', 'gdp', 'stock', 'economy', 'finance', 'money'],
            'Health & Demographics': ['covid', 'health', 'population', 'age', 'demographics', 'life expectancy'],
            'Entertainment & Media': ['movie', 'netflix', 'spotify', 'youtube', 'tv', 'music', 'game'],
            'Sports & Competition': ['olympic', 'sport', 'football', 'basketball', 'soccer', 'competition']
        }
        
        for theme_name, keywords in theme_keywords.items():
            matching_posts = []
            for post in posts:
                title_text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
                if any(keyword in title_text for keyword in keywords):
                    matching_posts.append(post)
            
            if matching_posts:
                avg_engagement = sum(p.get('score', 0) for p in matching_posts) / len(matching_posts)
                themes.append({
                    'theme': theme_name,
                    'post_count': len(matching_posts),
                    'avg_engagement': round(avg_engagement, 1),
                    'sample_titles': [p.get('title', '')[:100] for p in matching_posts[:3]]
                })
        
        return sorted(themes, key=lambda x: x['post_count'], reverse=True)
    
    def _generate_styled_summary(self, categorized_content: Dict, 
                                insights: Dict, 
                                style_profile: Dict) -> str:
        """
        Generate a LinkedIn post summary using the user's writing style.
        
        Args:
            categorized_content: Categorized Reddit posts
            insights: Extracted insights
            style_profile: User's writing style profile
            
        Returns:
            Styled summary text for LinkedIn
        """
        try:
            # Extract style characteristics
            ai_profile = style_profile.get('ai_style_profile', {})
            tone = ai_profile.get('tone', 'professional')
            voice_characteristics = ai_profile.get('voice_characteristics', [])
            common_phrases = ai_profile.get('common_phrases', [])
            engagement_techniques = ai_profile.get('engagement_techniques', [])
            
            linguistic = style_profile.get('linguistic_patterns', {})
            structural = style_profile.get('structural_patterns', {})
            
            # Prepare content for summarization
            content_summary = self._prepare_content_for_ai(categorized_content, insights)
            
            # Create style instruction
            style_instruction = self._create_style_instruction(style_profile)
            
            prompt = f"""
            Create a LinkedIn post that summarizes the latest trends from r/dataisbeautiful. 
            
            Content to summarize:
            {content_summary}
            
            Writing Style Guidelines:
            {style_instruction}
            
            Requirements:
            1. Write in the specified tone and style
            2. Include 2-3 key insights or trends
            3. Make it engaging and professional
            4. Keep it between 150-250 words
            5. Include relevant emojis if the original style uses them
            6. End with an engaging question or call-to-action if that matches the style
            
            Write the LinkedIn post now:
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn content creator who specializes in data science and technology topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate styled summary: {str(e)}")
            return self._generate_fallback_summary(categorized_content, insights)
    
    def _prepare_content_for_ai(self, categorized_content: Dict, insights: Dict) -> str:
        """
        Prepare structured content summary for AI processing.
        
        Args:
            categorized_content: Categorized posts
            insights: Extracted insights
            
        Returns:
            Formatted content string
        """
        content_parts = []
        
        # Category summaries
        content_parts.append("CATEGORIES:")
        for category, posts in categorized_content.items():
            if posts:
                content_parts.append(f"- {category}: {len(posts)} posts")
                # Add sample titles
                sample_titles = [p.get('title', '')[:80] for p in posts[:2]]
                for title in sample_titles:
                    content_parts.append(f"  * {title}")
        
        # Key insights
        content_parts.append("\nKEY INSIGHTS:")
        if insights.get('trending_keywords'):
            top_keywords = [kw[0] for kw in insights['trending_keywords'][:5]]
            content_parts.append(f"- Trending topics: {', '.join(top_keywords)}")
        
        if insights.get('top_tools'):
            top_tools = [tool[0] for tool in insights['top_tools'][:3]]
            content_parts.append(f"- Popular tools: {', '.join(top_tools)}")
        
        if insights.get('content_themes'):
            top_themes = [theme['theme'] for theme in insights['content_themes'][:3]]
            content_parts.append(f"- Main themes: {', '.join(top_themes)}")
        
        return '\n'.join(content_parts)
    
    def _create_style_instruction(self, style_profile: Dict) -> str:
        """
        Create detailed style instructions for the AI.
        
        Args:
            style_profile: User's writing style profile
            
        Returns:
            Style instruction string
        """
        instructions = []
        
        # AI profile characteristics
        ai_profile = style_profile.get('ai_style_profile', {})
        if ai_profile.get('tone'):
            instructions.append(f"Tone: {ai_profile['tone']}")
        
        if ai_profile.get('voice_characteristics'):
            characteristics = ', '.join(ai_profile['voice_characteristics'])
            instructions.append(f"Voice: {characteristics}")
        
        # Structural patterns
        structural = style_profile.get('structural_patterns', {})
        if structural.get('uses_lists_pct', 0) > 30:
            instructions.append("Use numbered lists or bullet points")
        
        if structural.get('call_to_action_pct', 0) > 50:
            instructions.append("Include a call-to-action or engaging question")
        
        # Linguistic patterns
        linguistic = style_profile.get('linguistic_patterns', {})
        avg_words = linguistic.get('avg_words_per_post', 0)
        if avg_words > 0:
            instructions.append(f"Target word count: around {int(avg_words)} words")
        
        emoji_usage = linguistic.get('punctuation_usage', {}).get('emojis', 0)
        if emoji_usage > 0:
            instructions.append("Include relevant emojis")
        
        hashtag_usage = linguistic.get('punctuation_usage', {}).get('hashtags', 0)
        if hashtag_usage > 0:
            instructions.append("Include 2-3 relevant hashtags")
        
        return '; '.join(instructions) if instructions else "Write in a professional, engaging style"
    
    def _generate_fallback_summary(self, categorized_content: Dict, insights: Dict) -> str:
        """
        Generate a basic fallback summary if AI generation fails.
        
        Args:
            categorized_content: Categorized posts
            insights: Extracted insights
            
        Returns:
            Basic summary string
        """
        summary_parts = []
        
        summary_parts.append("🔍 Latest insights from r/dataisbeautiful:")
        summary_parts.append("")
        
        # Top categories
        top_categories = [(cat, posts) for cat, posts in categorized_content.items() if posts]
        top_categories.sort(key=lambda x: len(x[1]), reverse=True)
        
        for i, (category, posts) in enumerate(top_categories[:3]):
            category_name = category.replace('_', ' ').title()
            summary_parts.append(f"{i+1}. {category_name}: {len(posts)} trending posts")
        
        summary_parts.append("")
        
        # Key trends
        if insights.get('trending_keywords'):
            top_keywords = [kw[0] for kw in insights['trending_keywords'][:3]]
            summary_parts.append(f"🔥 Hot topics: {', '.join(top_keywords)}")
        
        if insights.get('top_tools'):
            top_tools = [tool[0] for tool in insights['top_tools'][:3]]
            summary_parts.append(f"🛠️ Popular tools: {', '.join(top_tools)}")
        
        summary_parts.append("")
        summary_parts.append("The data visualization community continues to create amazing insights!")
        summary_parts.append("What's your favorite data story this week?")
        
        return '\n'.join(summary_parts)
    
    def generate_multiple_variations(self, reddit_posts: List[Dict], 
                                   style_profile: Dict, 
                                   num_variations: int = 3) -> List[Dict]:
        """
        Generate multiple variations of the summary with different angles.
        
        Args:
            reddit_posts: List of Reddit posts
            style_profile: User's writing style profile
            num_variations: Number of variations to generate
            
        Returns:
            List of summary variations
        """
        variations = []
        
        # Generate base summary
        base_summary = self.summarize_reddit_content(reddit_posts, style_profile)
        
        # Create variations with different focuses
        focus_angles = [
            "trending tools and technologies",
            "interesting datasets and findings",
            "visualization techniques and best practices"
        ]
        
        for i in range(num_variations):
            angle = focus_angles[i % len(focus_angles)]
            
            # Modify the generation to focus on specific angle
            variation = self._generate_focused_summary(reddit_posts, style_profile, angle)
            variations.append({
                'variation': i + 1,
                'focus': angle,
                'summary': variation,
                'timestamp': datetime.now().isoformat()
            })
        
        return variations
    
    def _generate_focused_summary(self, reddit_posts: List[Dict], 
                                 style_profile: Dict, 
                                 focus_angle: str) -> str:
        """
        Generate a summary focused on a specific angle or theme.
        
        Args:
            reddit_posts: List of Reddit posts
            style_profile: User's writing style profile
            focus_angle: Specific angle to focus on
            
        Returns:
            Focused summary string
        """
        # This would be similar to the main summary generation
        # but with modified prompts to focus on the specific angle
        base_summary = self.summarize_reddit_content(reddit_posts, style_profile)
        
        try:
            focused_prompt = f"""
            Take this summary and rewrite it to focus specifically on: {focus_angle}
            
            Original summary:
            {base_summary.get('summary', '')}
            
            Keep the same writing style but emphasize the {focus_angle} aspect.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at adapting content focus while maintaining writing style."},
                    {"role": "user", "content": focused_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate focused summary: {str(e)}")
            return base_summary.get('summary', 'Unable to generate focused summary.')
    
    def save_summary(self, summary_data: Dict, filename: str = "reddit_summary.json"):
        """Save the generated summary to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Summary saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save summary: {str(e)}")