import math
import random

class MinimaxAI:
    
    def __init__(self, max_depth=2):
        self.max_depth = max_depth

    # Función principal que decide el mejor movimiento de la IA
    def get_best_move(self, model, opponent_card, opponent_mode):
        """
        Decide si la IA combina cartas o realiza un movimiento de ataque/defensa.
        """

        
        
        if hasattr(model, 'can_combine_this_turn') and model.can_combine_this_turn:
            # Evalúa si existe una buena combinación
            combine_option = self._evaluate_ai_combination(model)

            # Si la combinación genera una ganancia de poder suficientemente alta
            if combine_option and combine_option['score'] > 2000:
                # Se elige la combinación y se termina el turno
                return combine_option

        
        return self._get_best_fight_move(model, opponent_card, opponent_mode)

    # Función que busca el mejor movimiento de pelea contra el jugador
    def _get_best_fight_move(self, model, user_card, user_mode):
        """
        Busca el mejor movimiento (qué carta usar y en qué modo: ataque o defensa)
        para contrarrestar la carta del usuario.
        """

        best_score = -float('inf')
        best_move = None

        # Obtiene todos los movimientos posibles de la IA
        possible_moves = self.get_valid_moves(model)

       
        if not possible_moves:
            return None

        # Recorre todos los movimientos posibles
        for move in possible_moves:
            # Calcula un puntaje heurístico que indica qué tan bueno es el movimiento
            score = self.evaluate_counter_move(move, user_card, user_mode)

        
            if score > best_score:
                best_score = score
                best_move = move


        
        if best_move:
            return {
                'type': 'fight',          
                'index': best_move['index'],  
                'mode': best_move['mode'],    
            }

        return None

    
    def _evaluate_ai_combination(self, model):
        """
        Busca la mejor combinación (fusión) de dos cartas para la IA.
        """

        best_combination = None
        max_power_gain = 0

        # Recorre todas las parejas posibles de cartas
        for i in range(5):
            for j in range(i + 1, 5):
                card1 = model.machine_cards[i]
                card2 = model.machine_cards[j]

                
                if card1 and card2:
                    # Simula la fusión: toma el mayor ataque/defensa y suma 1000
                    new_atk = max(card1.atk, card2.atk) + 1000
                    new_def = max(card1.defe, card2.defe) + 1000

                    
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
                            'score': power_gain 
                        }

        # La IA solo combina si la ganancia de poder es muy alta
        if best_combination and best_combination['score'] > 4000:
            return best_combination


        return None

    
    def get_valid_moves(self, model):
        """
        Genera una lista de todos los movimientos posibles:
        cada carta puede atacar o defender.
        """
        moves = []
        cards = getattr(model, 'machine_cards', [])

        # Recorre todas las cartas de la máquina
        for index, card in enumerate(cards):
            if card is not None:
                
                moves.append({'index': index, 'mode': 'attack', 'card_ref': card})

                
                moves.append({'index': index, 'mode': 'defense', 'card_ref': card})

        return moves

    
    def evaluate_counter_move(self, ai_move, user_card, user_mode):
        """
        Calcula un puntaje dependiendo de si la IA gana, empata o pierde
        contra la carta del usuario.
        """

       
        ai_card = ai_move['card_ref']
        ai_mode = ai_move['mode']

        # Estadísticas de la carta de la IA
        atk_ai = ai_card.atk
        def_ai = ai_card.defe

        # Estadísticas de la carta del usuario
        atk_user = user_card.atk
        def_user = user_card.defe

        
        score = 0

        
        if user_mode == "attack":
            if ai_mode == "attack":
                # Choque ataque vs ataque
                diff = atk_ai - atk_user
                if diff > 0:
                    score = 10000 + diff  # Victoria clara
                elif diff == 0:
                    score = 0           
                else:
                    score = -10000 + diff  # Derrota

            elif ai_mode == "defense":
                # Defensa contra ataque
                diff = def_ai - atk_user
                if diff > 0:
                    score = 5000 + diff   # Buena defensa
                elif diff == 0:
                    score = 2000          # Defensa neutral
                else:
                    score = -5000 + diff  # Defensa rota

        
        elif user_mode == "defense":
            try:
                
                if ai_mode == "attack":
                    # Ataque contra defensa
                    diff = atk_ai - def_user
                    if diff > 0:
                        score = 10000 + diff  # Rompe la defensa
                    else:
                        score = -2000 + diff  # Ataque fallido
            except:
                print("No se puede jugar defensa contra defensa.")

        

        # Factor de aleatoriedad para evitar decisiones idénticas
        score += random.randint(0, 5)

        return score
