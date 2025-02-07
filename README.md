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

## Dev
### First install
Copy the `.env.example` file to a `.env` file and set your database URL and your secret key for JWT token validation.

```
poetry config virtualenvs.in-project true
poetry install
poetry run alembic upgrade head
```

### Start
```
# Start DB container
docker compose up -d
# Start FastAPI
cd app && poetry run fastapi dev main.py
```

### Utils
```
# Format command manually
poetry run pre-commit run
poetry run pre-commit run --all-files

# Create migration file
poetry run alembic revision --autogenerate -m "create XXX table"
# Apply migrations
poetry run alembic upgrade head
# Show migration status
poetry run alembic history --verbose

# Run tests
poetry run pytest tests/* --verbose -s -x
```
