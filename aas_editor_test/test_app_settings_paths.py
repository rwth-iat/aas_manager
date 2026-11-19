import pytest


@pytest.fixture(scope="module")
def app_settings(qapp):
    from aas_editor.settings import app_settings as s
    return s


class TestAppSettingsPaths:
    def test_settings_and_recovery_outside_package(self, app_settings):
        package_dir = app_settings.THEMES_FOLDER.parent
        assert not app_settings.SETTINGS_FILE.is_relative_to(package_dir)
        assert not app_settings.RECOVERY_DIR.is_relative_to(package_dir)

    def test_themes_folder_exists(self, app_settings):
        assert app_settings.THEMES_FOLDER.is_dir()

    def test_icons_folder_exists(self, app_settings):
        assert app_settings.ICONS_FOLDER.is_dir()

    def test_custom_column_lists_file_exists(self, app_settings):
        assert app_settings.CUSTOM_COLUMN_LISTS_FILE.is_file()

    def test_submodel_templates_folder_exists(self, app_settings):
        assert app_settings.SUBMODEL_TEMPLATES_FOLDER.is_dir()

    def test_pyproject_toml_loaded(self, app_settings):
        assert isinstance(app_settings.PYPROJECT_TOML, dict)
        assert "project" in app_settings.PYPROJECT_TOML
