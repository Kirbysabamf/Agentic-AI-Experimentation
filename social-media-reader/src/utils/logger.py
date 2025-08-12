import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'ENDC': '\033[0m'         # End color
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
        
        return super().format(record)


def setup_logger(name: str = 'social-media-reader', 
                log_file: Optional[str] = None,
                log_level: str = 'INFO',
                console_output: bool = True,
                file_output: bool = True) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console output
        file_output: Enable file output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    
    # File handler
    if file_output and log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (max 10MB, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG in file
        logger.addHandler(file_handler)
    
    return logger


def setup_component_logger(component_name: str, 
                          parent_logger: Optional[logging.Logger] = None) -> logging.Logger:
    """
    Set up a logger for a specific component that inherits from parent logger.
    
    Args:
        component_name: Name of the component
        parent_logger: Parent logger (optional)
        
    Returns:
        Component logger
    """
    if parent_logger:
        logger_name = f"{parent_logger.name}.{component_name}"
    else:
        logger_name = f"social-media-reader.{component_name}"
    
    logger = logging.getLogger(logger_name)
    
    # Don't add handlers if parent exists (inherit from parent)
    if not parent_logger:
        # Set up basic handler if no parent
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


class LoggerContextManager:
    """Context manager for temporary logging level changes."""
    
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


def log_execution_time(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('social-media-reader.timing')
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper


def log_method_calls(cls):
    """Class decorator to log all method calls."""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, log_execution_time(attr))
    return cls


class StructuredLogger:
    """Logger with structured logging support."""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(name)
    
    def log_structured(self, level: str, message: str, **kwargs):
        """Log with structured data."""
        structured_data = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # Convert to string for logging
        log_message = f"{message} | {' | '.join(f'{k}={v}' for k, v in kwargs.items())}"
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, log_message)
    
    def info_structured(self, message: str, **kwargs):
        """Log info with structured data."""
        self.log_structured('INFO', message, **kwargs)
    
    def error_structured(self, message: str, **kwargs):
        """Log error with structured data."""
        self.log_structured('ERROR', message, **kwargs)
    
    def warning_structured(self, message: str, **kwargs):
        """Log warning with structured data."""
        self.log_structured('WARNING', message, **kwargs)
    
    def debug_structured(self, message: str, **kwargs):
        """Log debug with structured data."""
        self.log_structured('DEBUG', message, **kwargs)


def get_app_logger() -> logging.Logger:
    """Get the main application logger."""
    return logging.getLogger('social-media-reader')


def get_component_logger(component: str) -> logging.Logger:
    """Get a logger for a specific component."""
    return logging.getLogger(f'social-media-reader.{component}')


# Pre-configured loggers for common components
def get_scraper_logger() -> logging.Logger:
    """Get logger for scrapers."""
    return get_component_logger('scrapers')


def get_analyzer_logger() -> logging.Logger:
    """Get logger for analyzers."""
    return get_component_logger('analyzers')


def get_generator_logger() -> logging.Logger:
    """Get logger for generators."""
    return get_component_logger('generators')


# Initialize default logger
default_logger = setup_logger(
    name='social-media-reader',
    log_file='./data/application.log',
    log_level='INFO'
)