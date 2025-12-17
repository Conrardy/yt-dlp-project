---
name: FastAPI YouTube UI
overview: Créer une interface web avec FastAPI backend et HTML/CSS/JS frontend pour télécharger des audios YouTube, afficher les métadonnées, suivre la progression et consulter l'historique.
todos:
  - id: deps
    content: Ajouter les dépendances FastAPI dans requirements.txt
    status: completed
  - id: models
    content: Créer src/api/models.py avec les schémas Pydantic
    status: completed
  - id: database
    content: Créer src/api/database.py pour l'historique SQLite
    status: completed
  - id: routes
    content: Créer src/api/routes.py avec tous les endpoints API
    status: completed
  - id: app
    content: Créer src/api/app.py point d'entrée FastAPI
    status: completed
  - id: html
    content: Créer src/templates/index.html page principale
    status: completed
  - id: css
    content: Créer src/static/css/style.css styles modernes
    status: completed
  - id: js
    content: Créer src/static/js/app.js logique frontend avec SSE
    status: completed
  - id: test
    content: Tester l'application complète
    status: completed
---

# FastAPI YouTube Downloader UI

## Architecture

```mermaid
flowchart TB
    subgraph Frontend["Frontend (HTML/CSS/JS)"]
        UI[Interface Web]
        SSE[Server-Sent Events]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        API[API Endpoints]
        WS[SSE Progress]
        DB[SQLite History]
    end
    
    subgraph Existing["Modules Existants"]
        AD[AudioDownloader]
        ME[MetadataExtractor]
        UV[URLValidator]
    end
    
    UI -->|POST /api/download| API
    UI -->|GET /api/info| API
    API --> AD
    API --> ME
    API --> UV
    WS -->|Progress updates| SSE
    API --> DB
    UI -->|GET /api/history| DB
```

## Structure des fichiers à créer

```
src/
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── routes.py           # API endpoints
│   ├── models.py           # Pydantic schemas
│   └── database.py         # SQLite pour historique
├── static/
│   ├── css/
│   │   └── style.css       # Styles modernes
│   └── js/
│       └── app.js          # Logique frontend
└── templates/
    └── index.html          # Page principale
```

## Endpoints API

- `GET /` - Page HTML principale
- `GET /api/info?url=...` - Récupérer métadonnées sans télécharger
- `POST /api/download` - Lancer téléchargement (retourne task_id)
- `GET /api/progress/{task_id}` - SSE pour progression temps réel
- `GET /api/history` - Liste des téléchargements passés
- `GET /api/downloads/{filename}` - Télécharger le fichier audio

## Backend FastAPI

### Fichier principal ([`src/api/app.py`](src/api/app.py))

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="YouTube Audio Downloader")
app.mount("/static", StaticFiles(directory="src/static"))
templates = Jinja2Templates(directory="src/templates")
```

### Modèles Pydantic ([`src/api/models.py`](src/api/models.py))

```python
class DownloadRequest(BaseModel):
    url: str

class VideoInfo(BaseModel):
    title: str
    uploader: str
    duration: str
    thumbnail: str
```

### Progression avec SSE

Utiliser `sse-starlette` pour envoyer les mises à jour de progression en temps réel au frontend via Server-Sent Events.

## Frontend

### Page HTML avec sections

- Input URL + bouton "Analyser"
- Affichage métadonnées (thumbnail, titre, durée)
- Bouton "Télécharger" + barre de progression
- Tableau historique des téléchargements

### Style CSS moderne

- Design responsive
- Animations de progression
- Thème sombre/clair

## Dépendances à ajouter

```
fastapi>=0.109.0
uvicorn>=0.27.0
jinja2>=3.1.0
sse-starlette>=1.8.0
aiosqlite>=0.19.0
python-multipart>=0.0.6
```

## Points d'intégration avec le code existant

Réutiliser directement :

- `AudioDownloader.download_audio()` depuis [`src/audio_downloader.py`](src/audio_downloader.py)
- `MetadataExtractor.extract_metadata()` depuis [`src/metadata_extractor.py`](src/metadata_extractor.py)
- `URLValidator.is_valid_youtube_url()` depuis [`src/audio_downloader.py`](src/audio_downloader.py)
- `Config` depuis [`src/config.py`](src/config.py)