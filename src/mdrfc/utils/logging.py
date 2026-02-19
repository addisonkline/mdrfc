import logging
from sys import exit


logger = logging.getLogger() # root logger


def init_logger(
    log_file: str = "mdrfc.log",
    log_level_file: str = "INFO",
    log_level_console: str = "INFO"
) -> None:
    """
    Initialize the MDRFC logger.
    """
    _ensure_valid_log_level(log_level_file)
    _ensure_valid_log_level(log_level_console)

    format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

    # file handler
    logging.basicConfig(
        filename=log_file,
        format=format,
        level=log_level_file
    )

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_console)
    formatter = logging.Formatter(format)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"initialized logger with log_file = '{log_file}', log_level_file = '{log_level_file}', log_level_console = '{log_level_console}'")


def _ensure_valid_log_level(
    log_level: str
) -> None:
    """
    Exit the process if the given log level is not valid.
    """
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        print(f"unrecognized log_level {log_level}, must be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITIAL'")
        exit(1)