__all__ = ["LoadRunner", "main"]


def __getattr__(name):
    if name in __all__:
        from .cli import LoadRunner, main

        exports = {"LoadRunner": LoadRunner, "main": main}
        return exports[name]
    raise AttributeError(f"module 'asyncload' has no attribute {name!r}")
