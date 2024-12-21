"""This is a game theory game which is known as "prisoners' dilemma"."""

import strategies 

utility_table = {
    "cooperate for betray": 0,
    "betray for cooperate": 5,
    "cooperate for cooperate": 3,
    "betray for betray": 1
}

class Prisoner():
    """
    建构器，创建玩家对象（罪犯）。
    基本属性有：
        得分 策略def

    Constuctor, creating an object.
    basic attributes:
        points, strategy function
    """
    strategy = "cooperate"

    def __init__(self, name, strategy): # 这里是将策略和名字存储
        self.name = name
        self.strategy = strategy
        self.point = 0 # 初始化分数
        self.player0or1 = 0 

    def decision(self, *args):
         # I place number_of_rounds = 1, player_point = 0, opponent_point = 0 all in game_record
        return self.strategy(*args)
    
    def gain_point(self,point): # if the point is negative, it will be lose point
        self.point += point

class Whole_game(): # 整个大局游戏的逻辑放在这里。  
    def __init__(self, number_of_players = 2, rounds = 100): # here I initialize the game.
        self.rounds = min(max(1, rounds), 1000)  # 限制回合数在1-1000之间
        self.number_of_players = number_of_players
        # choose strategy and initialize players
        self.players = []
        for i in range(number_of_players):
            name = f"player{i + 1}"
            self.players.append(Prisoner(name, strategies.cooperate))  # 默认策略设为cooperate

        # Choose the mode for the game.
        self.mode = self.choose_mode(number_of_players)

        self.whole_game_record = {
            "scores": {player.name: player.point for player in self.players},
            "game_mode": "{mode.__name__}"
        }
        self.current_game = None  # 添加此行以存储当前游戏
        # Done! But not yet call simple game.
    
    def play_whole_game(self):
       self.mode()

    def choose_mode(self, num_of_players):
        if (num_of_players == 2):
            return self.simple_game
        else:
            return self.tournament

    def simple_game(self): # Have just two players
        player1 = self.players[0]
        player2 = self.players[1]
        rounds = self.rounds
        self.current_game = A_game(player1, player2, rounds)
        self.current_game.play()
        # 将游戏记录复制给玩家
        player1.game_record = self.current_game.game_record
        player2.game_record = self.current_game.game_record

    def tournament(self):
        """
        This function deals with a whole game between more than 2 players.
        It execute the games between every two players.
        """
        for i in range(self.number_of_players):
            for j in range(i + 1, self.number_of_players):
                player1 = self.players[i]
                player2 = self.players[j]
                rounds = self.rounds
                a_game = A_game(player1, player2, rounds)
                a_game.play()

class A_game(): # 一局两个人的游戏的逻辑放在这里
    @classmethod

    def __init__(self, player1, player2, rounds = 100):
        self.rounds = min(max(1, rounds), 1000)  # 限制回合数在1-1000之间
        self.player1 = player1
        self.player2 = player2
        self.player1.player0or1 = 0
        self.player2.player0or1 = 1        
        self.game_record ={
            "history": [],
            "the_number_of_round": 0,
            "player1_point": player1.point,
            "player2_point": player2.point, # 之所以这个字典里还要存一遍双方目前分数，是为了给strategy函数传递。
        }

    def play(self):
        """
        两个人的一局游戏 包括rounds次的博弈
        a game between two people.
        """
        for _ in range(self.rounds):
            
            self.a_game_round(self.player1.decision(self.game_record, 0), self.player2.decision(self.game_record, 1))
        # 我考虑在开始一局游戏时就把0和1设置好（设置在对象内部），这样调用的strategy可以直接通过self.player0or1来得到自己在这局当中的编号。
            if self.player1.strategy is strategies.select_every_turn: # 如何判断函数是不是某个函数？或者如何调用函数的名字？
                self.update()

    def a_game_round(self, player1_decision, player2_decision):
        """
        一回合博弈 这里包含了效用函数
        This is just a bout of game, not the whole picture of game.
        It executes with 2 participants' strategy and judge the game point.
        It returns nothing.
        """
        self.game_record["the_number_of_round"] += 1
        self.game_record["history"].append((player1_decision, player2_decision))
        utility = round_judgement(utility_table, player1_decision, player2_decision)
        self.game_record["player1_point"] += utility[0]
        self.game_record["player2_point"] += utility[1]
        self.player1.point += utility[0]
        self.player2.point += utility[1]
        
        # 由于这里没有把更新game_record的函数和判断输赢的函数分开，导致在后续编写win-stay，lose-shift策略时出现困难。
        # 现更改成分离性更高的写法

    def update(self):
        """
        This function is to output the points every round.
        It should be used when we choose turn by turn.

        parameter:
            game_record(a dictionary)

        return nothing.
        """
        print(self.game_record)

def round_judgement(utility_table, player1_decision, player2_decision):
    """
    Decide the winner or loser.
    
    Take 2 argument and a utility table.
    
    Return a pair int which is how much points they gain.
    Like (5, 5)
    """
    if player1_decision and player2_decision:
        return (utility_table["cooperate for cooperate"], utility_table["cooperate for cooperate"])
    elif player1_decision and not player2_decision:
        return (utility_table["cooperate for betray"], utility_table["betray for cooperate"])
    elif not player1_decision and player2_decision:
        return (utility_table["betray for cooperate"], utility_table["cooperate for betray"])
    elif not player1_decision and not player2_decision:
        return (utility_table["betray for betray"], utility_table["betray for betray"])




