present:
	@echo "                _ __              __"
	@echo "    ____  _____(_) /_  __  ______/ /"
	@echo "   / __ \/ ___/ / __ \/ / / / __  /"
	@echo "  / /_/ / /  / / / / / /_/ / /_/ /"
	@echo " / .___/_/  /_/_/ /_/\__,_/\__,_/"
	@echo "/_/"

dev_run: present
	python manage.py runserver

dbu: present
	docker-compose down && docker-compose build && docker-compose up

dbu_bg: present
	docker-compose down && docker-compose build && docker-compose up -d

test:
	coverage run --source="." manage.py test ${ARGS} && coverage html
