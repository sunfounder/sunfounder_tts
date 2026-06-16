import logging
from ._logger import Logger


class _Base:
    """Base class for TTS engines.

    Provides a ``self.log`` Logger instance.
    """

    def __init__(self, *args, log: logging.Logger = None,
                 log_level: [int, str] = logging.INFO, **kwargs):
        if log is None:
            log = Logger(__name__)
        self.log = log
        self.log.setLevel(log_level)
