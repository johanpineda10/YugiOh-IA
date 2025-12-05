# controller/game_controller.py
from tkinter import messagebox
from model.card_model import CardAPI
from model.game_model import GameModel


class GameController:

    def __init__(self, view):
        self.view = view
        self.model = GameModel()

        # conectar botones
        self.view.btnFight.configure(command=self.fight)
        self.view.btnLog.configure(command=self.show_log)

        # cargar lista inicial
        # primero cargar cartas en cola (usuario y máquina)
        self.load_queue_cards()

        # cargar las manos iniciales (usuario y máquina)
        self.load_initial_hands()

        # indicar que el usuario ya tiene 3 cartas (para evitar selección adicional)
        self.user_slot_index = 3

    # -------------------------------
    # Cargar cartas máquina
    # -------------------------------
    def load_machine_cards(self):
        for i in range(3):
            card = CardAPI.get_random_monster()
            self.model.add_machine_card(i, card)
            self.view.machine_slots[i].update(card)

    def load_initial_hands(self):
        """Carga 3 cartas aleatorias tanto para el usuario como para la máquina al iniciar."""
        # usuario
        for i in range(3):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_user_card(i, card)
                self.view.user_slots[i].update(card)
            except Exception:
                pass

        # máquina
        for i in range(3):
            try:
                card = CardAPI.get_random_monster()
                self.model.add_machine_card(i, card)
                self.view.machine_slots[i].update(card)
            except Exception:
                pass

        # desactivar botón de seleccionar porque las manos ya están llenas
        try:
            self.view.btnSelect.configure(state="disabled")
        except Exception:
            pass

    # -------------------------------
    # Cargar cartas en cola (espera)
    # -------------------------------
    def load_queue_cards(self):
        # cargar 2 cartas para la cola del usuario
        try:
            for i in range(len(self.view.user_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_user_queue(i, card)
                self.view.user_queue_slots[i].update(card)
        except Exception:
            pass

        # cargar 2 cartas para la cola de la máquina
        try:
            for i in range(len(self.view.machine_queue_slots)):
                card = CardAPI.get_random_monster()
                self.model.set_machine_queue(i, card)
                self.view.machine_queue_slots[i].update(card)
        except Exception:
            pass

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

        # si hay un ganador de la ronda, quitar la carta derrotada y reemplazarla
        if result == "user":
            # la máquina perdió: sacar la carta de la máquina en m_slot
            try:
                self.model.machine_cards[m_slot] = None
                # actualizar vista: si hay carta en cola, moverla; si no, limpiar el slot
                self._dequeue_machine_to_slot(m_slot)
            except Exception:
                pass

        elif result == "machine":
            # el usuario perdió: sacar la carta de usuario en u_slot
            try:
                self.model.user_cards[u_slot] = None
                self._dequeue_user_to_slot(u_slot)
            except Exception:
                pass

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
    # Cola -> Tablero helpers
    # -------------------------------
    def _update_queue_views(self):
        # refrescar vista de cola de usuario
        try:
            for i, slot in enumerate(self.view.user_queue_slots):
                card = self.model.user_queue[i]
                if card:
                    slot.update(card)
                else:
                    # limpiar visual
                    slot.name_label.configure(text="")
                    slot.atk_label.configure(text="")
                    slot.def_label.configure(text="")
                    slot.img_label.configure(image="")
            
        except Exception:
            pass

        # refrescar vista de cola de máquina
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
            # limpiar slot si no hay carta
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

        # recargar cartas en cola para la nueva partida
        try:
            self.load_queue_cards()
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
