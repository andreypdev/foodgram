# Foodgram Project
Foodgram is a culinary assistant with a database of recipes. Foodgram allows you to publish recipes, save your favorite ones, and create a shopping list for selected recipes. You can also subscribe to your favorite authors to see if they have published anything new.

## Tech Stack
[![Python](https://img.shields.io/badge/-Python-464646?style=&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=008080)](https://jwt.io/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

### Workflow
> *Before cloning the repository, make sure to install Docker and Docker Compose*

> **Before running the workflows, add the following action secrets to the cloned GitHub repo**

- ```DOCKER_USERNAME``` - DockerHub username
- ```DOCKER_PASSWORD``` - DockerHub password
- ```HOST``` - server address
- ```USER``` - username on the server
- ```SSH_KEY``` - private SSH key
- ```SSH_PASSPHRASE``` - SSH passphrase
- ```TELEGRAM_TO``` - your Telegram account id. To find your Telegram id, message @userinfobot
- ```TELEGRAM_TOKEN``` - your Telegram bot's token. To get your own token, message @BotFather

---

```build_and_push_backend_to_docker_hub```
* Builds and deploys the backend to Docker Hub

```build_and_push_frontend_to_docker_hub```
* Builds and deploys the frontend to Docker Hub

```deploy```
* Automatically deploys the project to your server

```send_message```
* Telegram bot will send you a message if the deploy was successful

---

Clone this repository and navigate to the backend folder:
```
git clone https://github.com/andreypdev/foodgram
cd backend
```

Create and activate venv and update your pip.


## How to deploy Foodgram on a server
**Connect:**
```
ssh username@server_address
```
**Update:**
```
sudo apt update
sudo apt upgrade -y
```
**Create the nginx folder:**
```
mkdir nginx
```
**Edit the ```default.conf``` file in the ```/nginx``` folder and add the IP of your virtual server.**

**Copy ```docker-compose.yml``` and ```nginx/default.conf``` to your server:**
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
sudo mkdir nginx
scp default.conf <username>@<host>/home/<username>/nginx/default.conf
```
**Install Docker and Docker compose:**

> https://docs.docker.com/compose/install/linux/

**Create a new file named ```.env``` with the following:**
```
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram
DB_NAME=foodgram
DB_PORT=5432
DB_HOST=db
ALLOWED_HOSTS=list of allowed addresses
SECRET_KEY=your own secret Django key
DEBUG=False
```
**You can see an example ```.env``` file here:**

* https://github.com/andreypdev/foodgram/blob/master/docs/.env.example

Copy the ```.env``` file to the server.

### After a successful deploy
Build with Docker compose:
```
sudo docker-compose up -d --build
```
The provided Docker file will:
* collect static elements
* execute the ```makemigrations``` Django command
* execute the ```migrate``` Django command
* load ingredients and tags from the ```data``` folder

After building, create a superuser
```
docker-compose exec backend python manage.py createsuperuser
```

*Foodgram should be up and running on your server. You can manage Foodgram via the new superuser.*