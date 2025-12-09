import customtkinter as ctk
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from view.game_view import GameView
    from controller.game_controller import GameController
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que las carpetas se llamen 'view' y 'controller' (sin s) y estén junto a main.py")
    sys.exit(1)

def main():
    ctk.set_appearance_mode("dark")
    
    app = ctk.CTk()
    app.title("YugiOh MVC Python")
    app.geometry("1300x800")

    # Inicializar Vista
    view = GameView(app)
    
    # Inicializar Controlador
    controller = GameController(view)

    # Guardamos el controlador dentro de 'view' o 'app' para que Python
    # sepa que esta variable ES IMPORTANTE y no la ignore.
    view.controller = controller 
    # Opcional: También puedes hacer app.controller = controller

    app.mainloop()

if __name__ == "__main__":
    main()