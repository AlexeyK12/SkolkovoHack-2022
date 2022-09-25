# Skolkovo Hack 2022. Команда DA44
# Трек от Ростелеком. Интеллектуальный анализ работы хранилища данных на основании обработки логов.

## Описание проектов:
| Номер проекта | Название и ссылка | О чем проект                                                     |
|---------------|-------------------|------------------------------------------------------------------|
|1              |[Интеллектуальный анализ работы хранилища данных на основании обработки логов](https://github.com/AlexeyK12/SkolkovoHack-2022/blob/main/skolkovo_hack.ipynb), [Презентация](https://github.com/AlexeyK12/SkolkovoHack-2022/blob/main/Ростелеком%20-%20DA44.pdf), [Приложение](https://github.com/AlexeyK12/SkolkovoHack-2022/blob/main/app.py)|Имеются таблицы, которые редко используются или совсем не используются разработчиками, при этом они наполняются данными. Выявить такие таблицы и проранжировать их по степени "бесполезности"|

### Решение нашей команды:
- проведен исследовательский анализ проблемы в jupiter notebook;
- разработана метрика "бесполезности": отношение числа записей в таблицу к числу обращений от разработчиков;
- реализовано веб-приложение Dash, в котором выведены:
  - топ-10 таблиц по нашей метрике;
  - топ-10 пользователей по кол-ву запросов в разрезе типа: etl и dev;
  - топ-10 пользователей по кол-ву операций в запросе в разрезе типа: etl и dev.
  
  ### Как использовать
  Необходимое ПО:
  - Python 3.9+
  - библиотеки Python:
    - dash
    - regex
    - plotly
    - pandas
    
   Путь к csv-файлу с логами необходимо указать в файле congif.py.   
   Для запуска веб-приложения необходимо открыть терминал и выполнить команду:
   - для Windows и Mac: python app.py
   - для Linux: python3 app.py
   - для запуска на виртуально машине: необходимо добавить host в конце app.py - app.run_server(debug=True, host='0.0.0.0')
