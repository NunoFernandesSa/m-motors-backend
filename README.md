# M-Motors Backend

Backend Django REST API pour la plateforme de gestion des demandes d'achat et de location de véhicules.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/NunoFernandesSa/m-motors-backend)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)](https://github.com/NunoFernandesSa/m-motors-backend)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 📌 Contexte

Ce projet est une solution complète de gestion de demandes automobiles (achat ou location longue durée).  
Les clients peuvent consulter un catalogue, déposer un dossier avec leurs documents, et suivre l’état de leur demande.  
Les administrateurs et commerciaux peuvent gérer les véhicules, traiter les dossiers et communiquer le motif de validation ou de refus.

Le backend est développé avec Django et Django REST Framework, et expose une API sécurisée consommée par un frontend Next.js.

## 🚀 Technologies

- **Django** 5.2
- **Django REST Framework** 3.15
- **PostgreSQL** (production) / **SQLite** (développement)
- **JWT (Simple JWT)** avec cookies HttpOnly
- **WhiteNoise** pour la gestion des fichiers statiques
- **AWS S3** pour le stockage des fichiers médias en production
- **Coverage** pour les tests et le suivi de la couverture de code
- **UptimeRobot** pour la surveillance proactive des endpoints

---

## 📦 Installation locale

### Prérequis

- Python 3.13+
- PostgreSQL (optionnel en développement)

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-compte/m-motors-backend.git
cd m-motors-backend
```

### 2. Créer un environnement virtuel

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
DEBUG=True
SECRET_KEY=votre-cle-secrete
DATABASE_URL=postgresql://user:password@localhost:5432/m_motors_db
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:3000
```

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'API sera disponible à l'adresse :

```text
http://localhost:8000
```

---

## 🧪 Tests et couverture de code

### Exécuter les tests

```bash
python manage.py test
```

### Générer un rapport de couverture

```bash
coverage run manage.py test
coverage report
```

### Générer un rapport HTML détaillé

```bash
coverage html
```

Ouvrez ensuite :

```text
htmlcov/index.html
```

---

## 🌍 Endpoints API principaux

| Méthode | Endpoint                       | Description                            |
| ------- | ------------------------------ | -------------------------------------- |
| POST    | `/api/auth/register/`          | Inscription utilisateur                |
| POST    | `/api/auth/login/`             | Connexion (JWT + cookies)              |
| GET     | `/api/auth/me/`                | Profil de l'utilisateur connecté       |
| POST    | `/api/auth/logout/`            | Déconnexion                            |
| GET     | `/api/vehicles/`               | Liste des véhicules                    |
| GET     | `/api/vehicles/{id}/`          | Détail d'un véhicule                   |
| POST    | `/api/vehicles/`               | Ajouter un véhicule (admin/commercial) |
| GET     | `/api/folders/`                | Liste des dossiers selon le rôle       |
| POST    | `/api/folders/`                | Créer un dossier                       |
| GET     | `/api/folders/{id}/`           | Détail d'un dossier                    |
| PATCH   | `/api/folders/{id}/validate/`  | Valider ou refuser un dossier          |
| POST    | `/api/folders/{id}/documents/` | Ajouter un document                    |

### Documentation Swagger

Accessible à l'adresse :

```text
http://localhost:8000/api/docs/
```

---

## 🚢 Déploiement sur Render

### 1. Préparer le dépôt GitHub

Poussez votre projet sur GitHub (public ou privé).

Assurez-vous que le script de build est exécutable :

```bash
chmod +x build.sh
```

### 2. Créer une base PostgreSQL

Depuis le tableau de bord Render :

```text
New → PostgreSQL
```

Choisissez un plan adapté puis récupérez la valeur de :

```text
Internal Database URL
```

### 3. Créer un Web Service

Depuis Render :

```text
New → Web Service
```

Connectez votre dépôt GitHub puis configurez :

#### Build Command

```bash
./build.sh
```

#### Start Command

```bash
gunicorn core.wsgi:application
```

### 4. Variables d'environnement

| Variable          | Valeur                                     |
| ----------------- | ------------------------------------------ |
| DATABASE_URL      | URL PostgreSQL Render                      |
| DJANGO_SECRET_KEY | Clé secrète Django                         |
| DEBUG             | False                                      |
| ALLOWED_HOSTS     | localhost,127.0.0.1,votre-app.onrender.com |
| PYTHON_VERSION    | 3.13.5                                     |

### 5. Configuration AWS S3 (optionnel)

Pour stocker les fichiers médias sur S3 :

| Variable                | Valeur                                   |
| ----------------------- | ---------------------------------------- |
| AWS_ACCESS_KEY_ID       | Votre clé AWS                            |
| AWS_SECRET_ACCESS_KEY   | Votre clé secrète AWS                    |
| AWS_STORAGE_BUCKET_NAME | m-motors-media                           |
| AWS_S3_REGION_NAME      | eu-west-3                                |
| DEFAULT_FILE_STORAGE    | storages.backends.s3boto3.S3Boto3Storage |

### 6. Déployer l'application

Chaque push sur la branche principale déclenchera automatiquement :

- La phase de build
- Les migrations éventuelles
- Le déploiement de l'application

---

## 📁 Structure du projet

```text
m-motors-backend/
├── core/                # Configuration Django
├── users/               # Authentification et profils utilisateurs
├── vehicles/            # Gestion des véhicules
├── folders/             # Dossiers clients et documents
├── media/               # Fichiers uploadés (local)
├── staticfiles/         # Fichiers statiques collectés
├── requirements.txt
├── build.sh
├── .coveragerc
└── manage.py
```

---

## 👤 Auteur

**Nuno Fernandes**

- Email : [n.fernandes.contact@gmail.com](mailto:votre.email@example.com)
- GitHub : https://github.com/NunoFernandesSa

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.
