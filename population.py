import numpy as np
import torch
from network import Network
from config import input_size, elitism_pct, mutation_prob, weights_mutate_power, device


class Population:
    """ 遺伝的アルゴリズムの各世代を管理するクラス
    """

    def __init__(self, size=50, old_population=None):
        """ イニシャライザ

        :param size: 各世代の個体数
        :param old_population: (次世代を生成する場合には前世代のPopulationを与える)
        """
        self.size = size
        if old_population is None:
            # 前世代なしの場合は、個体数全て初期値でモデルを生成する
            self.models = [Network() for i in range(size)]
        else:
            # 前世代が与えられた場合は交叉(crossover),突然変異(mutate)を行い次世代を生成する
            self.old_models = old_population.models
            self.old_fitnesses = old_population.fitnesses
            self.models = []
            self.crossover()
            self.mutate()
        # 各個体の評価値を保存する配列を初期化
        self.fitnesses = np.zeros(self.size)

    def crossover(self):
        """ 交叉(crossover)
        :return:
        """
        # 全ての個体の評価値の合計および各個体評価値を正規化
        sum_fitnesses = np.sum(self.old_fitnesses)
        probs = [self.old_fitnesses[i] / sum_fitnesses for i in
                 range(self.size)]

        sort_indices = np.argsort(probs)[::-1]
        for i in range(self.size):
            if i < self.size * elitism_pct:
                # 優秀な個体は(上位20%)はそのまま
                model_c = self.old_models[sort_indices[i]]
            else:
                # それ以外はランダムな2つの個体をかけ合わせる
                a, b = np.random.choice(self.size, size=2, p=probs,
                                        replace=False)
                prob_neuron_from_a = 0.5

                # モデルの各ウエイトを50/50の確率で交叉
                model_a, model_b = self.old_models[a], self.old_models[b]
                model_c = Network()

                for j in range(input_size):
                    if np.random.random() > prob_neuron_from_a:
                        model_c.output.weight.data[0][j] = \
                            model_b.output.weight.data[0][j]
                    else:
                        model_c.output.weight.data[0][j] = \
                            model_a.output.weight.data[0][j]

            self.models.append(model_c)

    def mutate(self):
        """ 突然変異(mutate)
        :return:
        """
        for model in self.models:
            for i in range(input_size):
                # 一定の確率(20%)で突然変異を行ったモデルとする
                if np.random.random() < mutation_prob:
                    # 一定のノイズをモデルに加える
                    with torch.no_grad():
                        noise = torch.randn(1).mul_(
                            weights_mutate_power).to(device)
                        model.output.weight.data[0][i].add_(noise[0])