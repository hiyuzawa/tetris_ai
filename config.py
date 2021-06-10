BLOCK_SIZE = 20             # 各ブロックのサイズ(描画用サイズ)
BLOCK_IMG_SIZE = 40         # 各ブロックのサイズ(原画(tile.png)の各サイズ)

elitism_pct = 0.2           # 交叉を行う際に優秀な個体としてそのまま世代以降する割合
mutation_prob = 0.2         # 突然変異を行う確率
weights_mutate_power = 0.5  # 突然変異でのノイズ割合

input_size = 9              # PyTouch NetworkモデルのInput次数
output_size = 1             # PyTouch NetworkモデルのOutput次数
weights_init_min = -1       # PyTouch 初期ウエイト下限
weights_init_max = 1        # PyTouch 初期ウエイト上限
device = 'cpu'              # PyTouch は CPU を利用する
