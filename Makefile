init-repo :
	python3 -m venv .venv
	. .venv/bin/activate; pip install -r requirements.txt --quiet
	mkdir -p data
	python3 src/create_data.py
