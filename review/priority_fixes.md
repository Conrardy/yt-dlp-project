# Corrections Prioritaires - Code YouTube Audio Downloader

Ce document liste les corrections prioritaires avec des exemples de code prêts à l'emploi.

---

## 🔴 Priorité 1 - Sécurité (CRITIQUE)

### 1. Restreindre CORS

**Fichier**: `src/api/app.py`

**Avant**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Après**:

```python
import os

# Récupérer les origines depuis les variables d'environnement
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

### 2. Corriger Path Traversal

**Fichier**: `src/api/routes.py`

**Avant**:

```python
@router.get("/downloads/{filename}")
async def download_file(filename: str):
    file_path = config.paths.downloads_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )
```

**Après**:

```python
@router.get("/downloads/{filename}")
async def download_file(filename: str):
    # Normaliser et valider le chemin
    file_path = (config.paths.downloads_dir / filename).resolve()
    downloads_dir_resolved = config.paths.downloads_dir.resolve()
    
    # Vérifier que le fichier est bien dans le dossier downloads
    if not str(file_path).startswith(str(downloads_dir_resolved)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Vérifier que le fichier existe
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Vérifier que c'est un fichier (pas un dossier)
    if not file_path.is_file():
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,  # Utiliser le nom réel du fichier
        media_type='application/octet-stream'
    )
```

---

### 3. Ajouter Rate Limiting

**Fichier**: `requirements.txt`

Ajouter:

```
slowapi>=0.1.9
```

**Fichier**: `src/api/app.py`

**Ajouter**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Fichier**: `src/api/routes.py`

**Modifier les routes**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/download")
@limiter.limit("5/minute")  # 5 téléchargements par minute
async def start_download(...):
    # ...

@router.get("/info")
@limiter.limit("30/minute")  # 30 requêtes par minute
async def get_video_info(...):
    # ...
```

---

## 🟠 Priorité 2 - Robustesse (IMPORTANT)

### 1. Nettoyage automatique des tâches

**Fichier**: `src/api/routes.py`

**Ajouter en haut du fichier**:

```python
import time
from datetime import datetime, timedelta

# TTL pour les tâches (1 heure)
TASK_TTL_SECONDS = 3600

def cleanup_old_tasks():
    """Nettoyer les tâches anciennes."""
    current_time = time.time()
    expired_tasks = []
    
    for task_id, task in tasks.items():
        # Nettoyer les tâches terminées ou en erreur après TTL
        if task.get('status') in ['finished', 'error']:
            created_at = task.get('created_at', 0)
            if current_time - created_at > TASK_TTL_SECONDS:
                expired_tasks.append(task_id)
    
    for task_id in expired_tasks:
        del tasks[task_id]
        logger.debug(f"Cleaned up expired task: {task_id}")
    
    return len(expired_tasks)
```

**Modifier `start_download`**:

```python
@router.post("/download", response_model=DownloadResponse)
async def start_download(...):
    # Nettoyer les anciennes tâches avant de créer une nouvelle
    cleanup_old_tasks()
    
    # ... reste du code ...
    
    # Ajouter timestamp lors de la création
    tasks[task_id] = {
        'task_id': task_id,
        'url': request.url,
        'status': 'pending',
        'percentage': 0,
        'message': 'Task created',
        'created_at': time.time()  # Ajouter timestamp
    }
```

**Ajouter une tâche périodique de nettoyage**:

```python
import asyncio

async def periodic_cleanup():
    """Nettoyer les tâches périodiquement."""
    while True:
        await asyncio.sleep(300)  # Toutes les 5 minutes
        cleaned = cleanup_old_tasks()
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired tasks")

# Dans app.py, ajouter au startup:
@app.on_event("startup")
async def startup_event():
    # ... code existant ...
    
    # Démarrer le nettoyage périodique
    asyncio.create_task(periodic_cleanup())
```

---

### 2. Améliorer la gestion d'erreurs

**Fichier**: `src/api/routes.py`

**Modifier `download_task`**:

```python
async def download_task(task_id: str, url: str):
    """Background task for downloading audio."""
    try:
        tasks[task_id]['status'] = 'downloading'
        tasks[task_id]['message'] = 'Starting download...'
        
        progress_callback = progress_callback_wrapper(task_id)
        task_downloader = AudioDownloader(config, progress_callback)
        
        # Download audio
        result = task_downloader.download_audio(url)
        
        if result['success']:
            # ... code existant pour succès ...
        else:
            tasks[task_id].update({
                'status': 'error',
                'message': result.get('error', 'Download failed'),
                'error': result.get('error')
            })
            
    except DownloadError as e:
        logger.error(f"Download error for task {task_id}: {e}")
        tasks[task_id].update({
            'status': 'error',
            'message': f'Download failed: {str(e)}',
            'error': str(e)
        })
    except MetadataError as e:
        logger.warning(f"Metadata extraction error for task {task_id}: {e}")
        # Continuer sans métadonnées si le téléchargement a réussi
        if tasks[task_id].get('status') == 'finished':
            # Téléchargement réussi mais métadonnées échouées
            pass
    except FileNotFoundError as e:
        logger.error(f"File not found for task {task_id}: {e}")
        tasks[task_id].update({
            'status': 'error',
            'message': 'Downloaded file not found',
            'error': str(e)
        })
    except Exception as e:
        logger.critical(f"Unexpected error for task {task_id}: {e}", exc_info=True)
        tasks[task_id].update({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'error': str(e)
        })
```

**Modifier `get_video_info`**:

```python
@router.get("/info", response_model=VideoInfo)
async def get_video_info(url: str = Query(..., description="YouTube video URL")):
    """Get video information without downloading."""
    if not URLValidator.is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        metadata = metadata_extractor.extract_metadata(url)
        # ... reste du code ...
    except MetadataError as e:
        logger.error(f"Metadata extraction error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error extracting video info: {str(e)}"
        )
    except Exception as e:
        logger.critical(f"Unexpected error extracting video info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred"
        )
```

---

### 3. Ajouter validation d'URL dans Pydantic

**Fichier**: `src/api/models.py`

**Modifier**:

```python
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class DownloadRequest(BaseModel):
    """Request model for download endpoint."""
    url: str
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is a YouTube URL."""
        from ..audio_downloader import URLValidator
        if not URLValidator.is_valid_youtube_url(v):
            raise ValueError('URL must be a valid YouTube URL')
        return v
```

---

## 🟡 Priorité 3 - Améliorations (MINEUR)

### 1. Améliorer les type hints

**Fichier**: `src/api/models.py`

**Modifier**:

```python
from typing import Optional, List  # Ajouter List

class VideoInfo(BaseModel):
    # ...
    tags: Optional[List[str]] = None  # Au lieu de Optional[list]
```

**Fichier**: `src/api/routes.py`

**Modifier**:

```python
from typing import Dict, Any, Optional, Callable

def progress_callback_wrapper(task_id: str) -> Callable[[Dict[str, Any]], None]:
    """Create a progress callback for a specific task."""
    def callback(info: Dict[str, Any]) -> None:
        # ...
    return callback
```

---

### 2. Ajouter validation côté client

**Fichier**: `src/static/js/app.js`

**Ajouter fonction de validation**:

```javascript
// Valider l'URL YouTube avant l'envoi
function isValidYouTubeURL(url) {
    const patterns = [
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
        /^https?:\/\/youtu\.be\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/embed\/[\w-]+/,
    ];
    return patterns.some(pattern => pattern.test(url));
}

// Modifier handleAnalyze
async function handleAnalyze() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Veuillez entrer une URL YouTube');
        return;
    }
    
    // Valider l'URL avant l'envoi
    if (!isValidYouTubeURL(url)) {
        showError('URL YouTube invalide. Format attendu: https://www.youtube.com/watch?v=...');
        return;
    }
    
    // ... reste du code ...
}
```

---

## 📝 Notes d'Implémentation

1. **Tester chaque correction individuellement** avant de passer à la suivante
2. **Vérifier que les tests existants passent toujours** après chaque modification
3. **Ajouter des tests** pour les nouvelles fonctionnalités de sécurité
4. **Documenter les changements** dans le CHANGELOG

---

## ✅ Checklist de Déploiement

Avant de déployer en production, vérifier:

- [ ] CORS restreint aux origines autorisées
- [ ] Path traversal corrigé et testé
- [ ] Rate limiting activé et configuré
- [ ] Nettoyage automatique des tâches implémenté
- [ ] Gestion d'erreurs améliorée
- [ ] Tests unitaires ajoutés pour les corrections de sécurité
- [ ] Variables d'environnement configurées
- [ ] Logs configurés pour la production
- [ ] Documentation mise à jour

---

**Fin du document de corrections prioritaires**
