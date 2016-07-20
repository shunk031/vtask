# -*- coding: utf-8 -*-

import os
import pandas as pd
import math
import time

DATA_DIR = os.path.join(os.path.dirname(
    os.path.realpath("__file__")), "ml-100k")

ALL_USERS = 943
ALL_ITEMS = 1682
ALL_RATING = 100000


def sim_pearson(user1, user2):

    # 同じデータ同士では0を返すようにする
    if user1.equals(user2):
        return 0

    # ユーザの評価値の平均を計算
    user1_mean = user1.mean()
    user2_mean = user2.mean()

    # ピアソン相関係数の分子部分を計算
    _sum = 0
    for i in range(1, ALL_ITEMS + 1):
        movie_name = "movie%d" % i

        # 欠損値を含まない評価値どうしで計算を行う
        if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):

            # print("user1[%s] = %f, user2[%s] = %f" % (movie_name,
            # user1[movie_name], movie_name, user2[movie_name]))

            _calc = (user1[movie_name] - user1_mean) * \
                    (user2[movie_name] - user2_mean)

            _sum += _calc

            # print("sum = %f" % _sum)

    # ピアソン相関係数の分母部分を計算
    sos1 = 0
    sos2 = 0
    for i in range(1, ALL_ITEMS + 1):
        movie_name = "movie%d" % i

        # 欠損値を含まない評価値どうしで計算を行う
        if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):
            _v1 = (user1[movie_name] - user1_mean) ** 2
            _v2 = (user2[movie_name] - user2_mean) ** 2

            # print("%s: v1 = %f, v2 = %f" % (movie_name, _v1, _v2))

            sos1 += _v1
            sos2 += _v2

    _sqrt1 = math.sqrt(sos1)
    _sqrt2 = math.sqrt(sos2)

    # print("sos1 = %.1f, sos2 = %.1f" % (sos1, sos2))
    # print("sqrt1 = %.1f, sqrt2 = %.1f" % (_sqrt1, _sqrt2))

    # ピアソン相関係数を計算する
    try:
        pearson_corr = _sum / (_sqrt1 * _sqrt2)

    except ZeroDivisionError as e:
        pearson_corr = 0

    return pearson_corr


def get_similar_user(target_user, movie_data):
    score_dict = {}
    best_score = {}

    for i in range(1, ALL_USERS + 1):
        user_name = "user%d" % i

        user = movie_data.ix[user_name]
        pc = sim_pearson(target_user, user)
        score_dict[user_name] = pc

    count = 0
    for user, score in sorted(score_dict.items(), key=lambda x: x[1], reverse=True):
        if count == 10:
            break

        print("%s: %f" % (user, score))
        best_score[user] = score
        count += 1


def recommend(target_user, movie_data):

    start = time.time()

    sum1 = 0
    for i in range(1, ALL_USERS + 1):
        user_name = "user%d" % i
        user = movie_data.ix[user_name]

        for j in range(1, ALL_ITEMS + 1):
            movie_name = "movie%d" % j

            if not(math.isnan(user[movie_name])):
                pc = sim_pearson(target_user, user)
                sum1 += user[movie_name] * pc

    sum2 = 0
    for i in range(1, ALL_USERS + 1):
        user_name = "user%d" % i
        user = movie_data.ix[user_name]

        pc = sim_pearson(target_user, user)
        sum2 += math.fabs(pc)

    recom = sum1 / sum2

    end = time.time() - start
    print("processing time: %.1f [sec]" % end)

    return recom


def main():

    # データの読み込み
    movie_table_file = "movie_table.csv"
    movie_data = pd.read_csv(movie_table_file, index_col=0)

    user1 = movie_data.ix['user1']
    user2 = movie_data.ix['user2']

    # ピアソン相関係数を計算する
    pc = sim_pearson(user1, user2)
    print("pearson corr = %f" % pc)

    # target_userに似ているユーザを上位10人表示する
    target_user = movie_data.ix['user2']
    get_similar_user(target_user, movie_data)


if __name__ == '__main__':
    main()
