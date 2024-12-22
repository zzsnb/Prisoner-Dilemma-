"""web server for prisoner dilemma."""
import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from strategies import * 
from app import utility_table 
from app import Whole_game, Prisoner
from config import STRATEGY_CONFIG, GAME_CONFIG

app_gui = Flask(__name__)

# 配置 Flask-Session
app_gui.config["SESSION_PERMANENT"] = False
app_gui.config["SESSION_TYPE"] = "filesystem"
Session(app_gui)

# 添加密钥(我咋感觉这行没啥用啊？感觉就是Flask所必须的)
app_gui.secret_key = os.urandom(24)

# 替换原来的 strategy_names
def get_available_strategies(mode):
    """获取指定模式下可用的策略"""
    return {k: v['name'] for k, v in STRATEGY_CONFIG.items() if mode in v['modes']}

@app_gui.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@app_gui.route('/begin', methods=["POST"])
def begin():
    # 在开始新游戏时清除之前的游戏记录
    session.pop('game_history', None)
    session.pop('final_scores', None)
    session.pop('single_game_state', None)
    session.pop('game_state', None)
    
    if not request.form.get("player_number"):
        flash("请输入玩家数量")
        return redirect(url_for('index'))
    
    try:
        number = int(request.form.get("player_number"))
        if number < 1:
            flash("玩家数量必须大于等于1")
            return redirect(url_for('index'))
        
        session["number_of_players"] = number
        if number == 1:
            return redirect(url_for('single_player'))
        elif number == 2:
            return redirect(url_for('two_players'))
        else:
            return redirect(url_for('multi_players'))
    except ValueError:
        flash("请输入有效的数字")
        return redirect(url_for('index'))

@app_gui.route('/single_player', methods=["GET", "POST"])
def single_player():
    if request.method == "GET":
        return render_template("single_player.html",
                            utility_table=utility_table,
                            game_history=session.get("game_history", []),
                            final_scores=session.get("final_scores"),
                            strategies=get_available_strategies('single'),
                            show_round_choices=session.get('single_game_state') is not None,
                            current_round=session.get('single_game_state', {}).get('current_round'))
    if request.method == "POST":
        # 每次点击“进入游戏”按钮，都清除之前的游戏记录
        session.pop('game_history', None)
        session.pop('final_scores', None)
        session.pop('single_game_state', None)
        
        player_strategy = request.form.get("player_strategy")
        computer_strategy = request.form.get("computer_strategy")
        rounds = int(request.form.get("rounds", 100))
        
        # 验证输入
        if not all([player_strategy, computer_strategy]):
            flash("请填写所有必需的信息")
            return redirect(url_for('single_player'))
        
        if rounds < 1 or rounds > 1000:
            flash("回合数必须在1-1000之间")
            return redirect(url_for('single_player'))
            
        # 如果玩家选择了逐轮选择策略
        if player_strategy == 'select_every_turn':
            session['single_game_state'] = {
                'rounds': rounds,
                'current_round': 1,
                'player_strategy': player_strategy,
                'computer_strategy': computer_strategy,
                'player_total': 0,
                'computer_total': 0,
                'game_history': []
            }
            return render_template('single_player.html',
                                utility_table=utility_table,
                                show_round_choices=True,
                                current_round=1,
                                game_history=[],
                                strategies=get_available_strategies('single'))
        else:
        # 如果是自动策略，执行原有逻辑
            player1 = Prisoner("玩家", globals()[player_strategy])
            player2 = Prisoner("电脑", globals()[computer_strategy])
        
        # 创建游戏实例并设置回合数
        game = Whole_game(number_of_players=2, rounds=rounds)
        game.players = [player1, player2]
        
        # 开始游戏
        game.play_whole_game()
        
        # 获取最后一局游戏的记录
        final_game = game.current_game.game_record if game.current_game else None
        
        # 记录游戏历史
        game_history = []
        if final_game and "history" in final_game:
            player1_score = 0
            player2_score = 0
            for i, (p1_choice, p2_choice) in enumerate(final_game["history"]):
                # 计算当前回合的得分
                utility = round_judgement(utility_table, p1_choice, p2_choice)
                player1_score += utility[0]
                player2_score += utility[1]
                
                round_data = {
                    "round_number": i + 1,
                    "player_choice": p1_choice,
                    "computer_choice": p2_choice,
                    "player_score": player1_score,  # 使用累计得分
                    "computer_score": player2_score  # 使用累计得分
                }
                game_history.append(round_data)
        
        # 保存到session
        session["game_history"] = game_history
        session["final_scores"] = {
            "player": {
                "name": player1.name,
                "strategy": player_strategy,
                "score": player1.point
            },
            "computer": {
                "name": player2.name,
                "strategy": computer_strategy,
                "score": player2.point
            }
        }
        
        return render_template("single_player.html",
                             utility_table=utility_table,
                             game_history=game_history,
                             final_scores=session["final_scores"],
                             strategies=get_available_strategies('single'))
    
    return render_template("single_player.html",
                         utility_table=utility_table,
                         game_history=session.get("game_history", []),
                         final_scores=session.get("final_scores"),
                         strategies=get_available_strategies('single'))

@app_gui.route('/make_choice_single', methods=["POST"])
def make_choice_single():
    if 'single_game_state' not in session:
        return redirect(url_for('single_player'))
        
    game_state = session['single_game_state']
    choice = request.form.get('choice') == 'cooperate'
    
    # 获取电脑的选择
    computer = Prisoner("电脑", globals()[game_state['computer_strategy']])
    game_history = game_state.get('game_history', [])
    game_record = {
        "history": [(r.get("player_choice", True), r.get("computer_choice", True)) for r in game_history],
        "the_number_of_round": len(game_history)
    }
    computer_choice = computer.decision(game_record, 1)
    
    # 计算得分
    utility = round_judgement(utility_table, choice, computer_choice)
    game_state['player_total'] += utility[0]
    game_state['computer_total'] += utility[1]
    
    # 记录这一轮的结果
    round_data = {
        "round_number": game_state['current_round'],
        "player_choice": choice,
        "computer_choice": computer_choice,
        "player_score": game_state['player_total'],
        "computer_score": game_state['computer_total']
    }
    game_state['game_history'].append(round_data)
    
    # 检查游戏是否结束
    if game_state['current_round'] >= game_state['rounds']:
        session['final_scores'] = {
            "player": {
                "strategy": game_state['player_strategy'],
                "score": game_state['player_total']
            },
            "computer": {
                "strategy": game_state['computer_strategy'],
                "score": game_state['computer_total']
            }
        }
        session['game_history'] = game_state['game_history']
        session.pop('single_game_state', None)
        return render_template('single_player.html',
                             utility_table=utility_table,
                             game_history=game_state['game_history'],
                             final_scores=session['final_scores'])
    
    # 准备下一轮
    game_state['current_round'] += 1
    session['single_game_state'] = game_state
    
    return render_template('single_player.html',
                         utility_table=utility_table,
                         show_round_choices=True,
                         current_round=game_state['current_round'],
                         game_history=game_state['game_history'],
                         strategies=get_available_strategies('single'))

@app_gui.route('/two_players', methods=["GET", "POST"])
def two_players():
    if request.method == "GET":
        strategies = get_available_strategies('two')
        return render_template("two_players.html",
                            utility_table=utility_table,
                            strategies=strategies,
                            game_history=session.get("game_history", []),
                            final_scores=session.get("final_scores"))
    if request.method == "POST":
        # 清除之前的游戏记录
        session.pop('game_history', None)
        session.pop('final_scores', None)
        
        player1_strategy = request.form.get("player1_strategy")
        player2_strategy = request.form.get("player2_strategy")
        rounds = request.form.get("rounds", type=int, default=100)
        
        # 验证输入
        if not all([player1_strategy, player2_strategy, rounds]):
            flash("请填写所有必需信息")
            return redirect(url_for('two_players'))
            
        # 检查是否有人选择了逐轮选择策略
        needs_choice = (player1_strategy == 'select_every_turn' or 
                       player2_strategy == 'select_every_turn')
        
        if needs_choice:
            # 初始化游戏状态
            session['game_state'] = {
                'rounds': rounds,
                'current_round': 1,
                'player1_strategy': player1_strategy,
                'player2_strategy': player2_strategy,
                'waiting_for_player1': player1_strategy == 'select_every_turn',
                'waiting_for_player2': player2_strategy == 'select_every_turn',
                'player1_total': 0,
                'player2_total': 0,
                'choices': [],
                'game_history': []
            }
            return render_template('two_players.html',
                                utility_table=utility_table,
                                show_round_choices=True,
                                current_round=1,
                                waiting_for_player1=player1_strategy == 'select_every_turn',
                                waiting_for_player2=player2_strategy == 'select_every_turn',
                                strategies=get_available_strategies('two'))
        
        # 如果没有人选择逐轮选择，直接执行自动对战逻辑
        player1 = Prisoner("玩家1", globals()[player1_strategy])
        player2 = Prisoner("玩家2", globals()[player2_strategy])
        game = Whole_game(number_of_players=2, rounds=rounds)
        game.players = [player1, player2]
        game.play_whole_game()
        
        # 处理游戏记录
        final_game = game.current_game.game_record if game.current_game else None
        game_history = []
        if final_game and "history" in final_game:
            player1_score = 0
            player2_score = 0
            for i, (p1_choice, p2_choice) in enumerate(final_game["history"]):
                utility = round_judgement(utility_table, p1_choice, p2_choice)
                player1_score += utility[0]
                player2_score += utility[1]
                game_history.append({
                    "round_number": i + 1,
                    "player1_choice": p1_choice,
                    "player2_choice": p2_choice,
                    "player1_score": player1_score,
                    "player2_score": player2_score
                })
        
        session["game_history"] = game_history
        session["final_scores"] = {
            "player1": {
                "strategy": player1_strategy,
                "score": player1.point
            },
            "player2": {
                "strategy": player2_strategy,
                "score": player2.point
            }
        }
        
        return render_template("two_players.html",
                             utility_table=utility_table,
                             game_history=game_history,
                             final_scores=session["final_scores"],
                             strategies=get_available_strategies('two'))
    
    return render_template("two_players.html",
                         utility_table=utility_table,
                         strategies=get_available_strategies('two'),
                         game_history=session.get("game_history", []),
                         final_scores=session.get("final_scores"))

@app_gui.route('/make_choice', methods=["POST"])
def make_choice():
    if 'game_state' not in session:
        return redirect(url_for('two_players'))
        
    game_state = session['game_state']
    
    # 修复选择逻辑
    choice1 = None
    choice2 = None
    
    # 验证是否需要两个玩家都选择
    if game_state['waiting_for_player1'] and game_state['waiting_for_player2']:
        if not all([request.form.get('choice1'), request.form.get('choice2')]):
            flash("两个玩家都需要做出选择")
            return redirect(url_for('two_players'))
    elif game_state['waiting_for_player1'] and not request.form.get('choice1'):
        flash("请玩家1做出选择")
        return redirect(url_for('two_players'))
    elif game_state['waiting_for_player2'] and not request.form.get('choice2'):
        flash("请玩家2做出选择")
        return redirect(url_for('two_players'))

    # 获取或计算玩家1的选择
    if game_state['player1_strategy'] == 'select_every_turn':
        choice1 = request.form.get('choice1') == 'cooperate'
    else:
        player1 = Prisoner("玩家1", globals()[game_state['player1_strategy']])
        game_record = {
            "history": [(r["player1_choice"], r["player2_choice"]) for r in game_state['game_history']],
            "the_number_of_round": game_state['current_round']
        }
        choice1 = player1.decision(game_record, 0)

    # 获取或计算玩家2的选择
    if game_state['player2_strategy'] == 'select_every_turn':
        choice2 = request.form.get('choice2') == 'cooperate'
    else:
        player2 = Prisoner("玩家2", globals()[game_state['player2_strategy']])
        game_record = {
            "history": [(r["player1_choice"], r["player2_choice"]) for r in game_state['game_history']],
            "the_number_of_round": game_state['current_round']
        }
        choice2 = player2.decision(game_record, 1)
    
    # 计算得分
    utility = round_judgement(utility_table, choice1, choice2)
    game_state['player1_total'] += utility[0]
    game_state['player2_total'] += utility[1]
    
    # 记录这一轮的结果
    round_data = {
        'round_number': game_state['current_round'],
        'player1_choice': choice1,
        'player2_choice': choice2,
        'player1_score': game_state['player1_total'],
        'player2_score': game_state['player2_total']
    }
    game_state['game_history'].append(round_data)
    
    # 检查游戏是否结束
    if game_state['current_round'] >= game_state['rounds']:
        # 游戏结束，记录最终得分
        session['final_scores'] = {
            'player1': {
                'strategy': game_state['player1_strategy'],
                'score': game_state['player1_total']
            },
            'player2': {
                'strategy': game_state['player2_strategy'],
                'score': game_state['player2_total']
            }
        }
        # 清除游戏状态
        session.pop('game_state', None)
        return render_template('two_players.html',
                            utility_table=utility_table,
                            game_history=game_state['game_history'],
                            final_scores=session['final_scores'],
                            show_round_choices=False,
                            strategies=get_available_strategies('two'))
    
    # 准备下一轮
    game_state['current_round'] += 1
    game_state['waiting_for_player1'] = game_state['player1_strategy'] == 'select_every_turn'
    game_state['waiting_for_player2'] = game_state['player2_strategy'] == 'select_every_turn'
    session['game_state'] = game_state
    
    # 保存更新后的游戏状态
    session.modified = True
    
    # 返回更新后的页面
    return render_template('two_players.html',
                         utility_table=utility_table,
                         show_round_choices=True,
                         current_round=game_state['current_round'],
                         waiting_for_player1=game_state['waiting_for_player1'],
                         waiting_for_player2=game_state['waiting_for_player2'],
                         game_history=game_state['game_history'],
                         final_scores=session.get('final_scores'),
                         strategies=get_available_strategies('two'))

@app_gui.route('/multi_players', methods=["GET", "POST"])
def multi_players():
    if request.method == "GET":
        number_of_players = session.get("number_of_players", 3)
        return render_template('multi_players.html',
                            number_of_players=number_of_players,
                            strategies=get_available_strategies('multi'),
                            match_results=session.get('match_results'),
                            final_scores=session.get('final_scores'))
    if request.method == "POST":
        # 清除之前的游戏记录
        session.pop('match_results', None)
        session.pop('final_scores', None)
        
        # 获取回合数
        rounds = int(request.form.get("rounds", 10))
        
        # 获取所有玩家的策略
        number_of_players = session.get("number_of_players", 3)
        players = []
        for i in range(number_of_players):
            strategy = request.form.get(f"player{i+1}_strategy")
            if not strategy:
                flash("请为所有玩家选择策略")
                return redirect(url_for('multi_players'))
            players.append(Prisoner(f"玩家{i+1}", globals()[strategy]))
        
        # 创建游戏实例
        game = Whole_game(number_of_players=number_of_players, rounds=rounds)
        game.players = players
        
        # 开始游戏
        game.play_whole_game()
        
        # 记录对战结果
        match_results = []
        # 遍历每对玩家
        for i in range(number_of_players):
            for j in range(i + 1, number_of_players):
                # 创建一个新的游戏实例来记录这两个玩家的对战
                two_player_game = Whole_game(number_of_players=2, rounds=rounds)
                two_player_game.players = [
                    Prisoner(f"玩家{i+1}", globals()[request.form.get(f"player{i+1}_strategy")]),
                    Prisoner(f"玩家{j+1}", globals()[request.form.get(f"player{j+1}_strategy")])
                ]
                two_player_game.play_whole_game()
                
                # 记录这一对玩家的对战结果
                match_results.append({
                    'player1': f"玩家{i+1}",
                    'player2': f"玩家{j+1}",
                    'score1': two_player_game.players[0].point,
                    'score2': two_player_game.players[1].point
                })
        
        # 记录总分（所有对战累计）
        final_scores = []
        for i, player in enumerate(players):
            final_scores.append({
                'name': f"玩家{i+1}",
                'strategy': request.form.get(f"player{i+1}_strategy"),
                'score': player.point
            })
        
        # 按分数排序
        final_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 保存到session
        session['match_results'] = match_results
        session['final_scores'] = final_scores
        
        return render_template('multi_players.html',
                             number_of_players=number_of_players,
                             strategies=get_available_strategies('multi'),
                             match_results=match_results,
                             final_scores=final_scores)
    
    # GET请求时显示初始页面
    number_of_players = session.get("number_of_players", 3)
    return render_template('multi_players.html',
                         number_of_players=number_of_players,
                         strategies=get_available_strategies('multi'),
                         match_results=session.get('match_results'),
                         final_scores=session.get('final_scores'))

@app_gui.route('/update_utility', methods=["POST"])
def update_utility():
    if request.method == "POST":
        # 获取新的效用值（现在每个情况有两个值）
        new_utility = {
            "cooperate for cooperate": int(request.form.get('cc1')),  # 只保存玩家1的值
            "cooperate for betray": int(request.form.get('cb1')),
            "betray for cooperate": int(request.form.get('bc1')),
            "betray for betray": int(request.form.get('bb1'))
        }
        
        # 更新全局效用表
        utility_table.update(new_utility)
        session['utility_table'] = new_utility
        
        flash("效用值已更新", "success")
        return redirect(url_for('single_player'))

# 添加错误处理
@app_gui.errorhandler(404)
def page_not_found(e):
    flash("页面未找到")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app_gui.run(debug=True)
