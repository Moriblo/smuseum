FROM python:3.9

# Defina a variável de ambiente para o pip
ENV PIP_DEFAULT_TIMEOUT=1000
# Declara ao flask o nome do serviço
ENV FLASK_APP=smuseum.py

RUN python --version
RUN pip --version
RUN pip install --upgrade pip

WORKDIR /tradutor
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -v
COPY . .

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5002"]