from block import Block


class Tetrimino:
    """ Tetrimino(テトリスでは各ブロック(全７種）をこう呼ぶらしいを管理するクラス

    O(四角)
    I(棒)
    S
    Z
    J
    L
    T
    """

    def __init__(self, x, y, r, t):
        """ イニシャライザ

        初期位置とタイプでインスタンス化する
        どのTetriminoもBlockクラス4つの集合（初期ブロックの配置で各々の形をつくる）

        :param x: 初期位置 x
        :param y: 初期位置 y
        :param r: 初期回転 r
        :param t: テトリミノのタイプ
        """
        self.x = x
        self.y = y
        self.r = r
        self.t = t
        self.s = 0
        if t == 0:
            # 0 (四角)の形のブロック
            self.shape = [Block(-1, -1, t), Block(-1, 0, t), Block(0, 0, t), Block(0, -1, t)]
        if t == 1:
            # I の形のブロック
            self.shape = [Block(-2, 0, t), Block(-1, 0, t), Block(0, 0, t), Block(1, 0, t)]
        if t == 2:
            # S の形のブロック
            self.shape = [Block(-1, 0, t), Block(0, 0, t), Block(0, -1, t), Block(1, -1, t)]
        if t == 3:
            # Z の形のブロック
            self.shape = [Block(-1, -1, t), Block(0, -1, t), Block(0, 0, t), Block(1, 0, t)]
        if t == 4:
            # J の形のブロック
            self.shape = [Block(0, -2, t), Block(0, -1, t), Block(-1, 0, t), Block(0, 0, t)]
        if t == 5:
            # L の形のブロック
            self.shape = [Block(-1, -2, t), Block(-1, -1, t), Block(-1, 0, t), Block(0, 0, t)]  # L
        if t == 6:
            # T の形のブロック
            self.shape = [Block(-1, 0, t), Block(0, 0, t), Block(0, -1, t), Block(1, 0, t)]     # T

        for _ in range(r%4):
            for b in self.shape:
                b.rotate()

        for b in self.shape:
            b.move(x, y)

    def get_blocks(self):
        """ 現在のブロック4つを返す

        :return: 4つのBlockインスタンス配列
        """
        return self.shape

    def get_type(self):
        """ タイプを返す

        :return: タイプ
        """
        return self.t

    def collision(self, field):
        """ 壁や他のブロックとの接触判定
        field(盤面を引数にとり現在位置のBlockでfieldとの障害があれば当たり判定とする

        :param field: 盤面
        :return: True 当たり判定あり / False なし
        """
        for b in self.shape:
            x, y = b.get_pos()
            if x < 0 or x > 10:
                return True
            tile = field.get_tile(x, y)
            if tile != -1:
                return True
        return False

    def set_score(self, score):
        """ スコアをセットする
        :param score: スコア値(落下の高さ)
        :return:
        """
        self.s = score

    def get_score(self):
        """ スコアを得る
        :return: スコア値
        """
        return self.s

    def draw(self, screen, colors):
        """ 画面にブロックを描画する
        実際の描画処理はBlock内で行うのでここではそれを呼び出すだけ

        :param screen: PyGame Screen オブジェクト
        :param colors: PyGame Surface オブジェクト(色ブロックの配列)
        :return:
        """
        for b in self.shape:
            b.draw(screen, colors)

    def clone(self, dx=0, dy=0, dr=0):
        """ 指定の移動を行った後のクローンを生成する

        :param dx: x移動値
        :param dy: y移動値
        :param dr: r回転値
        :return: インスタンスから指定の移動回転を行った後のTetriminoオブジェクト
        """
        return Tetrimino(self.x+dx, self.y+dy, self.r+dr, self.t)