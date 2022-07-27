# Foodgram - Продуктовый помощник

**Foodgram** это сервис для публикации рецептов.
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов в формате pdf, необходимых для приготовления одного или нескольких выбранных блюд.

### Стэк технологий:
- Python 3.10
- Django 3.2
- Django Rest Framework 3.13
- JavaScript
- React
- Postgres 13
- Docker
- Nginx

### Где посмотреть
 URL : http://84.201.152.180/
 
 Логин и пароль для админа
 
  username: admin
  
  email: admin@foodgram.ru
  
  password: f4UodKM36

## Запуск проекта в Docker контейнерах
* Склонировать репозиторий на локальную машину:
```bash
git clone https://github.com/yoninjago/foodgram-project-react.git
cd foodgram-project-react
```
* Cоздайте файл `.env` в директории `/infra/` со следующим содержанием:
```
SECRET_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
* Запустить Docker
```
sudo docker-compose up -d
```

После этого приложение будет доступно по адресу http://localhost/

### Авторы
[Трошин Сергей](https://github.com/yoninjago/) - Python разработчик. Разработал бэкенд и деплой для сервиса Foodgram.  
[Яндекс.Практикум](https://github.com/yandex-praktikum) Фронтенд для сервиса Foodgram.
