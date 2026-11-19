"""Init param/default introspection for constructors with keyword-only args."""

import pytest


class KwOnlyDefault:
    def __init__(self, a: int, *, b: int = 2) -> None:
        pass


class KwOnlyRequiredBetween:
    def __init__(self, a: int, x: int = 1, *, k: str, b: int = 2) -> None:
        pass


class NoDefaults:
    def __init__(self, a: int, b: str) -> None:
        pass


@pytest.fixture
def util(qapp):
    import aas_editor.settings  # noqa: F401  util and settings import each other
    from aas_editor.utils import util

    return util


def test_kwOnlyDefault(util) -> None:
    params, defaults = util.getParamsAndTypehints4init(KwOnlyDefault)
    assert params == {"a": int, "b": int}
    assert defaults == {"b": 2}
    assert util.getReqParams4init(KwOnlyDefault) == {"a": int}


def test_kwOnlyRequiredBetween(util) -> None:
    params, defaults = util.getParamsAndTypehints4init(KwOnlyRequiredBetween)
    assert params == {"a": int, "x": int, "k": str, "b": int}
    assert defaults == {"x": 1, "b": 2}
    assert util.getReqParams4init(KwOnlyRequiredBetween) == {"a": int, "k": str}


def test_noDefaults(util) -> None:
    params, defaults = util.getParamsAndTypehints4init(NoDefaults)
    assert params == {"a": int, "b": str}
    assert defaults == {}
    assert util.getReqParams4init(NoDefaults) == {"a": int, "b": str}


def test_kwargObjectDefaultsKwOnlyRequiredBetween(util) -> None:
    from aas_editor.kwargPackage import KwargObject

    assert KwargObject(KwOnlyRequiredBetween, (), {}).kwargs == {"x": 1, "b": 2}
