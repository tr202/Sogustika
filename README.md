# Sogustika

Sogustika социальная сеть гурманов.

## Возможности
- Публикация и редактирование оригинальных рецептов.
- Подсчет количества продуктов для приготовления.
- Экспорт расчета в pdf

## Работает на Python 3.9 и Django 3.2

## Infra
- Linux (ububtu based)   
- Nginx
- Gunicorn
- Docker
- Docker-compose

# Запуск проекта
- отредактируйте nginx.conf в соответствии с Вашим доменным именем
- Проект требует наличия SSL сертификатов для работы
- Получите и скопируйте SSL сертификаты в папки назначения
- ssl_certificate /etc/nginx/ssl/live/Ваш_домен/fullchain.pem;
- ssl_certificate_key /etc/nginx/ssl/live/Ваш_домен/privkey.pem;
- В домашней директории сервера создайте папку sogustika
- Разместите в ней файл .env следующего содержания (все переменные должны быть заменены на Ваши)
###### POSTGRES_USER=django_user
###### POSTGRES_PASSWORD=django
###### POSTGRES_DB=django
###### DB=postgres
###### DB_HOST=db
###### DB_PORT=5432
###### SECRET_KEY=Your-secret-key
###### ALLOWED_HOSTS=localhost
- Выполните следующие комманды из данной папки
- sudo docker compose -f docker-compose.production.yml pull 
- sudo docker compose -f docker-compose.production.yml up -d
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
- sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_data

## Для разработки дополнительно настройте Github Actions
- Отредактируйте файл main.yml в соответствии с вашим аккаунтом на dockerhub
- Добавьте ключи сервера в секреты репозитория
- Сделайте коммит в ветку deploy
- Теперь развертывание новых версий будет происходить автоматически при коммите в ветку deploy

## Production
Kostya https://github.com/tr202
