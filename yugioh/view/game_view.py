# view/game_view.py
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO


class CardSlot:
    def __init__(self, parent, row, col, variable=None, value=None, show_radio=True, img_size=(150, 200), show_labels=True, show_life_bar=False):
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid(row=row, column=col, padx=5, pady=2)
        self.img_size = img_size
        self.card_life = 0
        self.max_life = 3000  # Valor por defecto

        self.img_label = ctk.CTkLabel(self.frame, text="")
        self.img_label.pack()
        
        # Barra de vida de la carta (opcional)
        if show_life_bar:
            self.life_bar = ctk.CTkProgressBar(self.frame, width=img_size[0]-10, height=8, progress_color="#2ecc71")
            self.life_bar.set(1.0)
            self.life_bar.pack(pady=(2, 0))
            self.life_label = ctk.CTkLabel(self.frame, text="", font=("Helvetica", 8))
            self.life_label.pack()
        else:
            self.life_bar = None
            self.life_label = None
        
        self.name_label = ctk.CTkLabel(self.frame, text="") if show_labels else None
        if self.name_label:
            self.name_label.pack()
        
        self.atk_label = ctk.CTkLabel(self.frame, text="") if show_labels else None
        if self.atk_label:
            self.atk_label.pack()
        
        self.def_label = ctk.CTkLabel(self.frame, text="") if show_labels else None
        if self.def_label:
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

    def update(self, card, card_life=None):
        if self.name_label:
            self.name_label.configure(text=card.name)
        if self.atk_label:
            self.atk_label.configure(text="ATK: "+str(card.atk))
        if self.def_label:
            self.def_label.configure(text="DEF: "+str(card.defe))

        img_data = requests.get(card.img_url).content
        pil_img = Image.open(BytesIO(img_data)).resize(self.img_size)
        self.img_cache = ImageTk.PhotoImage(pil_img)

        self.img_label.configure(image=self.img_cache)
        if self.radio:
            self.radio.configure(state="normal")
        
        # Actualizar barra de vida si existe
        if card_life is not None:
            self.update_life(card_life)

    def update_life(self, current_life, max_life=3000):
        """Actualiza la barra de vida de la carta."""
        if not self.life_bar:
            return
        
        self.card_life = current_life
        self.max_life = max_life
        
        life_percent = max(0, current_life / max_life)
        self.life_bar.set(life_percent)
        
        # Cambiar color según el porcentaje
        if life_percent > 0.5:
            self.life_bar.configure(progress_color="#2ecc71")  # Verde
        elif life_percent > 0.25:
            self.life_bar.configure(progress_color="#f39c12")  # Naranja
        else:
            self.life_bar.configure(progress_color="#e74c3c")  # Rojo
        
        if self.life_label:
            self.life_label.configure(text=f"{current_life}/{max_life}")

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
        # ahora usamos 13 columnas: 0=cola izq, 1-5=usuario, 6=separador, 7-11=máquina, 12=cola der
        for c in range(13):
            self.grid_columnconfigure(c, weight=1)

        try:
            self.lblUserTitle = ctk.CTkLabel(self, text="YUGIOH USUARIO", font=("Helvetica", 16, "bold"))
            self.lblUserTitle.grid(row=0, column=1, columnspan=5)
            self.lblMachineTitle = ctk.CTkLabel(self, text="YUGIOH MAQUINA", font=("Helvetica", 16, "bold"))
            self.lblMachineTitle.grid(row=0, column=7, columnspan=5)
        except Exception:
            pass

        # Barras de vida globales en fila 1
        user_bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        user_bar_frame.grid(row=1, column=1, columnspan=5, sticky="ew", padx=5, pady=2)
        
        self.user_life_bar = ctk.CTkProgressBar(user_bar_frame, width=360, height=20, progress_color="#2ecc71")
        self.user_life_bar.set(1.0)
        self.user_life_bar.pack()
        
        self.user_life_label = ctk.CTkLabel(user_bar_frame, text="8000/8000", font=("Helvetica", 14, "bold"))
        self.user_life_label.pack()
        
        machine_bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        machine_bar_frame.grid(row=1, column=7, columnspan=5, sticky="ew", padx=5, pady=2)
        
        self.machine_life_bar = ctk.CTkProgressBar(machine_bar_frame, width=360, height=20, progress_color="#2ecc71")
        self.machine_life_bar.set(1.0)
        self.machine_life_bar.pack()
        
        self.machine_life_label = ctk.CTkLabel(machine_bar_frame, text="8000/8000", font=("Helvetica", 14, "bold"))
        self.machine_life_label.pack()

        self.btnLog = ctk.CTkButton(self, text="LOG")
        self.btnLog.grid(row=2, column=1)

        # Puntajes
        self.lblUserScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblUserScore.grid(row=2, column=2)

        # mover puntaje máquina al lado derecho
        self.lblMachineScore = ctk.CTkLabel(self, text="Puntaje: 0")
        self.lblMachineScore.grid(row=2, column=6)

        # variables compartidas para que solo se pueda seleccionar uno por grupo
        self.user_var = ctk.IntVar(value=-1)
        self.machine_var = ctk.IntVar(value=-1)

        # Cinco slots en la misma fila, cartas más pequeñas para que quepan
        small_size = (110, 150)
        self.user_slots = [
            CardSlot(self, 3, 1, variable=self.user_var, value=0, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 2, variable=self.user_var, value=1, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 3, variable=self.user_var, value=2, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 4, variable=self.user_var, value=3, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 5, variable=self.user_var, value=4, show_life_bar=False, img_size=small_size)
        ]
        
        self.machine_slots = [
            CardSlot(self, 3, 7, variable=self.machine_var, value=0, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 8, variable=self.machine_var, value=1, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 9, variable=self.machine_var, value=2, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 10, variable=self.machine_var, value=3, show_life_bar=False, img_size=small_size),
            CardSlot(self, 3, 11, variable=self.machine_var, value=4, show_life_bar=False, img_size=small_size)
        ]

        # separador vertical entre usuario y máquina
        try:
            self.sep = ctk.CTkFrame(self, width=2, fg_color="#5a5a5a")
            self.sep.grid(row=3, column=6, rowspan=3, sticky="ns", pady=10)
        except Exception:
            pass

        self.grid_rowconfigure(7, weight=0)

        # colocar las colas en los laterales - 4 cartas visibles por lado (más pequeñas)
        self.user_queue_slots = [CardSlot(self, 3 + i, 0, show_radio=False, img_size=(90, 130), show_labels=False) for i in range(4)]
        self.machine_queue_slots = [CardSlot(self, 3 + i, 12, show_radio=False, img_size=(90, 130), show_labels=False) for i in range(4)]

        try:
            self.lblUserQueue = ctk.CTkLabel(self, text="Cola usuario")
            self.lblUserQueue.grid(row=2, column=0, sticky="n", padx=5, pady=5)
            self.lblMachineQueue = ctk.CTkLabel(self, text="Cola máquina")
            self.lblMachineQueue.grid(row=2, column=12, sticky="n", padx=5, pady=5)
        except Exception:
            pass

        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=7, column=0, columnspan=13, pady=0, sticky="nsew")

        self.mode_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.mode_frame.pack(pady=(10, 5))

        self.btnAttackUsu = ctk.CTkButton(
            self.mode_frame,
            text="MODO ATAQUE",
            width=250,
            height=45,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Helvetica", 14, "bold")
        )
        self.btnAttackUsu.pack(side="right", padx=10)

        self.btnDefenseUsu = ctk.CTkButton(
            self.mode_frame,
            text="MODO DEFENSA",
            width=250,
            height=45,
            fg_color="#1976d2",
            hover_color="#0d47a1",
            font=("Helvetica", 14, "bold")
        )
        self.btnDefenseUsu.pack(side="left", padx=10)

        self.btnAttackMaq = ctk.CTkButton(
            self.mode_frame,
            text="MODO ATAQUE",
            width=250,
            height=45,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Helvetica", 14, "bold")
        )
        self.btnAttackMaq.pack(side="left", padx=10)

        self.btnDefenseMaq = ctk.CTkButton(
            self.mode_frame,
            text="MODO DEFENSA",
            width=250,
            height=45,
            fg_color="#1976d2",
            hover_color="#0d47a1",
            font=("Helvetica", 14, "bold")
        )
        self.btnDefenseMaq.pack(side="left", padx=10)

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

        self.btnConfig = ctk.CTkButton(
            self.mode_frame,
            text="CONFIGURAR COLAS",
            width=250,
            height=45,
            fg_color="#15a2bb",
            hover_color="#0a6066",
            font=("Helvetica", 14, "bold")
        )
        self.btnConfig.pack(side="right", padx=10)

    def update_life_bars(self, user_life, machine_life, max_life=8000):
        """Actualiza las barras de vida globales de usuario y máquina."""
        # Usuario
        user_percent = max(0, user_life / max_life)
        self.user_life_bar.set(user_percent)
        
        if user_percent > 0.5:
            self.user_life_bar.configure(progress_color="#2ecc71")  # Verde
        elif user_percent > 0.25:
            self.user_life_bar.configure(progress_color="#f39c12")  # Naranja
        else:
            self.user_life_bar.configure(progress_color="#e74c3c")  # Rojo
        
        self.user_life_label.configure(text=f"{user_life}/{max_life}")
        
        # Máquina
        machine_percent = max(0, machine_life / max_life)
        self.machine_life_bar.set(machine_percent)
        
        if machine_percent > 0.5:
            self.machine_life_bar.configure(progress_color="#2ecc71")  # Verde
        elif machine_percent > 0.25:
            self.machine_life_bar.configure(progress_color="#f39c12")  # Naranja
        else:
            self.machine_life_bar.configure(progress_color="#e74c3c")  # Rojo
        
        self.machine_life_label.configure(text=f"{machine_life}/{max_life}")