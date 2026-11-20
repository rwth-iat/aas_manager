import datetime


def test_splash_shows_logos_author_and_copyright(qapp) -> None:
    from aas_editor.splash import newSplash

    splash = newSplash()
    assert not splash.pixmap().isNull()
    text = splash.message()
    assert "Igor Garmaev" in text
    assert "RWTH Aachen" in text
    assert f"2021–{datetime.date.today().year}" in text

