"""
log.py: Definition of standard log wrapper.
"""
from logging import Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL


class Log(object):
    """An implementation of internal logging class which is actually just a wrapper of standard python logger. The only
    reason of this implementation is to avoid if-else conditions in case logger is not initialized.

    """
    def __init__(self, logger: Logger = None):
        """A constructor of internal Log class.

        :param logger: Instance of standard python logger.
        """
        self._log = logger

    def debug(self, msg, *args, **kwargs):
        """Print debug message if allowed and log object has valid configuration.

        :param msg: Message to print.
        :param args: Log arguments.
        :param kwargs: Dictionary with arguments
        :return: None
        """
        if self._log is None:
            return
        if not self._log.isEnabledFor(DEBUG):
            return
        self._log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Print info message if allowed and log object has valid configuration.

        :param msg: Message to print.
        :param args: Log arguments.
        :param kwargs: Dictionary with arguments
        :return: None
        """
        if self._log is None:
            return
        if not self._log.isEnabledFor(INFO):
            return
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Print debug message if allowed and log object has valid configuration.

        :param msg: Message to print.
        :param args: Log arguments.
        :param kwargs: Dictionary with arguments
        :return: None
        """
        if self._log is None:
            return
        if not self._log.isEnabledFor(WARNING):
            return
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Print debug message if allowed and log object has valid configuration.

        :param msg: Message to print.
        :param args: Log arguments.
        :param kwargs: Dictionary with arguments
        :return: None
        """
        if self._log is None:
            return
        if not self._log.isEnabledFor(ERROR):
            return
        self._log.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Print debug message if allowed and log object has valid configuration.

        :param msg: Message to print.
        :param args: Log arguments.
        :param kwargs: Dictionary with arguments
        :return: None
        """
        if self._log is None:
            return
        if not self._log.isEnabledFor(CRITICAL):
            return
        self._log.critical(msg, *args, **kwargs)
