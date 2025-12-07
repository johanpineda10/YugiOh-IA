# model/game_model.py

class GameModel:

    def __init__(self):
        self.user_cards = [None, None, None]
        self.machine_cards = [None, None, None]
        
        # Vida individual de cada carta (3000 por defecto)
        self.user_cards_life = [3000, 3000, 3000]
        self.machine_cards_life = [3000, 3000, 3000]

        # colas/espera (por defecto 8 espacios)
        self.user_queue = [None, None, None, None, None, None, None, None]
        self.machine_queue = [None, None, None, None, None, None, None, None]

        self.user_score = 0
        self.machine_score = 0

        self.final_user_score = 0
        self.final_machine_score = 0

    def add_user_card(self, slot, card):
        self.user_cards[slot] = card
        self.user_cards_life[slot] = 3000  # Resetear vida al agregar nueva carta

    def add_machine_card(self, slot, card):
        self.machine_cards[slot] = card
        self.machine_cards_life[slot] = 3000  # Resetear vida al agregar nueva carta


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
        Retorna:
        - "user" si usuario gana
        - "machine" si máquina gana
        - "user_dead" si la carta del usuario murió (vida <= 0)
        - "machine_dead" si la carta de la máquina murió (vida <= 0)
        - "both_dead" si ambas cartas murieron
        - "draw" empate sin daño
        """

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        user_card_died = False
        machine_card_died = False

        if mode_user == "atk" and mode_machine == "atk":
            # Gana el que tenga mayor ataque; el perdedor recibe daño igual a la diferencia de ataque
            if atkU > atkM:
                dmg = atkU - atkM
                self.machine_cards_life[m_slot] -= dmg
                if self.machine_cards_life[m_slot] < 0:
                    self.machine_cards_life[m_slot] = 0
                if self.machine_cards_life[m_slot] <= 0:
                    self.user_score += 1
                    machine_card_died = True
            elif atkM > atkU:
                dmg = atkM - atkU
                self.user_cards_life[u_slot] -= dmg
                if self.user_cards_life[u_slot] < 0:
                    self.user_cards_life[u_slot] = 0
                if self.user_cards_life[u_slot] <= 0:
                    self.machine_score += 1
                    user_card_died = True
            else:
                return "draw"

        elif mode_user == "atk" and mode_machine == "def":
            # El defensor recibe daño proporcional al ataque completo
            self.machine_cards_life[m_slot] -= atkU
            if self.machine_cards_life[m_slot] < 0:
                self.machine_cards_life[m_slot] = 0
            if self.machine_cards_life[m_slot] <= 0:
                self.user_score += 1
                machine_card_died = True

        elif mode_user == "def" and mode_machine == "atk":
            # El defensor (usuario) recibe daño proporcional al ataque completo de la máquina
            self.user_cards_life[u_slot] -= atkM
            if self.user_cards_life[u_slot] < 0:
                self.user_cards_life[u_slot] = 0
            if self.user_cards_life[u_slot] <= 0:
                self.machine_score += 1
                user_card_died = True

        elif mode_user == "def" and mode_machine == "def":
            return "draw"
        else:
            return "draw"

        # Determinar el resultado basado en quién murió
        if user_card_died and machine_card_died:
            return "both_dead"
        elif machine_card_died:
            return "machine_dead"
        elif user_card_died:
            return "user_dead"
        elif self.machine_cards_life[m_slot] < self.user_cards_life[u_slot]:
            return "user"
        elif self.user_cards_life[u_slot] < self.machine_cards_life[m_slot]:
            return "machine"
        else:
            return "draw"


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
