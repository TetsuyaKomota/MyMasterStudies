# coding = utf-8

# やること
# 動作データ → 符号列

# メソッド
# ・学習
#   tmp/log にあるデータを全部 SOINN に代入
#   できた SOINN を dill.dump
#
# ・符号化
#   tmp/dills/soinn.dill をロード
#   tmp/log にあるデータを全部符号化
#   できた符号列を，ファイル名キーの dict にする
#   それを dill.dump
