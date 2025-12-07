# model/game_model.py

class GameModel:

    def __init__(self):
        self.user_cards = [None, None, None, None, None]
        self.machine_cards = [None, None, None, None, None]
        
        # Vida global de cada jugador
        self.user_life = 10000
        self.machine_life = 10000

        # colas/espera (por defecto 8 espacios)
        self.user_queue = [None, None, None, None, None, None, None, None]
        self.machine_queue = [None, None, None, None, None, None, None, None]

        self.user_score = 0
        self.machine_score = 0

        self.final_user_score = 0
        self.final_machine_score = 0

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
        - resultado: "user_loses", "machine_loses", "both_lose", "draw"
        - daño_usuario: cantidad a restar de vida del usuario
        - daño_maquina: cantidad a restar de vida de la máquina
        """

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        damage_to_user = 0
        damage_to_machine = 0
        result = "draw"

        if mode_user == "atk" and mode_machine == "atk":
            # Ataque vs Ataque: gana el mayor, perdedor pierde su carta y recibe daño por diferencia
            if atkU > atkM:
                damage_to_machine = atkU - atkM
                result = "machine_loses"
                self.user_score += 1
            elif atkM > atkU:
                damage_to_user = atkM - atkU
                result = "user_loses"
                self.machine_score += 1
            else:
                result = "draw"

        elif mode_user == "atk" and mode_machine == "def":
            # Usuario ataca, máquina defiende
            if atkU > defM:
                damage_to_machine = atkU - defM
                result = "machine_loses"
                self.user_score += 1
            else:
                result = "draw"

        elif mode_user == "def" and mode_machine == "atk":
            # Usuario defiende, máquina ataca
            if atkM > defU:
                damage_to_user = atkM - defU
                result = "user_loses"
                self.machine_score += 1
            else:
                result = "draw"

        elif mode_user == "def" and mode_machine == "def":
            result = "draw"

        # Aplicar daño a las vidas globales
        self.user_life -= damage_to_user
        self.machine_life -= damage_to_machine
        
        if self.user_life < 0:
            self.user_life = 0
        if self.machine_life < 0:
            self.machine_life = 0

        return result, damage_to_user, damage_to_machine


    def check_winner(self):
        # Verificar si la vida de algún jugador llegó a 0
        if self.machine_life <= 0:
            self.final_user_score += 1
            return "user"
        if self.user_life <= 0:
            self.final_machine_score += 1
            return "machine"
        
        # Verificar si ya no quedan cartas en la cola y todos los slots están vacíos
        user_has_cards = any(self.user_cards) or any(self.user_queue)
        machine_has_cards = any(self.machine_cards) or any(self.machine_queue)
        
        if not machine_has_cards and not user_has_cards:
            # Desempate por puntaje
            if self.user_score > self.machine_score:
                self.final_user_score += 1
                return "user"
            elif self.machine_score > self.user_score:
                self.final_machine_score += 1
                return "machine"
            else:
                return "draw"
        elif not machine_has_cards:
            self.final_user_score += 1
            return "user"
        elif not user_has_cards:
            self.final_machine_score += 1
            return "machine"
        
        return None

    def reset(self):
        self.__init__()
