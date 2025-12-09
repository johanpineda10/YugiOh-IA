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

    def config_queues(self, size=8):
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
        """Saca la primera carta de la cola del usuario y mantiene el tamaño fijo."""
        if not self.user_queue:
            return None
        card = self.user_queue.pop(0)
        self.user_queue.append(None)
        return card

    def dequeue_machine(self):
        """Saca la primera carta de la cola de la máquina y mantiene el tamaño fijo."""
        if not self.machine_queue:
            return None
        card = self.machine_queue.pop(0)
        self.machine_queue.append(None)
        return card

    def fight_round(self, u_card, m_card, mode_user, mode_machine, u_slot, m_slot):
        """
        Retorna tupla: (resultado, daño_usuario, daño_maquina)
        """
        # Aseguramos que existan las cartas
        if not u_card or not m_card:
            return "draw", 0, 0

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        damage_to_user = 0
        damage_to_machine = 0
        result = "draw"

        # Normalizamos a minúsculas por seguridad
        mode_user = mode_user.lower()
        mode_machine = mode_machine.lower()

        # Mapeo de términos por si acaso llegan mezclados
        if mode_user == "atk": mode_user = "attack"
        if mode_user == "def": mode_user = "defense"
        if mode_machine == "atk": mode_machine = "attack"
        if mode_machine == "def": mode_machine = "defense"

        # Lógica de Batalla
        if mode_user == "attack" and mode_machine == "attack":
            # Ataque vs Ataque
            if atkU > atkM:
                damage_to_machine = atkU - atkM
                result = "machine_loses"
                self.user_score += 1
            elif atkM > atkU:
                damage_to_user = atkM - atkU
                result = "user_loses"
                self.machine_score += 1
            else:
                result = "draw" # Empate de ataque, ambas mueren en reglas oficiales, aqui draw simple

        elif mode_user == "attack" and mode_machine == "defense":
            # Usuario ataca, máquina defiende
            if atkU > defM:
                damage_to_machine = 0 # La IA pierde carta pero no vida
                result = "machine_loses"
                self.user_score += 1
            else:
                # Si la defensa de la IA es mayor, TÚ recibes daño
                if defM > atkU:
                    damage_to_user = defM - atkU
                result = "draw"

        elif mode_user == "defense" and mode_machine == "attack":
            # Usuario defiende, máquina ataca
            if atkM > defU:
                # Regla Oficial: Carta destruida, pero USUARIO NO RECIBE DAÑO
                damage_to_user = 0  # <--- CAMBIO IMPORTANTE (Antes era atkM - defU)
                result = "user_loses"
                self.machine_score += 1
            else:
                # Si la defensa del usuario es mayor, la máquina recibe daño
                if defU > atkM:
                    damage_to_machine = defU - atkM
                result = "draw"

        # Aplicar daño a las vidas globales
        self.user_life -= damage_to_user
        self.machine_life -= damage_to_machine
        
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