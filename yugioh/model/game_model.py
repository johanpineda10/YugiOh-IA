# model/game_model.py

class GameModel:

    def __init__(self):
        self.user_cards = [None, None, None]
        self.machine_cards = [None, None, None]

        # colas/espera (por defecto 2 espacios)
        self.user_queue = [None, None]
        self.machine_queue = [None, None]

        self.user_score = 0
        self.machine_score = 0
        self.user_life = 10000
        self.machine_life = 10000

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

    def fight_round(self, u_card, m_card, mode_user, mode_machine):
        """
        Retorna:
        - "user"
        - "machine"
        - "both"
        - "draw"
        """

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        if mode_user == "atk" and mode_machine == "atk":
            if atkU > atkM:
                self.user_score += 1
                dmg = atkU - atkM
                self.machine_life -= dmg
                return "user"
            elif atkU < atkM:
                dmg = atkU - atkM
                self.machine_score += 1
                self.user_life -= dmg
                return "machine"
            else:
                return "both"


        if mode_user == "atk" and mode_machine == "def":
            if atkU > defM:
                self.user_score += 1
                dmg = atkU - atkM
                self.machine_life -= dmg
                return "user"
            elif atkU < defM:
                dmg = atkU - atkM
                self.machine_score += 1
                self.user_life -= dmg
                return "machine"
            else:
                return "both"

        if mode_user == "def" and mode_machine == "atk":
            if defU > atkM:
                self.user_score += 1
                dmg = atkU - atkM
                self.machine_life -= dmg
                return "user"
            elif defU < atkM:
                dmg = atkU - atkM
                self.machine_score += 1
                self.user_life -= dmg
                return "machine"
            else:
                return "both"

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
