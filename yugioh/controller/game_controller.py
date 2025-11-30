# controller/game_controller.py
from tkinter import messagebox
from model.card_model import CardAPI
from model.game_model import GameModel


class GameController:

    def __init__(self, view):
        self.view = view
        self.model = GameModel()

        self.battleMode = None

        self.view.btnFight.configure(command=self.fight)
        self.view.btnAttack.configure(command=self.set_attack)
        self.view.btnDefense.configure(command=self.set_defense)
        self.view.btnLog.configure(command=self.show_log)

        self.load_queue_cards()

        self.load_initial_hands()

        self.user_slot_index = 3

        self.update_mode_buttons()

    def load_machine_cards(self):
        for i in range(3):
            card = CardAPI.get_random_monster()
            self.model.add_machine_card(i, card)
            self.view.machine_slots[i].update(card)

    def load_initial_hands(self):
        for i in range(3):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_user_card(i, card)
                self.view.user_slots[i].update(card)
                self.view.user_slots[i].radio.configure(state="normal")  
            except Exception:
                pass

        for i in range(3):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_machine_card(i, card)
                self.view.machine_slots[i].update(card)
                self.view.machine_slots[i].radio.configure(state="normal") 
            except Exception:
                pass


    def load_queue_cards(self):
        # cargar 2 cartas para la cola del usuario
        try:
            for i in range(len(self.view.user_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_user_queue(i, card)
                self.view.user_queue_slots[i].update(card)
        except Exception:
            pass

        # cargar 2 cartas para la cola de la maquina
        try:
            for i in range(len(self.view.machine_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_machine_queue(i, card)
                self.view.machine_queue_slots[i].update(card)
        except Exception:
            pass

    def set_attack(self):
        self.battleMode = "attack"
        self.update_mode_buttons()

    def set_defense(self):
        self.battleMode = "defense"
        self.update_mode_buttons()

    def update_mode_buttons(self):
        if self.battleMode == "attack":
            self.view.btnAttack.configure(
                fg_color="#2e7d32",
                border_width=3,
                border_color="#4caf50"
            )
            self.view.btnDefense.configure(
                fg_color="#1565c0",
                border_width=0
            )
        else:
            self.view.btnDefense.configure(
                fg_color="#1976d2",
                border_width=3,
                border_color="#42a5f5"
            )
            self.view.btnAttack.configure(
                fg_color="#1b5e20",
                border_width=0
            )

    def fight(self):
        if self.battleMode is None:
            messagebox.showwarning("Error", "Selecciona un modo de batalla")
            return
        
        u_slot = self.get_selected_slot(self.view.user_slots)
        m_slot = self.get_selected_slot(self.view.machine_slots)

        if u_slot is None or m_slot is None:
            messagebox.showwarning("Error", "Selecciona cartas válidas")
            return

        u = self.model.user_cards[u_slot]
        m = self.model.machine_cards[m_slot]

        result = self.model.fight_round(u, m)

        try:
            messagebox.showinfo("Ronda", f"Resultado: {result}\nUsuario: slot {u_slot} - Def {u.defe}\nMáquina: slot {m_slot} - Def {m.defe}")
        except Exception:
            pass

        self.view.user_slots[u_slot].def_label.configure(text=str(u.defe))
        self.view.machine_slots[m_slot].def_label.configure(text=str(m.defe))

        if result == "user":
            # si la máquina perdió: sacar la carta de la máquina en m_slot
            try:
                self.model.machine_cards[m_slot] = None
                self._dequeue_machine_to_slot(m_slot)
            except Exception:
                pass

        elif result == "machine":
            # si el usuario perdió: sacar la carta de usuario en u_slot
            try:
                self.model.user_cards[u_slot] = None
                self._dequeue_user_to_slot(u_slot)
            except Exception:
                pass

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

        first = slot_list[0]
        var = getattr(first, "radio_var", None)
        if var is not None:
            val = var.get()
            try:
                val_int = int(val)
            except Exception:
                return None

            if val_int < 0:
                return None
            
            if 0 <= val_int < len(slot_list):
                return val_int
            return None

        for i, slot in enumerate(slot_list):
            try:
                a = slot.radio.get()
                b = slot.radio.cget("value")
                try:
                    if int(a) == int(b):
                        return i
                except Exception:
                    if a == b:
                        return i
            except Exception:
                continue
        return None

    def _update_queue_views(self):
        try:
            for i, slot in enumerate(self.view.user_queue_slots):
                card = self.model.user_queue[i]
                if card:
                    slot.update(card)
                else:
                    slot.name_label.configure(text="")
                    slot.atk_label.configure(text="")
                    slot.def_label.configure(text="")
                    slot.img_label.configure(image="")
            
        except Exception:
            pass

        try:
            for i, slot in enumerate(self.view.machine_queue_slots):
                card = self.model.machine_queue[i]
                if card:
                    slot.update(card)
                else:
                    slot.name_label.configure(text="")
                    slot.atk_label.configure(text="")
                    slot.def_label.configure(text="")
                    slot.img_label.configure(image="")
        except Exception:
            pass

    def _dequeue_user_to_slot(self, target_slot):
        # sacar primera carta de la cola de usuario
        card = self.model.dequeue_user()
        if card:
            self.model.add_user_card(target_slot, card)
            self.view.user_slots[target_slot].update(card)
        else:
            try:
                s = self.view.user_slots[target_slot]
                s.name_label.configure(text="")
                s.atk_label.configure(text="")
                s.def_label.configure(text="")
                s.img_label.configure(image="")
                s.radio.configure(state="disabled")
            except Exception:
                pass

        # refrescar la vista de cola
        self._update_queue_views()

    def _dequeue_machine_to_slot(self, target_slot):
        card = self.model.dequeue_machine()
        if card:
            self.model.add_machine_card(target_slot, card)
            self.view.machine_slots[target_slot].update(card)
        else:
            try:
                s = self.view.machine_slots[target_slot]
                s.name_label.configure(text="")
                s.atk_label.configure(text="")
                s.def_label.configure(text="")
                s.img_label.configure(image="")
                s.radio.configure(state="disabled")
            except Exception:
                pass

        self._update_queue_views()


    def new_match(self):
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

        try:
            self.load_queue_cards()
        except Exception:
            pass

        messagebox.showinfo("Partida", "Partida reiniciada. Selecciona nuevas cartas.")
        
    def show_log(self):
        m = self.model
        msg = (
            f"Puntaje final usuario: {m.final_user_score}\n"
            f"Puntaje final máquina: {m.final_machine_score}\n"
        )
        messagebox.showinfo("Log", msg)
