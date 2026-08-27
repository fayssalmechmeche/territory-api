# Plan d'entraînement technique : Python / FastAPI / PostGIS

Objectif : se préparer pour un entretien de développeur Full Stack sur la
plateforme Map Analytix (API Python, PostgreSQL/PostGIS, OAuth2/OIDC, Docker).

Stratégie : un seul projet fil rouge qui couvre le maximum de compétences de
la fiche de poste, construit par étapes. Plus efficace à présenter en
entretien que plusieurs petits projets séparés.

## Projet : Mini API géospatiale "Territory API"

Une API qui gère des points d'intérêt géolocalisés (ex : stations, magasins,
équipements publics) avec calcul d'indicateurs territoriaux simples
(recherche par rayon, zone d'influence).

## Correspondance avec la fiche de poste

| Exigence de l'offre                                   | Ce que le projet couvre                  |
| ----------------------------------------------------- | ---------------------------------------- |
| API REST en Python                                    | FastAPI, routes CRUD                     |
| PostgreSQL, données géospatiales, vues, index         | PostGIS, GeoAlchemy2, index GIST         |
| Moteur de calcul géospatial (isochrones, indicateurs) | Recherche par rayon, buffer simplifié    |
| OAuth2 / OpenID Connect                               | Auth JWT, simulation d'un flow OIDC      |
| Interfaces cartographiques riches                     | Petite carte React avec Leaflet          |
| Traitements asynchrones et mise en cache              | Routes async, cache Redis                |
| Tests automatisés                                     | Suite pytest                             |
| Docker / Docker Compose                               | Conteneurisation de tous les services    |
| Versionnement Git                                     | Dépôt structuré avec commits progressifs |

## Stack technique

- Python 3.11+, FastAPI, Pydantic
- SQLAlchemy + Alembic (migrations)
- PostgreSQL + PostGIS + GeoAlchemy2
- Redis (cache)
- JWT (python-jose ou pyjwt)
- pytest + httpx (tests)
- Docker Compose
- React + Leaflet (front minimal, optionnel si le temps manque)

## Plan par étapes

### Étape 1 : Socle CRUD (jour 1)

- Mettre en place FastAPI, structure du projet (routers, models, schemas)
- Modèle `PointOfInterest` (nom, catégorie, coordonnées)
- Endpoints CRUD classiques (GET, POST, PUT, DELETE)
- Connexion PostgreSQL avec SQLAlchemy
- Première migration Alembic

Objectif : retrouver les réflexes API REST côté Python.

### Étape 2 : Couche géospatiale (jours 2-3)

- Ajouter l'extension PostGIS à la base
- Passer la colonne de coordonnées en `Geometry(Point, srid=4326)`
- Endpoint `/points/nearby` : recherche des points dans un rayon donné
  (`ST_DWithin`)
- Endpoint `/zones/buffer` : génère une zone tampon autour d'un point
  (`ST_Buffer`), à titre d'isochrone simplifié
- Index GIST sur la colonne géométrique

Objectif : pouvoir parler concrètement de données géospatiales et
d'indicateurs territoriaux en entretien.

### Étape 3 : Authentification (jour 4)

- Endpoint `/auth/login` qui génère un access token JWT et un refresh token
- Dépendance FastAPI (`Depends`) qui protège les routes sensibles
- Documentation courte du flow choisi et de son équivalent OIDC en
  production (authorization code flow, validation via JWKS)

Objectif : savoir expliquer la mécanique OAuth2/JWT même sans avoir un vrai
IdP en place.

### Étape 4 : Performance (jour 5)

- Passer les routes de lecture en `async def` avec un driver async
  (asyncpg)
- Mettre en cache le résultat de `/points/nearby` avec Redis (TTL court)
- Mesurer le gain avec un petit test de charge basique (optionnel)

### Étape 5 : Tests et Docker (jour 6)

- Suite pytest sur les routes principales (CRUD, auth, recherche
  géospatiale)
- `Dockerfile` pour l'API
- `docker-compose.yml` avec l'API, PostgreSQL/PostGIS et Redis
- README technique du projet (installation, variables d'environnement,
  commandes utiles)

### Étape 6 (bonus, si le temps le permet) : Front cartographique

- Petite page React avec Leaflet
- Affichage des points et de la zone tampon calculée par l'API

## Ce qu'il faut pouvoir raconter en entretien

- Pourquoi FastAPI plutôt que Flask pour ce type de projet (validation
  Pydantic intégrée, support natif de l'async, documentation Swagger
  automatique)
- Le rôle de PostGIS et la différence entre une colonne géométrique et des
  coordonnées classiques
- Le fonctionnement du flow OAuth2 choisi et pourquoi il conviendrait à un
  contexte SSO d'entreprise
- L'intérêt de l'async et du cache pour la performance sur des requêtes
  géospatiales, souvent coûteuses
- La structure Docker Compose et comment elle faciliterait un déploiement
  automatisé

## Notes

- Pas besoin d'aller très loin sur chaque brique : l'objectif est de
  pouvoir en parler avec assurance, pas de livrer un produit fini.
- Prioriser les étapes 1 à 3 si le temps manque : ce sont celles qui
  couvrent le cœur de la fiche de poste (API Python, PostgreSQL géospatial,
  auth).
