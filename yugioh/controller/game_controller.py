# controller/game_controller.py
from tkinter import messagebox
from model.card_model import CardAPI
from model.game_model import GameModel
from tkinter import simpledialog


class GameController:

    def __init__(self, view):
        self.view = view
        self.model = GameModel()

        self.userBattleMode = None
        self.machineBattleMode = None

        self.view.btnFight.configure(command=self.fight)
        self.view.btnAttackUsu.configure(command=self.set_user_attack)
        self.view.btnDefenseUsu.configure(command=self.set_user_defense)
        self.view.btnAttackMaq.configure(command=self.set_machine_attack)
        self.view.btnDefenseMaq.configure(command=self.set_machine_defense)
        self.view.btnConfig.configure(command=self.set_queue)
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
        for i in range(5):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_user_card(i, card)
                self.view.user_slots[i].update(card)
                self.view.user_slots[i].radio.configure(state="normal")
            except Exception:
                pass

        for i in range(5):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_machine_card(i, card)
                self.view.machine_slots[i].update(card)
                self.view.machine_slots[i].radio.configure(state="normal")
            except Exception:
                pass
        
        # Inicializar barras de vida globales
        self.view.update_life_bars(self.model.user_life, self.model.machine_life)


    def load_queue_cards(self):
        # cargar 8 cartas para la cola del usuario (se muestran 4)
        try:
            for i in range(len(self.view.user_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_user_queue(i, card)
                self.view.user_queue_slots[i].update(card)
        except Exception:
            pass

        # cargar 8 cartas para la cola de la maquina (se muestran 4)
        try:
            for i in range(len(self.view.machine_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_machine_queue(i, card)
                self.view.machine_queue_slots[i].update(card)
        except Exception:
            pass

    def set_user_attack(self):
        self.userBattleMode = "attack"
        self.update_mode_buttons()

    def set_user_defense(self):
        self.userBattleMode = "defense"
        self.update_mode_buttons()

    def set_machine_attack(self):
        self.machineBattleMode = "attack"
        self.update_mode_buttons()

    def set_machine_defense(self):
        self.machineBattleMode = "defense"
        self.update_mode_buttons()

    def set_queue(self):
        try:
            parent = self.view if hasattr(self.view, "winfo_toplevel") else None
            size = simpledialog.askinteger(
                "Configurar Cola",
                "Introduce el tamaño de la cola:",
                parent=parent,
                minvalue=1,
                maxvalue=40
            )
            if size is None:
                return
            self.model.config_queues(size=size)
            self.load_queue_cards()
        except Exception:
            messagebox.showwarning("Error", "No se pudo configurar la cola. Introduce un entero válido.")

    def update_mode_buttons(self):
        # Botones del usuario
        if self.userBattleMode == "attack":
            self.view.btnAttackUsu.configure(
                fg_color="#2e7d32",
                border_width=3,
                border_color="#4caf50"
            )
            self.view.btnDefenseUsu.configure(
                fg_color="#1565c0",
                border_width=0
            )
        elif self.userBattleMode == "defense":
            self.view.btnDefenseUsu.configure(
                fg_color="#1976d2",
                border_width=3,
                border_color="#42a5f5"
            )
            self.view.btnAttackUsu.configure(
                fg_color="#1b5e20",
                border_width=0
            )
        
        # Botones de la máquina
        if self.machineBattleMode == "attack":
            self.view.btnAttackMaq.configure(
                fg_color="#2e7d32",
                border_width=3,
                border_color="#4caf50"
            )
            self.view.btnDefenseMaq.configure(
                fg_color="#1565c0",
                border_width=0
            )
        elif self.machineBattleMode == "defense":
            self.view.btnDefenseMaq.configure(
                fg_color="#1976d2",
                border_width=3,
                border_color="#42a5f5"
            )
            self.view.btnAttackMaq.configure(
                fg_color="#1b5e20",
                border_width=0
            )

    def fight(self):
        # Detectar modo del usuario basado en el estado del botón
        user_mode = None
        if self.view.btnAttackUsu.cget("border_width") == 3:
            user_mode = "atk"
        elif self.view.btnDefenseUsu.cget("border_width") == 3:
            user_mode = "def"
        
        # Detectar modo de la máquina basado en el estado del botón
        machine_mode = None
        if self.view.btnAttackMaq.cget("border_width") == 3:
            machine_mode = "atk"
        elif self.view.btnDefenseMaq.cget("border_width") == 3:
            machine_mode = "def"
        
        if user_mode is None or machine_mode is None:
            messagebox.showwarning("Error", "Selecciona un modo de batalla para ambos jugadores")
            return
        
        u_slot = self.get_selected_slot(self.view.user_slots)
        m_slot = self.get_selected_slot(self.view.machine_slots)

        if u_slot is None or m_slot is None:
            messagebox.showwarning("Error", "Selecciona cartas válidas")
            return

        u = self.model.user_cards[u_slot]
        m = self.model.machine_cards[m_slot]

        result, damage_user, damage_machine = self.model.fight_round(u, m, user_mode, machine_mode, u_slot, m_slot)

        # Actualizar barras de vida globales en la vista
        self.view.update_life_bars(self.model.user_life, self.model.machine_life)

        if result == "user_loses":
            msg = f"¡Carta del usuario destruida! Daño: {damage_user}"
        elif result == "machine_loses":
            msg = f"¡Carta de la máquina destruida! Daño: {damage_machine}"
        elif result == "both_lose":
            msg = f"¡Ambas cartas destruidas! Usuario: {damage_user} | Máquina: {damage_machine}"
        else:
            msg = "Empate - No hay ganador"

        try:
            messagebox.showinfo("Ronda", f"Resultado: {msg}\nVida Usuario: {self.model.user_life}\nVida Máquina: {self.model.machine_life}")
        except Exception:
            pass

        # Reemplazar cartas perdedoras con cartas de la cola
        if result == "machine_loses":
            try:
                self.model.machine_cards[m_slot] = None
                self._dequeue_machine_to_slot(m_slot)
            except Exception:
                pass

        elif result == "user_loses":
            try:
                self.model.user_cards[u_slot] = None
                self._dequeue_user_to_slot(u_slot)
            except Exception:
                pass
                
        elif result == "both_lose":
            try:
                self.model.user_cards[u_slot] = None
                self._dequeue_user_to_slot(u_slot)
            except Exception:
                pass
            try:
                self.model.machine_cards[m_slot] = None
                self._dequeue_machine_to_slot(m_slot)
                self._dequeue_machine_to_slot(m_slot)
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
