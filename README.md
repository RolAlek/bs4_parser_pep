# Парсинг pep

Парсер данных документции PEP. Реализовано кэширование для ускорения работы парсера, кэш хранится в sqlite3.
Работа парсера осуществляется в 4х режимах:

* Запуск парсера информации из статей о нововведениях в Python.
  Собрать ссылки на статьи о нововведениях в Python, информацию об авторах и редакторах статей.

  ```
  (venv) ...$ python main.py whats-new
  ```
  Результат - вывод в терминал:
  ```
  "12.05.2024 15:27:19 - [INFO] - Парсинг запущен!"
  Открываю ссылки для https://docs.python.org/3/whatsnew/: 100%|████████████████████████████████████████████| 21/21 [00:04<00:00,  4.46it/s]
  Ссылка на статью Заголовок Редактор, Автор
  https://docs.python.org/3/whatsnew/3.12.html What’s New In Python 3.12¶  Editor: Adam Turner  
  https://docs.python.org/3/whatsnew/3.11.html What’s New In Python 3.11¶  Editor: Pablo Galindo Salgado  
  https://docs.python.org/3/whatsnew/3.10.html What’s New In Python 3.10¶  Editor: Pablo Galindo Salgado  
  ...
  "12.05.2024 15:27:25 - [INFO] - Парсинг завершен!"
  ```

* Запуск парсера статусов версий Python.
  Собирает информацию о версиях Python — номера, статусы (in development, pre-release, stable и так далее) и ссылки на документацию.

  ```
  (venv) ...$ python main.py latest-versions
  ```
  Результат - вывод в терминал:
  ```
  "12.05.2024 15:38:12 - [INFO] - Парсинг запущен!"
  100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 18/18 [00:00<00:00, 47662.55it/s]
  Ссылка на документацию Версия Статус
  https://docs.python.org/3.14/ 3.14 in development
  https://docs.python.org/3.13/ 3.13 pre-release
  https://docs.python.org/3.12/ 3.12 stable
  ...
  https://docs.python.org/2.6/ 2.6 EOL
  https://www.python.org/doc/versions/ All versions 
  "12.05.2024 15:38:13 - [INFO] - Парсинг завершен!"
  ```

* Запуск парсера, который скачивает архив документации Python.
```
(venv) ...$ python main.py download
```

* Запуск парсера данных обо всех документах PEP, сравнение статуса на странице PEP со статусом в общем списке, подсчет количества PEP в каждом статусе и общее количество PEP. Результат сохраняется в табличном виде в csv-файл.

  ```
  (venv) ...$ python main.py pep
  ```
  
### Дополнительные способы вывода данных можно сделать уставновив следующий флаг:
 -o {pretty,file}, --output {pretty,file}
* pretty - вывод данных в терминал в табличном(prettytable) формате:
```
+--------------------------------------+--------------+----------------+
| Ссылка на документацию               | Версия       | Статус         |
+--------------------------------------+--------------+----------------+
| https://docs.python.org/3.11/        | 3.11         | in development |
| https://docs.python.org/3.10/        | 3.10         | pre-release    |
| https://docs.python.org/3.9/         | 3.9          | stable         |
| https://docs.python.org/3.8/         | 3.8          | security-fixes |
| https://docs.python.org/3.7/         | 3.7          | security-fixes |
| https://docs.python.org/3.6/         | 3.6          | security-fixes |
| https://docs.python.org/3.5/         | 3.5          | EOL            |
| https://docs.python.org/2.7/         | 2.7          | EOL            |
| https://www.python.org/doc/versions/ | All versions |                |
+--------------------------------------+--------------+----------------+
```
