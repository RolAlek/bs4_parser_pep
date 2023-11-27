from argparse import Namespace
import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, FILE, PRETTY


def control_output(results: list[tuple], cli_args: Namespace) -> None:
    """Контролер вывода результатов парсинга."""
    output = cli_args.output

    if output == PRETTY:
        pretty_output(results)
    elif output == FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def pretty_output(results: list[tuple]) -> None:
    """Вывод данных в терминал в формате PrettyTable."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def default_output(results: list(tuple)) -> None:
    """Вывод данных в терминал, построчно."""
    for row in results:
        print(*row)


def file_output(results: list[tuple], cli_args: Namespace) -> None:
    """Вывод данных в файл."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)

    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)

    logging.info(f'Файл с результатами сохранен в: {file_path}')
