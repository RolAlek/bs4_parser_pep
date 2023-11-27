class ParserFindTagException(Exception):
    """Поднимается когда парсер не может найти заданный тег."""
    pass


class ResponseIsNone(Exception):
    """Поднимается когда 'requests_cache' возвращает None-type."""
    pass
