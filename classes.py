import sqlite3


class Fiche:
    def __init__(self, id_fiche: int, recto: str, verso: str, niveau_apprentissage: int, id_boite: int, creation_date:str, derniere_tentative:float):
        self.id_fiche = id_fiche
        self.recto = recto
        self.verso = verso
        self.niveau_apprentissage = niveau_apprentissage
        self.id_boite = id_boite
        self.creation_date = creation_date
        self.derniere_tentative = derniere_tentative

    def get_all(self):
        return self.id_fiche, self.recto, self.verso, self.niveau_apprentissage, self.id_boite

class Boite:
    def __init__(self, id_boite: int, nom: str):
        self.id_boite = id_boite
        self.nom = nom
        self.fiches = []

    def ajout_fiche(self, fiche: Fiche):
        self.fiches.append(fiche)

    def __str__(self):
        return f""" id_boite : {self.id_boite},\n nom : {self.nom},\n nombre_fiches : {len(self.fiches)}"""

def load_data_from_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    boites = cursor.execute("SELECT * FROM leitner_boxes").fetchall()
    fiches = cursor.execute("SELECT * FROM flashcards").fetchall()

    boite_dico = {}

    for boite_info in boites:
        boite_id, nom = boite_info[0], boite_info[1]
        boite_dico[boite_id] = Boite(boite_id, nom)

    for fiche_info in fiches:
        fiche_id, recto, verso, niveau_apprentissage, id_boite, creation_date, derniere_tentative = fiche_info
        fiche = Fiche(fiche_id, recto, verso, niveau_apprentissage, id_boite, creation_date, derniere_tentative)
        boite_dico[id_boite].ajout_fiche(fiche)

    conn.close()

    return boite_dico

if __name__ == "__main__":
    boite_dico = load_data_from_db("db_mnemopy.db")

    for v in boite_dico.values():
        print(v)
