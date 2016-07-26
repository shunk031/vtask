# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import math
import time
import csv


class Recommend:

    def __init__(self, rating_data, info_data, target_user):
        """
        :param TYPE dataset: データセットのファイル名
        :param TYPE info:    infoファイルのファイル名
        :rtype: TYPE
        """

        # PATHの追加
        self.DATA_DIR = os.path.join(os.path.dirname(
            os.path.realpath("__file__")), "ml-100k")

        # 評価データの読み込み
        self.rating_data = pd.read_csv(rating_data, index_col=0)
        # 評価データの基本情報の読み込み
        self.info_file = os.path.join(self.DATA_DIR, info_data)

        info_array = self._load_info_data()

        # 評価データの基本情報
        self.ALL_USERS = int(info_array[0])
        self.ALL_ITEMS = int(info_array[1])
        self.ALL_RATINGS = int(info_array[2])

        # レコメンドを行うターゲットユーザーのデータを抽出
        self.target_user = self.rating_data.ix[target_user]

        self._print_dataset_info()

    def _load_info_data(self):
        """
        infoファイルから情報を読み込む
        :rtype: TYPE info情報のリスト
        """
        info_array = []

        with open(self.info_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')

            for row in reader:
                info_ = row[0]
                info = info_.split(' ')
                info_array.append(info[0])

        return info_array

    def _print_dataset_info(self):
        """
        読み込んだデータの基本情報を出力する
        :rtype: TYPE なし
        """
        print("Loaded dataset")
        print("All users: %d, All items: %d, All ratings: %d" %
              (self.ALL_USERS, self.ALL_ITEMS, self.ALL_RATINGS))

    def sim_pearson(self, user1, user2):

        # 同じユーザ同士は0を返すようにする
        if user1.equals(user2):
            return 0.0

        user1_mean = user1.mean()
        user2_mean = user2.mean()

        _sum = 0
        _count = 0
        sos1 = 0
        sos2 = 0

        for i in range(1, self.ALL_ITEMS + 1):
            movie_name = "movie%d" % i

            if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):
                # 分子部分を計算
                _dev1 = user1[movie_name] - user1_mean
                _dev2 = user2[movie_name] - user2_mean
                _calc = _dev1 * _dev2
                _sum += _calc

                # 分母部分を計算
                _var1 = _dev1 ** 2
                _var2 = _dev2 ** 2
                sos1 += _var1
                sos2 += _var2

                _count += 1

        # 共通しているアイテムが1個以下の場合は0を返す
        if _count <= 1:
            return 0.0

        _sqrt1 = math.sqrt(sos1)
        _sqrt2 = math.sqrt(sos2)

        try:
            pearson_corr = _sum / (_sqrt1 * _sqrt2)
        except ZeroDivisionError as e:
            pearson_corr = 0

        return pearson_corr

    def get_similar_user(self):
        score_dict = {}
        best_score = {}

        for i in range(1, self.ALL_USERS + 1):
            user_name = "user%d" % i
            user_data = self.rating_data.ix[user_name]
            pc = self.sim_pearson(self.target_user, user_data)
            score_dict[user_name] = pc

        _count = 0
        for user, score in sorted(score_dict.items(), key=lambda x: x[1], reverse=True):
            if _count == 10:
                break

            print("%s: %f" % (user, score))
            best_score[user] = score
            _count += 1
            print("fin")

    def _calc_recom_score(self, target_movie):

        _sum1 = 0
        _sum2 = 0

        for i in range(1, self.ALL_USERS + 1):
            user_name = "user%d" % i
            user_data = self.rating_data.ix[user_name]

            if not(math.isnan(user_data[target_movie])):
                _pc = self.sim_pearson(self.target_user, user_data)
                _calc = _pc * (user_data[target_movie] - user_data.mean())
                _sum1 += _calc

                abs_pc = math.fabs(_pc)
                _sum2 += abs_pc

        recom = self.target_user.mean() + _sum1 / _sum2
        return recom

    def recommend(self):

        recom_rating = {}

        for i in range(1, self.ALL_ITEMS + 1):
            movie_name = "movie%d"

            # まだターゲットとなるユーザが評価していない映画について処理を行う
            if math.isnan(self.target_user[movie_name]):
                recom = self._calc_recom_score(movie_name)
                recom_rating[movie_name] = recom

        self.print_recom_movie(recom_rating)

    def _print_recom_movie(self, recom_rating):

        _count = 0
        for movie, score in sorted(recom_rating.items(), key=lambda x: x[1], reverse=True):
            # 上位10作品を表示する
            if _count == 10:
                break

            print("%s: score %.1f" % (movie, score))
            _count += 1


def main():

    rating_data = "movie_table.csv"
    info_file = "u.info"
    target_user = "user2"

    rc = Recommend(rating_data, info_file, target_user)
    print("Called get_similar_user()")
    rc.get_similar_user()

if __name__ == '__main__':
    main()
