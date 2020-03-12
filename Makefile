SHELL := /bin/bash

test:
	( \
	source ~/.virtualenvs/event_tracker/bin/activate; \
	export FLASK_ENV=dev; \
	pytest; \
	)
run:
	(\
	source ~/.virtualenvs/event_tracker/bin/activate; \
	export FLASK_ENV=dev; \
	python app.py; \
	)
freeze:
	( \
	source ~/.virtualenvs/event_tracker/bin/activate; \
	pip freeze > requierements.txt \
	)
