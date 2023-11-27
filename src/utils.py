import logging

from bs4 import BeautifulSoup
from requests import RequestException, Response
from requests_cache import CachedResponse

from exceptions import ParserFindTagException, ResponseIsNone


def get_response(session: CachedResponse, url: str) -> Response:
    """
    Вспомогательная функция для получения HTML-кода страницы для парсинга.
    """
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response

    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def get_soup(response: Response) -> BeautifulSoup:
    if response is None:
        raise ResponseIsNone('Ответ не может быть None-type!')
    return BeautifulSoup(response.text, 'lxml')


def find_tag(soup: BeautifulSoup, tag: str, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))

    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
