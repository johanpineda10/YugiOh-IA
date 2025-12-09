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
        
        self.selected_fusion_slots = [] 
        self.fusion_counter = 0 
        
        self.userBattleMode = None
        self.machineBattleMode = None

        # Conectar botones
        self.view.btnFight.configure(command=self.fight)
        self.view.btnAttackUsu.configure(command=self.set_user_attack)
        self.view.btnDefenseUsu.configure(command=self.set_user_defense)
        self.view.btnConfig.configure(command=self.set_queue)
        self.view.btnLog.configure(command=self.show_log)
        
        self.view.btnCombine.configure(command=self.combine_cards) # NUEVO: Botón Combinar

        self.view.controller = self # Aseguramos que la Vista tenga una referencia al Controller

        self.start_new_game()

    def start_new_game(self):
        self.model.reset()
        self.load_queue_cards()
        self.load_initial_hands()
        
        self.selected_fusion_slots = [] # Resetear
        self.view.update_card_selection(self.selected_fusion_slots)
        
        self.fusion_counter = 0 # Reiniciar el contador de fusiones
        
        self.userBattleMode = None
        self.machineBattleMode = None
        self.view.user_var.set(-1)
        self.view.machine_var.set(-1)
        
        self.update_mode_buttons()
        self.view.update_life_bars(self.model.user_life, self.model.machine_life)
        
    def handle_card_selection_for_fusion(self, slot_index):
        """Maneja el clic en una carta de usuario para la fusión."""
        card = self.model.user_cards[slot_index]
        if not card:
            return

        if slot_index in self.selected_fusion_slots:
            # Deseleccionar
            self.selected_fusion_slots.remove(slot_index)
        elif len(self.selected_fusion_slots) < 2:
            # Seleccionar
            self.selected_fusion_slots.append(slot_index)
        else:
            messagebox.showwarning("Fusión", "Solo puedes seleccionar dos cartas para combinar.")
            return

        # Actualizar la vista (bordes)
        self.view.update_card_selection(self.selected_fusion_slots)

    def combine_cards(self):
        """Lógica de fusión: combina dos cartas en una nueva."""
        if not self.model.user_can_combine:
            messagebox.showwarning("Fusión", "Solo puedes realizar una combinación por turno.")
            return

        if len(self.selected_fusion_slots) != 2:
            messagebox.showwarning("Fusión", "Debes seleccionar exactamente dos cartas para combinar.")
            return

        idx1, idx2 = self.selected_fusion_slots
        card1 = self.model.user_cards[idx1]
        card2 = self.model.user_cards[idx2]

        if not card1 or not card2:
            messagebox.showerror("Error", "Error: Slots seleccionados vacíos.")
            self.selected_fusion_slots = []
            self.view.update_card_selection(self.selected_fusion_slots)
            return
            
        # 1. Calcular ATK/DEF de la nueva carta
        # ATK/DEF base es el MAYOR entre las dos, más 1000.
        new_atk = max(card1.atk, card2.atk) + 1000
        new_def = max(card1.defe, card2.defe) + 1000
        
        # 2. Obtener la nueva carta (Nombre y URL aleatorios)
        new_combined_card_api = CardAPI.get_random_monster()
        
        if not new_combined_card_api:
            messagebox.showerror("Error", "No se pudo obtener una imagen base para la fusión.")
            return
        
        self.fusion_counter += 1
        new_card_name = f"COMBINACION {self.fusion_counter}"

        # 3. Crear el objeto Card con las estadísticas fusionadas
        from model.card_model import Card # Import local para evitar circular
        combined_card = Card(
            name=new_card_name,
            atk=new_atk,
            defe=new_def,
            img_url=new_combined_card_api.img_url # Usar la imagen de la carta API aleatoria
        )

        # 4. Determinar dónde colocar la nueva carta (reemplazando el slot con menor índice)
        target_slot = min(idx1, idx2)
        
        # 5. Reemplazar las dos cartas por una nueva:
        # a) La nueva carta ocupa target_slot
        self.model.add_user_card(target_slot, combined_card)
        self.view.user_slots[target_slot].update(combined_card)
        
        # b) El otro slot se llena con la siguiente carta de la cola (como si se hubiera destruido)
        # Esto requiere que la lógica de _handle_card_loss se use para el segundo slot
        other_slot = max(idx1, idx2)
        self.model.user_cards[other_slot] = None # Marcar para reemplazo
        self._handle_card_loss(other_slot, is_user=True)
        
        # 6. Limpiar el estado de fusión
        self.selected_fusion_slots = []
        self.view.update_card_selection(self.selected_fusion_slots)
        
        # --- Desactivar la fusión para este turno ---
        self.model.user_can_combine = False

        messagebox.showinfo("Fusión Exitosa", f"¡Combinación creada! ATK {new_atk}/DEF {new_def}. El slot {other_slot} se rellenó de la cola.")

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

    # game_controller.py (Función fight completa con el Log de la IA)

    def fight(self):
        """Lógica de la pelea, añadiendo una validación de fusión."""
        if self.selected_fusion_slots:
            messagebox.showwarning("Alerta", "Termina la fusión antes de pelear.")
            return
        
        # 1. Validaciones del usuario
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

        # 2. IA Decide entre COMBINAR o PELEAR
        
        # Le pasamos tu carta y tu modo a la IA para que elija su mejor counter o decida combinar
        ai_move = self.ai.get_best_move(self.model, u_card, self.userBattleMode)
        
        if ai_move and ai_move.get('type') == 'combine':
            # 2.1. La IA elige COMBINAR
            self.execute_machine_combination(ai_move)
            
            # El turno termina sin pelea. Reiniciamos el estado del juego para el próximo turno.
            self.model.user_can_combine = True # Habilita al usuario para combinar de nuevo en su turno
            self.userBattleMode = None
            self.view.user_var.set(-1)
            self.update_mode_buttons()

            return # Termina el turno sin la pelea real
        
        # 2.2. La IA elige PELEAR
        if ai_move:
            m_slot = ai_move.get('index', 0)
            self.machineBattleMode = ai_move.get('mode', 'attack')
            
            # --- AGREGADO: MOSTRAR LA DECISIÓN DE LA IA (Pelea) ---
            m_card_log = self.model.machine_cards[m_slot]
            if m_card_log:
                print(f"IA DECIDE: Usar carta del Slot {m_slot} ({m_card_log.name}) en modo {self.machineBattleMode.upper()}")
            # --------------------------------------------------------
            
        else:
            # Fallback por si la IA no tiene cartas jugables (debería ser raro)
            m_slot = 0
            self.machineBattleMode = "defense"
            # Si usa fallback, también mostramos el log
            print(f"IA DECIDE: Usar fallback en el Slot {m_slot} en modo {self.machineBattleMode.upper()}")

        m_card = self.model.machine_cards[m_slot]
        if not m_card:
            self.model.add_log("Error: La IA intentó jugar un slot vacío.")
            self._check_deck_exhaustion()
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

        # Resetear estado del turno y las banderas de Fusión
        self.userBattleMode = None
        self.machineBattleMode = None
        self.update_mode_buttons()
        self.view.user_var.set(-1)
        
        # --- Reiniciar la capacidad de Fusión para el siguiente turno ---
        self.model.user_can_combine = True
        self.model.machine_can_combine = True

        # Verificar ganador
        winner = self.model.check_winner()
        if winner == "user":
            messagebox.showinfo("Fin", "¡GANASTE LA PARTIDA!")
            self.new_match()
        elif winner == "machine":
            messagebox.showinfo("Fin", "¡LA IA GANA!")
            self.new_match()
        else:
            # Si no hay ganador por vida (winner es None), chequeamos agotamiento.
            self._check_deck_exhaustion()
            
    def execute_machine_combination(self, ai_move):
        """Ejecuta el movimiento de combinación decidido por la IA."""
        idx1, idx2 = ai_move['slots']
        new_atk = ai_move['new_atk']
        new_def = ai_move['new_def']
        
        # 1. Crear la carta combinada
        new_combined_card_api = CardAPI.get_random_monster()
        if not new_combined_card_api:
            messagebox.showerror("Error", "No se pudo obtener una imagen base para la fusión de la IA.")
            return
            
        self.fusion_counter += 1
        new_card_name = f"IA COMBINACION {self.fusion_counter}"

        from model.card_model import Card
        combined_card = Card(
            name=new_card_name,
            atk=new_atk,
            defe=new_def,
            img_url=new_combined_card_api.img_url
        )

        # 2. Determinar el slot de destino (el menor índice)
        target_slot = min(idx1, idx2)
        other_slot = max(idx1, idx2)
        
        # 3. Reemplazar las dos cartas por una nueva:
        self.model.add_machine_card(target_slot, combined_card)
        self.view.machine_slots[target_slot].update(combined_card)
        
        # 4. El otro slot se llena con la siguiente carta de la cola
        self.model.machine_cards[other_slot] = None # Marcar para reemplazo
        self._handle_card_loss(other_slot, is_user=False)
        
        # 5. Informar
        messagebox.showinfo("IA Fusión Exitosa", 
                            f"¡La IA combinó las cartas {idx1} y {idx2}!\n"
                            f"Nueva Carta: {new_card_name} (ATK {new_atk}/DEF {new_def}).")

        # 6. Desactivar la fusión para la IA (ya que su turno terminó)
        self.model.machine_can_combine = False
            
    def execute_machine_combination(self, ai_move):
        """Ejecuta el movimiento de combinación decidido por la IA."""
        idx1, idx2 = ai_move['slots']
        new_atk = ai_move['new_atk']
        new_def = ai_move['new_def']
        
        # 1. Crear la carta combinada
        new_combined_card_api = CardAPI.get_random_monster()
        if not new_combined_card_api:
            messagebox.showerror("Error", "No se pudo obtener una imagen base para la fusión de la IA.")
            return
            
        self.fusion_counter += 1
        new_card_name = f"IA COMBINACION {self.fusion_counter}"

        from model.card_model import Card
        combined_card = Card(
            name=new_card_name,
            atk=new_atk,
            defe=new_def,
            img_url=new_combined_card_api.img_url
        )

        # 2. Determinar el slot de destino (el menor índice)
        target_slot = min(idx1, idx2)
        other_slot = max(idx1, idx2)
        
        # 3. Reemplazar las dos cartas por una nueva:
        self.model.add_machine_card(target_slot, combined_card)
        self.view.machine_slots[target_slot].update(combined_card)
        
        # 4. El otro slot se llena con la siguiente carta de la cola
        self.model.machine_cards[other_slot] = None # Marcar para reemplazo
        self._handle_card_loss(other_slot, is_user=False)
        
        # 5. Informar
        messagebox.showinfo("IA Fusión Exitosa", 
                            f"¡La IA combinó las cartas {idx1} y {idx2}!\n"
                            f"Nueva Carta: {new_card_name} (ATK {new_atk}/DEF {new_def}).")

        # 6. Desactivar la fusión para la IA (ya que su turno terminó)
        self.model.machine_can_combine = False # <--- AHORA EN EL MODELO

    def _handle_card_loss(self, slot_index, is_user):
        """Maneja la eliminación y RELLENO INFINITO de cartas"""
        if is_user:
            self.model.user_cards[slot_index] = None
            # Sacamos carta de la cola (esto deja un hueco None al final)
            new_card = self.model.dequeue_user()
            target_slots = self.view.user_slots
            
            # # --- CORRECCIÓN: RELLENAR EL HUECO CON CARTA NUEVA ---
            # new_random_card = CardAPI.get_random_monster()
            # if self.model.user_queue:
            #     self.model.user_queue[-1] = new_random_card
            # # -----------------------------------------------------

        else:
            self.model.machine_cards[slot_index] = None
            new_card = self.model.dequeue_machine()
            target_slots = self.view.machine_slots
            
            # # --- CORRECCIÓN: RELLENAR EL HUECO CON CARTA NUEVA ---
            # new_random_card = CardAPI.get_random_monster()
            # if self.model.machine_queue:
            #     self.model.machine_queue[-1] = new_random_card
            # # -----------------------------------------------------

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
            
            self._check_deck_exhaustion()

        self._update_queue_views()
        
    def _check_deck_exhaustion(self):
        """Verifica si un jugador se queda sin cartas en mano y sin cola."""
        
        # Un jugador pierde si tiene 0 vida O si no tiene cartas en la mano
        # Y la cola está vacía.
        
        user_cards_in_hand = any(self.model.user_cards)
        machine_cards_in_hand = any(self.model.machine_cards)
        
        user_deck_empty = not user_cards_in_hand and not self.model.user_queue
        machine_deck_empty = not machine_cards_in_hand and not self.model.machine_queue
        
        if user_deck_empty and self.model.user_life > 0:
            self.model.user_life = 0
            messagebox.showinfo("Derrota", "¡El usuario pierde! Mazo y mano agotados.")
            self.new_match()
            
        if machine_deck_empty and self.model.machine_life > 0:
            self.model.machine_life = 0
            messagebox.showinfo("Derrota", "¡La IA pierde! Mazo y mano agotados.")
            self.new_match()
            return

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