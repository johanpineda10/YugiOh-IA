# main.py
import customtkinter as ctk
from view.game_view import GameView
from controller.game_controller import GameController

def main():
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("YugiOh MVC Python")
    app.geometry("1300x800")

    view = GameView(app)
    controller = GameController(view)

    app.mainloop()

if __name__ == "__main__":
    main()
