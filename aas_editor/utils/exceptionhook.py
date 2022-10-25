import sys
import logging
from PyQt5 import QtWidgets


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Solution from:
    https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
    - Ignore KeyboardInterrupt so a console python program can exit with Ctrl + C.
    I have no Idea what if block does
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    QtWidgets.QMessageBox.critical(None, "An Exception was raised", 'Caught Exception: {}'.format(exc_value))
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
