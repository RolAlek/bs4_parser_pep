from argparse import ArgumentParser
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, DT_FORMAT, LOG_FORMAT


def configure_argument_parser(available_modes: str) -> ArgumentParser:
    """
    Парсер аргументов командной строки.

    Позволяет добавить возможность работы с аргументами командной
     строки, что облегчает взаимодействие с программой через командную строку.

    Args:
    available_modes (str): Список доступных режимов работы парсера.

    С помощью метода add_argument, добавляются аргументы командной строки.

    Пример использования:
    parser = configure_argument_parser(['mode1', 'mode2'])
    args = parser.parse_args()
    """
    parser = ArgumentParser(description='Парсер документации Python')

    # Аргмуенты вызова:
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c', '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o', '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )

    return parser


def configure_logging():
    """Конфигуратор логгера."""
    # Создание дирректории и получение имени лог-файла.
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'

    # Инициальизатор хэндлера с перезаписью логов.
    rotating_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 ** 6,   # Максимальный объем лог-файла.
        backupCount=5,  # Максимальное количество лог-файлов.
    )

    # Инициализатор конфигурации логгера
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
