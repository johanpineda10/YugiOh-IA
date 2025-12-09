# model/game_model.py

class GameModel:

    def __init__(self):
        self.user_cards = [None, None, None, None, None]
        self.machine_cards = [None, None, None, None, None]
        
        # Vida global de cada jugador
        self.user_life = 8000
        self.machine_life = 8000

        # colas/espera fijas (8 espacios)
        self.user_queue = []
        self.machine_queue = []

        self.user_score = 0
        self.machine_score = 0

        self.final_user_score = 0
        self.final_machine_score = 0
        
        self.user_can_combine = True
        self.machine_can_combine = True

    def config_queues(self, size):
        self.user_queue = [None] * size
        self.machine_queue = [None] * size

    def add_user_card(self, slot, card):
        self.user_cards[slot] = card

    def add_machine_card(self, slot, card):
        self.machine_cards[slot] = card


    def set_user_queue(self, slot, card):
        if 0 <= slot < len(self.user_queue):
            self.user_queue[slot] = card

    def set_machine_queue(self, slot, card):
        if 0 <= slot < len(self.machine_queue):
            self.machine_queue[slot] = card

    def dequeue_user(self):
        """Saca la primera carta de la cola del usuario."""
        if not self.user_queue:
            return None
        card = self.user_queue.pop(0)
        return card

    def dequeue_machine(self):
        """Saca la primera carta de la cola de la máquina."""
        if not self.machine_queue:
            return None
        card = self.machine_queue.pop(0)
        return card

    def fight_round(self, u_card, m_card, mode_user, mode_machine, u_slot, m_slot):
        """
        Retorna tupla: (resultado, daño_usuario, daño_maquina)
        AHORA CON DAÑO DE PENETRACIÓN (Romper defensa baja vida).
        """
        # Aseguramos que existan las cartas
        if not u_card or not m_card:
            return "draw", 0, 0

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        damage_to_user = 0
        damage_to_machine = 0
        result = "draw"

        # Normalizamos a minúsculas
        mode_user = mode_user.lower()
        mode_machine = mode_machine.lower()

        # Mapeo de términos
        if mode_user == "atk": mode_user = "attack"
        if mode_user == "def": mode_user = "defense"
        if mode_machine == "atk": mode_machine = "attack"
        if mode_machine == "def": mode_machine = "defense"

        # --- CASO 1: AMBOS ATACAN ---
        if mode_user == "attack" and mode_machine == "attack":
            if atkU > atkM:
                damage_to_machine = atkU - atkM
                result = "machine_loses"
                self.user_score += 1
            elif atkM > atkU:
                damage_to_user = atkM - atkU
                result = "user_loses"
                self.machine_score += 1
            else:
                result = "draw" # Empate, ambas mueren (opcionalmente)

        # --- CASO 2: TÚ ATACAS vs IA DEFENSA ---
        elif mode_user == "attack" and mode_machine == "defense":
            if atkU > defM:
                # ANTES: damage_to_machine = 0
                # AHORA: Calculamos la diferencia para bajar vida (Piercing Damage)
                damage_to_machine = atkU - defM 
                result = "machine_loses"
                self.user_score += 1
            else:
                # Si la defensa de la IA es mayor que tu ataque, TÚ recibes daño (rebote)
                if defM > atkU:
                    damage_to_user = defM - atkU
                result = "draw" # Nadie muere, pero tú recibes daño

        # --- CASO 3: TÚ DEFIENDES vs IA ATACA ---
        elif mode_user == "defense" and mode_machine == "attack":
            if atkM > defU:
                # ANTES: damage_to_user = 0
                # AHORA: La IA también te hace daño de penetración si rompe tu defensa
                damage_to_user = atkM - defU
                result = "user_loses"
                self.machine_score += 1
            else:
                # Si tu defensa es mayor, la IA recibe daño (rebote)
                if defU > atkM:
                    damage_to_machine = defU - atkM
                result = "draw" # Nadie muere

        # --- CASO 4: AMBOS DEFIENDEN (Nada pasa usualmente) ---
        else:
            result = "draw"

        # Aplicar daño a las vidas globales
        self.user_life -= damage_to_user
        self.machine_life -= damage_to_machine
        
        # Evitar números negativos
        if self.user_life < 0: self.user_life = 0
        if self.machine_life < 0: self.machine_life = 0

        return result, damage_to_user, damage_to_machine

    def check_winner(self):
        if self.machine_life <= 0:
            self.final_user_score += 1
            return "user"
        if self.user_life <= 0:
            self.final_machine_score += 1
            return "machine"
        return None

    def reset(self):
        self.__init__()