# Projet Data Migration

## Objectif
Migrer les données clients héritées vers une base de données cloud propre.

## Stack utilisée
- Python 
- Pandas
- PostgreSQL
- Azure Data Factory

##  Étapes
1. Nettoyage des données
2. Transformation
3. Charger sur PostgreSQL 
4. Cloud migration
5. Validation

## Résultats
- Supprimer les doublons
- Correction des e-mails invalides
- Dates normalisées

## Exécution
python scripts/clean_data.py
python scripts/load_to_db.py

## Docker
- container PostgreSQL

## CI/CD
- GitHub Actions pour lancer scripts

## Sécurité
- anonymisation emails

