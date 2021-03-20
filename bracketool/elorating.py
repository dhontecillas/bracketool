import math

class EloRating:
    def __init__( self ):
        pass

    def get_k_multiplier( self, num_of_games, max_multiplier = 10.0, stable_number_of_games = 8 ):
        if num_of_games >= stable_number_of_games:
            return 1.0
        else:
            return num_of_games * (1 - max_multiplier)/stable_number_of_games + max_multiplier


    def calculate_elo_rating( self, rating_a, rating_b, a_won, k_a = 32.0, k_b = 32.0 ):
        """
            rating_a: current rating for player A
            rating_b: current rating for player B
            a_won: boolean indicating if A is the winner of the match
            k_a: multiplier for A
            k_b: multiplier for B
        """
        if a_won:
            result_a = 1.0
        else:
            result_a = 0.0
        expected_a =  1 / ( 1 + math.pow(10, (rating_b - rating_a)/400 ) )
        expected_b = 1 - expected_a
        result_b = 1 - result_a
        rating_result_a = int( rating_a + k_a * (result_a - expected_a) )
        rating_result_b = int( rating_b + k_b * (result_b - expected_b) )
        if rating_result_a < 100:
            rating_result_a = 100
        if rating_result_b < 100:
            rating_result_b = 100
        return (rating_result_a, rating_result_b)
