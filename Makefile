.PHONY: install test lint clean docker-build docker-run streamlit help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala o pacote em modo desenvolvimento"
	@echo "  make test          - Executa os testes com pytest"
	@echo "  make lint          - Executa flake8 nos scripts"
	@echo "  make clean         - Remove arquivos temporários e de build"
	@echo "  make docker-build  - Build da imagem Docker"
	@echo "  make docker-run    - Executa o container Docker"
	@echo "  make streamlit     - Inicia a interface web Streamlit"

install:
	pip install -e ".[dev,excel]"

test:
	pytest tests/ -v

lint:
	flake8 analise_processual_judicial/ scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 analise_processual_judicial/ scripts/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t analise-processual-judicial .

docker-run:
	docker run -v $$(pwd):/data analise-processual-judicial

streamlit:
	streamlit run app.py
