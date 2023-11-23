import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    """Контролер вывода результатов парсинга."""
    output = cli_args.output

    match output:
        case 'pretty':
            pretty_output(results)
        case 'file':
            file_output(results, cli_args)
        case _:
            default_output(results)


def pretty_output(results):
    """Вывод данных в формате PrettyTable."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def default_output(results):
    """Вывод данных в терминал, построчно."""
    for row in results:
        print(*row)


def file_output(results, cli_args):
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
