# Проект Yatube
Проект Yatube является социальной сетью, где любой пользователь может просматривать записи интересующей группы или автора. Авторизованные пользователи могут создавать собственные посты, подписываться на других авторов и оставлять комментарии к записям. Изменять или удалять записи имеет право лишь автор. Посты пользователей могут быть разделены по категориям групп.
# Стек технологии
- Python 3.7
- Django 2.2.19
- pytest 6.2.4
- django-debug-toolbar 2.2

# Запуск в dev-режиме
Клонировать репозиторий и перейти в него в командной строке:
```
    cd hw05_final
```
Cоздать и активировать виртуальное окружение:
```
    python3 -m venv env
```
```
    source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
    python3 -m pip install --upgrade pip
```
```
    pip install -r requirements.txt
```
Выполнить миграции:
```
    python3 manage.py migrate
```
Создайте суперпользователя:
```
    python3 manage.py createsuperuser
```
Запустить проект:
```
    python3 manage.py runserver
```
____
Ваш проект запустился на http://127.0.0.1:8000/
C помощью команды pytest вы можете запустить тесты и проверить работу модулей 
## Ресурсы Yatube
- Ресурс about: информация об авторе проекта.
- Ресурс posts: управление постами, комментариями, группами и возжностью подписки.
- Ресурс users: создание пользователя.
