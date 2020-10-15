setup:
	python3 -m venv ~/.msds498GroupProject

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C test.py
