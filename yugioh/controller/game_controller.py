import sys
import os
from tkinter import messagebox, simpledialog

# Aseguramos que Python encuentre las carpetas correctas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.card_model import CardAPI
from model.game_model import GameModel
from .ai_minimax import MinimaxAI 

class GameController:

    def __init__(self, view):
        self.view = view
        self.model = GameModel()
        # IA Nivel 3 para que piense bien sus jugadas
        self.ai = MinimaxAI(max_depth=3)

        self.userBattleMode = None
        self.machineBattleMode = None

        # Conectar botones
        self.view.btnFight.configure(command=self.fight)
        self.view.btnAttackUsu.configure(command=self.set_user_attack)
        self.view.btnDefenseUsu.configure(command=self.set_user_defense)
        self.view.btnConfig.configure(command=self.set_queue)
        self.view.btnLog.configure(command=self.show_log)

        self.start_new_game()

    def start_new_game(self):
        self.model.reset()
        self.load_queue_cards()
        self.load_initial_hands()
        
        self.userBattleMode = None
        self.machineBattleMode = None
        self.view.user_var.set(-1)
        self.view.machine_var.set(-1)
        
        self.update_mode_buttons()
        self.view.update_life_bars(self.model.user_life, self.model.machine_life)

    def load_initial_hands(self):
        """Carga las manos iniciales."""
        # Usuario
        for i in range(5):
            card = CardAPI.get_random_monster()
            if card:
                self.model.add_user_card(i, card)
                current_life = getattr(card, 'life', 3000) 
                self.view.user_slots[i].update(card, card_life=current_life)
                if self.view.user_slots[i].radio:
                    self.view.user_slots[i].radio.configure(state="normal")

        # Máquina
        for i in range(5):
            card = CardAPI.get_random_monster()
            if card:
                self.model.add_machine_card(i, card)
                current_life = getattr(card, 'life', 3000)
                self.view.machine_slots[i].update(card, card_life=current_life)

    def load_queue_cards(self):
        """Llena las colas completamente."""
        # Cola Usuario
        for i in range(len(self.model.user_queue)):
            card = CardAPI.get_random_monster()
            if card:
                self.model.set_user_queue(i, card)

        # Cola Máquina
        for i in range(len(self.model.machine_queue)):
            card = CardAPI.get_random_monster()
            if card:
                self.model.set_machine_queue(i, card)

        self._update_queue_views()

    def set_user_attack(self):
        self.userBattleMode = "attack"
        self.update_mode_buttons()

    def set_user_defense(self):
        self.userBattleMode = "defense"
        self.update_mode_buttons()

    def update_mode_buttons(self):
        if self.userBattleMode == "attack":
            self.view.btnAttackUsu.configure(fg_color="#2e7d32", border_width=3, border_color="#4caf50")
            self.view.btnDefenseUsu.configure(fg_color="#1565c0", border_width=0)
        elif self.userBattleMode == "defense":
            self.view.btnDefenseUsu.configure(fg_color="#1976d2", border_width=3, border_color="#42a5f5")
            self.view.btnAttackUsu.configure(fg_color="#1b5e20", border_width=0)
        else:
            self.view.btnAttackUsu.configure(border_width=0)
            self.view.btnDefenseUsu.configure(border_width=0)

    def fight(self):
        # 1. Validaciones
        u_slot = self.view.user_var.get()
        if u_slot == -1:
            messagebox.showwarning("Alerta", "Selecciona tu carta.")
            return
        
        if not self.userBattleMode:
            messagebox.showwarning("Alerta", "Selecciona tu MODO (Ataque/Defensa).")
            return

        u_card = self.model.user_cards[u_slot]
        if not u_card:
            messagebox.showerror("Error", "Error: Carta vacía o ya jugada.")
            return

        # 2. IA Decide en base a TU carta (Reactiva)
        print(f"IA analizando contra tu carta: {u_card.name} (ATK {u_card.atk}/DEF {u_card.defe})")
        
        # Le pasamos tu carta y tu modo a la IA para que elija su mejor counter
        ai_move = self.ai.get_best_move(self.model, u_card, self.userBattleMode)
        
        if ai_move:
            m_slot = ai_move.get('index', 0)
            self.machineBattleMode = ai_move.get('mode', 'attack')
            # No marcamos visualmente para no confundir (sin radio buttons)
        else:
            # Fallback por si la IA no tiene cartas
            m_slot = 0
            self.machineBattleMode = "defense"

        m_card = self.model.machine_cards[m_slot]
        if not m_card:
            return

        # 3. Pelear
        result, dmg_u, dmg_m = self.model.fight_round(
            u_card, m_card, self.userBattleMode, self.machineBattleMode, u_slot, m_slot
        )

        # 4. Actualizar interfaz
        self.view.update_life_bars(self.model.user_life, self.model.machine_life)
        self.view.lblUserScore.configure(text=f"Puntaje: {self.model.user_score}")
        self.view.lblMachineScore.configure(text=f"Puntaje: {self.model.machine_score}")

        modes_txt = f"Tú: {self.userBattleMode.upper()} vs IA: {self.machineBattleMode.upper()}"
        
        if result == "user_loses":
            msg = f"{modes_txt}\n\n¡Tu carta fue destruida!\nDaño recibido: {dmg_u}"
        elif result == "machine_loses":
            msg = f"{modes_txt}\n\n¡Carta IA destruida!\nDaño infligido: {dmg_m}"
        elif result == "both_lose":
            msg = f"{modes_txt}\n\n¡Ambas cartas destruidas!"
        else:
            msg = f"{modes_txt}\n\nEmpate/Defensa. Daño User: {dmg_u} | Daño IA: {dmg_m}"
        
        messagebox.showinfo("Resultado", msg)

        # 5. Reemplazar cartas perdidas y RELLENAR MAZO
        if result == "machine_loses":
            self._handle_card_loss(m_slot, is_user=False)
        elif result == "user_loses":
            self._handle_card_loss(u_slot, is_user=True)
        elif result == "both_lose":
            self._handle_card_loss(u_slot, is_user=True)
            self._handle_card_loss(m_slot, is_user=False)

        # Resetear
        self.userBattleMode = None
        self.machineBattleMode = None
        self.update_mode_buttons()
        self.view.user_var.set(-1)

        # Verificar ganador
        winner = self.model.check_winner()
        if winner == "user":
            messagebox.showinfo("Fin", "¡GANASTE LA PARTIDA!")
            self.new_match()
        elif winner == "machine":
            messagebox.showinfo("Fin", "¡LA IA GANA!")
            self.new_match()

    def _handle_card_loss(self, slot_index, is_user):
        """Maneja la eliminación y RELLENO INFINITO de cartas"""
        if is_user:
            self.model.user_cards[slot_index] = None
            # Sacamos carta de la cola (esto deja un hueco None al final)
            new_card = self.model.dequeue_user()
            
            # --- CORRECCIÓN: RELLENAR EL HUECO CON CARTA NUEVA ---
            new_random_card = CardAPI.get_random_monster()
            if self.model.user_queue:
                self.model.user_queue[-1] = new_random_card
            # -----------------------------------------------------

        else:
            self.model.machine_cards[slot_index] = None
            new_card = self.model.dequeue_machine()
            
            # --- CORRECCIÓN: RELLENAR EL HUECO CON CARTA NUEVA ---
            new_random_card = CardAPI.get_random_monster()
            if self.model.machine_queue:
                self.model.machine_queue[-1] = new_random_card
            # -----------------------------------------------------

        target_slots = self.view.user_slots if is_user else self.view.machine_slots
        
        if new_card:
            if is_user: self.model.add_user_card(slot_index, new_card)
            else: self.model.add_machine_card(slot_index, new_card)
            target_slots[slot_index].update(new_card)
        else:
            # Esto ya casi no debería pasar gracias al relleno, pero por seguridad:
            target_slots[slot_index].disable()
            if target_slots[slot_index].name_label:
                target_slots[slot_index].name_label.configure(text="VACÍO")
            target_slots[slot_index].img_label.configure(image=None) 

        self._update_queue_views()

    def _update_queue_views(self):
        """Refresca las colas visuales."""
        # Usuario
        for i, slot in enumerate(self.view.user_queue_slots):
            if i < len(self.model.user_queue):
                card = self.model.user_queue[i]
                if card: slot.update(card)
                else: self._clear_queue_slot(slot)
            else: self._clear_queue_slot(slot)
        
        # Máquina
        for i, slot in enumerate(self.view.machine_queue_slots):
            if i < len(self.model.machine_queue):
                card = self.model.machine_queue[i]
                if card: slot.update(card)
                else: self._clear_queue_slot(slot)
            else: self._clear_queue_slot(slot)

    def _clear_queue_slot(self, slot):
        """Limpia el slot de forma segura."""
        # Evitamos el error AttributeError si la etiqueta no existe
        if slot.name_label:
            slot.name_label.configure(text="")
        if slot.img_label:
            slot.img_label.configure(image=None) 

    def set_queue(self):
        try:
            size = simpledialog.askinteger("Cola", "Tamaño:", minvalue=1, maxvalue=40)
            if size:
                self.model.config_queues(size=size)
                self.load_queue_cards()
                messagebox.showinfo("Config", "Cola ajustada.")
        except: pass

    def new_match(self):
        if messagebox.askyesno("Reiniciar", "¿Jugar de nuevo?"):
            self.start_new_game()

    def show_log(self):
        m = self.model
        msg = f"User Score: {m.user_score} (Life: {m.user_life})\nIA Score: {m.machine_score} (Life: {m.machine_life})"
        messagebox.showinfo("Stats", msg)