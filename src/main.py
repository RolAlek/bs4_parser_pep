import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def get_soup(response):
    """Вспомогательная функция для создания 'супа'."""
    return BeautifulSoup(response.text, 'lxml')


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return

    main_div = find_tag(
        soup=get_soup(response),
        tag='section',
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        soup=main_div,
        tag='div',
        attrs={'class': 'toctree-wrapper'}
    )
    section_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(section_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue

        soup = get_soup(response)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_version(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    sidebar = find_tag(
        soup=get_soup(response),
        tag='div',
        attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось.')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return

    div_tag = find_tag(
        soup=get_soup(response),
        tag='div',
        attrs={'role': 'main'}
    )
    table_tag = find_tag(
        soup=div_tag,
        tag='table',
        attrs={'class': 'docutils'}
    )
    pdf_tag = find_tag(
        soup=table_tag,
        tag='a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_link = pdf_tag['href']
    archive_url = urljoin(downloads_url, pdf_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранен: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-version': latest_version,
    'download': download
}


def main():
    # Включение логирования парсера.
    configure_logging()
    logging.info('Парсинг запущен!')

    # Получение режима работы парсера из ввода в консоль.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    # Создаем кэширующуюся сессию.
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    # Запускаем парсер - передаем в него режим работы.
    parse_mode = args.mode
    results = MODE_TO_FUNCTION[parse_mode](session)

    if results is not None:
        control_output(results, args)

    # Логирование завершения работы парсера.
    logging.info('Парсинг завершен!')


if __name__ == '__main__':
    main()
