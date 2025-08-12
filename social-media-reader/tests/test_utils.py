import pytest
import os
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch, Mock

from src.utils.config import Config, get_config, load_config
from src.utils.logger import setup_logger, setup_component_logger, LoggerContextManager, StructuredLogger


class TestConfig:
    """Test cases for Configuration management."""
    
    def test_init_default(self):
        """Test default configuration initialization."""
        config = Config()
        
        # Test default values
        assert config.OPENAI_MODEL == 'gpt-4'
        assert config.USE_MOCK_DATA == False  # Default from env or False
        assert config.MAX_LINKEDIN_POSTS == 50
        assert config.MAX_REDDIT_POSTS == 100
        assert config.LOG_LEVEL == 'INFO'
        assert config.CHROME_HEADLESS == True
    
    def test_init_with_env_file(self, temp_dir):
        """Test initialization with environment file."""
        env_file = Path(temp_dir) / '.env'
        env_content = """
OPENAI_API_KEY=test-key-123
USE_MOCK_DATA=true
MAX_LINKEDIN_POSTS=25
LOG_LEVEL=DEBUG
CHROME_HEADLESS=false
        """
        
        with open(env_file, 'w') as f:
            f.write(env_content.strip())
        
        config = Config(str(env_file))
        
        assert config.OPENAI_API_KEY == 'test-key-123'
        assert config.USE_MOCK_DATA == True
        assert config.MAX_LINKEDIN_POSTS == 25
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.CHROME_HEADLESS == False
    
    def test_boolean_parsing(self):
        """Test boolean value parsing from environment variables."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('anything_else', False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'USE_MOCK_DATA': env_value}):
                config = Config()
                assert config.USE_MOCK_DATA == expected
    
    def test_integer_parsing(self):
        """Test integer value parsing with fallbacks."""
        # Valid integer
        with patch.dict(os.environ, {'MAX_LINKEDIN_POSTS': '75'}):
            config = Config()
            assert config.MAX_LINKEDIN_POSTS == 75
        
        # Invalid integer - should use default
        with patch.dict(os.environ, {'MAX_LINKEDIN_POSTS': 'invalid'}):
            config = Config()
            assert config.MAX_LINKEDIN_POSTS == 50  # Default value
    
    def test_validation_methods(self):
        """Test configuration validation methods."""
        config = Config()
        
        # Test OpenAI validation
        with patch.object(config, 'USE_MOCK_DATA', False):
            with patch.object(config, 'OPENAI_API_KEY', ''):
                assert config.validate_openai_config() == False
            
            with patch.object(config, 'OPENAI_API_KEY', 'valid-key'):
                assert config.validate_openai_config() == True
        
        with patch.object(config, 'USE_MOCK_DATA', True):
            assert config.validate_openai_config() == True  # Should pass with mock data
    
    def test_validate_all(self):
        """Test complete validation."""
        config = Config()
        
        validation_result = config.validate_all()
        
        assert 'openai' in validation_result
        assert 'linkedin' in validation_result
        assert 'reddit' in validation_result
        
        assert isinstance(validation_result['openai'], bool)
        assert isinstance(validation_result['linkedin'], bool)
        assert isinstance(validation_result['reddit'], bool)
    
    def test_create_directories(self, temp_dir):
        """Test directory creation."""
        config = Config()
        
        output_dir = Path(temp_dir) / 'test_output'
        data_dir = Path(temp_dir) / 'test_data'
        
        with patch.object(config, 'OUTPUT_DIR', str(output_dir)):
            with patch.object(config, 'DATA_DIR', str(data_dir)):
                config.create_directories()
                
                assert output_dir.exists()
                assert data_dir.exists()
    
    def test_get_config_summary(self):
        """Test configuration summary generation."""
        config = Config()
        summary = config.get_config_summary()
        
        required_keys = [
            'openai_model', 'use_mock_data', 'max_linkedin_posts',
            'max_reddit_posts', 'output_dir', 'data_dir', 'log_level',
            'chrome_headless', 'feature_flags'
        ]
        
        for key in required_keys:
            assert key in summary
        
        # Test feature flags structure
        feature_flags = summary['feature_flags']
        assert 'video_scripts' in feature_flags
        assert 'carousel_posts' in feature_flags
        assert 'polls' in feature_flags
        assert 'analytics' in feature_flags
    
    def test_save_and_load_config(self, temp_dir):
        """Test saving configuration to file."""
        config = Config()
        
        with patch.object(config, 'DATA_DIR', temp_dir):
            config.save_config('test_config.json')
            
            config_file = Path(temp_dir) / 'test_config.json'
            assert config_file.exists()
            
            # Verify JSON structure
            import json
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
            
            assert 'openai_model' in saved_config
            assert 'feature_flags' in saved_config
    
    def test_env_file_error_handling(self, temp_dir):
        """Test handling of invalid environment files."""
        # Non-existent file
        config = Config('non_existent.env')
        assert config.OPENAI_MODEL == 'gpt-4'  # Should use defaults
        
        # Invalid file content
        invalid_env = Path(temp_dir) / 'invalid.env'
        with open(invalid_env, 'w') as f:
            f.write('invalid content without equals')
        
        config = Config(str(invalid_env))
        assert config.OPENAI_MODEL == 'gpt-4'  # Should still work with defaults
    
    def test_global_config_functions(self):
        """Test global configuration functions."""
        # Test get_config
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2  # Should return same instance
        
        # Test load_config
        with patch('src.utils.config.Config') as mock_config_class:
            mock_instance = Mock()
            mock_config_class.return_value = mock_instance
            
            result = load_config('.env.test')
            
            mock_config_class.assert_called_once_with('.env.test')
            assert result == mock_instance


class TestLogger:
    """Test cases for logging utilities."""
    
    def test_setup_logger_basic(self, temp_dir):
        """Test basic logger setup."""
        log_file = Path(temp_dir) / 'test.log'
        
        logger = setup_logger(
            name='test_logger',
            log_file=str(log_file),
            log_level='INFO',
            console_output=True,
            file_output=True
        )
        
        assert logger.name == 'test_logger'
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 2  # Console and file handlers
        
        # Test logging
        logger.info("Test message")
        
        # Check file was created and contains log
        assert log_file.exists()
        with open(log_file, 'r') as f:
            log_content = f.read()
        assert "Test message" in log_content
    
    def test_setup_logger_console_only(self):
        """Test logger setup with console output only."""
        logger = setup_logger(
            name='console_logger',
            log_file=None,
            console_output=True,
            file_output=False
        )
        
        assert len(logger.handlers) == 1  # Only console handler
        assert logger.handlers[0].__class__.__name__ == 'StreamHandler'
    
    def test_setup_logger_file_only(self, temp_dir):
        """Test logger setup with file output only."""
        log_file = Path(temp_dir) / 'file_only.log'
        
        logger = setup_logger(
            name='file_logger',
            log_file=str(log_file),
            console_output=False,
            file_output=True
        )
        
        assert len(logger.handlers) == 1  # Only file handler
        assert 'FileHandler' in logger.handlers[0].__class__.__name__
    
    def test_setup_component_logger(self):
        """Test component logger setup."""
        # Without parent logger
        logger1 = setup_component_logger('scraper')
        assert 'scraper' in logger1.name
        
        # With parent logger
        parent_logger = setup_logger('parent')
        logger2 = setup_component_logger('analyzer', parent_logger)
        assert logger2.name == 'parent.analyzer'
    
    def test_logger_context_manager(self):
        """Test logger context manager for temporary level changes."""
        logger = setup_logger('context_test', log_level='INFO')
        original_level = logger.level
        
        # Test context manager
        with LoggerContextManager(logger, 'DEBUG') as ctx_logger:
            assert ctx_logger.level == logging.DEBUG
        
        # Should restore original level
        assert logger.level == original_level
    
    def test_structured_logger(self):
        """Test structured logging functionality."""
        base_logger = setup_logger('structured_test')
        struct_logger = StructuredLogger('test', base_logger)
        
        # Test structured logging methods
        with patch.object(base_logger, 'log') as mock_log:
            struct_logger.info_structured("Test message", user_id=123, action="test")
            
            mock_log.assert_called_once()
            args, kwargs = mock_log.call_args
            
            assert args[0] == logging.INFO  # Log level
            log_message = args[1]
            assert "Test message" in log_message
            assert "user_id=123" in log_message
            assert "action=test" in log_message
    
    def test_structured_logger_methods(self):
        """Test all structured logger methods."""
        base_logger = Mock()
        struct_logger = StructuredLogger('test', base_logger)
        
        # Test different log levels
        struct_logger.info_structured("Info message", key="value")
        struct_logger.error_structured("Error message", error_code=500)
        struct_logger.warning_structured("Warning message", warning_type="validation")
        struct_logger.debug_structured("Debug message", debug_info="details")
        
        assert base_logger.log.call_count == 4
    
    def test_colored_formatter(self, temp_dir):
        """Test colored formatter functionality."""
        from src.utils.logger import ColoredFormatter
        
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        
        # Create a log record
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted_message = formatter.format(record)
        
        # Should contain color codes for INFO level
        assert '\033[32m' in formatted_message  # Green color for INFO
        assert '\033[0m' in formatted_message   # Reset color
        assert 'Test message' in formatted_message
    
    def test_get_component_loggers(self):
        """Test pre-configured component loggers."""
        from src.utils.logger import (
            get_app_logger, get_component_logger,
            get_scraper_logger, get_analyzer_logger, get_generator_logger
        )
        
        app_logger = get_app_logger()
        assert 'social-media-reader' in app_logger.name
        
        component_logger = get_component_logger('test')
        assert 'social-media-reader.test' in component_logger.name
        
        scraper_logger = get_scraper_logger()
        assert 'scrapers' in scraper_logger.name
        
        analyzer_logger = get_analyzer_logger()
        assert 'analyzers' in analyzer_logger.name
        
        generator_logger = get_generator_logger()
        assert 'generators' in generator_logger.name
    
    def test_rotating_file_handler(self, temp_dir):
        """Test that rotating file handler is properly configured."""
        log_file = Path(temp_dir) / 'rotating.log'
        
        logger = setup_logger(
            name='rotating_test',
            log_file=str(log_file),
            file_output=True
        )
        
        # Find the rotating file handler
        rotating_handler = None
        for handler in logger.handlers:
            if 'RotatingFileHandler' in handler.__class__.__name__:
                rotating_handler = handler
                break
        
        assert rotating_handler is not None
        assert rotating_handler.maxBytes == 10*1024*1024  # 10MB
        assert rotating_handler.backupCount == 5
    
    def test_log_execution_time_decorator(self):
        """Test execution time logging decorator."""
        from src.utils.logger import log_execution_time
        
        test_logger = Mock()
        
        @log_execution_time
        def test_function():
            return "test_result"
        
        with patch('src.utils.logger.logging.getLogger') as mock_get_logger:
            mock_get_logger.return_value = test_logger
            
            result = test_function()
            
            assert result == "test_result"
            assert test_logger.info.called
            
            # Check that timing information was logged
            call_args = test_logger.info.call_args[0][0]
            assert "test_function executed in" in call_args
            assert "seconds" in call_args
    
    def test_log_execution_time_with_exception(self):
        """Test execution time decorator with exception."""
        from src.utils.logger import log_execution_time
        
        test_logger = Mock()
        
        @log_execution_time
        def failing_function():
            raise ValueError("Test error")
        
        with patch('src.utils.logger.logging.getLogger') as mock_get_logger:
            mock_get_logger.return_value = test_logger
            
            with pytest.raises(ValueError):
                failing_function()
            
            assert test_logger.error.called
            call_args = test_logger.error.call_args[0][0]
            assert "failing_function failed after" in call_args
            assert "Test error" in call_args


class TestUtilsIntegration:
    """Integration tests for utilities."""
    
    def test_config_logger_integration(self, temp_dir):
        """Test integration between config and logger."""
        # Create config with custom settings
        env_content = f"""
LOG_LEVEL=DEBUG
LOG_FILE={temp_dir}/integration.log
DATA_DIR={temp_dir}
OUTPUT_DIR={temp_dir}
        """
        
        env_file = Path(temp_dir) / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content.strip())
        
        # Load config
        config = Config(str(env_file))
        assert config.LOG_LEVEL == 'DEBUG'
        assert str(temp_dir) in config.LOG_FILE
        
        # Setup logger using config
        logger = setup_logger(
            name='integration_test',
            log_file=config.LOG_FILE,
            log_level=config.LOG_LEVEL
        )
        
        assert logger.level == logging.DEBUG
        
        # Test logging
        logger.debug("Debug message")
        logger.info("Info message")
        
        # Verify log file
        log_file = Path(config.LOG_FILE)
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert "Debug message" in log_content
        assert "Info message" in log_content
    
    def test_environment_variable_precedence(self, temp_dir):
        """Test that environment variables take precedence over file."""
        # Create env file
        env_file = Path(temp_dir) / '.env'
        with open(env_file, 'w') as f:
            f.write('LOG_LEVEL=INFO\nUSE_MOCK_DATA=false')
        
        # Set environment variable that should override
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG', 'USE_MOCK_DATA': 'true'}):
            config = Config(str(env_file))
            
            # Environment variables should take precedence
            assert config.LOG_LEVEL == 'DEBUG'
            assert config.USE_MOCK_DATA == True
    
    def test_error_resilience(self):
        """Test that utilities are resilient to errors."""
        # Test config with all invalid values
        with patch.dict(os.environ, {
            'MAX_LINKEDIN_POSTS': 'invalid',
            'MAX_REDDIT_POSTS': 'not_a_number',
            'CHROME_TIMEOUT': 'bad_value'
        }):
            config = Config()
            
            # Should fall back to defaults
            assert config.MAX_LINKEDIN_POSTS == 50
            assert config.MAX_REDDIT_POSTS == 100
            assert config.CHROME_TIMEOUT == 30
        
        # Test logger with invalid log file path
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Cannot create directory")
            
            # Should still create logger without crashing
            logger = setup_logger(
                name='error_test',
                log_file='/invalid/path/test.log',
                file_output=True
            )
            
            assert logger is not None
            assert logger.name == 'error_test'