# app/api.py
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from app.utils.utils_gemini import allowed_file, extract_info_with_gemini
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)

# Configuration pour les uploads leurs tailles maximales et dossier d'upload.
UPLOAD_FOLDER = 'temp_uploads'
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Créer le dossier d'upload s'il n'existe pas !
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/recto', methods=['POST'])
def extract_recto():
    """Endpoint pour extraire les informations du recto de la CNI"""
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Type de fichier non autorisé. Utilisez PNG, JPG ou JPEG'}), 400
        
        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"recto_{filename}")
        file.save(temp_path)
        
        try:
            # Prompt optimisé pour le recto
            prompt_recto = """
            Extrais les informations clés du RECTO de cette carte d'identité camerounaise.
            Le résultat doit être un objet JSON avec les champs suivants :
            - "pays_emission" (ex: "CAMEROUN")
            - "type_document" (toujours: "CARTE DE RESIDENT")
            - "nom" (nom de famille/surname)
            - "prenoms" (prénoms/given names)
            - "date_naissance" (format JJ.MM.AAAA)
            - "sexe" (M ou F)
            - "date_expiration" (format JJ.MM.AAAA)
            - "numero_document" (le numéro visible, souvent en haut à droite)
            - "signature" (le nom associé à la signature manuscrite)
            - "travail" (profession/work si visible)

            Si une information n'est pas trouvée ou n'est pas lisible, la valeur correspondante doit être null.
            Ne donne absolument rien d'autre que l'objet JSON valide.
            """
            
            # Extraire les informations
            result = extract_info_with_gemini(temp_path, prompt_recto)
            
            return jsonify({
                'success': True,
                'side': 'recto',
                'data': result
            })
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verso', methods=['POST'])
def extract_verso():
    """Endpoint pour extraire les informations du verso de la CNI"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Type de fichier non autorisé. Utilisez PNG, JPG ou JPEG'}), 400
        
        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"verso_{filename}")
        file.save(temp_path)
        
        try:
            prompt_verso = """
            Extrais les informations clés du VERSO de cette carte d'identité camerounaise.
            Le résultat doit être un objet JSON avec les champs suivants :
            - "nationalite" (ex: "ALLEMANDE")
            - "profession" (ex: "INGENIEUR")
            - "date_delivrance" (date de délivrance/issue, format JJ.MM.AAAA)
            - "date_expiration" (format JJ.MM.AAAA si visible)
            - "taille" (height, ex: "1,83 m")
            - "numero_cni" (numero CNI/NIC number, ex: "AA000000000")
            - "code_qr_present" (true/false selon si un QR code est présent)
            - "signature_autorite" (nom de l'autorité qui a signé, ex: "Martin MBARGA NGUÉLÉ")
            - "code_numerique" (le long code numérique vertical s'il est lisible)

            Si une information n'est pas trouvée ou n'est pas lisible, la valeur correspondante doit être null.
            Ne donne absolument rien d'autre que l'objet JSON valide.
            """
            
            result = extract_info_with_gemini(temp_path, prompt_verso)
            
            return jsonify({
                'success': True,
                'side': 'verso',
                'data': result
            })
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/complete', methods=['POST'])
def extract_complete():
    """Endpoint pour extraire les informations complètes (recto + verso)"""
    try:

        if 'recto' not in request.files or 'verso' not in request.files:
            return jsonify({'error': 'Les images recto ET verso sont requises'}), 400
        
        recto_file = request.files['recto']
        verso_file = request.files['verso']
        
        if recto_file.filename == '' or verso_file.filename == '':
            return jsonify({'error': 'Les deux fichiers doivent être sélectionnés'}), 400
        
        if not (allowed_file(recto_file.filename) and allowed_file(verso_file.filename)):
            return jsonify({'error': 'Types de fichiers non autorisés. Utilisez PNG, JPG ou JPEG'}), 400
        
        # Sauvegarder temporairement les fichiers
        recto_filename = secure_filename(recto_file.filename)
        verso_filename = secure_filename(verso_file.filename)
        
        recto_path = os.path.join(app.config['UPLOAD_FOLDER'], f"recto_{recto_filename}")
        verso_path = os.path.join(app.config['UPLOAD_FOLDER'], f"verso_{verso_filename}")
        
        recto_file.save(recto_path)
        verso_file.save(verso_path)
        
        try:
            # Prompts pour les deux côtés
            prompt_recto = """
            Extrais les informations clés du RECTO de cette carte d'identité.
            Retourne un objet JSON avec : pays_emission, type_document, nom, prenoms, date_naissance, sexe, date_expiration, numero_document, signature, travail.
            Valeurs null si non trouvées. Seulement du JSON valide.
            """
            
            prompt_verso = """
            Extrais les informations clés du VERSO de cette carte d'identité.
            Retourne un objet JSON avec : nationalite, profession, date_delivrance, taille, numero_cni, code_qr_present, signature_autorite.
            Valeurs null si non trouvées. Seulement du JSON valide.
            """
            
            # Extraire les informations des deux côtés
            recto_data = extract_info_with_gemini(recto_path, prompt_recto)
            verso_data = extract_info_with_gemini(verso_path, prompt_verso)
            
            # Combiner les données
            complete_data = {
                **recto_data,
                **verso_data
            }
            
            return jsonify({
                'success': True,
                'side': 'complete',
                'data': {
                    'recto': recto_data,
                    'verso': verso_data,
                    'combined': complete_data
                }
            })
            
        finally:
            # Nettoyer les fichiers temporaires
            for path in [recto_path, verso_path]:
                if os.path.exists(path):
                    os.remove(path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification du statut de l'API"""
    return jsonify({
        'status': 'healthy',
        'message': 'API CNI Extraction est opérationnelle',
        'endpoints': ['/recto', '/verso', '/complete', '/health']
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Fichier trop volumineux. Taille maximale : 2MB'}), 413

if __name__ == '__main__':
    # Configuration pour le développement
    app.run(debug=True, host='0.0.0.0', port=5000)