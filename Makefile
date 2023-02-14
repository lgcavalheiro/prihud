APP_DIR=/app
DB=db.sqlite3
PROJECT=prihud_app
PORT=8000

present:
	@echo "                _ __              __"
	@echo "    ____  _____(_) /_  __  ______/ /"
	@echo "   / __ \/ ___/ / __ \/ / / / __  /"
	@echo "  / /_/ / /  / / / / / /_/ / /_/ /"
	@echo " / .___/_/  /_/_/ /_/\__,_/\__,_/"
	@echo "/_/"

dev-run: present
	python manage.py runserver

dev-serve: present
	gunicorn -c gunicorn/dev.py

dev-docker-build: present
	docker build --no-cache --force-rm . -t ${PROJECT}_dev --build-arg DJANGO_ENV=dev --build-arg TZ=America/Sao_Paulo --target dockerized

dev-docker-run: dev-check-image
	docker run --rm --detach -v ${PWD}/${DB}:${APP_DIR}/${DB}:delegated -p 127.0.0.1:${PORT}:${PORT} --name ${PROJECT} ${PROJECT}_dev:latest

dev-check-image:
	if [ $(shell docker images -q ${PROJECT}_dev | wc -l) = 0 ]; then make dev-docker-build; fi

prod-docker-build: present
	docker build --no-cache --force-rm . -t ${PROJECT}_prod --build-arg DJANGO_ENV=prod --build-arg TZ=America/Sao_Paulo --target dockerized

prod-docker-run: prod-check-image
	docker run --rm --detach -v ${PWD}/${DB}:${APP_DIR}/${DB}:delegated -p 127.0.0.1:${PORT}:${PORT} --name ${PROJECT} ${PROJECT}_prod:latest

prod-check-image:
	if [ $(shell docker images -q ${PROJECT}_prod | wc -l) = 0 ]; then make prod-docker-build; fi

docker-stop:
	docker stop ${PROJECT}

dbu-dev: present
	docker-compose down && docker-compose build --build-arg DBU_ENV=dev --build-arg TZ=America/Sao_Paulo && docker-compose up -d

dbu-prod: present
	docker-compose down && docker-compose build --build-arg DBU_ENV=prod --build-arg TZ=America/Sao_Paulo && docker-compose up -d

test:
	export TESTING=True && coverage run --source="." manage.py test ${ARGS} && coverage html
