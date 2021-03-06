# -*- coding: utf-8 -*-

from recommend import Recommend
from preprocessing import PreprocessingDataset
from preprocessing import PreprocessingUItem
from utils import DATASET_DIR, DATA_DIR

import os
import sys


def main():

    # コマンドライン引数からターゲットユーザを読み込む
    argvs = sys.argv
    argc = len(argvs)

    if argc == 2:
        target_user = argvs[1]

        # データセットとinfoファイル名を指定
        dataset = os.path.join(DATASET_DIR, "u.data")
        info_file = os.path.join(DATASET_DIR, "u.info")

        # レコメンドシステム用にデータを生成
        rating_data = os.path.join(DATA_DIR, "movie_table.csv")
        if not(os.path.isfile(rating_data)):

            # データセットの前処理を行う
            ppd = PreprocessingDataset(dataset, info_file)

            # データセットから「縦：ユーザ、横：映画」の構成で
            # 各ユーザが評価した、映画の評価値が表になるように
            # data/movie_table.csvを生成
            ppd.preprocessing()

        # レコメンドシステム用にデータを生成
        u_item = os.path.join(DATA_DIR, "u_item.csv")
        if not(os.path.isfile(u_item)):

            # 映画名が列挙されているデータを読み込む
            u_item = os.path.join(DATASET_DIR, "u.item")
            ppui = PreprocessingUItem(u_item)

            # データセットをクリーニングして
            # data/u_item.csvを生成
            ppui.preprocessing()

        # 生成したデータを使ってレコメンドを行う
        rating_data = os.path.join(DATA_DIR, "movie_table.csv")
        print("Now target user: %s" % target_user)
        rc = Recommend(rating_data, info_file, u_item, target_user)

        # ターゲットに似ているユーザを表示する
        print("\n========== Similar Users ==========")
        rc.get_similar_user()
        # ターゲットにレコメンドを行う
        print("\n============ Recommend ============")
        rc.recommend()

    else:
        print("Please input target user.\n")
        print("For example: \n $ python main.py user1")


if __name__ == '__main__':
    main()
