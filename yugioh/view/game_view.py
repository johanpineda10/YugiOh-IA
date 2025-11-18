# view/game_view.py
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO


class CardSlot:
    def __init__(self, parent, row, col, variable=None, value=None):
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid(row=row, column=col, padx=10)

        self.img_label = ctk.CTkLabel(self.frame, text="")
        self.img_label.pack()
        self.name_label = ctk.CTkLabel(self.frame, text="")
        self.name_label.pack()
        self.atk_label = ctk.CTkLabel(self.frame, text="")
        self.atk_label.pack()
        self.def_label = ctk.CTkLabel(self.frame, text="")
        self.def_label.pack()

        # usar una variable compartida si se provee, para hacer grupos exclusivos
        self.var = variable if variable is not None else ctk.IntVar(value=-1)
        # el valor por defecto del radio es el índice de la columna, pero
        # normalmente pasamos un `value` (0..2) para agrupar por jugador
        radio_value = value if value is not None else col
        self.radio = ctk.CTkRadioButton(parent, variable=self.var, value=radio_value, text="")
        # exponer la variable para que el controlador pueda consultarla
        self.radio_var = self.var
        self.radio.grid(row=row + 1, column=col)
        self.radio.configure(state="disabled")

        self.img_cache = None

    def update(self, card):
        self.name_label.configure(text=card.name)
        self.atk_label.configure(text="ATK: "+str(card.atk))
        self.def_label.configure(text="DEF: "+str(card.defe))

        img_data = requests.get(card.img_url).content
        pil_img = Image.open(BytesIO(img_data)).resize((150, 200))
        self.img_cache = ImageTk.PhotoImage(pil_img)

        self.img_label.configure(image=self.img_cache)
        self.radio.configure(state="normal")

    def disable(self):
        self.radio.configure(state="disabled")


class GameView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # permitir que las filas escalen para mantener el botón abajo
        self.grid_rowconfigure(1, weight=1)
        # la fila 2 contiene los radios/segunda fila de los slots
        self.grid_rowconfigure(2, weight=0)
        # fila 3 será para la barra inferior (botón grande)
        self.grid_rowconfigure(3, weight=0)
        for c in range(6):
            self.grid_columnconfigure(c, weight=1)

        # Combobox
        self.combo = ctk.CTkComboBox(self, values=[])
        self.combo.grid(row=0, column=0)

        self.btnSelect = ctk.CTkButton(self, text="Seleccionar carta")
        self.btnSelect.grid(row=0, column=1)

        self.btnLog = ctk.CTkButton(self, text="LOG")
        self.btnLog.grid(row=0, column=3)

        # Puntajes
        self.lblUserScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblUserScore.grid(row=0, column=4)

        self.lblMachineScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblMachineScore.grid(row=0, column=5)

        # Slots
        # variables compartidas para que solo se pueda seleccionar uno por grupo
        self.user_var = ctk.IntVar(value=-1)
        self.machine_var = ctk.IntVar(value=-1)

        self.user_slots = [CardSlot(self, 1, i, variable=self.user_var, value=i) for i in range(3)]
        self.machine_slots = [CardSlot(self, 1, i + 4, variable=self.machine_var, value=i) for i in range(3)]

        # Barra inferior: botón de pelear grande y centrado
        self.bottom_frame = ctk.CTkFrame(self)
        # colocar en la fila 3 para no tapar los radio buttons (que usan row=2)
        self.bottom_frame.grid(row=3, column=0, columnspan=6, pady=20, sticky="ew")

        self.btnFight = ctk.CTkButton(
            self.bottom_frame,
            text="PELEAR",
            width=700,
            height=80,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            font=("Helvetica", 24, "bold")
        )
        # centrar el botón dentro del frame inferior
        self.btnFight.pack(pady=10)
