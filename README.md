# API pour Vote privé en Django REST Framework (DRF)

## Requirements / Pré-requis

- Python 3.10+ et pip
- Django 5.2

  Assurez-vous de les installer sur votre machine avant le démarrage.

1. ## Cloner le repo git via la commande :

   ```
   git clone git@github.com:Edoucompte/Election_vote.git

   ```

    Décompressez le fichier obtenu et ouvrez votre terminal dans le dossier racine
du projet Election_vote.

2. ## Créer un environnment virtuel

   Tapez la commamde suivante pour créer l'environnment virtuel:

   ```
   python -m venv env

   ```

   Activez le avec la commande, sous linux :

   ```
   source env/bin/activate  # Sous Windows : env\Scripts\activate

   ```

3. ## Installation des dependances

    Pour démarrer ce projet vous aurez besoin d'installer les dépendances renseignées dans
   le fichier `requirements.txt` à la racine du projet.

   ```
   python -m pip install -r requirements.txt

   ```

4. ## Migrations et Base de données

    Il faudra ensuite exécuter les migrations et créer la base de données

   ```
   python manage.py migrate

   ```

5. ## Lancement

    Lancez à présent le serveur par la commande :

   ```
   python manage.py runserver

   ```

L'application est disponible sur le navigateur à l'adresse
   `http://127.0.0.1:8000/api/v1/`. La documentation swagger de l'API
   est égalment disponible à l'adresse : `http://127.0.0.1:8000/api/v1/swagger/schema`
