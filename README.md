# Test SC

## Sujet
### Description
Le principe du test est de faire un sous-ensemble d'une plateforme de réservation de ressources, ce qui fait partie de notre quotidien.

Une ressource est composée de:
* un libellé
* un type de ressource
* une localisation
* une capacité (nombre de personnes)

Une réservation est composée de:
* un titre
* une date de début
* une date de fin

### Règles
Niveau 1:
* ~~Créer, modifier et supprimer des ressources~~
* ~~Tous les utilisateurs peuvent réserver une ressource~~
* ~~Un utilisateur peut voir ses réservations passés, en cours et à venir~~
* ~~Un utilisateur peut annuler ses réservations en cours ou à venir~~
* ~~Un utilisateur peut modifier ses réservations à venir~~

Niveau 2:
* ~~Mise en place de l'authentification sur l'API~~
* ~~Permettre à un administrateur de gérer les ressources~~
* ~~Permettre à un utilisateur de lister les ressources~~
* ~~Permettre à un administrateur d'accéder à toutes les réservations~~
* Filtrage sur la liste des ressources (type et localisation)

Niveau 3:
- Mise en place d'OAuth

## Dev
### Install
Copy `.env.example` file to `.env` file and set your database URL and your secret key for JWT token validation.\
`poetry config virtualenvs.in-project true`\
`poetry install`\
`poetry run alembic upgrade head`

### Run
Run DB with `docker compose up -d`\
Run FastAPI with `cd src && poetry run fastapi dev main.py`

### Tools
Format command manually: `poetry run pre-commit run` or `poetry run pre-commit run --all-files`\
Create migration file: `poetry run alembic revision --autogenerate -m "create XXX table"`\
Apply migrations: `poetry run alembic upgrade head`\
Show migration status: `poetry run alembic history --verbose`\
Run tests: `pytest tests/* --verbose -s`
