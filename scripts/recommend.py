# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import math
import time
import csv

from utils import DATA_DIR


class Recommend:

    def __init__(self, rating_data, info_data, target_user):
        """
        :param TYPE dataset: データセットのファイル名
        :param TYPE info:    infoファイルのファイル名
        :rtype: TYPE
        """

        # 評価データの読み込み
        self.rating_data = pd.read_csv(rating_data, index_col=0)
        # 評価データの基本情報の読み込み
        self.info_file = os.path.join(DATA_DIR, info_data)

        info_array = self._load_info_data()

        # 評価データの基本情報
        self.ALL_USERS = int(info_array[0])
        self.ALL_ITEMS = int(info_array[1])
        self.ALL_RATINGS = int(info_array[2])

        # レコメンドを行うターゲットユーザーのデータを抽出
        self.target_user = self.rating_data.ix[target_user]

        # 推薦度を格納するディクショナリを用意
        self.recom_rating = {}

        # 類似ユーザを格納するディクショナリを用意
        self.similar_user = {}

        # データセットの情報を表示する
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

        # 同じユーザ同士は0を返す
        if user1.equals(user2):
            return 0.0

        # user1, user2両者が評価した映画を取得
        both_rated = []
        for i in range(1, self.ALL_ITEMS + 1):
            movie_name = "movie%d" % i

            # user1, user2両者が評価した映画かどうか判定
            if not(math.isnan(user1[movie_name]) or math.isnan(user2[movie_name])):
                both_rated.append(movie_name)

        # user1とuser2両者が評価した映画の数を取得
        number_of_ratings = len(both_rated)
        # もし両方が評価した映画の数が0なら0を返す
        if number_of_ratings == 0:
            return 0.0

        user1_mean = sum([user1[movie]
                          for movie in both_rated]) / number_of_ratings
        user2_mean = sum([user2[movie]
                          for movie in both_rated]) / number_of_ratings

        # 分子の計算
        numer = float(sum([(user1[movie] - user1_mean) *
                           (user2[movie] - user2_mean) for movie in both_rated]))

        # 分母の計算
        denom1 = math.sqrt(
            sum([(user1[movie] - user1_mean) ** 2 for movie in both_rated]))
        denom2 = math.sqrt(
            sum([(user2[movie] - user2_mean) ** 2 for movie in both_rated]))

        # ピアソン相関係数を計算
        try:
            pearosn_corr = numer / (denom1 * denom2)
        except ZeroDivisionError as e:
            # print(e)
            pearosn_corr = 0

        return pearosn_corr

    def get_similar_user(self):
        """
        ターゲットユーザに似ているユーザを表示する
        :rtype: TYPE
        """
        score_dict = {}

        for i in range(1, self.ALL_USERS + 1):
            user_name = "user%d" % i
            user_data = self.rating_data.ix[user_name]
            pc = self.sim_pearson(self.target_user, user_data)
            score_dict[user_name] = pc

        count = 0
        for user, score in sorted(score_dict.items(), key=lambda x: x[1], reverse=True):
            if count == 10:
                break

            print("%s: %f" % (user, score))
            self.similar_user[user] = score
            count += 1

    def _calc_average(self, user):
        """
        受け取ったデータからnanを含めないデータ数で
        評価値の平均を計算する

        :param TYPE user: pandas.seriesのデータ
        :rtype: TYPE ユーザの評価値の平均
        """

        n = [x for x in user if not(math.isnan(x))]
        d = len(n)
        sum_n = sum(n)

        return sum_n / d

    def _calc_recom_score(self, target_movie):

        # target_movieを評価しているユーザを取得する
        rated_target_movie = []
        for i in range(1, self.ALL_USERS + 1):
            user_name = "user%d" % i
            user_data = self.rating_data.ix[user_name]

            # target_movieを評価しているユーザかどうか判定
            if not(math.isnan(user_data[target_movie])):
                rated_target_movie.append(user_name)

        # 推薦度を計算
        sum1 = 0
        sum2 = 0
        for user in rated_target_movie:
            user_data = self.rating_data.ix[user]
            pc = self.sim_pearson(self.target_user, user_data)

            # 分子の計算
            calc = pc * (user_data[target_movie] -
                         self._calc_average(user_data))
            sum1 += calc

            # 分母の計算
            abs_pc = math.fabs(pc)
            sum2 += abs_pc

        if sum2 == 0:
            recom = 0
        else:
            recom = self._calc_average(self.target_user) + sum1 / sum2

        return recom

    def recommend(self):

        for i in range(1, self.ALL_ITEMS + 1):
            movie_name = "movie%d" % i

            # ターゲットユーザがまだ評価していない映画について処理を行う
            if math.isnan(self.target_user[movie_name]):

                # 推薦度を計算
                recom = self._calc_recom_score(movie_name)
                self.recom_rating[movie_name] = recom

        # 推薦度が高い上位10作品について表示
        self.print_recom_movie(self.recom_rating)

    def print_recom_movie(self, recom_rating, num=10):

        count = 0
        for movie, score in sorted(recom_rating.items(), key=lambda x: x[1], reverse=True):
            # 上位num作品を表示する
            if count == num:
                break

            print("%s: score %.1f" % (movie, score))
            count += 1
