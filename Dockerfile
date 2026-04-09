FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# S'assurer que Python reconnaît scripts comme package
RUN touch scripts/__init__.py


CMD ["python3", "-m", "scripts.main"]
