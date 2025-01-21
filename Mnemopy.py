import tkinter as tk
import sqlite3
import tkinter.messagebox as tkMess
from tkinter import ttk
from datetime import datetime
import time
import random
import ctypes
import sys
from classes import Fiche, Boite, load_data_from_db

# Savoir si la version de windows est 11 ou non
win11 = sys.getwindowsversion().build >= 22000

ctypes.windll.shcore.SetProcessDpiAwareness(1)


class LeitnerApp:
    def __init__(self, root, boite_dico):
        self.root = root
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f'{550 if win11 else 400}x{820 if win11 else 600}+{width // 2 - 200}+{height // 2 - 400}')
        self.root.resizable(False, True)
        self.root.option_add("*TCombobox*Listbox*Background", "#FFFFFF")
        self.root.option_add("*TCombobox*Listbox*Foreground", "#0E0E10")
        self.root.option_add("*TCombobox*Listbox*Font", "Montserrat*bold 15")
        self.root.option_add("*TCombobox*Listbox*Justify", 'center')
        self.root.option_add("*TCombobox*Listbox*Relief", 'flat')

        # Initialisez votre dictionnaire de boîtes
        self.boite_dico = boite_dico
        self.boites_values_affichage = [f"{boite.id_boite}Boîte {index}: {boite.nom}" for index, boite in
                                        enumerate(self.boite_dico.values(), start=1)]
        self.boites_id = self.boites_values_affichage
        self.boite_shuffled = False
        self.default_value_combobox = None
        self.create_frame()
        self.main_menu()

    def main_menu(self, boite_selectionnee=None):
        """Renvoie au menu principal"""
        self.root.title("Mnemopy")
        self.frame.forget()
        self.create_frame()
        self.delete_boite_button_exists = False
        self.browse_index = 0
        self.boite_shuffled = False
        if boite_selectionnee and boite_selectionnee != "Aucune boîte disponible":
            self.default_value_combobox = boite_selectionnee

        text_label = tk.Label(self.frame, text="Choisir une Boîte :", font=('Montserrat', 16, 'bold'), wraplength=500)
        text_label.pack(pady=(10, 0))

        self.boite_selectionnee_var = tk.StringVar()
        self.create_combobox(self.boite_selectionnee_var)
        self.update_combobox()

        self.boite_combobox.bind("<<ComboboxSelected>>", self.update_default_combobox_value)
        self.update_default_combobox_value(None)

        self.niveau_apprentissage_a_reviser = tk.StringVar()
        niveau_values = [f"Niveau d'apprentissage {i}" for i in range(1, 8)]
        combobox_niveau = self.create_combobox(self.niveau_apprentissage_a_reviser, values=niveau_values)
        combobox_niveau.set(niveau_values[0])

        # Créez une nouvelle frame pour les deux widgets côte à côte
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=(20, 0))

        # Variable pour suivre l'état du bouton "Mélanger"
        self.shuffle_var = tk.BooleanVar()

        # Bouton personnalisé pour "Mélanger"
        self.shuffle_button = self.create_button("Mélanger", command=lambda: self.toggle_shuffle(), frame=button_frame,
                                                 side=tk.LEFT, pady=0, activebackground="#d6fdd6", padx=(0, 18 if win11 else 22))

        # Bouton "Réviser"
        self.create_button("Réviser", command=lambda: self.reviser_window(), frame=button_frame, side=tk.RIGHT, pady=0,
                           padx=(0, 0))

        # Bouton "Parcourir les fiches" pour afficher les fiches
        self.create_button("Parcourir les fiches", command=lambda: self.browse_fiches_window(), width=25 if win11 else 21,
                           font=("Montserrat", 15, "bold"))

        logo_label = tk.Label(self.frame, text="Mnemopy", font=('Segoe UI Black', 40, 'bold'), width=100,
                              justify='center', foreground='#0E0E10')
        logo_label.pack(pady=(5, 5 if win11 else 0))

        # Créez des boutons pour "Créer une fiche" et "Réviser" et "Editer les boîtes"
        self.create_button("Créer une fiche", command=lambda: self.create_fiche_window(), width=25 if win11 else 21,
                           font=("Montserrat", 15, "bold"))

        self.create_button("Editer les Boîtes", command=lambda: self.edit_boite_window(boite_selectionnee), width=25 if win11 else 21,
                           font=("Montserrat", 15, "bold"))

    def toggle_shuffle(self):
        # Inversez l'état de la variable et mettez à jour l'apparence du bouton
        self.shuffle_var.set(not self.shuffle_var.get())
        if self.shuffle_var.get():
            self.shuffle_button.configure(bg="#98fb98")
        else:
            self.shuffle_button.configure(bg="white")

    def reviser_window(self):
        """Menu de révision"""
        boite_selectionnee = self.boite_selectionnee_var.get()
        # On récupère le niveau d'apprentissage selectionné
        niveau_selectionne = int(self.niveau_apprentissage_a_reviser.get().split()[-1])
        if boite_selectionnee == "Aucune boîte disponible":
            tkMess.showwarning("Erreur", "Veuillez selectionner une boîte !")
            return None
        else:
            self.default_value_combobox = boite_selectionnee

        self.frame.forget()
        self.create_frame()
        self.root.title("Révisions")

        # Extraire l'ID de la boîte sélectionnée à partir de la chaîne de texte
        boite_id = self.get_boite_id(boite_selectionnee)

        toutes_fiches = boite_dico[boite_id].fiches

        if not self.boite_shuffled and self.shuffle_var.get():
            random.shuffle(toutes_fiches)

        # Récupérez une fiche à réviser à partir de la boîte de Leitner
        fiche_a_reviser = None
        for fiche in toutes_fiches:
            if fiche.niveau_apprentissage == niveau_selectionne:
                if fiche.derniere_tentative:
                    maintenant = time.time()  # Obtenez le temps actuel en secondes
                    if maintenant - fiche.derniere_tentative < liste_temps_derniere_tentative[
                        fiche.niveau_apprentissage - 1]:
                        # Attendez que le temps d'attente soit écoulé
                        continue  # Passez à la fiche suivante si le temps d'attente n'est pas fini
                fiche_a_reviser = fiche
                break

        if fiche_a_reviser:

            recto_label = tk.Label(self.frame, text="Recto :", font=('Montserrat', 16, 'bold'))
            recto_label.pack(pady=(10, 0))

            # Affichez le recto de la fiche
            recto_label = tk.Label(self.frame, text=fiche_a_reviser.recto, font=("Roboto", 14, 'bold'), wraplength=500 if win11 else 350)
            recto_label.pack(pady=(5, 0))

            # Laissez l'utilisateur entrer la réponse
            self.reponse_text = tk.Text(self.frame)
            self.reponse_text.config(font=("Roboto", 12, "bold"), width=35 if win11 else 33, height=5, wrap='word', relief='solid',
                                     borderwidth=4 if win11 else 3)
            self.reponse_text.pack(pady=(10, 0))

            self.button_frame = tk.Frame(self.frame)
            self.button_frame.pack()

            # Bouton "Retour" pour revenir au menu principal
            self.back_button = self.create_button("Retour", frame=self.button_frame, command=lambda: self.main_menu(),
                                                  side=tk.LEFT, padx=(0, 20))

            # Bouton "Soumettre" pour afficher le verso de la fiche
            self.submit_button = self.create_button("Soumettre", frame=self.button_frame,
                                                    command=lambda: self.show_verso(fiche_a_reviser),
                                                    side=tk.RIGHT, padx=(0, 0))

        else:
            no_fiche_label = tk.Label(self.frame,
                                      text=f"Aucune fiche de niveau {niveau_selectionne} disponible dans cette boîte.",
                                      font=("Montserrat", 16, "bold"), wraplength=500 if win11 else 350)
            no_fiche_label.pack(pady=(15, 0))

            # Bouton "Retour" pour revenir au menu principal
            self.create_button("Retour", command=lambda: self.main_menu(boite_selectionnee))

    def show_verso(self, fiche):
        """Affiche le verso de la fiche avec les boutons Échec et Réussite"""
        if len(self.reponse_text.get("1.0", 'end-1c')) == 0:
            tkMess.showwarning("Erreur", "Le champ de réponse ne doit pas rester vacant !")
            return None
        self.button_frame.forget()

        verso_label1 = tk.Label(self.frame, text="Verso :", font=("Montserrat", 16, "bold"))
        verso_label1.pack(pady=(5, 0))

        # Afficher le verso de la fiche
        verso_label2 = tk.Label(self.frame, text=fiche.verso, font=("Helvetica", 14, "bold"), wraplength=500 if win11 else 350)
        verso_label2.pack(pady=(5, 5))

        button_frame = tk.Frame(self.frame)
        button_frame.pack()

        # Bouton "Échec" pour réduire le niveau d'apprentissage
        self.create_button("Échec", frame=button_frame,
                           command=lambda: self.update_niveau_apprentissage(fiche, echec=True), side=tk.LEFT,
                           padx=(0, 20), bg="#dd655f", activebackground="#ecaaa6")

        # Bouton "Réussite" pour augmenter le niveau d'apprentissage
        self.create_button("Réussite", frame=button_frame,
                           command=lambda: self.update_niveau_apprentissage(fiche, echec=False), side=tk.RIGHT,
                           padx=(0, 0), bg="#98fb98", activebackground="#d6fdd6")

    def update_niveau_apprentissage(self, fiche, echec):
        """Mise à jour du niveau d'apprentissage de la fiche"""
        # Mettre à jour le niveau d'apprentissage en fonction de la réponse de l'utilisateur

        fiche.derniere_tentative = time.time()

        if echec:
            fiche.niveau_apprentissage = 1
        else:
            fiche.niveau_apprentissage += 1

        cursor.execute(
            f"UPDATE flashcards SET niveau_apprentissage = {fiche.niveau_apprentissage}, derniere_tentative = {fiche.derniere_tentative} WHERE id_fiche = {fiche.id_fiche}")
        if fiche.niveau_apprentissage > 7:
            boite_dico[fiche.id_boite].fiches.remove(fiche)
            cursor.execute(f"DELETE FROM flashcards WHERE id_fiche = {fiche.id_fiche}")

        db.commit()

        self.reviser_window()

    def browse_fiches_window(self):
        boite_selectionnee = self.boite_selectionnee_var.get()
        if boite_selectionnee == "Aucune boîte disponible":
            tkMess.showwarning("Erreur", "Veuillez selectionner une boîte !")
            return None

        boite_id = self.get_boite_id(boite_selectionnee)
        if len(boite_dico[boite_id].fiches) == 0:
            tkMess.showwarning("Erreur", "La Boîte selectionnée est vide !")
            return None

        self.root.title("Parcourir les fiches")
        self.frame.forget()
        self.create_frame()

        toutes_fiches_boite = boite_dico[boite_id].fiches
        if self.browse_index >= len(toutes_fiches_boite):
            self.browse_index = 0
        elif self.browse_index < 0:
            self.browse_index = len(toutes_fiches_boite) - 1
        fiche = toutes_fiches_boite[self.browse_index]

        info_label = tk.Label(self.frame,
                              text=f"Numéro fiche : {self.browse_index + 1}\nNiveau d'apprentissage : {fiche.niveau_apprentissage}\nDate de création : {fiche.creation_date}",
                              font=('Helvetica', 13, 'italic'))
        info_label.config(borderwidth=3, relief="groove", width=32 if win11 else 35, justify='center', height=4)
        info_label.pack(pady=(10, 0))

        recto_label = tk.Label(self.frame, text="Recto :", font=('Montserrat', 16, 'bold'))
        recto_label.pack(pady=(10, 0))

        recto_label = tk.Label(self.frame, text=toutes_fiches_boite[self.browse_index].recto,
                               font=("Roboto", 14, 'bold'), wraplength=500 if win11 else 350)
        recto_label.pack(pady=(5, 0))

        verso_label = tk.Label(self.frame, text="Verso :", font=('Montserrat', 16, 'bold'))
        verso_label.pack(pady=(10, 0))

        recto_label = tk.Label(self.frame, text=toutes_fiches_boite[self.browse_index].verso,
                               font=("Roboto", 14, 'bold'), wraplength=500 if win11 else 350)
        recto_label.pack(pady=(5, 0))

        # Créez un cadre pour les boutons au bas de la fenêtre
        button_frame = tk.Frame(self.frame, relief="solid", borderwidth=2)
        button_frame.pack(side=tk.BOTTOM, pady=(0, 20))

        # Boutons "Précédent" et "Suivant" pour naviguer entre les fiches
        self.create_button("<<<", frame=button_frame, command=lambda: self.show_previous_fiche(), width=5, side=tk.LEFT,
                           pady=0)

        self.create_button("Retour", frame=button_frame, command=lambda: self.main_menu(boite_selectionnee), width=7,
                           side=tk.LEFT, pady=0)

        self.create_button("Suppr.", frame=button_frame, command=lambda: self.delete_fiche(fiche), width=8,
                           side=tk.LEFT, pady=0, bg="#dd655f", activebackground="#ecaaa6")

        self.create_button(">>>", frame=button_frame, command=lambda: self.show_next_fiche(), width=5, side=tk.LEFT,
                           pady=0)

        self.frame.pack(expand=True, fill='both')

    def delete_fiche(self, fiche):
        """Supprime la fiche selectionnée"""
        if not tkMess.askyesno("Confirmation", f"Voulez vous vraiment supprimer la fiche ?"):
            return None
        boite_id = fiche.id_boite

        cursor.execute(f"DELETE FROM flashcards WHERE id_fiche = {fiche.id_fiche}")
        db.commit()

        if fiche in self.boite_dico[fiche.id_boite].fiches:
            self.boite_dico[fiche.id_boite].fiches.remove(fiche)

        if len(boite_dico[boite_id].fiches) > 0:
            self.browse_fiches_window()
        else:
            self.main_menu()
            tkMess.showinfo("Information", f"La boîte a été complètement vidée.")

    def show_previous_fiche(self):
        self.browse_index -= 1
        self.browse_fiches_window()

    def show_next_fiche(self):
        self.browse_index += 1
        self.browse_fiches_window()

    def create_fiche_window(self):
        """Menu de création de fiche"""
        self.frame.forget()
        self.create_frame()
        self.root.title("Créer une fiche")
        self.delete_boite_button_exists = False

        # Créez une boîte de combinaison pour choisir la boîte de Leitner
        boite_label = tk.Label(self.frame, text="Sélectionnez une boîte :", font=('Montserrat', 16, 'bold'))
        boite_label.pack(pady=(10, 0))

        self.boite_selectionnee_var = tk.StringVar()
        self.create_combobox(self.boite_selectionnee_var)
        self.update_combobox()

        self.boite_combobox.bind("<<ComboboxSelected>>", self.update_default_combobox_value)
        self.update_default_combobox_value(None)

        # Créez des champs pour le recto et le verso de la fiche
        recto_label = tk.Label(self.frame, text="Recto :", font=('Montserrat', 16, 'bold'))
        recto_label.pack(pady=(15, 5))

        self.recto_text = tk.Text(self.frame)
        self.recto_text.config(font=("Roboto", 12, "bold"), width=35, height=7, wrap='word', relief='solid',
                               borderwidth=4 if win11 else 3)
        self.recto_text.pack()

        verso_label = tk.Label(self.frame, text="Verso :", font=('Montserrat', 16, 'bold'))
        verso_label.pack(pady=(15, 5))

        self.verso_text = tk.Text(self.frame)
        self.verso_text.config(font=("Roboto", 12, "bold"), width=35, height=7, wrap='word', relief='solid',
                               borderwidth=4 if win11 else 3)
        self.verso_text.pack()

        # Créez un bouton "Retour" pour retourner au menu principal
        self.create_button("Retour", command=lambda: self.main_menu(self.boite_combobox.get()), side=tk.LEFT,
                           pady=(18, 0), padx=(0, 18))

        # Créez un bouton "Valider" pour sauvegarder la fiche
        self.create_button("Valider", command=lambda: self.save_fiche(), side=tk.RIGHT, pady=(18, 0), padx=(0, 0),
                           bg="#98fb98", activebackground="#d6fdd6")

    def save_fiche(self):
        """Sauvegarde la fiche dans la bdd"""
        recto = self.recto_text.get("1.0", 'end-1c')
        verso = self.verso_text.get("1.0", 'end-1c')
        self.recto_text.delete("1.0", "end")
        self.verso_text.delete("1.0", "end")
        if len(recto) == 0 or len(verso) == 0:
            tkMess.showwarning("Erreur", "Complétez le recto et le verso de la fiche !")
            return None
        boite_selectionnee = self.boite_selectionnee_var.get()

        if boite_selectionnee == "Aucune boîte disponible":
            tkMess.showwarning("Erreur", "Veuillez selectionner une boîte !")
            return None

        # Extraire l'ID de la boîte sélectionnée à partir de la chaîne de texte
        boite_id = self.get_boite_id(boite_selectionnee)

        # On récupère la date de création de la fiche
        now = datetime.now()
        creation_date = now.strftime("%Y-%m-%d %H:%M:%S")
        # Sauvegarde la fiche dans la base de données
        sql = "INSERT INTO flashcards (recto, verso, id_boite, creation_date) VALUES (?, ?, ?, ?)"
        values = (recto, verso, boite_id, creation_date)
        cursor.execute(sql, values)
        db.commit()

        # Créez la fiche et ajoutez-la à la boîte de Leitner appropriée (utilisez votre classe Boite ici)
        fiche_id = cursor.lastrowid
        fiche = Fiche(id_fiche=fiche_id, recto=recto, verso=verso, niveau_apprentissage=1, id_boite=boite_id,
                      creation_date=creation_date, derniere_tentative=None)
        boite_dico[boite_id].ajout_fiche(fiche)

    def edit_boite_window(self, boite_selectionnee=None):
        """Menu d'édition des boîtes"""
        self.frame.forget()
        self.create_frame()
        self.root.title("Éditer les boîtes")

        boite_label = tk.Label(self.frame, text="Boîte à supprimer :", font=('Montserrat', 16, 'bold'))
        boite_label.pack(pady=(10, 0))

        self.boite_selectionnee_var = tk.StringVar()
        self.create_combobox(self.boite_selectionnee_var)

        # Créez une étiquette pour afficher le nombre de fiches
        self.info_label = tk.Label(self.frame, text="", font=('Helvetica', 13, 'italic'))
        self.info_label.config(borderwidth=3, relief="groove", width=30, justify='center', height=1)
        self.info_label.pack(pady=(10, 0), padx=(1, 0))

        self.delete_boite_button = self.create_button("Supprimer", command=lambda: self.delete_boite(), bg="#dd655f",
                                                      activebackground="#ecaaa6")
        self.delete_boite_button_exists = True

        text_label = tk.Label(self.frame, text="Nommez la nouvelle Boîte :", font=('Montserrat', 16, 'bold'))
        text_label.pack(pady=(25, 15))

        self.name_entry_label = tk.Entry(self.frame)
        self.name_entry_label.config(font=('Helvetica', 18, 'bold'), justify="center", relief='solid', borderwidth=4 if win11 else 3,
                                     width=23)
        self.name_entry_label.pack()

        button_frame = tk.Frame(self.frame)
        button_frame.pack()

        self.back_button = self.create_button("Retour", frame=button_frame,
                                              command=lambda: self.main_menu(self.boite_combobox.get()), side=tk.LEFT,
                                              padx=(0, 23))

        self.create_button("Créer", frame=button_frame, command=lambda: self.save_boite(), side=tk.RIGHT, padx=(0, 0),
                           bg="#98fb98", activebackground="#d6fdd6")

        # Liez un événement à la mise à jour du nombre de fiches lorsque la combobox change de valeur
        self.boite_combobox.bind("<<ComboboxSelected>>", self.update_fiches_count)
        self.boite_combobox.bind("<<ComboboxSelected>>", self.update_default_combobox_value, add=True)
        self.update_combobox()
        self.update_default_combobox_value(None)
        self.update_fiches_count(None)


    def update_fiches_count(self, event):
        # Obtenir la boîte sélectionnée à partir de la combobox
        if len(self.boites_values_affichage) == 0:
            self.info_label.config(text="")
        else:
            boite_a_suppr = self.boite_selectionnee_var.get()
            if boite_a_suppr and boite_a_suppr != "Aucune boîte disponible":

                boite_id = self.get_boite_id(boite_a_suppr)
                # Mettre à jour le texte de l'étiquette avec le nombre de fiches dans la boîte
                fiches_count = len(self.boite_dico[boite_id].fiches)
                self.info_label.config(text=f"Contient {fiches_count} fiches")

    def update_default_combobox_value(self, event=None):
        """Met à jour dynamiquement la valeur de la boite selectionnée"""
        self.default_value_combobox = self.boite_selectionnee_var.get()

    def save_boite(self):
        """Sauvegarde la boite dans la bdd"""
        box_name = self.name_entry_label.get()
        self.name_entry_label.delete(0, 'end')
        if len(box_name) == 0:
            tkMess.showwarning("Erreur", "Ce champ ne doit pas rester vacant !")
            return None

        if box_name in [boite.nom for boite in self.boite_dico.values()]:
            tkMess.showwarning("Erreur", "Les noms de boîte sont uniques !")
            return None

        sql = "INSERT INTO leitner_boxes (nom) VALUES (?)"
        values = (box_name,)
        cursor.execute(sql, values)
        db.commit()

        boite_id = cursor.lastrowid
        boite = Boite(id_boite=boite_id, nom=box_name)
        boite_dico[boite_id] = boite
        self.update_combobox()
        self.update_fiches_count(None)

    def delete_boite(self):
        """Supprime la boîte sélectionnée et toutes les cartes associées"""
        boite_a_suppr = self.boite_selectionnee_var.get()
        boite_id = self.get_boite_id(boite_a_suppr)
        if not tkMess.askyesno(f"Confirmation", f"Voulez vous vraiment supprimer la {boite_a_suppr} ?"):
            return None

        # Supprimez d'abord toutes les cartes associées à la boîte
        cursor.execute(f"DELETE FROM flashcards WHERE id_boite = {boite_id}")

        # Ensuite, supprimez la boîte elle-même
        cursor.execute(f"DELETE FROM leitner_boxes WHERE id_boite = {boite_id}")

        db.commit()

        # Supprimez également la boîte du dictionnaire boite_dico si nécessaire
        if boite_id in boite_dico:
            del boite_dico[boite_id]

        # Mise à jour de l'interface utilisateur pour refléter les changements
        self.default_value_combobox = None
        self.update_combobox()
        self.update_fiches_count(None)

    def get_boite_id(self, boite_selectionnee):
        """Renvoie l'id de la boite selectionnée"""
        for boite_id in self.boites_id:
            if boite_selectionnee in boite_id:
                # Trouver la première occurrence de ";" dans le texte de la boîte sélectionnée
                colon_index = boite_id.find(";")

                # Extraire la partie du texte avant le ";" (c'est-à-dire l'ID)
                boite_id_str = boite_id[:colon_index]

                # Convertir l'ID en entier
                boite_id = int(boite_id_str)
                return boite_id

    def update_combobox(self):
        """Mettre à jour la Combobox avec les nouvelles valeurs des boîtes"""
        self.boites_values_affichage = [f"{boite.id_boite};Boîte {index}: {boite.nom}" for index, boite in
                                        enumerate(self.boite_dico.values(), start=1)]
        self.boites_id = self.boites_values_affichage
        if len(self.boites_values_affichage) == 0:
            # Aucune boîte disponible, désactivez la Combobox
            self.boite_combobox['state'] = 'disabled'
            self.boite_combobox['values'] = ['Aucune boîte disponible']
            self.boite_combobox.set('Aucune boîte disponible')  # Définissez une valeur par défaut
            if self.delete_boite_button_exists:
                self.delete_boite_button.config(state='disabled')
        else:
            # Il y a des boîtes, activez la Combobox et mettez à jour les valeurs
            self.boite_combobox['state'] = "readonly"
            self.boite_combobox['values'] = [boite.split(";", 1)[1] for boite in self.boites_values_affichage]
            if self.default_value_combobox == "Aucune boîte disponible":
                self.boite_combobox.set(self.boites_values_affichage[0].split(";", 1)[1])  # Définissez la première boîte comme valeur par défaut
            elif not self.default_value_combobox:
                self.boite_combobox.set(self.boites_values_affichage[0].split(";", 1)[1])  # Définissez la première boîte comme valeur par défaut
            else:
                self.boite_combobox.set(self.default_value_combobox)
            if self.delete_boite_button_exists:
                self.delete_boite_button.config(state='normal')

    def create_frame(self):
        """Crée une frame"""
        self.frame = tk.Frame(self.root)
        self.frame.pack()

    def create_button(self, text, frame=None, command=None, font=("Montserrat", 16 if win11 else 14, "bold"), height=2, width=11 if win11 else 10,
                      relief='solid',
                      borderwidth=4 if win11 else 3, pady=(18 if win11 else 15, 0), padx=(0, 0), side=None, bg=None, activebackground=None):
        """Crée un bouton"""
        if frame is None:
            frame = self.frame
        button = tk.Button(frame, text=text, command=command, font=font, height=height, width=width, relief=relief,
                           borderwidth=borderwidth, bg=bg, activebackground=activebackground, foreground="#0E0E10")
        button.pack(pady=pady, padx=padx, side=side)
        return button

    def create_combobox(self, textvariable, values=None, font=("Roboto", 16 if win11 else 14, "bold"), width=24 if win11 else 26, justify="center",
                        state="readonly", pady=(15 if win11 else 10, 0)):
        """Crée une Combobox"""
        if values is None:
            values = self.boites_values_affichage
        self.boite_combobox = ttk.Combobox(self.frame, textvariable=textvariable, values=values)
        self.boite_combobox.config(font=font, width=width, justify=justify, state=state)
        self.boite_combobox.pack(pady=pady)
        return self.boite_combobox


if __name__ == "__main__":
    # 10 mins, 1 jour, 3, jours, 6 jours, 13 jours, 20 jours, 30 jours
    liste_temps_derniere_tentative = [600, 86400, 259200, 518400, 1036800, 1555200, 2332800]
    boite_dico = load_data_from_db("db_mnemopy.db")
    db = sqlite3.connect("db_mnemopy.db")
    cursor = db.cursor()
    root = tk.Tk()
    app = LeitnerApp(root, boite_dico)
    root.mainloop()
