import re

_STRIP_CHARS = re.compile(r"""[\s"'“”‘’「」『』]""")


def normalize_text(value: str) -> str:
    return _STRIP_CHARS.sub("", value)


def quote_in_source(quote: str, source: str) -> bool:
    needle = normalize_text(quote)
    haystack = normalize_text(source)
    return bool(needle) and needle in haystack


def missing_quote_ids(questions: list, source: str) -> list[str]:
    missing: list[str] = []
    for item in questions:
        if not quote_in_source(item.sourceQuote.text, source):
            missing.append(item.id)
    return missing
