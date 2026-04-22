# 🚀 Déploiement sur PythonAnywhere

## 📋 Prérequis
- Compte PythonAnywhere (gratuit)
- Projet Django prêt
- Git installé localement

## 🛠️ Étapes de déploiement

### 1. Préparation locale
```bash
# Créer le fichier .env
cp .env.example .env

# Modifier les valeurs dans .env
nano .env
```

### 2. Push sur GitHub
```bash
git add .
git commit -m "Préparation pour PythonAnywhere"
git push origin main
```

### 3. Configuration PythonAnywhere

#### 3.1 Créer le compte
1. Allez sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Créez un compte gratuit
3. Choisissez le nom d'utilisateur (deviendra votre domaine)

#### 3.2 Cloner le projet
```bash
# Dans le Bash de PythonAnywhere
cd ~/ && git clone https://github.com/votrenom/votrerepo.git school-management
cd school-management
```

#### 3.3 Configurer l'environnement
```bash
# Créer un virtual environment
mkvirtualenv --python=/usr/bin/python3.10 school-env
workon school-env

# Installer les dépendances
pip install -r requirements.txt
```

#### 3.4 Configurer les variables d'environnement
```bashl
# Dans le bash de PythonAnywhere
export DATABASE_URL="postgres://username:password@username.postgres.database.azure.com:5432/defaultdb"
export SECRET_KEY="votre-secret-key"
export ALLOWED_HOSTS="votrenom.pythonanywhere.com,www.votrenom.pythonanywhere.com"
export DEBUG=False
```

#### 3.5 Créer la base de données
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 3.6 Configurer le Web App
1. Allez dans "Web" → "Add a new web app"
2. Choisissez "Manual configuration"
3. Python version: 3.10
4. Path to virtualenv: `/home/votrenom/.virtualenvs/school-env`
5. Path to project: `/home/votrenom/school-management`
6. Code: `/home/votrenom/school-management/school_app/wsgi.py`

#### 3.7 Configurer WSGI
```python
# Dans /var/www/votrenom_pythonanywhere_com_wsgi.py
import os
import sys

path = '/home/votrenom/school-management'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'school_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 3.8 Redémarrer le serveur
1. Allez dans "Web"
2. Cliquez sur "Reload" pour votre web app

## 🔧 Configuration requise

### Variables d'environnement
- `DATABASE_URL`: URL de la base de données PostgreSQL
- `SECRET_KEY`: Clé secrète Django
- `ALLOWED_HOSTS`: Votre domaine PythonAnywhere
- `DEBUG`: False en production

### Domaine
Votre site sera accessible à: `https://votrenom.pythonanywhere.com`

## 🐛 Dépannage

### Erreur 500
- Vérifiez les logs dans "Web" → "Error logs"
- Assurez-vous que `DEBUG=False` en production

### Fichiers statiques
- Exécutez `collectstatic` après chaque modification
- Vérifiez que `STATIC_ROOT` est correct

### Base de données
- Vérifiez la connexion PostgreSQL
- Assurez-vous que les migrations sont appliquées

## 📞 Support

- Documentation PythonAnywhere: [docs.pythonanywhere.com](https://help.pythonanywhere.com/)
- Forum communautaire: [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums/)

## 🎉 Succès !

Votre système de gestion scolaire est maintenant en ligne ! 🚀
