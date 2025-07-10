run:
	uvicorn app.main:app

test:
	pytest

lint:
	black .
	isort .
