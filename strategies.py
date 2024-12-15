"""Here have differents kinds of strategies"""

import random

def cooperate(*args):
    return True
    # DONE!

def betray(*args):
    return False
    # DONE!

def retaliate(*args):
    """
    Tit-for-Tat
    This is the classical strategies win the second tournament.
    If the opponent betrays last game, i will betray, if the opponenent cooperate last game, i will cooperate.

    parameter: 
        game_record, 
        player0or1(int)
    """
    game_record = args[0]
    player0or1 = args[1]
    if not game_record["history"]: # if the history is empty, this will be the first game.
        return True
    else:
        if game_record["history"][-1][1 - player0or1] == True: # examine whether the opponent cooperate last game.
            return True
        else:
            return False
    # Done!

def retaliate2(*args):
    """
    Tit-for-2Tat
    If the opponent betrays for two times , i will betray, otherwise i will cooperate.

    parameter: 
        game_record, 
        player0or1(int)
    """
    game_record = args[0]
    player0or1 = args[1]
    if len(game_record["history"]) < 2: # if the history is empty, this will be the first game.
        return True
    else:
        if game_record["history"][-1][1 - player0or1] == False and game_record["history"][-2][1 - player0or1] == False: # examine whether the opponent cooperate last game.
            return False
        else:
            return True
    # Done!    

def select_every_turn(*args):
    while True:
        user_input = input("Please choose: (C for cooperate, B for betray) ").strip()
        # strip是用来去掉输入两端的空格的
        if user_input in ["c", "C", "b", "B"]:
            break  # 输入有效，退出循环
        else:
            print("Invalid input, please choose 'C' for cooperate or 'B' for betray.")

    if user_input in ["c", "C"]:
        return True
    else:
        return False
    # DONE!

def totalrandom(*args):
    """
    A totally random strategy.
    
    Takes no arguments
    """
    i = random.random()
    if i < 0.5:
        return True
    else:
        return False
    
def judas(*args):
    """
    Judas: a strategy cooperates if they are winning and betrays if they are losing.
    """
    # this strategy is from a project on github. the strategy is from thabott
    # this is the urlhttps://github.com/thabbott/prisoners-dilemma/blob/master/Judas.py
    # i hope i can provide as much as strategies as i can
    game_record = args[0]
    isplayer0or1 = args[1]
    my_point = game_record[f"player{isplayer0or1 + 1}_point"]
    opponent_point = game_record[f"player{(1-isplayer0or1) + 1}_point"]
    if my_point >= opponent_point:
        return True
    else:
        return False
    
def win_stay_lose_shift(*args):
    """not finished"""
    """
    a strategy starts with cooperate, shift if gain less, otherwise stay.
    """
    game_record = args[0]
    if len(game_record["history"]) < 2:
        return True
    else:
        pass 