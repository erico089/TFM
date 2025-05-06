import logging
import sys
import contextlib

logger = logging.getLogger("agent_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("agent_output.log", mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class LoggerWriter:
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level
        self._buffer = ""

    def write(self, message):
        if message != '\n':
            self._buffer += message
            if self._buffer.endswith('\n'):
                self.logger.log(self.level, self._buffer.rstrip())
                self._buffer = ""

    def flush(self):
        if self._buffer:
            self.logger.log(self.level, self._buffer.rstrip())
            self._buffer = ""

@contextlib.contextmanager
def redirect_stdout_to_logger():
    original_stdout = sys.stdout
    sys.stdout = LoggerWriter(logger)
    try:
        yield
    finally:
        sys.stdout = original_stdout
