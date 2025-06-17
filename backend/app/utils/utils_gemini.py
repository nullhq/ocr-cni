# app/utils.py
import os
import base64
import json
import requests
from dotenv import load_dotenv
load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
API_KEY = os.getenv('API_KEY')
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def allowed_file(filename):
    """Vérifier si le fichier a une extension autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    """Déterminer le type MIME basé sur l'extension du fichier"""
    if filename.lower().endswith('.png'):
        return "image/png"
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        return "image/jpeg"
    return None

def encode_image(image_path):
    """Encoder une image en base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f"Erreur lors de l'encodage de l'image : {str(e)}")

def extract_info_with_gemini(image_path, prompt):
    """Extraire les informations d'une image avec l'API Gemini"""
    try:
        # Encoder l'image en base64 et obtenir le type MIME.
        encoded_image = encode_image(image_path)
        mime_type = get_mime_type(image_path)
        
        if not mime_type:
            raise Exception("Type d'image non supporté")
        
        # Construire la requête pour envoyer à l'API Gemini.
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": encoded_image
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            candidate = response_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'text' in part:
                        text_content = part['text'].strip()
                        
                        # Nettoyer le texte si c'est dans un bloc markdown
                        if text_content.startswith('```json'):
                            # Extraire le JSON du bloc markdown
                            json_start = text_content.find('{')
                            json_end = text_content.rfind('}') + 1
                            if json_start != -1 and json_end != 0:
                                text_content = text_content[json_start:json_end]
                        elif text_content.startswith('```'):
                            # Autres blocs de code
                            lines = text_content.split('\n')
                            text_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else text_content
                        
                        try:
                            # Parser le JSON nettoyé
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            # Si ce n'est pas du JSON valide, retourner le texte brut
                            return {"raw_text": text_content}
        
        return {"error": "Aucune réponse valide reçue de l'API !"}
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur de requête API : {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction : {str(e)}")
