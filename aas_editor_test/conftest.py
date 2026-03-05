import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Absolute path to test data — works regardless of where pytest is invoked from
TEST_FILES_DIR = Path(__file__).parent / "aas_files"


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication.

    Must be requested by every test that imports aas_editor, because
    aas_editor.settings.app_settings creates QFont/QSize/QIcon objects at
    module load time, which require an active QApplication context.
    """
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture(scope="session")
def aasx_file() -> Path:
    return TEST_FILES_DIR / "IDTA 02002-1-0_Template_ContactInformation.aasx"


@pytest.fixture(scope="session")
def json_file() -> Path:
    return TEST_FILES_DIR / "IDTA 02002-1-0_Template_ContactInformation.json"
