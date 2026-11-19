import os
import subprocess
import sys


def testImportWithoutQApplication() -> None:
    """Modules must import before a QApplication exists (pytest collection)."""
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, "-c", "import aas_editor.dialogs, aas_editor.editorApp"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
