import logging
import sys
from pathlib import Path
from threading import Lock
from typing import Optional


class LogLevels:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerSingleton:
    """
    Process-wide singleton logger.
    - File handler always logs DEBUG+
    - Console handler logs at requested level
    - Safe to call multiple times (no duplicate handlers)
    """

    _instance: Optional[logging.Logger] = None
    _lock = Lock()

    def __init__(self, name: str = "mcp_server", log_file: str = "logs/mcp_server.log"):
        self.name = name
        self.log_file = log_file

    def get_logger(self, level: str = LogLevels.INFO) -> logging.Logger:
        with self._lock:
            if self.__class__._instance is None:
                self.__class__._instance = self._create_logger(self.name, self.log_file, level)
            else:
                # If re-called, keep singleton but update levels/paths if needed.
                self._reconfigure_logger(self.__class__._instance, self.name, self.log_file, level)

            return self.__class__._instance

    def _create_logger(self, name: str, log_file: str, level: str) -> logging.Logger:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(self._parse_level(level))

        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._parse_level(level))
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _reconfigure_logger(self, logger: logging.Logger, name: str, log_file: str, level: str) -> None:
        # Keep singleton instance; adjust visible properties when re-initialized.
        new_level = self._parse_level(level)
        logger.setLevel(new_level)
        logger.propagate = False

        # If name changed, update logger name by creating/getting correct logger and moving handlers.
        # (Avoid breaking existing references: best effort; most users keep one name.)
        if logger.name != name:
            target = logging.getLogger(name)
            target.propagate = False
            target.setLevel(new_level)
            for h in list(logger.handlers):
                logger.removeHandler(h)
                target.addHandler(h)
            self.__class__._instance = target
            logger = target

        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Update handlers without duplicating
        file_handler = None
        console_handler = None

        for h in logger.handlers:
            if isinstance(h, logging.FileHandler):
                file_handler = h
            elif isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout:
                console_handler = h

        # File handler: always DEBUG, update path if changed
        if file_handler is None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(file_handler)
        else:
            # If file path differs, replace handler safely
            current_path = Path(getattr(file_handler, "baseFilename", ""))
            if current_path != Path(log_file):
                logger.removeHandler(file_handler)
                try:
                    file_handler.close()
                except Exception:
                    pass
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                )
                logger.addHandler(file_handler)

        # Console handler: respect requested level
        if console_handler is None:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
            )
            logger.addHandler(console_handler)
        console_handler.setLevel(new_level)

    @staticmethod
    def _parse_level(level: str) -> int:
        if not isinstance(level, str):
            return logging.INFO
        return getattr(logging, level.upper(), logging.INFO)
