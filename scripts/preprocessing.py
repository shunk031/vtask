# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import time
import csv

from utils import DATA_DIR


class PreprocessingDataset:

    def __init__(self, dataset, info):
        """
        :param TYPE dataset: データセットのファイル名
        :param TYPE info: インフォファイルのファイル名
        :rtype: TYPE
        """

        self.dataset_file = dataset
        self.info_file = info

        info_array = self._load_info_data()

        self.ALL_USERS = int(info_array[0])
        self.ALL_ITEMS = int(info_array[1])
        self.ALL_RATINGS = int(info_array[2])

        self._print_dataset_info()

    def _load_info_data(self):
        """
        infoファイルから情報を読み込む
        :rtype: TYPE info情報のリスト
        """
        info_array = []

        # infoファイルを読み込む
        with open(self.info_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')

            # 各行に書かれている内容を取得
            for row in reader:
                info_ = row[0]
                info = info_.split(" ")
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

    def preprocessing(self):
        """
        ユーザが評価した映画の表を再構成して保存する
        :rtype: TYPE なし
        """
        # データセットの読み込み
        udata_name = ['user_id', 'item_id', 'rating', 'timestamp']
        udata = pd.read_csv(self.dataset_file,
                            sep='\t', names=udata_name)
        # user_id と item_id を基準に昇順で並び替え
        sorted_udata = udata.sort_values(by=['user_id', 'item_id'])

        # 処理時間計測開始
        start = time.time()

        movie_array = []
        for user_num in range(1, self.ALL_USERS + 1):
            print("Now processing user no.%d" % user_num)
            movie_array_ = []

            # 同じuser idのデータを取り出す
            user_data = sorted_udata[sorted_udata['user_id'] == user_num]

            for movie_num in range(1, self.ALL_ITEMS + 1):
                # 取り出した同一user idの中から特定の映画のものを取り出す
                movie_rating = user_data[user_data['item_id'] == movie_num]

                # 取り出した結果データが存在しない場合はnanを入れる
                if len(movie_rating) == 0:
                    movie_array_ .append(np.nan)

                else:
                    # レーティングの数値を取り出す
                    rating = int(movie_rating['rating'].values)
                    movie_array_.append(rating)

            movie_array.append(movie_array_)

        # 処理時間計測終了
        end = time.time() - start
        print("processing time: " + str(end) + "[sec]")

        # 生成したリストをnumpyに変換
        np_movie_table = np.array(movie_array)

        # column名を指定してDataFrameを作成
        column_name = ["movie%d" %
                       movie_num for movie_num in range(1, self.ALL_ITEMS + 1)]
        df_movie_table = pd.DataFrame(np_movie_table, columns=column_name)

        # index名を変更
        index_name = ["user%d" %
                      user_num for user_num in range(1, self.ALL_USERS + 1)]
        df_movie_table.index = index_name

        # CSVファイルへ出力
        output_file = os.path.join(DATA_DIR, "movie_table.csv")
        df_movie_table.to_csv(output_file)


class PreprocessingUItem:

    def __init__(self, uitem, file_encoding='ISO-8859-1'):
        """
        :param TYPE uitem: u.itemのpath
        :param TYPE file_encoding='ISO-8859-1': u.itemのエンコーディングを指定
        :rtype: TYPE
        """
        self.uitem_file = uitem
        self.file_encoding = file_encoding

    def preprocessing(self):

        # u.itemを読み込む
        with open(self.uitem_file, 'r', encoding=self.file_encoding) as f:
            reader = csv.reader(f, delimiter='\t')
            u_items = [row for row in reader]

        # "|"で区切ったものをリストに格納する
        new_u_items = [self._split_items(u_item) for u_item in u_items]

        # ファイルの出力
        output_file = os.path.join(DATA_DIR, "u_item.csv")
        with open(output_file, 'w', encoding='utf-8') as w:
            writer = csv.writer(w)

            # データのヘッダーを指定
            header = ["movie id", "movie title", "release data", "video release date", "IMDb URL", "unknown", "Action", "Adventure", "Animation", "Children's",
                      "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]

            writer.writerow(header)
            for row in new_u_items:
                writer.writerow(row)

    def _split_items(self, u_item):
        """
        :param TYPE u_item: u_itemの行
        :rtype: TYPE \"|\"で区切ったリスト
        """

        s = u_item[0]
        s = s.split("|")

        return s
