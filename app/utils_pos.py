import re

def get_coords(pos_string):
    """
    Parse les codes de position complexes de Marsa Maroc.
    Formats supportes :
    - TC3 (ex: 02D57B4) -> Bloc: 02D, Travee: 57, Cellule: B, Niveau: 4
    - TCE (ex: L008A01) -> Bloc: L, Travee: 008, Cellule: A, Niveau: 01
    - TCE Special (ex: TP014C11) -> Bloc: TP, Travee: 014, Cellule: C, Niveau: 11
    """
    pos_string = str(pos_string).strip().upper()
    
    # 1. Format TCE Special (ex: TP014C11) -> 2 lettres + 3 chiffres + 1 lettre + 2 chiffres
    match_tce_spec = re.match(r'^([A-Z]{2})(\d{3})([A-Z])(\d{2})$', pos_string)
    if match_tce_spec:
        return {
            "bloc": match_tce_spec.group(1),
            "travee": match_tce_spec.group(2),
            "cellule": match_tce_spec.group(3),
            "niveau": int(match_tce_spec.group(4)),
            "terminal": "TCE"
        }
        
    # 2. Format TC3 (ex: 02D57B4) -> 3 char (02D) + 2 chiffres + 1 lettre + 1 chiffre
    match_tc3 = re.match(r'^([A-Z0-9]{3})(\d{2})([A-Z])(\d{1})$', pos_string)
    if match_tc3:
        return {
            "bloc": match_tc3.group(1),
            "travee": match_tc3.group(2),
            "cellule": match_tc3.group(3),
            "niveau": int(match_tc3.group(4)),
            "terminal": "TC3"
        }
        
    # 3. Format TCE Standard (ex: L008A01) -> 1 lettre + 3 chiffres + 1 lettre + 2 chiffres
    match_tce_std = re.match(r'^([A-Z])(\d{3})([A-Z])(\d{2})$', pos_string)
    if match_tce_std:
        return {
            "bloc": match_tce_std.group(1),
            "travee": match_tce_std.group(2),
            "cellule": match_tce_std.group(3),
            "niveau": int(match_tce_std.group(4)),
            "terminal": "TCE"
        }

    return None

def get_safety_status(niveau):
    if niveau > 6:
        return "Niveau Critique Hors Norme"
    elif niveau >= 5:
        return "Attention: Haute Densite"
    return "Conforme"
