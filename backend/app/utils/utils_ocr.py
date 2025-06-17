import re

def extract_cni_info(text_results):
    data = {
        "surname": "",
        "given_names": "",
        "date_of_birth": "",
        "place_of_birth": "",
        "sex": "",
        "height": "",
        "profession": ""
    }
    
    # Variables pour suivre le contexte de l'etat actuel du json.
    current_field = None
    
    for (_, text, _) in text_results:
        text = text.strip()
        
        if "NOM/SURNAME" in text or "NoMSURNAME" in text:
            current_field = "surname"
            continue
        elif "PRÉNOMS/GIVEN" in text or "PREnOMSiGIVEN" in text:
            current_field = "given_names"
            continue
        elif "DATE DE NAISSANCE" in text or "DATEPEaNCEDareofeth" in text:
            current_field = "date_of_birth"
            continue
        elif "LIEU DE NAISSANCE" in text or "LFuEE" in text:
            current_field = "place_of_birth"
            continue
        elif "SEXE/SEX" in text or "S8ssex" in text:
            current_field = "sex"
            continue
        elif "TAILLE/MERGHT" in text or "TailLE Hesser" in text:
            current_field = "height"
            continue
        elif "PROFESSION/OCCUPATION" in text or "PROFESSIONOCCUPATION" in text:
            current_field = "profession"
            continue
            
        # Remplissage des données en fonction du champ actuel.
        if current_field == "surname" and not data["surname"]:
            # Nettoyer le nom (enlever les chiffres et caractères spéciaux)
            clean_name = re.sub(r'[^a-zA-Z\s]', '', text)
            data["surname"] = clean_name.strip()
        elif current_field == "given_names" and not data["given_names"]:
            clean_name = re.sub(r'[^a-zA-Z\s]', '', text)
            data["given_names"] = clean_name.strip()
        elif current_field == "date_of_birth" and not data["date_of_birth"]:
            # Expression réguliere pour tenter de trouver une date dans le texte
            date_match = re.search(r'\d{1,2}[.,/]\d{1,2}[.,/]\d{2,4}', text)
            if date_match:
                data["date_of_birth"] = date_match.group().replace(',', '.').replace('/', '.')
        elif current_field == "place_of_birth" and not data["place_of_birth"]:
            # Prendre le premier texte en majuscules comme lieu de naissance
            if text.isupper() and len(text) > 3:
                data["place_of_birth"] = text
        elif current_field == "sex" and not data["sex"]:
            if text.upper() in ['F', 'M']:
                data["sex"] = text.upper()
        elif current_field == "height" and not data["height"]:
            # Trouver une valeur de taille (format 1,63)
            height_match = re.search(r'\d,\d{2}', text)
            if height_match:
                data["height"] = height_match.group()
        elif current_field == "profession" and not data["profession"]:
            if text.isupper() and len(text) > 2:
                data["profession"] = text
    
    return data
