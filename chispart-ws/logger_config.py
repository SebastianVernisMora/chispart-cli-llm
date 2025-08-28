import logging
import sys

def setup_logging():
    """
    Sets up structured logging for the application.
    """
    logger = logging.getLogger("chispart-ws")
    logger.setLevel(logging.INFO)

    # Create a handler to write to stdout
    handler = logging.StreamHandler(sys.stdout)

    # Create a formatter that is safe and structured
    # We avoid logging full request data to prevent secrets from leaking.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# Global logger instance
logger = setup_logging()
