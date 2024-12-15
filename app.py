"""This is a game theory game which is known as "prisoners' dilemma"."""

# I set True for cooperate, False for betray.
import strategies 

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
        self.rounds = rounds
        
        # choose strategy and initialize players
        self.players = []
        for i in range(number_of_players):
            name = f"player{i + 1}"
            strategy = Whole_game.choose_strategy(name)
            self.players.append(Prisoner(name, strategy))

        # Choose the mode for the game.
        self.mode = Whole_game.simple_game
        "***If there are other game types, here should be changed.***"

        self.whole_game_record = {
            "scores": {player.name: player.point for player in self.players},
            "game_mode": "{mode.__name__}"
        }
        # Done! But not yet call simple game.
    
    def choose_strategy(name): # 如果增加了新的策略，那么策略函数这里必须要更改。
        '''
        while True:
            user_input = input("Please choose the strategy for {name}.\n" # if there are other strategies, here should be changed
                            + "B for always betray\n"
                            + "C for always cooperate\n"
                            + "T for choosing turn by turn\n"
                            + "R for Tit-for-Tat\n"
                            + "R2 for Tit-for-2Tat\n"
                            + "RD for random\n").strip().lower()
            if user_input in ["c", "b", "t", "r", "r2", "rd"]: # if there are other strategies, here should be changed
                break
            else:
                print("Invalid input, there are no this kinds of stragetegy.")

        match user_input:# if there are other strategies, here should be changed
            case "c":
                return strategies.cooperate
            case "b":
                return strategies.betray
            case "t":
                return strategies.select_every_turn
            case "r":
                return strategies.retaliate
            case "r2":
                return strategies.retaliate2
            case "rd":
                return strategies.random
        '''
    # 定义一个策略映射字典，键为用户输入的选项，值为相应的策略函数
        strategy_map = {
            "c": strategies.cooperate,         # 始终合作
            "b": strategies.betray,            # 始终背叛
            "t": strategies.select_every_turn, # 轮流选择
            "r": strategies.retaliate,         # 以牙还牙
            "r2": strategies.retaliate2,       # Tit-for-2Tat
            "rd": strategies.totalrandom,           # 随机
            "jd": strategies.judas
        }

        while True:
            user_input = input(f"Please choose the strategy for {name}.\n"
                            + "B for always betray\n"
                            + "C for always cooperate\n"
                            + "T for choosing turn by turn\n"
                            + "R for Tit-for-Tat\n"
                            + "R2 for Tit-for-2Tat\n"
                            + "RD for random\n"
                            + "JD for Judas(cooperate when winning and betray when losing)\n").strip().lower()
            
            # 检查用户输入是否有效
            if user_input in strategy_map:
                return strategy_map[user_input]  # 返回对应的策略函数
            else:
                print("Invalid input, there is no such strategy.")

    def simple_game(self): # Have just two players
        player1 = self.players[0]
        player2 = self.players[1]
        rounds = self.rounds
        the_only_game = A_game(player1, player2, rounds)
        the_only_game.play()

    def tournament():
        return "***Not Complete Yet.***"

class A_game(): # 一局两个人的游戏的逻辑放在这里
    @classmethod

    def __init__(self, player1, player2, rounds = 100):
        self.rounds = rounds
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
        self.utility_table = {
            "cooperate for betray": 0,
            "betray for cooperate": 5,
            "cooperate for cooperate": 3,
            "betray for betray": 0
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
        self.game_record["history"].append((player1_decision, player2_decision))
        utility = self.round_judgement(player1_decision, player2_decision)
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

    def round_judgement(self, player1_decision, player2_decision):
        """
        Decide the winner or loser.
        
        Take 2 argument and a utility table.
        
        Return a pair int which is how much points they gain.
        Like (5, 5)
        """
        if player1_decision and player2_decision:
            return (self.utility_table["cooperate for cooperate"], self.utility_table["cooperate for cooperate"])
        elif player1_decision and not player2_decision:
            return (self.utility_table["cooperate for betray"], self.utility_table["betray for cooperate"])
        elif not player1_decision and player2_decision:
            return (self.utility_table["betray for cooperate"], self.utility_table["cooperate for betray"])
        elif not player1_decision and not player2_decision:
            return (self.utility_table["betray for betray"], self.utility_table["betray for betray"])

if __name__ == "__main__":
    # 创建游戏实例，设置玩家数量和回合数
    game = Whole_game(number_of_players=2, rounds=5)
    
    # 启动简单游戏模式
    game.simple_game()

    # 输出最终分数
    for player in game.players:
        print(f"{player.name} final score: {player.point}")



    