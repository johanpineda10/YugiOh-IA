import math
import random

class MinimaxAI:
    def __init__(self, max_depth=2):
        self.max_depth = max_depth

    def get_best_move(self, model, user_card, user_mode):
        """
        Analiza las cartas de la IA y elige la que mejor contrarresta a la carta del usuario.
        """
        # Obtenemos movimientos posibles de la IA
        possible_moves = self.get_valid_moves(model)
        
        if not possible_moves:
            print("AI: No tiene cartas.")
            return None

        best_score = -math.inf
        best_move = None

        print(f"\n--- IA CONTRARRESTANDO A {user_card.name} ({user_mode}) ---")

        for move in possible_moves:
            # Evaluamos contra la carta ESPECIFICA del usuario
            score = self.evaluate_counter_move(move, user_card, user_mode)
            
            # Logs para ver qué piensa
            idx = move['index']
            mode = move['mode']
            print(f"IA Slot {idx} [{mode}] -> Score: {score}")

            if score > best_score:
                best_score = score
                best_move = move

        print(f"--- IA ELIGE: Slot {best_move['index']} {best_move['mode']} ---\n")
        return best_move

    def get_valid_moves(self, model):
        moves = []
        cards = getattr(model, 'machine_cards', [])
        for index, card in enumerate(cards):
            if card is not None:
                moves.append({'index': index, 'mode': 'attack', 'card_ref': card})
                moves.append({'index': index, 'mode': 'defense', 'card_ref': card})
        return moves

    def evaluate_counter_move(self, ai_move, user_card, user_mode):
        """
        Calcula puntaje basado en si ganamos, empatamos o perdemos contra la carta del usuario.
        """
        ai_card = ai_move['card_ref']
        ai_mode = ai_move['mode']
        
        atk_ai = ai_card.atk
        def_ai = ai_card.defe
        
        atk_user = user_card.atk
        def_user = user_card.defe
        
        score = 0
        
        # CASO 1: EL USUARIO VIENE EN ATAQUE
        if user_mode == "attack":
            if ai_mode == "attack":
                # Choque de Ataques
                diff = atk_ai - atk_user
                if diff > 0:
                    score = 10000 + diff # GRAN VICTORIA: Destruyo carta rival
                elif diff == 0:
                    score = 0 # Empate (ambas mueren)
                else:
                    score = -10000 + diff # DERROTA: Pierdo mi carta y vida
            
            elif ai_mode == "defense":
                # Yo defiendo
                diff = def_ai - atk_user
                if diff > 0:
                    score = 5000 + diff # BUENA DEFENSA: Rival pierde vida
                elif diff == 0:
                    score = 2000 # DEFENSA NEUTRA: No pasa nada
                else:
                    score = -5000 + diff # DEFENSA ROTA: Pierdo carta pero no vida (en reglas std) 
                                         # (o pierdo vida según tu modelo)

        # CASO 2: EL USUARIO ESTÁ EN DEFENSA
        elif user_mode == "defense":
            if ai_mode == "attack":
                # Yo ataco su defensa
                diff = atk_ai - def_user
                if diff > 0:
                    score = 10000 + diff # ROMPO DEFENSA: Destruyo carta
                else:
                    score = -2000 + diff # FALLO: Recibo daño por diferencia
            
            elif ai_mode == "defense":
                # Ambos defienden
                score = -100 # Aburrido, nada pasa. Evitar si es posible.
                # Pero si mis cartas son malas, mejor esto que morir.
                if def_ai > def_user: score += 50

        # Pequeño factor aleatorio para romper empates idénticos
        score += random.randint(0, 5)
        return score