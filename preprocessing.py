# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import time

ALL_USERS = 943
ALL_ITEMS = 1682
ALL_RATINGS = 100000


def main():
    # データセットのディレクトリのパスを追加
    DATA_DIR = os.path.join(os.path.dirname(
        os.path.realpath("__file__")), "ml-100k")

    # データセットの読み込み
    udata_name = ['user_id', 'item_id', 'rating', 'timestamp']
    udata = pd.read_csv(os.path.join(DATA_DIR, "u.data"),
                        sep='\t', names=udata_name)

    # user_id と item_id を基準に昇順で並び替え
    sorted_udata = udata.sort_values(by=['user_id', 'item_id'])

    # 処理時間計測開始
    start = time.time()

    movie_array = []
    for user_num in range(1, ALL_USERS + 1):
        movie_array_ = []

        # 同じuser idのデータを取り出す
        user_data = sorted_udata[sorted_udata['user_id'] == user_num]

        for movie_num in range(1, ALL_ITEMS + 1):
            # 取り出した同一user idの中から特定の映画のものを取り出す
            movie_rating = user_data[user_data['item_id'] == movie_num]

            # 取り出した結果データが存在しない場合はnanを入れる
            if len(movie_rating) == 0:
                movie_array_ .append(np.nan)
                # print("Now id: %d Movie no. %d unrated." %
                #       (user_num, movie_num))
            else:
                # レーティングの数値を取り出す
                rating = int(movie_rating['rating'].values)
                movie_array_.append(rating)
                # print("Now id: %d, add rating %s (Movie no. %d)" %
                #       (user_num, rating, movie_num))

        movie_array.append(movie_array_)

    # 処理時間計測終了
    end = time.time() - start
    print("processing time: " + str(end) + "[sec]")

    # 生成したリストをnumpyに変換
    np_movie_table = np.array(movie_array)

    # column名を指定してDataFrameを作成
    column_name = range(1, ALL_ITEMS + 1)
    df_movie_table = pd.DataFrame(np_movie_table, columns=column_name)

    # CSVファイルへ出力
    df_movie_table.to_csv('movie_table.csv')


if __name__ == '__main__':
    main()
