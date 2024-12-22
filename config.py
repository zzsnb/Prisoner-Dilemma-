# 通过这个文件，就可以让我每次更改策略/添加策略的时候，只需要更改config.py文件和strategies.py.
STRATEGY_CONFIG = {
    'cooperate': {
        'name': '始终合作',
        'function': 'cooperate',
        'modes': ['single', 'two', 'multi']  # 该策略可用于哪些模式
    },
    'betray': {
        'name': '始终背叛',
        'function': 'betray',
        'modes': ['single', 'two', 'multi']
    },
    'select_every_turn': {
        'name': '逐轮选择',
        'function': 'select_every_turn',
        'modes': ['single', 'two']  # 多人模式下不可用
    },
    'retaliate': {
        'name': '以牙还牙',
        'function': 'retaliate',
        'modes': ['single', 'two', 'multi']
    },
    'retaliate2': {
        'name': '两次以牙还牙',
        'function': 'retaliate2',
        'modes': ['single', 'two', 'multi']
    },
    'totalrandom': {
        'name': '随机选择',
        'function': 'totalrandom',
        'modes': ['single', 'two', 'multi']
    },
    'judas': {
        'name': '犹大策略',
        'function': 'judas',
        'modes': ['single', 'two', 'multi']
    },
    'win_stay_lose_shift': {
        'name': '赢留输变',
        'function': 'win_stay_lose_shift',
        'modes': ['single', 'two', 'multi']
    },
    'reputation': {
        'name': '声誉策略',
        'function': 'reputation',
        'modes': ['single', 'two', 'multi']
    }
}

# 游戏设置
GAME_CONFIG = {
    'default_rounds': 10,
    'min_rounds': 1,
    'max_rounds': 1000
}
