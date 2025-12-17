# Code Review Command

Effectue une revue de code complète et approfondie du projet YouTube Audio Downloader.

## Objectifs de la review

1. **Qualité du code** : Style, lisibilité, maintenabilité
2. **Architecture** : Structure, séparation des responsabilités, design patterns
3. **Gestion d'erreurs** : Robustesse, gestion des exceptions, messages d''erreur
4. **Tests** : Couverture, qualité des tests, cas limites
5. **Documentation** : Docstrings, README, commentaires
6. **Sécurité** : Validation des entrées, gestion des chemins de fichiers
7. **Performance** : Optimisations possibles, gestion mémoire
8. **Bonnes pratiques Python** : PEP 8, type hints, conventions

## Processus de review

### 1. Analyse globale
- Examiner la structure du projet et l'organisation des fichiers
- Vérifier la cohérence de l''architecture globale
- Identifier les dépendances entre modules

### 2. Review par module

Pour chaque fichier Python dans `src/` :

#### Structure et organisation
- [ ] La classe/module a-t-elle une responsabilité claire ?
- [ ] Les imports sont-ils organisés correctement ?
- [ ] Y a-t-il des dépendances circulaires ?

#### Qualité du code
- [ ] Le code suit-il PEP 8 ?
- [ ] Les noms de variables/fonctions sont-ils explicites ?
- [ ] Y a-t-il du code dupliqué ?
- [ ] Les fonctions sont-elles de taille raisonnable (< 50 lignes) ?

#### Type hints et annotations
- [ ] Les fonctions ont-elles des type hints complets ?
- [ ] Les types de retour sont-ils documentés ?
- [ ] Les types optionnels sont-ils correctement annotés (`Optional[T]`) ?

#### Gestion d'erreurs
- [ ] Les exceptions sont-elles gérées de manière appropriée ?
- [ ] Les messages d''erreur sont-ils informatifs ?
- [ ] Y a-t-il des `try/except` trop larges (`except Exception`) ?
- [ ] Les erreurs sont-elles loggées correctement ?

#### Documentation
- [ ] Chaque fonction/classe a-t-elle une docstring ?
- [ ] Les docstrings suivent-elles le format Google/NumPy ?
- [ ] Les paramètres et valeurs de retour sont-ils documentés ?
- [ ] Y a-t-il des commentaires pour le code complexe ?

#### Tests
- [ ] Les fonctions sont-elles testables ?
- [ ] Y a-t-il des tests unitaires pour les fonctions critiques ?
- [ ] Les cas limites sont-ils testés ?

#### Sécurité
- [ ] Les entrées utilisateur sont-elles validées ?
- [ ] Les chemins de fichiers sont-ils sécurisés (pas de path traversal) ?
- [ ] Y a-t-il des risques d'injection ou d''exécution de code ?

### 3. Points spécifiques à vérifier

#### `src/main.py`
- [ ] La CLI est-elle bien structurée ?
- [ ] Les arguments sont-ils correctement validés ?
- [ ] Les messages utilisateur sont-ils clairs ?
- [ ] La gestion des erreurs CLI est-elle robuste ?

#### `src/config.py`
- [ ] La validation de configuration est-elle complète ?
- [ ] Les valeurs par défaut sont-elles raisonnables ?
- [ ] La sérialisation/désérialisation JSON est-elle sûre ?
- [ ] Les chemins sont-ils correctement gérés (Windows/Linux) ?

#### `src/audio_downloader.py`
- [ ] La gestion des téléchargements est-elle robuste ?
- [ ] Les callbacks de progression sont-ils bien gérés ?
- [ ] Y a-t-il des risques de fuites mémoire ?
- [ ] La gestion des erreurs réseau est-elle appropriée ?

#### `src/metadata_extractor.py`
- [ ] L'extraction de métadonnées est-elle fiable ?
- [ ] Les données sont-elles correctement nettoyées ?
- [ ] La gestion des champs manquants est-elle robuste ?

### 4. Tests et qualité

- [ ] Examiner `test_functionality.py`
- [ ] Vérifier la couverture des tests
- [ ] Identifier les fonctions non testées
- [ ] Suggérer des tests manquants

### 5. Documentation

- [ ] Le README est-il à jour ?
- [ ] Les exemples d'utilisation sont-ils corrects ?
- [ ] La documentation API est-elle complète ?

### 6. Performance et optimisation

- [ ] Y a-t-il des opérations coûteuses qui pourraient être optimisées ?
- [ ] Les fichiers sont-ils correctement fermés ?
- [ ] Y a-t-il des risques de fuites mémoire ?
- [ ] Les opérations I/O sont-elles efficaces ?

### 7. Suggestions d'amélioration

Pour chaque problème identifié :
- **Criticité** : Critique / Important / Mineur
- **Description** : Explication claire du problème
- **Impact** : Conséquence potentielle
- **Suggestion** : Solution proposée avec exemple de code si pertinent

## Format de sortie

Organiser la review en sections :

### 📊 Résumé exécutif
- Points forts du code
- Problèmes critiques à corriger
- Problèmes importants à considérer
- Améliorations suggérées

### 🔍 Analyse détaillée par fichier
Pour chaque fichier :
- Points positifs
- Problèmes identifiés avec suggestions
- Code examples pour les améliorations

### 🧪 Tests
- Couverture actuelle
- Tests manquants recommandés
- Améliorations suggérées

### 📚 Documentation
- État actuel
- Améliorations suggérées

### ⚡ Performance
- Points d'attention
- Optimisations possibles

### 🔒 Sécurité
- Vulnérabilités potentielles
- Recommandations

## Critères de qualité

- **Excellent** : Code propre, bien documenté, bien testé, aucune amélioration critique nécessaire
- **Bon** : Code de qualité avec quelques améliorations mineures suggérées
- **À améliorer** : Code fonctionnel mais nécessitant des refactorisations
- **Problématique** : Code avec des problèmes critiques à corriger

## Notes importantes

- Être constructif et positif dans les commentaires
- Prioriser les problèmes critiques et importants
- Fournir des exemples de code pour les suggestions
- Considérer le contexte du projet (projet personnel vs production)
- Respecter les conventions Python et les bonnes pratiques de la communauté

