from config import BLOCK_SIZE


class Block:
    """ 1つのブロックをこれで管理するクラス

    テトリスのゲーム内ブロック(４ブロックの塊)は Tetrimino で集合体とするが
    このBlock４つでそれが構成される。
    上下左右の動作および回転はこのクラスで１ブロック単位で行う
    """

    def __init__(self, x, y, c):
        """ イニシャライザ

        :param x: 初期位置 x
        :param y: 初期位置 y
        :param c: 色インデックス
        """
        self.x = x
        self.y = y
        self.c = c

    def get_pos(self):
        """ 現在の位置を返す

        :return: ブロックの位置
        """
        return self.x, self.y

    def move(self, x, y):
        """x, y づつ移動する

        :param x: x移動値
        :param y: y移動値
        :return:
        """
        self.x += x
        self.y += y

    def rotate(self):
        """ 回転させる
        時計回りのみサポート
        :return:
        """
        x = self.x
        y = self.y
        self.x = -y
        self.y = x

    def draw(self, screen, colors):
        """ 盤面にブロックを描画する
        :param screen: PyGame Screen オブジェクト
        :param colors: PyGame Surface オブジェクト(ブロック用の色配列)
        :return:
        """
        screen.blit(colors[self.c], (BLOCK_SIZE*self.x, BLOCK_SIZE*self.y, BLOCK_SIZE, BLOCK_SIZE))
