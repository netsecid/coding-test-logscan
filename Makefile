.PHONY: help venv install test demo clean regen-sample

help:
	@echo "make install  - buat venv + install dependency"
	@echo "make test     - jalankan seluruh test"
	@echo "make demo     - jalankan CLI pada samples/auth_sample.log"
	@echo "make clean    - hapus cache"

install:
	python3 -m venv .venv
	.venv/bin/pip install -q --upgrade pip
	.venv/bin/pip install -q -r requirements.txt

test:
	python3 -m pytest -q

demo:
	python3 -m logscan samples/auth_sample.log
	@echo "--- mode JSON (dipotong 40 baris) ---"
	python3 -m logscan samples/auth_sample.log --json | head -40

clean:
	rm -rf .pytest_cache
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
