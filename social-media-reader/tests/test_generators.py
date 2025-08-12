import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

from src.generators.linkedin_post_generator import LinkedInPostGenerator


class TestLinkedInPostGenerator:
    """Test cases for LinkedIn Post Generator."""
    
    @pytest.fixture
    def generator(self, mock_openai_client):
        """Create generator with mocked OpenAI client."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            generator = LinkedInPostGenerator("test-api-key", "gpt-4")
            return generator
    
    def test_init(self):
        """Test generator initialization."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            generator = LinkedInPostGenerator("test-key", "gpt-3.5-turbo")
            assert generator.model == "gpt-3.5-turbo"
    
    def test_generate_post_from_summary_standard(self, generator, sample_summary_data, sample_style_profile):
        """Test generating standard post from summary data."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="standard"
        )
        
        assert result['post_type'] == 'standard'
        assert 'content' in result
        assert 'hashtags' in result
        assert 'mentions' in result
        assert 'estimated_engagement' in result
        assert 'character_count' in result
        assert 'word_count' in result
        assert 'generation_timestamp' in result
        assert 'metadata' in result
        
        # Check engagement estimation
        engagement = result['estimated_engagement']
        assert 'estimated_likes' in engagement
        assert 'estimated_comments' in engagement
        assert 'estimated_shares' in engagement
        assert 'engagement_score' in engagement
        
        # Check metadata
        metadata = result['metadata']
        assert 'style_applied' in metadata
        assert metadata['style_applied'] == True
    
    def test_generate_post_from_summary_carousel(self, generator, sample_summary_data, sample_style_profile):
        """Test generating carousel post."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="carousel"
        )
        
        assert result['post_type'] == 'carousel'
        assert 'main_content' in result
        assert 'slides' in result
        assert 'total_slides' in result
        assert 'instructions' in result
        
        # Check slides structure
        slides = result['slides']
        assert len(slides) > 0
        
        for slide in slides:
            assert 'slide_number' in slide
            assert 'title' in slide
            assert 'content' in slide
            assert 'type' in slide
    
    def test_generate_post_from_summary_video_script(self, generator, sample_summary_data, sample_style_profile):
        """Test generating video script."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="video_script"
        )
        
        assert result['post_type'] == 'video_script'
        assert 'full_script' in result
        assert 'sections' in result
        assert 'estimated_duration' in result
        assert 'video_type' in result
        assert 'production_notes' in result
        
        # Check sections
        sections = result['sections']
        assert isinstance(sections, list)
    
    def test_generate_post_from_summary_poll(self, generator, sample_summary_data, sample_style_profile):
        """Test generating poll post."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="poll"
        )
        
        assert result['post_type'] == 'poll'
        assert 'content' in result
        assert 'poll_question' in result
        assert 'poll_options' in result
        assert 'context_text' in result
        assert 'poll_duration' in result
        assert 'engagement_tips' in result
        
        # Check poll options
        options = result['poll_options']
        assert isinstance(options, list)
        assert len(options) >= 2  # Minimum for a poll
        assert len(options) <= 4  # LinkedIn poll limit
    
    def test_generate_post_unknown_type(self, generator, sample_summary_data, sample_style_profile):
        """Test handling unknown post type."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="unknown_type"
        )
        
        # Should default to standard post
        assert result['post_type'] == 'standard'
    
    def test_create_standard_post_prompt(self, generator, sample_style_profile):
        """Test standard post prompt creation."""
        summary_text = "Test summary of data trends"
        insights = {
            'trending_keywords': [('python', 10), ('data', 8)],
            'top_tools': [('matplotlib', 5), ('seaborn', 3)],
            'engagement_stats': {'avg_score': 1500, 'avg_comments': 100}
        }
        
        prompt = generator._create_standard_post_prompt(summary_text, insights, sample_style_profile)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Content Summary:" in prompt
        assert "Key Insights:" in prompt
        assert "Writing Style Guidelines:" in prompt
        assert "Requirements:" in prompt
    
    def test_get_style_summary(self, generator, sample_style_profile):
        """Test style summary extraction."""
        style_summary = generator._get_style_summary(sample_style_profile)
        
        assert isinstance(style_summary, str)
        assert len(style_summary) > 0
        
        # Should contain key style elements
        expected_elements = ['tone', 'voice', 'words']
        style_lower = style_summary.lower()
        assert any(element in style_lower for element in expected_elements)
    
    def test_extract_hashtags(self, generator):
        """Test hashtag extraction."""
        content = "Great insights about #DataScience and #MachineLearning trends! #AI #Analytics"
        hashtags = generator._extract_hashtags(content)
        
        expected_hashtags = ['#DataScience', '#MachineLearning', '#AI', '#Analytics']
        assert hashtags == expected_hashtags
    
    def test_extract_mentions(self, generator):
        """Test mention extraction."""
        content = "Thanks to @johndoe and @janedoe for the collaboration!"
        mentions = generator._extract_mentions(content)
        
        expected_mentions = ['@johndoe', '@janedoe']
        assert mentions == expected_mentions
    
    def test_estimate_engagement(self, generator, sample_style_profile):
        """Test engagement estimation."""
        content = "This is a test post with optimal length and a question? #DataScience 📊"
        
        engagement = generator._estimate_engagement(content, sample_style_profile)
        
        assert 'estimated_likes' in engagement
        assert 'estimated_comments' in engagement
        assert 'estimated_shares' in engagement
        assert 'engagement_score' in engagement
        assert 'confidence' in engagement
        
        # Check values are reasonable
        assert engagement['estimated_likes'] > 0
        assert engagement['estimated_comments'] >= 0
        assert engagement['estimated_shares'] >= 0
        assert engagement['engagement_score'] > 0
    
    def test_estimate_engagement_with_boost(self, generator, sample_style_profile):
        """Test engagement estimation with boost factor."""
        content = "Test post content"
        
        normal_engagement = generator._estimate_engagement(content, sample_style_profile, boost=1.0)
        boosted_engagement = generator._estimate_engagement(content, sample_style_profile, boost=1.5)
        
        # Boosted engagement should be higher
        assert boosted_engagement['engagement_score'] > normal_engagement['engagement_score']
        assert boosted_engagement['estimated_likes'] > normal_engagement['estimated_likes']
    
    def test_parse_video_script(self, generator):
        """Test video script parsing."""
        script = """
        Hook: Attention-grabbing opening
        Main Point 1: First key insight
        Main Point 2: Second key insight
        Call to Action: Ask for engagement
        """
        
        sections = generator._parse_video_script(script)
        
        assert isinstance(sections, list)
        assert len(sections) > 0
        
        for section in sections:
            assert 'type' in section
            assert 'content' in section
            assert 'timing' in section
    
    def test_parse_poll_content(self, generator):
        """Test poll content parsing."""
        poll_content = """
        What's your favorite data visualization tool?
        
        A) Python (matplotlib/seaborn)
        B) R (ggplot2)
        C) Tableau
        D) Power BI
        
        I'm curious about the community preferences!
        """
        
        parsed = generator._parse_poll_content(poll_content)
        
        assert 'question' in parsed
        assert 'options' in parsed
        assert 'context' in parsed
        
        # Check question was extracted
        assert '?' in parsed['question']
        
        # Check options were extracted
        options = parsed['options']
        assert len(options) == 4
        assert 'Python' in options[0]
        assert 'R' in options[1]
    
    def test_generate_fallback_post(self, generator, sample_summary_data):
        """Test fallback post generation."""
        fallback = generator._generate_fallback_post(sample_summary_data)
        
        assert fallback['post_type'] == 'standard'
        assert 'content' in fallback
        assert 'hashtags' in fallback
        assert fallback['is_fallback'] == True
        
        # Check content has expected elements
        content = fallback['content']
        assert 'r/dataisbeautiful' in content
        assert '#DataScience' in content
        assert len(content) > 0
    
    def test_generate_content_calendar(self, generator, sample_summary_data, sample_style_profile):
        """Test content calendar generation."""
        calendar = generator.generate_content_calendar(
            sample_summary_data, 
            sample_style_profile, 
            days=5
        )
        
        assert len(calendar) == 5
        
        for day, entry in enumerate(calendar):
            assert entry['day'] == day + 1
            assert 'suggested_post_time' in entry
            assert 'post_type' in entry
            assert 'post_data' in entry
            assert 'notes' in entry
            assert 'priority' in entry
            
            # Check post data structure
            post_data = entry['post_data']
            assert 'post_type' in post_data
            assert entry['post_type'] == post_data['post_type']
    
    def test_get_scheduling_notes(self, generator):
        """Test scheduling notes generation."""
        post_types = ['standard', 'poll', 'carousel', 'video_script', 'unknown']
        
        for post_type in post_types:
            notes = generator._get_scheduling_notes(post_type)
            assert isinstance(notes, list)
            assert len(notes) > 0
            assert all(isinstance(note, str) for note in notes)
    
    def test_save_generated_content(self, generator, temp_dir):
        """Test saving generated content."""
        test_content = {
            'post_type': 'standard',
            'content': 'Test content',
            'hashtags': ['#test'],
            'generation_timestamp': '2024-01-15T10:00:00'
        }
        
        filename = Path(temp_dir) / "test_content.json"
        generator.save_generated_content(test_content, str(filename))
        
        assert filename.exists()
        
        with open(filename, 'r') as f:
            saved_content = json.load(f)
        
        assert saved_content == test_content
    
    def test_api_error_handling(self, sample_summary_data, sample_style_profile):
        """Test handling of OpenAI API errors."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            # Mock API error
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            generator = LinkedInPostGenerator("test-key")
            
            # Should fall back to basic generation
            result = generator.generate_post_from_summary(
                sample_summary_data, 
                sample_style_profile, 
                post_type="standard"
            )
            
            # Should return fallback post
            assert 'is_fallback' in result
            assert result['is_fallback'] == True
    
    def test_empty_data_handling(self, generator, sample_style_profile):
        """Test handling of empty or invalid data."""
        empty_summary = {
            'summary': '',
            'metadata': {},
            'insights': {}
        }
        
        result = generator.generate_post_from_summary(
            empty_summary, 
            sample_style_profile, 
            post_type="standard"
        )
        
        # Should still generate a post (using fallback if necessary)
        assert 'content' in result
        assert len(result['content']) > 0
    
    def test_content_length_validation(self, generator, sample_summary_data, sample_style_profile):
        """Test that generated content meets length requirements."""
        result = generator.generate_post_from_summary(
            sample_summary_data, 
            sample_style_profile, 
            post_type="standard"
        )
        
        content = result['content']
        word_count = result['word_count']
        char_count = result['character_count']
        
        # Basic validation
        assert word_count > 0
        assert char_count > 0
        assert word_count == len(content.split())
        assert char_count == len(content)
        
        # LinkedIn has character limits
        assert char_count <= 3000  # LinkedIn post limit
    
    def test_hashtag_limit_enforcement(self, generator):
        """Test that hashtag extraction respects limits."""
        content_with_many_hashtags = """
        Great insights about #DataScience #MachineLearning #AI #Analytics 
        #Visualization #Python #R #Tableau #Statistics #BigData #Cloud #Tech
        """
        
        hashtags = generator._extract_hashtags(content_with_many_hashtags)
        
        # Should extract all hashtags found (the limit is enforced during generation)
        assert len(hashtags) > 5  # More than typical limit
        assert all(tag.startswith('#') for tag in hashtags)


class TestGeneratorIntegration:
    """Integration tests for the post generator."""
    
    def test_full_generation_pipeline(self, sample_summary_data, sample_style_profile):
        """Test complete post generation pipeline."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            # Mock successful API response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Generated LinkedIn post about data visualization trends! 📊 #DataScience"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            generator = LinkedInPostGenerator("test-key")
            
            # Test different post types
            post_types = ['standard', 'carousel', 'video_script', 'poll']
            
            for post_type in post_types:
                result = generator.generate_post_from_summary(
                    sample_summary_data,
                    sample_style_profile,
                    post_type=post_type
                )
                
                assert result['post_type'] == post_type
                assert 'generation_timestamp' in result
                
                # Verify type-specific fields
                if post_type == 'standard':
                    assert 'content' in result
                    assert 'hashtags' in result
                elif post_type == 'carousel':
                    assert 'slides' in result
                    assert 'main_content' in result
                elif post_type == 'video_script':
                    assert 'full_script' in result
                    assert 'sections' in result
                elif post_type == 'poll':
                    assert 'poll_question' in result
                    assert 'poll_options' in result
    
    def test_style_consistency_across_types(self, sample_summary_data, sample_style_profile):
        """Test that style is consistently applied across different post types."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Professional data insights with engaging tone! 🔍"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            generator = LinkedInPostGenerator("test-key")
            
            # Generate different post types
            standard_post = generator.generate_post_from_summary(
                sample_summary_data, sample_style_profile, "standard"
            )
            
            poll_post = generator.generate_post_from_summary(
                sample_summary_data, sample_style_profile, "poll"
            )
            
            # Both should have similar engagement characteristics
            standard_engagement = standard_post['estimated_engagement']
            poll_engagement = poll_post['estimated_engagement']
            
            # Poll posts typically get higher engagement
            assert poll_engagement['engagement_score'] >= standard_engagement['engagement_score']
    
    def test_content_calendar_consistency(self, sample_summary_data, sample_style_profile):
        """Test content calendar generation consistency."""
        with patch('src.generators.linkedin_post_generator.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Calendar post content"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            generator = LinkedInPostGenerator("test-key")
            
            calendar = generator.generate_content_calendar(
                sample_summary_data,
                sample_style_profile,
                days=7
            )
            
            # Check that different post types are distributed
            post_types = [entry['post_type'] for entry in calendar]
            unique_types = set(post_types)
            assert len(unique_types) > 1  # Should have variety
            
            # Check that all entries have required fields
            for entry in calendar:
                assert 'day' in entry
                assert 'suggested_post_time' in entry
                assert 'post_data' in entry
                assert 'notes' in entry
                assert 'priority' in entry
                
                # Verify post data is properly structured
                post_data = entry['post_data']
                assert 'post_type' in post_data
                assert 'generation_timestamp' in post_data