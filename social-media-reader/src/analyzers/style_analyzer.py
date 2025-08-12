import openai
import json
import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import statistics
import logging
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index

logger = logging.getLogger(__name__)


class WritingStyleAnalyzer:
    """
    AI-powered writing style analyzer that learns from LinkedIn posts
    and can mimic the writing style for new content generation.
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the style analyzer with OpenAI API credentials.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use for analysis
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        self.style_profile = {}
        
    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """
        Analyze a collection of LinkedIn posts to extract writing style patterns.
        
        Args:
            posts: List of LinkedIn post dictionaries
            
        Returns:
            Dictionary containing comprehensive style analysis
        """
        if not posts:
            logger.warning("No posts provided for analysis")
            return {}
        
        logger.info(f"Analyzing writing style from {len(posts)} posts")
        
        # Extract text content
        texts = [post.get('text', '') for post in posts if post.get('text')]
        if not texts:
            logger.warning("No text content found in posts")
            return {}
        
        # Perform multi-dimensional analysis
        style_analysis = {
            'linguistic_patterns': self._analyze_linguistic_patterns(texts),
            'structural_patterns': self._analyze_structural_patterns(texts),
            'content_themes': self._analyze_content_themes(texts),
            'engagement_patterns': self._analyze_engagement_patterns(posts),
            'ai_style_profile': self._generate_ai_style_profile(texts)
        }
        
        # Store for later use
        self.style_profile = style_analysis
        
        logger.info("Writing style analysis completed")
        return style_analysis
    
    def _analyze_linguistic_patterns(self, texts: List[str]) -> Dict:
        """
        Analyze linguistic patterns including vocabulary, sentence structure, etc.
        
        Args:
            texts: List of post texts
            
        Returns:
            Dictionary with linguistic analysis
        """
        combined_text = ' '.join(texts)
        
        # Basic statistics
        word_counts = [len(text.split()) for text in texts]
        sentence_counts = [len(re.split(r'[.!?]+', text)) for text in texts]
        char_counts = [len(text) for text in texts]
        
        # Vocabulary analysis
        all_words = re.findall(r'\b\w+\b', combined_text.lower())
        word_freq = Counter(all_words)
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        # Readability metrics
        readability_scores = []
        for text in texts:
            if len(text.strip()) > 0:
                try:
                    readability_scores.append({
                        'flesch_reading_ease': flesch_reading_ease(text),
                        'flesch_kincaid_grade': flesch_kincaid_grade(text),
                        'automated_readability_index': automated_readability_index(text)
                    })
                except:
                    continue
        
        # Punctuation and formatting patterns
        punctuation_usage = {
            'exclamation_marks': combined_text.count('!'),
            'question_marks': combined_text.count('?'),
            'emojis': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', combined_text)),
            'hashtags': len(re.findall(r'#\w+', combined_text)),
            'mentions': len(re.findall(r'@\w+', combined_text)),
            'urls': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', combined_text))
        }
        
        return {
            'avg_words_per_post': statistics.mean(word_counts) if word_counts else 0,
            'avg_sentences_per_post': statistics.mean(sentence_counts) if sentence_counts else 0,
            'avg_chars_per_post': statistics.mean(char_counts) if char_counts else 0,
            'vocabulary_diversity': unique_words / total_words if total_words > 0 else 0,
            'most_common_words': word_freq.most_common(20),
            'readability': {
                'avg_flesch_reading_ease': statistics.mean([s['flesch_reading_ease'] for s in readability_scores]) if readability_scores else 0,
                'avg_flesch_kincaid_grade': statistics.mean([s['flesch_kincaid_grade'] for s in readability_scores]) if readability_scores else 0,
                'avg_automated_readability_index': statistics.mean([s['automated_readability_index'] for s in readability_scores]) if readability_scores else 0
            },
            'punctuation_usage': punctuation_usage
        }
    
    def _analyze_structural_patterns(self, texts: List[str]) -> Dict:
        """
        Analyze structural patterns in posts (lists, bullet points, formatting).
        
        Args:
            texts: List of post texts
            
        Returns:
            Dictionary with structural analysis
        """
        patterns = {
            'uses_lists': 0,
            'uses_bullet_points': 0,
            'uses_numbers': 0,
            'uses_line_breaks': 0,
            'opening_patterns': [],
            'closing_patterns': [],
            'call_to_action_usage': 0
        }
        
        # Call-to-action phrases
        cta_patterns = [
            r'what do you think\?',
            r'share your thoughts',
            r'let me know',
            r'comment below',
            r'thoughts\?',
            r'what\'s your experience',
            r'agree or disagree\?'
        ]
        
        for text in texts:
            # Check for list patterns
            if re.search(r'\d+[\.\)]\s', text):
                patterns['uses_numbers'] += 1
            
            if re.search(r'[•·▪▫-]\s', text) or re.search(r'\n\s*[-*]\s', text):
                patterns['uses_bullet_points'] += 1
            
            if '\n' in text:
                patterns['uses_line_breaks'] += 1
            
            # Extract opening and closing sentences
            sentences = re.split(r'[.!?]+', text.strip())
            if sentences and len(sentences[0]) > 10:
                patterns['opening_patterns'].append(sentences[0].strip())
            
            if len(sentences) > 1 and len(sentences[-1]) > 10:
                patterns['closing_patterns'].append(sentences[-1].strip())
            
            # Check for call-to-action patterns
            for cta_pattern in cta_patterns:
                if re.search(cta_pattern, text.lower()):
                    patterns['call_to_action_usage'] += 1
                    break
        
        # Calculate percentages
        total_posts = len(texts)
        if total_posts > 0:
            patterns['uses_lists_pct'] = (patterns['uses_numbers'] / total_posts) * 100
            patterns['uses_bullet_points_pct'] = (patterns['uses_bullet_points'] / total_posts) * 100
            patterns['uses_line_breaks_pct'] = (patterns['uses_line_breaks'] / total_posts) * 100
            patterns['call_to_action_pct'] = (patterns['call_to_action_usage'] / total_posts) * 100
        
        return patterns
    
    def _analyze_content_themes(self, texts: List[str]) -> Dict:
        """
        Analyze content themes and topics using keyword extraction.
        
        Args:
            texts: List of post texts
            
        Returns:
            Dictionary with content theme analysis
        """
        combined_text = ' '.join(texts).lower()
        
        # Professional themes
        professional_keywords = {
            'career': ['career', 'job', 'work', 'profession', 'experience', 'role'],
            'learning': ['learn', 'education', 'skill', 'knowledge', 'growth', 'development'],
            'technology': ['tech', 'technology', 'digital', 'ai', 'data', 'software', 'coding'],
            'leadership': ['lead', 'leadership', 'manage', 'team', 'mentor', 'coach'],
            'networking': ['network', 'connect', 'relationship', 'community', 'collaboration'],
            'success': ['success', 'achievement', 'goal', 'accomplish', 'win', 'victory'],
            'insights': ['insight', 'lesson', 'takeaway', 'learning', 'realization', 'discovery']
        }
        
        theme_scores = {}
        for theme, keywords in professional_keywords.items():
            score = sum(combined_text.count(keyword) for keyword in keywords)
            theme_scores[theme] = score
        
        # Emotional tone indicators
        positive_words = ['great', 'amazing', 'excellent', 'fantastic', 'wonderful', 'love', 'excited', 'proud']
        negative_words = ['difficult', 'challenge', 'problem', 'issue', 'struggle', 'hard', 'tough']
        
        positive_score = sum(combined_text.count(word) for word in positive_words)
        negative_score = sum(combined_text.count(word) for word in negative_words)
        
        return {
            'theme_scores': theme_scores,
            'dominant_themes': sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:5],
            'emotional_tone': {
                'positive_score': positive_score,
                'negative_score': negative_score,
                'overall_tone': 'positive' if positive_score > negative_score else 'negative' if negative_score > positive_score else 'neutral'
            }
        }
    
    def _analyze_engagement_patterns(self, posts: List[Dict]) -> Dict:
        """
        Analyze which types of posts get better engagement.
        
        Args:
            posts: List of LinkedIn post dictionaries
            
        Returns:
            Dictionary with engagement analysis
        """
        if not posts:
            return {}
        
        # Calculate engagement metrics
        likes = [post.get('likes', 0) for post in posts]
        comments = [post.get('comments', 0) for post in posts]
        shares = [post.get('shares', 0) for post in posts]
        word_counts = [len(post.get('text', '').split()) for post in posts]
        
        # Find correlations
        high_engagement_posts = []
        for i, post in enumerate(posts):
            total_engagement = likes[i] + comments[i] + shares[i]
            if total_engagement > statistics.mean(likes + comments + shares):
                high_engagement_posts.append({
                    'text': post.get('text', ''),
                    'likes': likes[i],
                    'comments': comments[i],
                    'shares': shares[i],
                    'word_count': word_counts[i]
                })
        
        return {
            'avg_likes': statistics.mean(likes) if likes else 0,
            'avg_comments': statistics.mean(comments) if comments else 0,
            'avg_shares': statistics.mean(shares) if shares else 0,
            'high_engagement_posts': high_engagement_posts,
            'optimal_word_count_range': self._find_optimal_word_count(posts)
        }
    
    def _find_optimal_word_count(self, posts: List[Dict]) -> Tuple[int, int]:
        """Find the word count range that generates the best engagement."""
        if not posts:
            return (0, 0)
        
        engagement_by_length = []
        for post in posts:
            word_count = len(post.get('text', '').split())
            total_engagement = post.get('likes', 0) + post.get('comments', 0) + post.get('shares', 0)
            engagement_by_length.append((word_count, total_engagement))
        
        # Sort by engagement and find the word count range of top 25% posts
        sorted_by_engagement = sorted(engagement_by_length, key=lambda x: x[1], reverse=True)
        top_quarter = sorted_by_engagement[:len(sorted_by_engagement)//4 or 1]
        
        word_counts = [wc for wc, _ in top_quarter]
        if word_counts:
            return (min(word_counts), max(word_counts))
        return (0, 0)
    
    def _generate_ai_style_profile(self, texts: List[str]) -> Dict:
        """
        Use AI to generate a comprehensive style profile.
        
        Args:
            texts: List of post texts
            
        Returns:
            Dictionary with AI-generated style insights
        """
        try:
            sample_texts = texts[:5]  # Use first 5 posts as sample
            
            prompt = f"""
            Analyze the following LinkedIn posts and create a comprehensive writing style profile. 
            Focus on:
            1. Tone and voice characteristics
            2. Common phrases and expressions
            3. Storytelling approach
            4. Professional vs personal balance
            5. Call-to-action style
            6. Use of questions, lists, and engagement techniques
            
            Posts to analyze:
            {json.dumps(sample_texts, indent=2)}
            
            Please provide a detailed analysis in JSON format with the following structure:
            {{
                "tone": "description of overall tone",
                "voice_characteristics": ["characteristic1", "characteristic2"],
                "common_phrases": ["phrase1", "phrase2"],
                "storytelling_style": "description",
                "engagement_techniques": ["technique1", "technique2"],
                "typical_post_structure": "description",
                "key_style_elements": ["element1", "element2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in writing style analysis and social media content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the JSON response
            style_profile = json.loads(response.choices[0].message.content)
            return style_profile
            
        except Exception as e:
            logger.error(f"Failed to generate AI style profile: {str(e)}")
            return {
                "tone": "professional",
                "voice_characteristics": ["analytical"],
                "common_phrases": [],
                "storytelling_style": "direct",
                "engagement_techniques": [],
                "typical_post_structure": "linear",
                "key_style_elements": []
            }
    
    def generate_style_summary(self) -> str:
        """
        Generate a human-readable summary of the analyzed writing style.
        
        Returns:
            String summary of the writing style
        """
        if not self.style_profile:
            return "No style analysis available. Run analyze_posts() first."
        
        linguistic = self.style_profile.get('linguistic_patterns', {})
        structural = self.style_profile.get('structural_patterns', {})
        themes = self.style_profile.get('content_themes', {})
        ai_profile = self.style_profile.get('ai_style_profile', {})
        
        summary_parts = []
        
        # Basic stats
        avg_words = linguistic.get('avg_words_per_post', 0)
        summary_parts.append(f"Average post length: {avg_words:.0f} words")
        
        # Tone and style
        tone = ai_profile.get('tone', 'professional')
        summary_parts.append(f"Writing tone: {tone}")
        
        # Engagement techniques
        if structural.get('call_to_action_pct', 0) > 50:
            summary_parts.append("Frequently uses call-to-action phrases")
        
        if structural.get('uses_lists_pct', 0) > 30:
            summary_parts.append("Often uses numbered lists")
        
        if linguistic.get('punctuation_usage', {}).get('emojis', 0) > 0:
            summary_parts.append("Uses emojis for engagement")
        
        # Content themes
        dominant_themes = themes.get('dominant_themes', [])
        if dominant_themes:
            top_theme = dominant_themes[0][0]
            summary_parts.append(f"Primary content theme: {top_theme}")
        
        return ". ".join(summary_parts) + "."
    
    def save_style_profile(self, filename: str = "style_profile.json"):
        """Save the analyzed style profile to a JSON file."""
        if not self.style_profile:
            logger.warning("No style profile to save. Run analyze_posts() first.")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.style_profile, f, indent=2, ensure_ascii=False)
            logger.info(f"Style profile saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save style profile: {str(e)}")
    
    def load_style_profile(self, filename: str = "style_profile.json"):
        """Load a previously saved style profile."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.style_profile = json.load(f)
            logger.info(f"Style profile loaded from {filename}")
        except Exception as e:
            logger.error(f"Failed to load style profile: {str(e)}")