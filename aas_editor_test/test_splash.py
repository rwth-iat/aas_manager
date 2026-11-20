import datetime


def test_splash_shows_logos_author_and_copyright(qapp) -> None:
    from aas_editor.splash import newSplash

    splash = newSplash()
    assert not splash.pixmap().isNull()
    text = splash.message()
    assert "Igor Garmaev" in text
    assert "RWTH Aachen" in text
    assert f"2021–{datetime.date.today().year}" in text



def test_splash_stays_at_least_minimum_time(qapp) -> None:
    from aas_editor.splash import SPLASH_MIN_SECONDS, splashRemainingMs

    assert SPLASH_MIN_SECONDS >= 2
    assert splashRemainingMs(shownAt=100.0, now=100.5) == \
        round((SPLASH_MIN_SECONDS - 0.5) * 1000)
    assert splashRemainingMs(shownAt=100.0, now=100.0 + SPLASH_MIN_SECONDS + 1) == 0
