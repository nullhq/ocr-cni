# API Flask d'Extraction CNI

Une API REST Flask pour extraire automatiquement les informations des cartes nationales d'identité (CNI) camerounaises à partir d'images, en utilisant l'API Google Gemini Vision.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Endpoints](#endpoints)
- [Formats de réponse](#formats-de-réponse)
- [Gestion des erreurs](#gestion-des-erreurs)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Limitations](#limitations)
- [Contributions](#contributions)

## Fonctionnalités

- Extraction automatique des informations du recto de la CNI
- Extraction automatique des informations du verso de la CNI
- Traitement combiné recto + verso
- Support des formats d'image PNG, JPG, JPEG
- Validation et sécurisation des fichiers uploadés
- Gestion robuste des erreurs
- API RESTful avec réponses JSON structurées
- Nettoyage automatique des fichiers temporaires

## Prérequis

- Python 3.7 ou supérieur
- Une clé API Google Gemini valide
- Connexion Internet (pour l'API Gemini)

## Installation

1. Cloner le projet
```bash
git clone <url-du-projet>
cd api-cni-extraction
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## Configuration

1. Obtenir une clé API Google Gemini
   - Aller sur [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Créer une nouvelle clé API
   - Copier la clé générée

2. Configurer la clé API dans le code
```txt
API_KEY = 'votre_cle_api_gemini_ici'
```

3. (Optionnel) Configurer les variables d'environnement
```bash
export API_KEY=votre_cle_api_gemini_ici
export FLASK_ENV=development
export FLASK_PORT=5000
```

## Utilisation

### Démarrage du serveur

```bash
python app.py
```

Le serveur sera accessible sur `http://127.0.0.1:5000`

### Test rapide

```bash
curl http://127.0.0.1:5000/health
```

## Endpoints

### GET /health

Vérification du statut de l'API.

**Réponse:**
```json
{
    "status": "healthy",
    "message": "API CNI Extraction est opérationnelle",
    "endpoints": ["/recto", "/verso", "/complete"]
}
```

### POST /recto

Extraction des informations du recto de la CNI.

**Paramètres:**
- `image` (file): Image du recto de la CNI

**Exemple avec curl:**
```bash
curl -X POST http://127.0.0.1:5000/recto \
  -F "image=@recto.jpg"
```

**Réponse:**
```json
{
    "success": true,
    "side": "recto",
    "data": {
        "pays_emission": "CAMEROUN",
        "type_document": "CARTE DE RESIDENT",
        "nom": "DOE",
        "prenoms": "JOHN MARIE",
        "date_naissance": "15.03.1990",
        "sexe": "M",
        "date_expiration": "15.03.2030",
        "numero_document": "123456789",
        "signature": "John Doe",
        "travail": "INGENIEUR"
    }
}
```

### POST /verso

Extraction des informations du verso de la CNI.

**Paramètres:**
- `image` (file): Image du verso de la CNI

**Exemple avec curl:**
```bash
curl -X POST http://127.0.0.1:5000/verso \
  -F "image=@verso.jpg"
```

**Réponse:**
```json
{
    "success": true,
    "side": "verso",
    "data": {
        "nationalite": "CAMEROUNAISE",
        "profession": "INGENIEUR",
        "date_delivrance": "15.03.2020",
        "taille": "1,75 m",
        "numero_cni": "CM123456789",
        "code_qr_present": true,
        "signature_autorite": "MINISTRE DELEGUE",
        "code_numerique": "A<CMR123456789..."
    }
}
```

### POST /complete

Extraction complète des informations (recto + verso).

**Paramètres:**
- `recto` (file): Image du recto de la CNI
- `verso` (file): Image du verso de la CNI

**Exemple avec curl:**
```bash
curl -X POST http://127.0.0.1:5000/complete \
  -F "recto=@recto.jpg" \
  -F "verso=@verso.jpg"
```

**Réponse:**
```json
{
    "success": true,
    "side": "complete",
    "data": {
        "recto": {
            "pays_emission": "CAMEROUN",
            "nom": "DOE",
            // ... autres champs recto
        },
        "verso": {
            "nationalite": "CAMEROUNAISE",
            "profession": "INGENIEUR",
            // ... autres champs verso
        },
        "combined": {
            // Tous les champs combinés
        }
    }
}
```

## Formats de réponse

### Champs extraits du recto

| Champ | Type | Description |
|-------|------|-------------|
| pays_emission | string | Pays d'émission (ex: "CAMEROUN") |
| type_document | string | Type de document (ex: "CARTE DE RESIDENT") |
| nom | string | Nom de famille |
| prenoms | string | Prénoms |
| date_naissance | string | Date de naissance (format JJ.MM.AAAA) |
| sexe | string | Sexe (M ou F) |
| date_expiration | string | Date d'expiration (format JJ.MM.AAAA) |
| numero_document | string | Numéro du document |
| signature | string | Nom associé à la signature |
| travail | string | Profession mentionnée |

### Champs extraits du verso

| Champ | Type | Description |
|-------|------|-------------|
| nationalite | string | Nationalité |
| profession | string | Profession |
| date_delivrance | string | Date de délivrance (format JJ.MM.AAAA) |
| taille | string | Taille (ex: "1,75 m") |
| numero_cni | string | Numéro CNI complet |
| code_qr_present | boolean | Présence d'un QR code |
| signature_autorite | string | Nom de l'autorité signataire |
| code_numerique | string | Code numérique vertical |

## Gestion des erreurs

### Codes d'erreur HTTP

- `400 Bad Request`: Fichier manquant ou invalide
- `413 Payload Too Large`: Fichier trop volumineux (>16MB)
- `500 Internal Server Error`: Erreur de traitement

### Exemples d'erreurs

**Aucun fichier fourni:**
```json
{
    "error": "Aucune image fournie"
}
```

**Type de fichier non supporté:**
```json
{
    "error": "Type de fichier non autorisé. Utilisez PNG, JPG ou JPEG"
}
```

**Erreur API Gemini:**
```json
{
    "error": "Erreur de requête API : 403 Forbidden"
}
```

## Tests

### Tests manuels avec Postman

1. Importer la collection Postman (fichier fourni)
2. Configurer l'URL de base: `http://127.0.0.1:5000`
3. Tester chaque endpoint avec des images de CNI

### Tests avec curl

```bash
# Test de santé
curl http://127.0.0.1:5000/health

# Test recto
curl -X POST http://127.0.0.1:5000/recto \
  -F "image=@test_recto.jpg"

# Test verso
curl -X POST http://127.0.0.1:5000/verso \
  -F "image=@test_verso.jpg"

# Test complet
curl -X POST http://127.0.0.1:5000/complete \
  -F "recto=@test_recto.jpg" \
  -F "verso=@test_verso.jpg"
```

## Structure du projet backend

```
api-cni-extraction/
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances Python
├── README.md          # Documentation
├── temp_uploads/      # Dossier temporaire (créé automatiquement)
├── tests/            # Tests unitaires
│   ├── test_app.py
│   └── test_images/
└── docs/             # Documentation supplémentaire
    ├── postman_collection.json
    └── api_examples.md
```

## Contributteur

TABOUTSA NOUADJE FREDY TRESOR  <br>
BARRA MARTIAL ARISTIDE	<br>
DOUANLA BRUNA CHROIQUE	<br>
KENNE KEYANYEM FRANK	<br>
NGONO NGUIETSI SYLLA	<br>


## Encadreur
Mr TINKU CLAUDE (tinkuclaude@gmail.com)