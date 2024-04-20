![workflow badge](https://github.com/abramenkova07/foodgram-project-react/actions/workflows/main.yml/badge.svg)

#  Проект Foodgram

## Описание проекта

Проект «Фудграм» — сайт, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект доступен по ссылке: [Foodgram](https://foodgram.run.place/signin) <br>

## Стек использованных технологий

Проект представляет собой сайт, состоящий из **frontend** и **backend** части.
* **Frontend:** React
* **Backend:** СУБД PostgreSQL, Django Rest Framework
* **Деплой:** Docker, GitAction

## Развертывание проекта на удаленной сервере

Чтобы развернуть проект на удаленном сервере, необходимо создать на сервере папку `foodgram-project-react`. <br>
В нее необходимо скопировать файл `docker-compose.production.yml`, а также там же создать и заполнить файл `.env`(см. ниже). <br>
Получите доменное имя и сертификат SSL любым удобным способом. <br>
Также отредактируйте на сервере файл `/etc/nginx/sites-enabled/default`, чтобы подключить проект. <br>
В нашем случае код был следующий:
```bash
server {
    server_name <IP сервера> <доменное имя>;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9090;
    }
```
После нужно склонировать к себе текущий проект и перейти в папку проекта: <br>
```bash
git clone https://github.com/abramenkova07/foodgram-project-react.git
cd foodgram-project-react
```
Необходимо создать виртуальное окружение: <br>
```bash
python -m venv venv
source venv/Scripts/activate
```
В GitHub необходимо создать следующие `Actions secrets and variables`: <br>
* DOCKER_PASSWORD
* DOCKER_USERNAME
* HOST (ID сервера)
* SSH_KEY (private)
* SSH_PASSPHRASE
* TELEGRAM_TO
* TELEGRAM_TOKEN
* USER (имя юзера на сервере)

Далее необходимо запушить проект на GitHub:
```bash
git add .
git commit -m '<Название коммита>'
git push
```
На GitHub во вкладке Actions будет отображаться процесс деплоя, при успешном деплое вам придет сообщение в Telegram. <br>
На сервере теперь созданы контейнеры Docker. <br>
Получите список контейнеров: <br>
```bash
sudo docker container ls -a
```
Зайдите в контейнер `backend`: <br>
```bash
sudo docker exec -it <ID контейнера> bash
```
Последовательно в контейнере выполните следующие команды: <br>
```bash
python manage.py migrate
python manage.py csvtodb
python manage.py collectstatic
python manage.py createsuperuser --noinput --first_name <имя> --last_name <фамилия>
```
## Заполнение файла .env

Файл `.env` должен иметь следующий вид: <br>
```python
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<здесь нужно вставить свое значение>
DEBUG=<true или false>
ALLOWED_HOSTS=<все используемые хосты и доменные имена через пробел>
USE_SQLITE=<false для использования PostgreSQL или true для отладки>
DJANGO_SUPERUSER_PASSWORD=<пароль суперюзера>
DJANGO_SUPERUSER_USERNAME=<имя суперюзера>
DJANGO_SUPERUSER_EMAIL=<имейл суперюзера>
```
#### Автор проекта:
[Арина Абраменкова](https://github.com/abramenkova07)