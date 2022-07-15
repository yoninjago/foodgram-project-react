# Foodgram - Продуктовый помощник

**Foodgram** это сервис для публикации рецептов.
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов в формате pdf, необходимых для приготовления одного или нескольких выбранных блюд.

### Стэк технологий:
- Python 3.10
- Django 3.2
- Django Rest Framework 3.13
- Postgres 13
- Docker
- Nginx

### Установка проекта локально

* Склонировать репозиторий на локальную машину:
```bash
git clone https://github.com/yoninjago/foodgram-project-react.git
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```bash
python3.10 -m venv venv
```

```bash
source venv/bin/activate
```

* Перейти в директорию и установить зависимости из файла requirements.txt:

```bash
cd backend/
pip install -r requirements.txt
```

* Выполнить миграции:

```bash
python manage.py migrate
```

* Загрузить ингредиенты в БД:

```bash
python manage.py load_data ingredients.json
```

* Запустить сервер:
```bash
python manage.py runserver
```

### Запуск проекта в Docker контейнерах на сервере
Будет доступно после прохождения первой части ревью