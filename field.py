import pygame
import numpy as np
import copy
from config import BLOCK_SIZE


class Field:
    """ テトリスの盤面全体を管理するクラス

    盤面の個々のブロックを
    ・9 = 壁
    ・-1 = 空き
    ・0-6 = 埋まっているブロック(値はブロック色)
    で表現する
    """

    EMPTY_LINE = [9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 9]
    FLOOR_LINE = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    def __init__(self):
        """ イニシャライザ

        self.tile が盤面を表す2次元配列
        高さは20マス
        """
        self.tiles = [self.FLOOR_LINE]
        for _ in range(20):
            self.tiles.insert(0, copy.deepcopy(self.EMPTY_LINE))

    def get_tile(self, x, y):
        """ 指定のタイルのブロック状況を返す

        :param x: x座標
        :param y: y座標
        :return: 与えられた座標にセットされている盤面の値
        """
        return self.tiles[y][x]

    def set_blocks(self, blocks):
        """ ブロックを盤面に確定反映する

        :param blocks:
        :return:
        """
        for block in blocks:
            self.tiles[block.y][block.x] = block.c

    def line_erase(self):
        """ 埋まった行があればそれを消す関数

        :return: 消去された行数
        """
        erase = []
        for y in range(len(self.tiles)-1):  # 全ての行について捜査する
            flag = True
            for x in range(len(self.tiles[0])):   # 横一列ブロックがすべて埋まっているか調べる
                if self.tiles[y][x] == -1:
                    flag = False
            if flag:  # flag = True である場合には埋まっているので消去リストに追加
                erase.append(y)
        # 埋まったラインがあった場合
        for i in erase:
            self.tiles.pop(i)  # そのラインを取り除く
            self.tiles.insert(0, copy.deepcopy(self.EMPTY_LINE))  # 最上部に新たなラインを追加する
        return len(erase)

    def draw(self, screen, colors):
        """ 画面に盤面を描画する

        :param screen: pygame の Screen オブジェクト
        :param colors: pygame の Surface (描画用の色ブロック)
        :return:
        """
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                if self.tiles[y][x] == 9:
                    pygame.draw.rect(screen, (80, 80, 80), (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                elif self.tiles[y][x] == -1:
                    pygame.draw.rect(screen, (80, 80, 80), (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
                else:
                    screen.blit(colors[self.tiles[y][x]], (BLOCK_SIZE*x, BLOCK_SIZE*y, BLOCK_SIZE, BLOCK_SIZE))

    def get_bit_field(self, candidate_blocks=None):
        """ 盤面の評価用の-1, 1 の2値の盤面値を返す関数

        :param candidate_blocks: 現在の盤面に特定のテトリミノが次に配置されたと仮定した状況で応答する
        :return: 盤面の2次元配列(埋まっている:1, 空いている:0). (壁は含めない)
        """
        bit_field = [[0 if self.tiles[y][x] == -1 else 1 for x in range(1, len(self.tiles[0])-1)] for y in range(0, len(self.tiles)-1)]
        if candidate_blocks:
            for block in candidate_blocks:
                bit_field[block.y][block.x-1] = 1
        return bit_field

    def get_field_score(self, candidate_blocks=None):
        """ 盤面の評価値を返す

        :param candidate_blocks: 現在の盤面に特定のテトリミノが次に配置されたと仮定した状況で評価する
        :return: 9つの1次元配列 (Numpy array型)
        https://ichi.pro/identeki-arugorizumu-de-tetorisu-gb-no-sekai-kiroku-o-yaburu-118795294920347

        戻り配列詳細:
        0: 高さ総合計
        1: 穴数合計
        2: 少なくとも1つ以上穴のある列数
        3: 行遷移数
        4: 列遷移数
        5: 凸凹数
        6: ブロックが1つも無い列数
        7: 最大井戸高さ
        8: 消去行数
        """
        area = np.array(self.get_bit_field(candidate_blocks))
        peaks = self.get_peaks(area)
        highest_peak = np.max(peaks)
        agg_height = np.sum(peaks)

        holes = self.get_holes(peaks, area)
        n_holes = np.sum(holes)
        n_cols_with_holes = np.count_nonzero(np.array(holes) > 0)

        row_transitions = self.get_row_transition(area, highest_peak)
        col_transitions = self.get_col_transition(area, peaks)

        bumpiness = self.get_bumpiness(peaks)

        num_pits = np.count_nonzero(np.count_nonzero(area, axis=0) == 0)

        wells = self.get_wells(peaks)
        max_wells = np.max(wells)

        cleard = area.min(axis=1).sum()

        return np.array([agg_height, n_holes, n_cols_with_holes,
                         row_transitions, col_transitions, bumpiness, num_pits, max_wells, cleard])

    @staticmethod
    def get_peaks(area):
        """高さ計算

        :param area: 盤面
        :return: 各列での最大のブロックの高さ
        """
        peaks = np.array([])
        for col in range(area.shape[1]):
            if 1 in area[:, col]:
                p = area.shape[0] - np.argmax(area[:, col], axis=0)
                peaks = np.append(peaks, p)
            else:
                peaks = np.append(peaks, 0)
        return peaks

    @staticmethod
    def get_holes(peaks, area):
        """ 穴数計算

        :param peaks: get_peaksで得られた値(各列での最大の高さ)
        :param area: 盤面
        :return: 各列での穴(空白)の数
        """
        holes = []
        for col in range(area.shape[1]):
            start = -peaks[col]
            if start == 0:
                holes.append(0)
            else:
                holes.append(np.count_nonzero(area[int(start):, col] == 0))
        return holes

    @staticmethod
    def get_row_transition(area, highest_peak):
        """行遷移数

        :param area: 盤面
        :param highest_peak: 最大のブロック高さ
        :return: 各行の占有タイルから非占有タイルへの遷移の合計数
        """
        s = 0
        for row in range(int(area.shape[0] - highest_peak), area.shape[0]):
            for col in range(1, area.shape[1]):
                if area[row, col] != area[row, col - 1]:
                    s += 1
        return s

    @staticmethod
    def get_col_transition(area, peaks):
        """列遷移数

        :param area: 盤面
        :param peaks: get_peaksで得られた値(各列での最大の高さ)
        :return: 各列の占有タイルから非占有タイルへの遷移の合計数
        """
        s = 0
        for col in range(area.shape[1]):
            if peaks[col] <= 1:
                continue
            for row in range(int(area.shape[0] - peaks[col]), area.shape[0] - 1):
                if area[row, col] != area[row + 1, col]:
                    s += 1
        return s

    @staticmethod
    def get_bumpiness(peaks):
        """ 凸凹値

        :param peaks: get_peaksで得られた値(各列での最大の高さ)
        :return: 隣り合う列間の絶対的な高さの差の合計
        """
        s = 0
        for i in range(9):
            s += np.abs(peaks[i] - peaks[i + 1])
        return s

    @staticmethod
    def get_wells(peaks):
        """ 最も深い井戸

        :param peaks: get_peaksで得られた値(各列での最大の高さ)
        :return: 各列で最も深い井戸
        """
        wells = []
        for i in range(len(peaks)):
            if i == 0:
                w = peaks[1] - peaks[0]
                w = w if w > 0 else 0
                wells.append(w)
            elif i == len(peaks) - 1:
                w = peaks[-2] - peaks[-1]
                w = w if w > 0 else 0
                wells.append(w)
            else:
                w1 = peaks[i - 1] - peaks[i]
                w2 = peaks[i + 1] - peaks[i]
                w1 = w1 if w1 > 0 else 0
                w2 = w2 if w2 > 0 else 0
                w = w1 if w1 >= w2 else w2
                wells.append(w)
        return wells


if __name__ == "__main__":
    import pprint

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, 9]
    fields.tiles[17] = [9, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 9]
    fields.tiles[18] = [9, -1, 1, 1, 1, -1, 1, -1, 1, -1, -1, 9]
    fields.tiles[19] = [9, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 9]
    fields.tiles[17] = [9, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 9]
    fields.tiles[18] = [9, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 9]
    fields.tiles[19] = [9, -1, 1, -1, -1, 1, 1, 1, -1, 1, -1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, 9]
    fields.tiles[17] = [9, -1, -1, -1, 1, -1, -1, -1, 1, 1, 1, 9]
    fields.tiles[18] = [9, -1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 9]
    fields.tiles[19] = [9, 1, 1, -1, 1, 1, 1, 1, -1, -1, 1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 9]
    fields.tiles[17] = [9, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 9]
    fields.tiles[18] = [9, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 9]
    fields.tiles[19] = [9, -1, 1, -1, -1, 1, 1, 1, -1, 1, -1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[15] = [9, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 9]
    fields.tiles[16] = [9, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1, 9]
    fields.tiles[17] = [9, -1, 1, 1, -1, 1, -1, 1, -1, -1, 1, 9]
    fields.tiles[18] = [9, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9]
    fields.tiles[19] = [9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 9]
    fields.tiles[17] = [9, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, 9]
    fields.tiles[18] = [9, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, 9]
    fields.tiles[19] = [9, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 9]
    print(fields.get_field_score())

    fields = Field()
    fields.tiles[16] = [9, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, 9]
    fields.tiles[17] = [9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9]
    fields.tiles[18] = [9, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, 9]
    fields.tiles[19] = [9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9]
    print(fields.get_field_score())

    fields = Field()
    print(fields.get_field_score())