import torch
import torch.nn as nn
from config import input_size, output_size, weights_init_max, weights_init_min, device


class Network(nn.Module):
    """ PyTouchのモデル

    単純な1層の線形関数のネットワーク
    Input=9, Output=1 (InputはField.get_field_scoreで得られた盤面評価値(9次のNumpy.Array)
    """
    def __init__(self):
        super(Network, self).__init__()
        # 線形関数１層のみ
        self.output = nn.Linear(
            input_size, output_size, bias=False).to(device)
        # 今回は逆伝搬は必要ない
        self.output.weight.requires_grad_(False)
        # ウエイトを,一様分布で初期化
        nn.init.uniform_(self.output.weight,
                         a=weights_init_min, b=weights_init_max)

    def activate(self, x):
        """ 与えられたベクトルでモデル評価値を返す

        :param x: 9次元ベクトル(Numpy.Array)
        :return: 1次元ベクトル(評価結果)
        """
        with torch.no_grad():
            x = torch.from_numpy(x).float().to(device)
            x = self.output(x)
        return x
