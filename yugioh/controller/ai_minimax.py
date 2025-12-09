import math
import random

class MinimaxAI:
    def __init__(self, max_depth=2):
        self.max_depth = max_depth

    def get_best_move(self, model, opponent_card, opponent_mode):
        """Decide entre combinar cartas o elegir el mejor movimiento de ataque/defensa."""
        
        # 1. EVALUAR COMBINACIÓN (Solo si está disponible en el modelo)
        # Nota: Asumimos que model.can_combine_this_turn existe en GameModel
        if hasattr(model, 'can_combine_this_turn') and model.can_combine_this_turn:
            combine_option = self._evaluate_ai_combination(model)
            
            # Umbral de ganancia de poder para que valga la pena combinar
            if combine_option and combine_option['score'] > 2000: 
                # Si la combinación es muy rentable, la elegimos y terminamos el turno.
                return combine_option
        
        # 2. Si no combina o la combinación no es rentable, procede a la pelea
        return self._get_best_fight_move(model, opponent_card, opponent_mode)

    
    def _get_best_fight_move(self, model, user_card, user_mode):
        """Busca el mejor movimiento (carta + modo) para contrarrestar al usuario."""
        
        best_score = -float('inf')
        best_move = None
        
        # Usamos get_valid_moves (que ya existe en tu código)
        possible_moves = self.get_valid_moves(model) 
        
        # Si la IA no tiene cartas válidas para jugar
        if not possible_moves:
            return None 

        for move in possible_moves:
            # Aquí aplicarías Minimax si fuera la implementación completa, 
            # pero usamos la evaluación heurística directa para un 'counter'.
            
            # Nota: Esto no usa la profundidad (self.max_depth) ni Minimax real, 
            # solo la heurística de 'evaluate_counter_move' que tú definiste.
            score = self.evaluate_counter_move(move, user_card, user_mode)
            
            if score > best_score:
                best_score = score
                best_move = move

        # Aseguramos que el movimiento de pelea tenga el formato esperado por el controlador
        if best_move:
            return {
                'type': 'fight',
                'index': best_move['index'],
                'mode': best_move['mode'],
                # No es necesario retornar card_ref al controlador
            }
        return None

    # NUEVA FUNCIÓN: Genera todas las posibles combinaciones para la IA
    def _evaluate_ai_combination(self, model):
        best_combination = None
        max_power_gain = 0
        
        # Iterar sobre todas las parejas de cartas de la IA
        for i in range(5):
            for j in range(i + 1, 5):
                card1 = model.machine_cards[i]
                card2 = model.machine_cards[j]
                
                if card1 and card2:
                    # Simular la fusión (misma lógica que en GameController)
                    new_atk = max(card1.atk, card2.atk) + 1000
                    new_def = max(card1.defe, card2.defe) + 1000
                    
                    # Heurística: ¿Cuánto poder gana la IA?
                    current_power = card1.atk + card1.defe + card2.atk + card2.defe
                    new_power = new_atk + new_def 
                    power_gain = new_power - current_power
                    
                    if power_gain > max_power_gain:
                        max_power_gain = power_gain
                        best_combination = {
                            'type': 'combine',
                            'slots': (i, j),
                            'new_atk': new_atk,
                            'new_def': new_def,
                            'score': power_gain # Usamos la ganancia de poder como score
                        }

        # La IA solo combina si gana un poder muy significativo (ej. > 4000)
        if best_combination and best_combination['score'] > 4000:
            return best_combination
        return None

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