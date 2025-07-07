run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	black .
	isort .
