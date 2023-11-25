import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    section_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(
        section_by_python, desc=f'Открываю ссылки для {whats_new_url}'
    ):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
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

    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
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

    soup = BeautifulSoup(response.text, features='lxml')
    div_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(div_tag, 'table', attrs={'class': 'docutils'})
    pdf_tag = find_tag(
        table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_link = pdf_tag['href']
    archive_url = urljoin(downloads_url, pdf_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def peps(session):
    """Парсер PEP-документации."""
    EXPECTED_STATUS = {
        'A': ('Active', 'Accepted'),
        'D': ('Deferred',),
        'F': ('Final',),
        'P': ('Provisional',),
        'R': ('Rejected',),
        'S': ('Superseded',),
        'W': ('Withdrawn',),
        '': ('Draft', 'Active'),
    }

    peps_url = 'https://peps.python.org/'
    response = get_response(session, peps_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    table_tag = find_tag(
        main_tag,
        'table',
        attrs={'class': 'pep-zero-table docutils align-default'}
    )
    tbody_tag = find_tag(table_tag, 'tbody')
    rows_by_pep = tbody_tag.find_all('tr')

    temp = {}

    for row in tqdm(rows_by_pep, desc='Проверка главного списка'):
        # Добываем общий статус для дальнейшей проверки:
        abbr_tag = row.find('abbr')
        type_status = abbr_tag.text
        status_index = type_status[1] if len(type_status) == 2 else ''
        general_status = EXPECTED_STATUS[status_index]

        # Добываем ссылку определенного PEPа:
        a_tag = row.find('a')
        href = a_tag['href']
        pep_link = urljoin(peps_url, href)
        response = get_response(session, pep_link)
        if response is None:
            return

        # Добываем статус непосредственно из PEP:
        soup = BeautifulSoup(response.text, features='lxml')
        status_dt_tag = soup.find(string='Status').parent
        status_of_page = status_dt_tag.find_next_sibling().text

        temp[status_of_page] = temp.get(status_of_page, 0) + 1

        if status_of_page not in general_status:
            info_msg = (
                f'Несовпадающие статусы:'
                f'{pep_link}\n'
                f'Статус в карточке: {status_of_page}\n'
                f'Ожидаемые статусы: {general_status}\n'
            )
            logging.info(info_msg)

    results = [('Статус', 'Количество')]

    for key, value in temp.items():
        results.append((key, value))

    results.append(
        ('Total', sum(temp.values()))
    )
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-version': latest_version,
    'download': download,
    'pep': peps,
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
