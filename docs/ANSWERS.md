# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

1. Création d'un environnement virtuel:
    - cd data_flow/
    - conda create --name moveaitest python=3.9
    - conda activate moveaitest
    - pip install -r requirements.txt (installer les dépendances)
2. Pour lancer la pipeline de flux de données: (les URLs sensibles sont stockées dans un gestionnaire de secrets eg. Google Secret Manager et injectées lors de l'exécution sous forme de ENV vars). La base de données est une instance gratuite de mysql:
```bash
cd data_flow/
```
``` python
python main.py --batch_size 5 --api_base_url http://127.0.0.1:8000 --pipeline_runtime 00:00 --timezone EST --database_url 'mysql+pymysql://avnadmin:AVNS_gKvSFEto1ZIBhma42zG@mysql-1d845ed5-youness-7db7.f.aivencloud.com:13542/defaultdb'
```

3. Pour lancer les test:
```bash
cd data_flow
```
```python
python -m pytest test
```

## Questions (étapes 4 à 7)

### Étape 4

**Users table**
```sql
users {
    bigint id PrimaryKey
    varchar first_name
    varchar last_name
    varchar email
    varchar gender
    varchar favorite_genres
    timestamp created_at
    timestamp updated_at
}
```

**Tracks table**
```sql
tracks {
    bigint id PrimaryKey
    varchar name
    varchar artist
    varchar songwriters
    time duration
    varchar genres
    varchar album
    timestamp created_at
    timestamp updated_at
}
```

**Listen history table**
```sql
listen_history {
    bigint id PrimaryKey
    bigint user_id ForeignKey
    bigint track_id ForeignKey
    timestamp listened_at
    timestamp created_at
}
```

Pour ce système, je recommande PostgreSQL comme système de base de données pour les raisons suivantes :
- Excellente gestion des charges de lecture/écriture importantes
- ACID compliant, garantissant l'intégrité des données
- Support du partitionnement de tables et de la réplication

### Étape 5

Voici les métriques clés et la stratégie de surveillance :

1. Métriques clés:
   - **Temps de traitement** :
     - Durée totale d'exécution du pipeline
     - Temps par étape (extraction, transformation, chargement vers la base de données)

   - **Volume de données** :
     - Nombre d'enregistrements traités
     - Taille des données par source
     - Taux de croissance des données (selon le log file)

   - **Taux de réussite** :
     - Nombre d'échecs
     - Taux d'erreur par étape
     - Types d'erreurs rencontrées
    
    - **Qualité des Données** : Nombre de champs manquants obligatoires et de champs null

    - **Ressources** :
        - Utilisation CPU
        - Consommation mémoire
        - Espace disque
        - I/O réseau

On peut implémenter un système d'alertes sur Slack + email pour :

- Échec complet du pipeline
- Dépassement des seuils critiques
- Problèmes de qualité des données majeurs

On peut aussi implémenter un tableau de bord pour vérifier l'état actuel du pipeline et visualiser les métriques clés

On peut utiliser ces outils de Monitoring :
   - **Prometheus** : pour la collecte des métriques
   - **Grafana** : pour la visualisation

### Étape 6
Pour automatiser le calcul des recommandations, on utilisera un workflow d'orchestration réactif:


- **Ingestion des données** : Un orchestrateur (comme Apache Airflow) déclenche régulièrement des tâches d'extraction, de transformation et de chargement des données (ETL)

- **Calcul des features utilisateurs** : Des tâches automatisées analysent les données d'historique d'écoute et de métadonnées pour extraire des features pertinentes pour la recommandation (préférences des utilisateurs). Ces features sont stockées dans un feature store (base de données ou système de fichiers) pour être réutilisées facilement par le moteur de recommandation.

- **Calcul des recommandations**: Lorsqu'un utilisateur consulte l'application, une requête est envoyée au moteur de recommandation, qui charge le modèle pré-entraîné et les features de l'utilisateur.

- **Stockage et mise à jour des recommandations**: Les recommandations générées sont stockées dans une base de données ou un cache en mémoire (Redis) pour un accès rapide depuis l'application. Et on met régulièrement à jour les recommandations en fonction des nouvelles données d'écoute collectées, en utilisant un processus automatisé 

### Étape 7

- Étapes automatisées de la pipeline de réentrainement:
    1. Préparation des données : Extraction automatique des nouvelles données et nettoyage et validation des données.Création des features et stockage dans un feature store versionné

    2. Processus d'entraînement : Sélection du meilleur jeu de données d'entraînement, configuration des hyperparamètres, et entraînement du modèle sur infrastructure (cloud). Enfin stockage du modèle avec versioning

    3. Évaluation et validation : Tests sur le jeu de données de test final et comparaison avec le modèle en production

On utilisera également  un orchestrateur (par exemple, Airflow) pour coordonner entre les différentes étapes du processus de réentrainement. La pipeline est redéclenchée automatiquement soit : De façon périodique (quotidienne/hebdomadaire), ou sur détection de dégradation des performances, ou à l'atteinte d'un certain volume de nouvelles données.

