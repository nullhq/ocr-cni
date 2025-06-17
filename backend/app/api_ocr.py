from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from utils.utils_ocr import extract_cni_info
from flask_cors import CORS
import easyocr
import os

app = Flask(__name__)
CORS(app)

# Configuration des extensions d'images valides.
UPLOAD_FOLDER = './temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
reader = easyocr.Reader(['fr', 'en'], gpu=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/extract-cni', methods=['POST'])
def extract_cni():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    
    file = request.files['file']
    
    # Vérifier si le fichier a un nom sinon on retourne une erreur.
    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Lire le texte avec la methode readtext d'EasyOCR.
            results = reader.readtext(filepath)
            
            # Extraire les informations structurées.
            cni_data = extract_cni_info(results)
            
            # Supprimer le fichier du stockage temporaire après traitement !
            os.remove(filepath)
            
            return jsonify(cni_data), 201
            
        except Exception as e:
            return jsonify({"error": f"Erreur lors du traitement: {str(e)}"}), 500
    
    return jsonify({"error": "Type de fichier non autorisé"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)