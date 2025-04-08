import logging


def create_logger(name, log_level=logging.DEBUG, log_file=None):
    """
    Creates and returns a logger with the specified name, level, and optional file logging.

    Parameters:
        name (str): The name of the logger.
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO, etc.).
        log_file (str): If specified, the log messages will be written to this file.

    Returns:
        logging.Logger: A logger instance configured with handlers and formatters.
    """
    # Create a logger instance
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(log_level)

    # Create a formatter for the log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Optionally, create a file handler to log to a file
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


HELPER_LOGGER = create_logger(
    name="Helper Logger",
    log_level=logging.DEBUG,
    log_file="",
)

# Usage Example
if __name__ == "__main__":
    # Create a logger instance
    my_logger = create_logger(
        "MyLogger",
        log_level=logging.DEBUG,
        log_file="logs.log",
    )

    # Log messages with different severity levels
    my_logger.debug("This is a debug message")
    my_logger.info("This is an info message")
    my_logger.warning("This is a warning message")
    my_logger.error("This is an error message")
    my_logger.critical("This is a critical message")
