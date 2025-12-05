# view/game_view.py
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO


class CardSlot:
    def __init__(self, parent, row, col, variable=None, value=None, show_radio=True):
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

        self.var = variable if variable is not None else ctk.IntVar(value=-1)
        radio_value = value if value is not None else col
        self.radio = None
        self.radio_var = None

        if show_radio:
            self.radio = ctk.CTkRadioButton(self.frame, variable=self.var, value=radio_value, text="")
            # exponer la variable para que el controlador pueda consultarla
            self.radio_var = self.var
            # ubicar el radio dentro del frame, debajo de las labels
            self.radio.pack(pady=(6, 0))
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
        if self.radio:
            self.radio.configure(state="normal")

    def disable(self):
        try:
            if self.radio:
                self.radio.configure(state="disabled")
        except Exception:
            pass


class GameView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(2, weight=1)
        # la fila 3 contiene los radios/segunda fila de los slots
        self.grid_rowconfigure(3, weight=0)
        # fila 4 será para etiquetas/colas intermedias
        self.grid_rowconfigure(4, weight=0)
        # ahora usamos 9 columnas: 0=cola izq, 1-3=usuario, 4=separador, 5-7=máquina, 8=cola der
        for c in range(9):
            self.grid_columnconfigure(c, weight=1)

        try:
            self.lblUserTitle = ctk.CTkLabel(self, text="YUGIOH USUARIO", font=("Helvetica", 16, "bold"))
            self.lblUserTitle.grid(row=0, column=1, columnspan=3)
            self.lblMachineTitle = ctk.CTkLabel(self, text="YUGIOH MAQUINA", font=("Helvetica", 16, "bold"))
            self.lblMachineTitle.grid(row=0, column=5, columnspan=3)
        except Exception:
            pass

        self.btnLog = ctk.CTkButton(self, text="LOG")
        self.btnLog.grid(row=1, column=1)

        # Puntajes
        self.lblUserScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblUserScore.grid(row=1, column=2)

        # mover puntaje máquina al lado derecho
        self.lblMachineScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblMachineScore.grid(row=1, column=6)

        # variables compartidas para que solo se pueda seleccionar uno por grupo
        self.user_var = ctk.IntVar(value=-1)
        self.machine_var = ctk.IntVar(value=-1)

        # mover slots centrales
        self.user_slots = [CardSlot(self, 2, i + 1, variable=self.user_var, value=i) for i in range(3)]
        self.machine_slots = [CardSlot(self, 2, i + 5, variable=self.machine_var, value=i) for i in range(3)]

        # separador vertical entre usuario y máquina
        try:
            self.sep = ctk.CTkFrame(self, width=2, fg_color="#5a5a5a")
            self.sep.grid(row=2, column=4, rowspan=2, sticky="ns", pady=10)
        except Exception:
            pass

        self.grid_rowconfigure(5, weight=0)

        # colocar las colas en los laterales
        self.user_queue_slots = [CardSlot(self, 2 + i, 0, show_radio=False) for i in range(2)]
        self.machine_queue_slots = [CardSlot(self, 2 + i, 8, show_radio=False) for i in range(2)]

        try:
            self.lblUserQueue = ctk.CTkLabel(self, text="Cola usuario")
            self.lblUserQueue.grid(row=1, column=0, sticky="n", padx=5, pady=5)
            self.lblMachineQueue = ctk.CTkLabel(self, text="Cola máquina")
            self.lblMachineQueue.grid(row=1, column=8, sticky="n", padx=5, pady=5)
        except Exception:
            pass

        self.grid_rowconfigure(7, weight=1)
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=7, column=0, columnspan=9, pady=0, sticky="nsew")

        self.mode_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.mode_frame.pack(pady=(10, 5))

        self.btnAttack = ctk.CTkButton(
            self.mode_frame,
            text="MODO ATAQUE",
            width=250,
            height=45,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Helvetica", 14, "bold")
        )
        self.btnAttack.pack(side="left", padx=10)

        self.btnDefense = ctk.CTkButton(
            self.mode_frame,
            text="MODO DEFENSA",
            width=250,
            height=45,
            fg_color="#1976d2",
            hover_color="#0d47a1",
            font=("Helvetica", 14, "bold")
        )
        self.btnDefense.pack(side="left", padx=10)

        self.btnFight = ctk.CTkButton(
            self.bottom_frame,
            text="PELEAR",
            width=700,
            height=80,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            font=("Helvetica", 24, "bold")
        )
        self.btnFight.pack(pady=(5, 10))