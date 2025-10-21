# YouTube Audio Downloader - Tâches à Réaliser

## ✅ Tâches Complétées

- [x] Configuration de l'environnement Python (venv + yt-dlp)
- [x] Création de la structure de projet (src/, downloads/, logs/, metadata/)
- [x] Installation des dépendances système (FFmpeg)
- [x] Définir la classe de configuration avec les paramètres par défaut
- [x] Gérer la qualité audio (320 kbps MP3)
- [x] Configurer les chemins de sortie (downloads/, metadata/, logs/)
- [x] Implémenter la gestion des formats de sortie
- [x] Ajouter la configuration des options YT-DLP
- [x] Créer un système de validation des paramètres

## 📋 Tâches en Cours

### 1. ✅ Module de configuration (`src/config.py`) - TERMINÉ

- [x] Définir la classe de configuration avec les paramètres par défaut
- [x] Gérer la qualité audio (320 kbps MP3)
- [x] Configurer les chemins de sortie (downloads/, metadata/, logs/)
- [x] Implémenter la gestion des formats de sortie
- [x] Ajouter la configuration des options YT-DLP
- [x] Créer un système de validation des paramètres

### 2. 🔄 Développer le téléchargeur audio (`src/audio_downloader.py`) - EN COURS

- [ ] Créer la classe AudioDownloader
- [ ] Implémenter la méthode de téléchargement avec YT-DLP
- [ ] Configurer les options pour la meilleure qualité audio
- [ ] Ajouter le suivi de progression (progress hooks)
- [ ] Implémenter la conversion automatique en MP3 320kbps
- [ ] Gérer les erreurs de téléchargement et les retry
- [ ] Ajouter la validation des URLs YouTube
- [ ] Implémenter le nettoyage des noms de fichiers

### 3. Créer l'extracteur de métadonnées (`src/metadata_extractor.py`)

- [ ] Développer la classe MetadataExtractor
- [ ] Extraire les métadonnées de base (titre, auteur, durée)
- [ ] Récupérer les métadonnées étendues (description, tags, date)
- [ ] Implémenter la sauvegarde en format JSON
- [ ] Ajouter les métadonnées techniques (bitrate, codec, taille)
- [ ] Créer un système de templates pour les métadonnées
- [ ] Gérer l'encodage des caractères spéciaux

### 4. Développer l'interface CLI principale (`src/main.py`)

- [ ] Configurer argparse avec toutes les options
- [ ] Implémenter les commandes de base (download, info, batch)
- [ ] Ajouter les options de qualité et format
- [ ] Créer l'affichage de progression en temps réel
- [ ] Implémenter la gestion des erreurs utilisateur
- [ ] Ajouter le mode verbose/quiet
- [ ] Créer l'aide contextuelle et les exemples d'usage
- [ ] Implémenter le mode batch pour plusieurs URLs

### 5. Système de logging et gestion d'erreurs

- [ ] Configurer le système de logging (logs/)
- [ ] Implémenter différents niveaux de log (DEBUG, INFO, WARNING, ERROR)
- [ ] Créer la rotation des fichiers de log
- [ ] Ajouter la journalisation des téléchargements
- [ ] Implémenter la gestion des exceptions personnalisées
- [ ] Créer un système de rapport d'erreurs détaillé

### 6. Fonctionnalités avancées - before starting this group task wait for user confirmation

- [ ] Implémenter le téléchargement de playlists
- [ ] Ajouter le support des sous-titres
- [ ] Créer un mode de mise à jour automatique de YT-DLP
- [ ] Implémenter la reprise de téléchargements interrompus
- [ ] Ajouter la vérification d'intégrité des fichiers
- [ ] Créer un système de cache pour les métadonnées

### 7. Tests et validation

- [ ] Créer des tests unitaires pour chaque module
- [ ] Implémenter des tests d'intégration
- [ ] Tester avec différents types de vidéos YouTube
- [ ] Valider la qualité audio des téléchargements
- [ ] Tester la gestion des erreurs et cas limites
- [ ] Créer des tests de performance

### 8. Documentation et finalisation

- [ ] Mettre à jour le README.md avec la documentation complète
- [ ] Créer des exemples d'utilisation
- [ ] Documenter l'API des modules
- [ ] Ajouter les instructions de déploiement
- [ ] Créer un guide de contribution
- [ ] Finaliser les commentaires dans le code

## 🎯 Ordre de Priorité Suggéré

1. ✅ **config.py** - Base de configuration pour tous les autres modules (TERMINÉ)
2. 🔄 **audio_downloader.py** - Fonctionnalité core du téléchargement (EN COURS)
3. **metadata_extractor.py** - Extraction des informations
4. **main.py** - Interface utilisateur
5. **Logging et gestion d'erreurs** - Robustesse du système
6. **Tests et validation** - Qualité et fiabilité
7. **Fonctionnalités avancées** - Améliorations
8. **Documentation** - Finalisation du projet

## 📝 Notes Techniques

### Dépendances Python à considérer

- `yt-dlp` (déjà installé)
- `argparse` (standard library)
- `logging` (standard library)
- `json` (standard library)
- `pathlib` (standard library)
- `datetime` (standard library)
- `re` (standard library)

### Configuration YT-DLP recommandée

- Format audio : `bestaudio/best`
- Post-processor : `FFmpegExtractAudioPP`
- Codec préféré : `mp3`
- Qualité : `320K`

### Structure des métadonnées JSON

```json
{
  "title": "string",
  "uploader": "string",
  "duration": "number",
  "upload_date": "string",
  "description": "string",
  "tags": ["array"],
  "view_count": "number",
  "like_count": "number",
  "file_info": {
    "filename": "string",
    "size": "number",
    "bitrate": "number",
    "codec": "string"
  }
}
```
