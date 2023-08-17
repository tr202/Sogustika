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
- Скопируйте папку infra на сервер в домашнюю директорию
- Перейдите в эту папку и выполните следующие команды 
- sudo docker compose -f docker-compose.production.yml up -d
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
- sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static
- sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_data
- отредактируйте nginx.conf в соответствии с Вашим доменным именем
- Проект требует наличия SSL сертификатов для работы
- Получите и скопируйте SSL сертификаты в папки назначения
ssl_certificate /etc/nginx/ssl/live/Ваш_домен/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/live/Ваш_домен/privkey.pem;
   

## CI/CD
- Github Actions

## Production
Kostya https://github.com/tr202
