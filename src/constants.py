from pathlib import Path


BASE_DIR = Path(__file__).parent

DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

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


PEP_DOC_URL = 'https://peps.python.org/'
MAIN_DOC_URL = 'https://docs.python.org/3/'
# Шаблон поиска версии и статуса python
PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

FILE, PRETTY = 'file', 'pretty'
