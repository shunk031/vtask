# -*- coding: utf-8 -*-

import os
import pandas as pd
import math

DATA_DIR = os.path.join(os.path.dirname(
    os.path.realpath("__file__")), "ml-100k")

ALL_USERS = 943
ALL_ITEMS = 1682
ALL_RATING = 100000


def sim_pearson(user1, user2):

    # ユーザの評価値の平均を計算
    user1_mean = user1.mean()
    user2_mean = user2.mean()

    # ピアソン相関係数の分子部分を計算
    _sum = 0
    for i in range(1, ALL_ITEMS + 1):
        movie_name = "movie%d" % i

        # 欠損値を含まない評価値どうしで計算を行う
        if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):
            _calc = (user1[movie_name] - user1_mean) * \
                    (user2[movie_name] - user2_mean)

            _sum += _calc

    # ピアソン相関係数の分母部分を計算
    sos1 = 0
    sos2 = 0
    for i in range(1, ALL_ITEMS + 1):
        movie_name = "movie%d" % i

        # 欠損値を含まない評価値どうしで計算を行う
        if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):
            _v1 = (user1[movie_name] - user1_mean) ** 2
            _v2 = (user2[movie_name] - user2_mean) ** 2

            sos1 += _v1
            sos2 += _v2

    _sqrt1 = math.sqrt(sos1)
    _sqrt2 = math.sqrt(sos2)

    # ピアソン相関係数を計算する
    pearson_corr = _sum / (_sqrt1 * _sqrt2)
    return pearson_corr


def main():
    movie_table_file = "movie_table.csv"
    movie_data = pd.read_csv(movie_table_file, index_col=0)

    user1 = movie_data.ix['user1']
    user2 = movie_data.ix['user2']

    pc = sim_pearson(user1, user2)
    print("pearson corr = %f" % pc)


if __name__ == '__main__':
    main()
