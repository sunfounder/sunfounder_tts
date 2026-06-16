import logging
from ._logger import Logger


class _Base:
    """Base class for TTS engines.

    Provides a ``self.log`` :class:`Logger` instance for all TTS subclasses.

    Args:
        log: A pre-configured :class:`logging.Logger`. If ``None`` (default),
             a new :class:`Logger` is created with *log_level*.
        log_level: Log level for the auto-created logger, default
                   :data:`logging.INFO`.
    """

    def __init__(self, *args, log: logging.Logger = None,
                 log_level: [int, str] = logging.INFO, **kwargs):
        if log is None:
            log = Logger(__name__)
        self.log = log
        self.log.setLevel(log_level)
