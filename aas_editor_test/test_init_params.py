"""Init param/default introspection for constructors with keyword-only args."""


class KwOnlyDefault:
    def __init__(self, a: int, *, b: int = 2) -> None:
        pass


class KwOnlyRequiredBetween:
    def __init__(self, a: int, x: int = 1, *, k: str, b: int = 2) -> None:
        pass


class NoDefaults:
    def __init__(self, a: int, b: str) -> None:
        pass


def test_kwOnlyDefault(qapp) -> None:
    import aas_editor.settings  # noqa: F401  util and settings import each other
    from aas_editor.utils.util import getParamsAndTypehints4init, getReqParams4init

    params, defaults = getParamsAndTypehints4init(KwOnlyDefault)
    assert params == {"a": int, "b": int}
    assert defaults == {"b": 2}
    assert getReqParams4init(KwOnlyDefault) == {"a": int}


def test_kwOnlyRequiredBetween(qapp) -> None:
    import aas_editor.settings  # noqa: F401  util and settings import each other
    from aas_editor.utils.util import getParamsAndTypehints4init, getReqParams4init

    params, defaults = getParamsAndTypehints4init(KwOnlyRequiredBetween)
    assert params == {"a": int, "x": int, "k": str, "b": int}
    assert defaults == {"x": 1, "b": 2}
    assert getReqParams4init(KwOnlyRequiredBetween) == {"a": int, "k": str}


def test_noDefaults(qapp) -> None:
    import aas_editor.settings  # noqa: F401  util and settings import each other
    from aas_editor.utils.util import getParamsAndTypehints4init, getReqParams4init

    params, defaults = getParamsAndTypehints4init(NoDefaults)
    assert params == {"a": int, "b": str}
    assert defaults == {}
    assert getReqParams4init(NoDefaults) == {"a": int, "b": str}
