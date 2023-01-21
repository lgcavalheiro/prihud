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
	docker build --no-cache --force-rm . -t ${PROJECT}_dev --target dev

dev-docker-run: dev-check-image
	docker run --rm -v ${PWD}/${DB}:${APP_DIR}/${DB}:delegated -p ${PORT}:${PORT} --name ${PROJECT} ${PROJECT}_dev:latest

dev-check-image:
	if [ $(shell docker images -q ${PROJECT}_dev | wc -l) = 0 ]; then make dev-docker-build; fi

prod-docker-build: present
	docker build --no-cache --force-rm . -t ${PROJECT}_prod --target prod

prod-docker-run: dev-check-image
	docker run --rm -v ${PWD}/${DB}:${APP_DIR}/${DB}:delegated -p ${PORT}:${PORT} --name ${PROJECT} ${PROJECT}_prod:latest

prod-check-image:
	if [ $(shell docker images -q ${PROJECT}_prod | wc -l) = 0 ]; then make prod-docker-build; fi

docker-stop:
	docker stop ${PROJECT}

dbu-dev: present
	docker-compose down && docker-compose build --build-arg DBU_ENV=dev && docker-compose up

dbu-prod: present
	docker-compose down && docker-compose build --build-arg DBU_ENV=prod && docker-compose up

test:
	export TESTING=True && coverage run --source="." manage.py test ${ARGS} && coverage html
