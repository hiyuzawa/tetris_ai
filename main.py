import pygame
import numpy as np
from population import Population
from field import Field
from play import make_colors, generate_tetrimino


def get_candidate_list(init_mino, field):
    """ 盤面の状況を踏まえて落下可能なテトリミノ候補をすべて返す

    :param init_mino: 与えられたテトリミノ
    :param field: 盤面
    :return: 落下可能な位置にあるテトリミノ配列 (落下の高さに応じてscore値をセットする)
    """
    candidate = []
    rotete_num = 1
    mino_type = init_mino.get_type()

    # タイプによって回転のバリエーションが2 or 4 となる
    if 1 <= mino_type <= 3:
        rotete_num = 2
    if mino_type >= 4:
        rotete_num = 4

    # 各回転パターンに応じて
    for i in range(rotete_num):
        mino = init_mino.clone(0, 0, i)

        # まずは最も左に寄せる
        while True:
            next_mino = mino.clone(-1, 0, 0)
            if next_mino.collision(field):
                break
            mino = next_mino
        base_mino = mino

        while True:
            mino = base_mino
            score = 0
            while True:
                # 可能なところまで落下させる
                next_mino = mino.clone(0, 1, 0)
                if next_mino.collision(field):
                    break
                mino = next_mino
                score += 1
            mino.set_score(score)
            candidate.append(mino)

            # １つづつ右に移動させる
            next_mino = base_mino.clone(1, 0, 0)
            if next_mino.collision(field):
                break
            base_mino = next_mino
    return candidate


def get_next(model, mino, field):
    """ モデルと盤面から与えれたテトリミノが落下位置を計算する

    :param model: モデル
    :param mino:  移動対象のテトリミノ
    :param field: 現在の盤面
    :return: 落下後の盤面のスコアが最も高いテトリミノ(落下後位置)
    """

    # 回転や左右移動を行って落下可能な候補を全て計算する
    candidate_mino = get_candidate_list(mino, field)
    max_score = np.NINF
    best_mino = None
    for m in candidate_mino:
        # 各落下候補において落下後の盤面の評価を行う(スコア計算を行う)
        field_score = field.get_field_score(m.get_blocks())
        s = model.activate(field_score)
        if max_score < s:
            best_mino = m
            max_score = s
    # 最もスコア値の高い落下位置を戻す
    return best_mino


def eval_network(model):
    """ モデルを自動で3回Playさせてスコアの平均を応答する

    :param model: モデル
    :return: 3回プレイしたスコアの平均値
    """
    scores = []
    for i in range(3):
        field = Field()
        i += 1
        score = 0
        while True:
            mino = generate_tetrimino()
            if mino.collision(field):
                break
            best_mino = get_next(model, mino, field)
            field.set_blocks(best_mino.get_blocks())
            field.line_erase()
            score += best_mino.get_score()
            scores.append(score)

    return np.average(scores)


def preview_ai(model):
    """ モデルを与えて自動でPlayする関数
    移動のアニメーションは無し、テトリミノが生成されたらモデルから算出された
    落下位置に一気に移動する

    :param model: モデル
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("tetris_ai")
    clock = pygame.time.Clock()
    colors = make_colors()
    font = pygame.font.SysFont("Arial", 40)

    field = Field()

    score = 0
    erase_line = 0
    game_over_flag = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        if game_over_flag:
            return score, erase_line

        # ランダムにテトリミノを生成する
        mino = generate_tetrimino()
        screen.fill((0, 0, 0))

        screen.blit(font.render("score: {}".format(score), True, (255, 255, 255)), (300, 100))
        screen.blit(font.render("erase: {}".format(erase_line), True, (255, 255, 255)), (300, 150))

        field.draw(screen, colors)
        mino.draw(screen, colors)
        pygame.display.update()
        clock.tick(30)

        # 生成した時点で当たり判定であればGame Over
        if mino.collision(field):
            game_over_flag = True

        # モデルと盤面の状況から落下位置を算出する
        mino = get_next(model, mino, field)
        field.set_blocks(mino.get_blocks())
        field.draw(screen, colors)

        screen.fill((0, 0, 0))
        field.draw(screen, colors)
        pygame.display.update()

        # 消去可能な行があれば消去
        erase = field.line_erase()
        if erase > 0:
            clock.tick(30)
            erase_line += erase
        else:
            clock.tick(30)

        score += mino.get_score()


def main():
    """メイン関数

    遺伝的アルゴリズムを用いて世代を繰り返す
    各世代の最もスコアの高い個体はプレビューを5回行いその平均スコアをアウトプットする
    :return:
    """
    pop_size = 50  # 各遺伝世代における個体数
    population = Population(size=pop_size)
    score = 0
    lines = 0
    for i in range(5):
        s, l = preview_ai(population.models[0])
        score += s
        lines += l
    print("score: {} line: {}".format(score/5, lines/5))


    iteration = 0
    while True:
        iteration += 1
        print("{} : ".format(iteration), end="")
        for i in range(pop_size):
            population.fitnesses[i] = eval_network(population.models[i])
            print("*".format(iteration), end="")
        print()

        print(population.fitnesses)
        best_model_idx = population.fitnesses.argmax()
        best_model = population.models[best_model_idx]
        score = 0
        lines = 0
        for i in range(5):
            s, l = preview_ai(best_model)
            score += s
            lines += l
        print("score: {} line: {}".format(score/5, lines/5))

        population = Population(size=pop_size, old_population=population)


if __name__ == "__main__":
    main()
