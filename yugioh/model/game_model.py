# model/game_model.py

class GameModel:

    def __init__(self):
        self.user_cards = [None, None, None]
        self.machine_cards = [None, None, None]

        self.user_score = 0
        self.machine_score = 0

        self.final_user_score = 0
        self.final_machine_score = 0

    def add_user_card(self, slot, card):
        self.user_cards[slot] = card

    def add_machine_card(self, slot, card):
        self.machine_cards[slot] = card

    def fight_round(self, u_card, m_card):
        """
        Retorna:
        - "user"
        - "machine"
        - "draw"
        - "lower_user_def"
        - "lower_machine_def"
        """

        atkU, defU = u_card.atk, u_card.defe
        atkM, defM = m_card.atk, m_card.defe

        atkModeU = atkU >= defU
        atkModeM = atkM >= defM

        if atkModeU and atkModeM:
            if atkU > atkM:
                self.user_score += 1
                return "user"
            elif atkU < atkM:
                self.machine_score += 1
                return "machine"
            else:
                return "draw"

        if not atkModeU and atkModeM:
            new_def = defU - atkM
            u_card.defe = max(0, new_def)

            if new_def <= 0:
                self.machine_score += 1
                return "machine"
            return "lower_user_def"

        if atkModeU and not atkModeM:
            new_def = defM - atkU
            m_card.defe = max(0, new_def)

            if new_def <= 0:
                self.user_score += 1
                return "user"
            return "lower_machine_def"

        return "draw"  # ambos en defensa

    def check_winner(self):
        if self.user_score == 2:
            self.final_user_score += 1
            return "user"
        if self.machine_score == 2:
            self.final_machine_score += 1
            return "machine"
        return None

    def reset(self):
        self.__init__()
