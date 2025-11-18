# controller/game_controller.py
from tkinter import messagebox
from model.card_model import CardAPI
from model.game_model import GameModel


class GameController:

    def __init__(self, view):
        self.view = view
        self.model = GameModel()

        # conectar botones
        self.view.btnSelect.configure(command=self.select_card)
        self.view.btnFight.configure(command=self.fight)
        self.view.btnLog.configure(command=self.show_log)

        # cargar lista inicial
        self.load_card_list()

        self.user_slot_index = 0

    # -------------------------------
    # API → Combobox
    # -------------------------------
    def load_card_list(self):
        names = CardAPI.get_cards_list()
        self.view.combo.configure(values=names)
        if names:
            self.view.combo.set(names[0])

    # -------------------------------
    # Seleccionar carta usuario
    # -------------------------------
    def select_card(self):
        # evitar seleccionar más de 3
        if self.user_slot_index >= 3:
            messagebox.showinfo("Info", "Ya seleccionaste 3 cartas.")
            return

        name = self.view.combo.get()
        card = CardAPI.get_card_by_name(name)

        if card:
            self.model.add_user_card(self.user_slot_index, card)
            self.view.user_slots[self.user_slot_index].update(card)
            self.user_slot_index += 1

            # Si justo seleccionó la tercera carta, cargar las cartas de la máquina
            if self.user_slot_index == 3:
                messagebox.showinfo("Info", "Se seleccionaron 3 cartas. Cargando máquina…")
                self.load_machine_cards()

    # -------------------------------
    # Cargar cartas máquina
    # -------------------------------
    def load_machine_cards(self):
        for i in range(3):
            card = CardAPI.get_random_monster()
            self.model.add_machine_card(i, card)
            self.view.machine_slots[i].update(card)

    # -------------------------------
    # PELEAR
    # -------------------------------
    def fight(self):
        u_slot = self.get_selected_slot(self.view.user_slots)
        m_slot = self.get_selected_slot(self.view.machine_slots)

        if u_slot is None or m_slot is None:
            messagebox.showwarning("Error", "Selecciona cartas válidas")
            return

        u = self.model.user_cards[u_slot]
        m = self.model.machine_cards[m_slot]

        result = self.model.fight_round(u, m)

        # Mostrar resultado de la ronda para feedback inmediato
        try:
            messagebox.showinfo("Ronda", f"Resultado: {result}\nUsuario: slot {u_slot} - Def {u.defe}\nMáquina: slot {m_slot} - Def {m.defe}")
        except Exception:
            pass

        # actualizar defensas en pantalla
        self.view.user_slots[u_slot].def_label.configure(text=str(u.defe))
        self.view.machine_slots[m_slot].def_label.configure(text=str(m.defe))

        # desactivar si corresponde
        if result in ["user", "machine"]:
            self.view.user_slots[u_slot].disable()
            self.view.machine_slots[m_slot].disable()

        # actualizar puntajes
        self.view.lblUserScore.configure(text=f"Puntaje: {self.model.user_score}")
        self.view.lblMachineScore.configure(text=f"Puntaje: {self.model.machine_score}")

        winner = self.model.check_winner()
        if winner == "user":
            messagebox.showinfo("Partida", "Usuario gana partida!")
            self.new_match()
        elif winner == "machine":
            messagebox.showinfo("Partida", "Máquina gana partida!")
            self.new_match()

    def get_selected_slot(self, slot_list):
        """Devuelve índice seleccionado o None"""
        if not slot_list:
            return None

        # si los slots exponen una variable compartida (radio_var), usarla
        first = slot_list[0]
        var = getattr(first, "radio_var", None)
        if var is not None:
            val = var.get()
            try:
                # intentar convertir a int por seguridad (puede venir como str)
                val_int = int(val)
            except Exception:
                return None

            if val_int < 0:
                return None
            # validar rango
            if 0 <= val_int < len(slot_list):
                return val_int
            return None

        # fallback: comprobar radios individuales (compatibilidad)
        for i, slot in enumerate(slot_list):
            try:
                a = slot.radio.get()
                b = slot.radio.cget("value")
                # comparar como enteros si es posible
                try:
                    if int(a) == int(b):
                        return i
                except Exception:
                    if a == b:
                        return i
            except Exception:
                continue
        return None

    # -------------------------------
    # Nueva partida
    # -------------------------------
    def new_match(self):
        # resetear modelo
        self.model.reset()

        # limpiar vista: scores y slots
        self.view.lblUserScore.configure(text=f"Puntaje: {self.model.user_score}")
        self.view.lblMachineScore.configure(text=f"Puntaje: {self.model.machine_score}")

        # limpiar slots de usuario
        for slot in self.view.user_slots:
            try:
                slot.name_label.configure(text="")
                slot.atk_label.configure(text="")
                slot.def_label.configure(text="")
                slot.img_label.configure(image="")
                slot.radio.configure(state="disabled")
            except Exception:
                pass

        # limpiar slots de máquina
        for slot in self.view.machine_slots:
            try:
                slot.name_label.configure(text="")
                slot.atk_label.configure(text="")
                slot.def_label.configure(text="")
                slot.img_label.configure(image="")
                slot.radio.configure(state="disabled")
            except Exception:
                pass

        # reset índices y variables de selección
        self.user_slot_index = 0
        try:
            # si existen variables compartidas en la vista
            if hasattr(self.view, 'user_var'):
                self.view.user_var.set(-1)
            if hasattr(self.view, 'machine_var'):
                self.view.machine_var.set(-1)
        except Exception:
            pass

        messagebox.showinfo("Partida", "Partida reiniciada. Selecciona nuevas cartas.")

    # -------------------------------
    # LOG
    # -------------------------------
    def show_log(self):
        m = self.model
        msg = (
            f"Puntaje final usuario: {m.final_user_score}\n"
            f"Puntaje final máquina: {m.final_machine_score}\n"
        )
        messagebox.showinfo("Log", msg)
