from typing import Any, Callable


def safe_cast(value: Any, to: Callable, on_error: Any = None) -> Any:
    """"Safe casts value to type with provided casting constructor.

    If cast falls for some reason, default on_error value is returned.*

    :param value: Source value to cast*
    :param to: Callable constructor, which can accept typed value*
    :param on_error: Value to return is cast falls: bad constructor, unacceptable source type*
     :return: casted value or fallback*
    """
    try:
        casted: Any = to(value)
    except (ValueError, TypeError):  # noqa
        return on_error

    return casted
