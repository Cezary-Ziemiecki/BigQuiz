

def print_game_state(func, quiz):
    """
        Print game state before and after function launching
    Parameters
    ----------
    func : function
        Launched function
    quiz : Game
        Game for state checking
    """
    def inner(*args, **kwargs):
        print(
            f"Before: {quiz.current_question} | {quiz._score} | {quiz._users_answers} | {quiz._order} | {quiz._shuffled_answers}")
        output = func(*args, **kwargs)
        print(
            f"After: {quiz.current_question} | {quiz._score} | {quiz._users_answers} | {quiz._order} | {quiz._shuffled_answers}")
        return output
    inner.__name__ = func.__name__
    return inner
