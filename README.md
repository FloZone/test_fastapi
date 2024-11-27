# Test SC

## Sujet
### Description
Le principe du test est de faire un sous-ensemble d'une plateforme de réservation de ressources, ce qui fait partie de notre quotidien. Une ressource est composée d'un libellé, d'un type de ressource, d'une localisation et d'une capacité (nombre de personnes). Une réservation est composée d'un titre, d'une date de début et d'une date de fin.

### Règles
Niveau 1:
* Créer, modifier et supprimer des ressources
* Tous les utilisateurs peuvent réserver une ressource
* Un utilisateur peut voir ses réservations passés, en cours et à venir
* Un utilisateur peut annuler ses réservations en cours ou à venir
* Un utilisateur peut modifier ses réservations à venir

Niveau 2:
* Mise en place de l'authentification sur l'API
* Permettre à un administrateur de gérer les ressources
* Permettre à un utilisateur de lister les ressources
* Permettre à un administrateur d'accéder à toutes les réservations
* Filtrage sur la liste des ressources (type et localisation)

Niveau 3:
- Mise en place d'OAuth

## Dev
### Install
`poetry install`\
`poetry run pre-commit install`

### Run
Run DB with `docker compose up -d`\
Run FastAPI with `poetry run fastapi dev src/main.py`

### Tools
Format command manually: `poetry run pre-commit run` or `poetry run pre-commit run --all-files`
