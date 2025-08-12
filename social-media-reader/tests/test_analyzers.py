import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from pathlib import Path

from src.analyzers.style_analyzer import WritingStyleAnalyzer
from src.analyzers.content_summarizer import ContentSummarizer


class TestWritingStyleAnalyzer:
    """Test cases for Writing Style Analyzer."""
    
    @pytest.fixture
    def analyzer(self, mock_openai_client):
        """Create analyzer with mocked OpenAI client."""
        with patch('src.analyzers.style_analyzer.openai.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            analyzer = WritingStyleAnalyzer("test-api-key", "gpt-4")
            return analyzer
    
    def test_init(self):
        """Test analyzer initialization."""
        with patch('src.analyzers.style_analyzer.openai.OpenAI') as mock_openai:
            analyzer = WritingStyleAnalyzer("test-key", "gpt-3.5-turbo")
            assert analyzer.model == "gpt-3.5-turbo"
            assert analyzer.style_profile == {}
    
    def test_analyze_posts_empty_input(self, analyzer):
        """Test analyzing empty post list."""
        result = analyzer.analyze_posts([])
        assert result == {}
    
    def test_analyze_posts_no_text(self, analyzer):
        """Test analyzing posts without text content."""
        posts_without_text = [
            {"likes": 50, "comments": 10},
            {"timestamp": "2024-01-15", "shares": 5}
        ]
        result = analyzer.analyze_posts(posts_without_text)
        assert result == {}
    
    def test_analyze_linguistic_patterns(self, analyzer, sample_linkedin_posts):
        """Test linguistic pattern analysis."""
        texts = [post['text'] for post in sample_linkedin_posts]
        patterns = analyzer._analyze_linguistic_patterns(texts)
        
        assert 'avg_words_per_post' in patterns
        assert 'avg_sentences_per_post' in patterns
        assert 'vocabulary_diversity' in patterns
        assert 'most_common_words' in patterns
        assert 'readability' in patterns
        assert 'punctuation_usage' in patterns
        
        # Check that values are reasonable
        assert patterns['avg_words_per_post'] > 0
        assert patterns['vocabulary_diversity'] > 0
        assert patterns['vocabulary_diversity'] <= 1
        
        # Check punctuation usage
        punctuation = patterns['punctuation_usage']
        assert 'exclamation_marks' in punctuation
        assert 'question_marks' in punctuation
        assert 'emojis' in punctuation
        assert 'hashtags' in punctuation
    
    def test_analyze_structural_patterns(self, analyzer, sample_linkedin_posts):
        """Test structural pattern analysis."""
        texts = [post['text'] for post in sample_linkedin_posts]
        patterns = analyzer._analyze_structural_patterns(texts)
        
        assert 'uses_lists_pct' in patterns
        assert 'uses_bullet_points_pct' in patterns
        assert 'call_to_action_pct' in patterns
        assert 'opening_patterns' in patterns
        assert 'closing_patterns' in patterns
        
        # Check percentage calculations
        assert 0 <= patterns['uses_lists_pct'] <= 100
        assert 0 <= patterns['call_to_action_pct'] <= 100
    
    def test_analyze_content_themes(self, analyzer, sample_linkedin_posts):
        """Test content theme analysis."""
        texts = [post['text'] for post in sample_linkedin_posts]
        themes = analyzer._analyze_content_themes(texts)
        
        assert 'theme_scores' in themes
        assert 'dominant_themes' in themes
        assert 'emotional_tone' in themes
        
        # Check theme scores
        theme_scores = themes['theme_scores']
        assert 'technology' in theme_scores
        assert 'learning' in theme_scores
        
        # Check emotional tone
        tone = themes['emotional_tone']
        assert 'positive_score' in tone
        assert 'negative_score' in tone
        assert 'overall_tone' in tone
        assert tone['overall_tone'] in ['positive', 'negative', 'neutral']
    
    def test_analyze_engagement_patterns(self, analyzer, sample_linkedin_posts):
        """Test engagement pattern analysis."""
        patterns = analyzer._analyze_engagement_patterns(sample_linkedin_posts)
        
        assert 'avg_likes' in patterns
        assert 'avg_comments' in patterns
        assert 'avg_shares' in patterns
        assert 'high_engagement_posts' in patterns
        assert 'optimal_word_count_range' in patterns
        
        # Check averages are reasonable
        assert patterns['avg_likes'] >= 0
        assert patterns['avg_comments'] >= 0
        assert patterns['avg_shares'] >= 0
    
    def test_find_optimal_word_count(self, analyzer, sample_linkedin_posts):
        """Test optimal word count calculation."""
        min_count, max_count = analyzer._find_optimal_word_count(sample_linkedin_posts)
        
        assert min_count >= 0
        assert max_count >= min_count
    
    @patch('src.analyzers.style_analyzer.json.loads')
    def test_generate_ai_style_profile(self, mock_json_loads, analyzer, sample_linkedin_posts):
        """Test AI style profile generation."""
        # Mock the JSON response
        mock_style_profile = {
            "tone": "professional",
            "voice_characteristics": ["analytical", "engaging"],
            "common_phrases": ["data shows", "insights reveal"],
            "storytelling_style": "data-driven",
            "engagement_techniques": ["questions", "statistics"],
            "typical_post_structure": "hook-content-cta",
            "key_style_elements": ["emojis", "hashtags"]
        }
        mock_json_loads.return_value = mock_style_profile
        
        texts = [post['text'] for post in sample_linkedin_posts]
        profile = analyzer._generate_ai_style_profile(texts)
        
        assert 'tone' in profile
        assert 'voice_characteristics' in profile
        assert 'common_phrases' in profile
        assert profile == mock_style_profile
    
    def test_full_analysis_workflow(self, analyzer, sample_linkedin_posts):
        """Test complete analysis workflow."""
        with patch.object(analyzer, '_generate_ai_style_profile') as mock_ai_profile:
            mock_ai_profile.return_value = {
                "tone": "professional",
                "voice_characteristics": ["analytical"],
                "engagement_techniques": ["questions"]
            }
            
            result = analyzer.analyze_posts(sample_linkedin_posts)
            
            assert 'linguistic_patterns' in result
            assert 'structural_patterns' in result
            assert 'content_themes' in result
            assert 'engagement_patterns' in result
            assert 'ai_style_profile' in result
            
            # Check that style_profile was stored
            assert analyzer.style_profile == result
    
    def test_generate_style_summary(self, analyzer, sample_style_profile):
        """Test style summary generation."""
        analyzer.style_profile = sample_style_profile
        summary = analyzer.generate_style_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Average post length" in summary
    
    def test_save_and_load_style_profile(self, analyzer, sample_style_profile, temp_dir):
        """Test saving and loading style profiles."""
        analyzer.style_profile = sample_style_profile
        
        # Save profile
        filename = Path(temp_dir) / "test_style.json"
        analyzer.save_style_profile(str(filename))
        
        assert filename.exists()
        
        # Load profile
        new_analyzer = WritingStyleAnalyzer("test-key")
        new_analyzer.load_style_profile(str(filename))
        
        assert new_analyzer.style_profile == sample_style_profile


class TestContentSummarizer:
    """Test cases for Content Summarizer."""
    
    @pytest.fixture
    def summarizer(self, mock_openai_client):
        """Create summarizer with mocked OpenAI client."""
        with patch('src.analyzers.content_summarizer.openai.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            summarizer = ContentSummarizer("test-api-key", "gpt-4")
            return summarizer
    
    def test_init(self):
        """Test summarizer initialization."""
        with patch('src.analyzers.content_summarizer.openai.OpenAI') as mock_openai:
            summarizer = ContentSummarizer("test-key", "gpt-3.5-turbo")
            assert summarizer.model == "gpt-3.5-turbo"
    
    def test_summarize_reddit_content_empty_input(self, summarizer, sample_style_profile):
        """Test summarizing empty Reddit posts."""
        result = summarizer.summarize_reddit_content([], sample_style_profile)
        assert result == {}
    
    def test_select_top_posts(self, summarizer, sample_reddit_posts):
        """Test selecting top posts for analysis."""
        selected_posts = summarizer._select_top_posts(sample_reddit_posts, max_posts=2)
        
        assert len(selected_posts) == 2
        # Posts should be sorted by engagement (score + comments)
        assert selected_posts[0]['score'] >= selected_posts[1]['score']
    
    def test_categorize_content(self, summarizer, sample_reddit_posts):
        """Test content categorization."""
        categories = summarizer._categorize_content(sample_reddit_posts)
        
        expected_categories = [
            'data_visualizations', 'datasets_and_tools', 'analysis_and_insights',
            'tutorials_and_guides', 'trends_and_patterns', 'personal_projects'
        ]
        
        for category in expected_categories:
            assert category in categories
            assert isinstance(categories[category], list)
        
        # At least some posts should be categorized
        total_categorized = sum(len(posts) for posts in categories.values())
        assert total_categorized > 0
    
    def test_extract_insights(self, summarizer, sample_reddit_posts):
        """Test insight extraction."""
        insights = summarizer._extract_insights(sample_reddit_posts)
        
        assert 'trending_keywords' in insights
        assert 'top_tools' in insights
        assert 'popular_data_sources' in insights
        assert 'engagement_stats' in insights
        assert 'content_themes' in insights
        
        # Check engagement stats
        stats = insights['engagement_stats']
        assert 'avg_score' in stats
        assert 'avg_comments' in stats
        assert 'total_posts_analyzed' in stats
        assert stats['total_posts_analyzed'] == len(sample_reddit_posts)
    
    def test_identify_content_themes(self, summarizer, sample_reddit_posts):
        """Test content theme identification."""
        themes = summarizer._identify_content_themes(sample_reddit_posts)
        
        assert isinstance(themes, list)
        
        # Check theme structure
        for theme in themes:
            assert 'theme' in theme
            assert 'post_count' in theme
            assert 'avg_engagement' in theme
            assert 'sample_titles' in theme
            assert isinstance(theme['sample_titles'], list)
    
    def test_prepare_content_for_ai(self, summarizer, sample_reddit_posts, sample_style_profile):
        """Test content preparation for AI processing."""
        categorized_content = summarizer._categorize_content(sample_reddit_posts)
        insights = summarizer._extract_insights(sample_reddit_posts)
        
        content_summary = summarizer._prepare_content_for_ai(categorized_content, insights)
        
        assert isinstance(content_summary, str)
        assert "CATEGORIES:" in content_summary
        assert "KEY INSIGHTS:" in content_summary
    
    def test_create_style_instruction(self, summarizer, sample_style_profile):
        """Test style instruction creation."""
        instruction = summarizer._create_style_instruction(sample_style_profile)
        
        assert isinstance(instruction, str)
        assert len(instruction) > 0
        
        # Should contain some style guidance
        style_keywords = ['tone', 'voice', 'words', 'professional']
        assert any(keyword in instruction.lower() for keyword in style_keywords)
    
    def test_generate_styled_summary(self, summarizer, sample_reddit_posts, sample_style_profile):
        """Test styled summary generation."""
        categorized_content = summarizer._categorize_content(sample_reddit_posts)
        insights = summarizer._extract_insights(sample_reddit_posts)
        
        summary = summarizer._generate_styled_summary(categorized_content, insights, sample_style_profile)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_generate_fallback_summary(self, summarizer, sample_reddit_posts, sample_style_profile):
        """Test fallback summary generation."""
        categorized_content = summarizer._categorize_content(sample_reddit_posts)
        insights = summarizer._extract_insights(sample_reddit_posts)
        
        fallback_summary = summarizer._generate_fallback_summary(categorized_content, insights)
        
        assert isinstance(fallback_summary, str)
        assert len(fallback_summary) > 0
        assert "r/dataisbeautiful" in fallback_summary
        assert "🔍" in fallback_summary  # Should contain emojis
    
    def test_full_summarization_workflow(self, summarizer, sample_reddit_posts, sample_style_profile):
        """Test complete summarization workflow."""
        result = summarizer.summarize_reddit_content(
            sample_reddit_posts, 
            sample_style_profile, 
            max_posts_to_analyze=10
        )
        
        assert 'summary' in result
        assert 'metadata' in result
        assert 'insights' in result
        assert 'categorized_content' in result
        
        # Check metadata
        metadata = result['metadata']
        assert 'posts_analyzed' in metadata
        assert 'total_posts_available' in metadata
        assert 'categories' in metadata
        assert 'generation_timestamp' in metadata
        assert metadata['style_applied'] == True
    
    def test_generate_multiple_variations(self, summarizer, sample_reddit_posts, sample_style_profile):
        """Test generating multiple summary variations."""
        variations = summarizer.generate_multiple_variations(
            sample_reddit_posts, 
            sample_style_profile, 
            num_variations=3
        )
        
        assert len(variations) == 3
        
        for i, variation in enumerate(variations):
            assert 'variation' in variation
            assert 'focus' in variation
            assert 'summary' in variation
            assert 'timestamp' in variation
            assert variation['variation'] == i + 1
    
    def test_save_summary(self, summarizer, sample_summary_data, temp_dir):
        """Test saving summary to file."""
        filename = Path(temp_dir) / "test_summary.json"
        summarizer.save_summary(sample_summary_data, str(filename))
        
        assert filename.exists()
        
        with open(filename, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == sample_summary_data


class TestAnalyzerIntegration:
    """Integration tests for analyzers."""
    
    def test_style_analysis_to_summarization_workflow(self, sample_linkedin_posts, sample_reddit_posts):
        """Test complete workflow from style analysis to summarization."""
        with patch('src.analyzers.style_analyzer.openai.OpenAI') as mock_openai1, \
             patch('src.analyzers.content_summarizer.openai.OpenAI') as mock_openai2:
            
            # Mock OpenAI responses
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "tone": "professional",
                "voice_characteristics": ["analytical"],
                "common_phrases": ["data shows"],
                "storytelling_style": "direct",
                "engagement_techniques": ["questions"],
                "typical_post_structure": "linear",
                "key_style_elements": ["hashtags"]
            })
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_openai1.return_value = mock_client
            mock_openai2.return_value = mock_client
            
            # Analyze writing style
            analyzer = WritingStyleAnalyzer("test-key")
            style_profile = analyzer.analyze_posts(sample_linkedin_posts)
            
            assert len(style_profile) > 0
            
            # Generate summary using style profile
            summarizer = ContentSummarizer("test-key")
            summary_result = summarizer.summarize_reddit_content(
                sample_reddit_posts, 
                style_profile,
                max_posts_to_analyze=5
            )
            
            assert 'summary' in summary_result
            assert 'metadata' in summary_result
            assert summary_result['metadata']['style_applied'] == True
    
    def test_error_handling_in_analyzers(self):
        """Test error handling in analyzers."""
        # Test style analyzer with invalid API key
        with patch('src.analyzers.style_analyzer.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            analyzer = WritingStyleAnalyzer("invalid-key")
            
            # Should handle API errors gracefully
            style_profile = analyzer._generate_ai_style_profile(["test text"])
            assert isinstance(style_profile, dict)
            assert 'tone' in style_profile  # Should return fallback profile
        
        # Test content summarizer with API errors
        with patch('src.analyzers.content_summarizer.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            summarizer = ContentSummarizer("invalid-key")
            
            # Should fall back to non-AI summary
            summary = summarizer._generate_styled_summary({}, {}, {})
            assert isinstance(summary, str)
            assert len(summary) > 0
    
    def test_data_consistency_across_analyzers(self, sample_linkedin_posts, sample_reddit_posts):
        """Test data consistency between analyzers."""
        with patch('src.analyzers.style_analyzer.openai.OpenAI'), \
             patch('src.analyzers.content_summarizer.openai.OpenAI'):
            
            # Analyze style
            analyzer = WritingStyleAnalyzer("test-key")
            
            # Mock AI response to avoid API calls
            with patch.object(analyzer, '_generate_ai_style_profile') as mock_ai:
                mock_ai.return_value = {
                    "tone": "professional",
                    "voice_characteristics": ["analytical"]
                }
                
                style_profile = analyzer.analyze_posts(sample_linkedin_posts)
                
                # Check that all required sections exist
                required_sections = [
                    'linguistic_patterns', 'structural_patterns', 
                    'content_themes', 'engagement_patterns', 'ai_style_profile'
                ]
                
                for section in required_sections:
                    assert section in style_profile
                    assert isinstance(style_profile[section], dict)
                
                # Use style profile in summarizer
                summarizer = ContentSummarizer("test-key")
                
                # Mock summarizer methods to avoid API calls
                with patch.object(summarizer, '_generate_styled_summary') as mock_summary:
                    mock_summary.return_value = "Test summary content"
                    
                    result = summarizer.summarize_reddit_content(
                        sample_reddit_posts, style_profile
                    )
                    
                    # Verify the style profile was used
                    assert result['metadata']['style_applied'] == True