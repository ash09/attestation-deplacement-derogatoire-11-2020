# AttesationNumeriqueCOVID-19
Générateur d'attestation numérique dérogatoire pour le confinement dû au Covid-19.
Version du 28 novembre 2020.

## Installation
```bash
# Création de l'environment python
python3 -m venv venv

# Installation des dépendances
pip install -r requirements 
```

## Utilisation
Complétez vos informations dans le fichier `profiles.json`.
Exécutez :
```bash
python web-server.py
```

Les attestations sont ensuites disponibles dans le dossier `attestations`.