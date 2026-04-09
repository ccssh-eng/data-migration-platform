# Choisir une image Python
FROM python:3.12-slim

# Créer dossier de travail
WORKDIR /app

# Copier seulement requirements.txt d’abord
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# S'assurer que Python reconnaît scripts comme package
RUN touch scripts/__init__.py

# Commande par défaut
CMD ["python3", "-m", "scripts.main"]
