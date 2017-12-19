# coding = utf-8

# やること
# 符号列 → 単語列

# メソッド
# ・学習
#   tmp/dills/encoded.dill で log の全部の符号列をロード
#   全部 NPYLM に代入
#   できた NPYLM を dill.dump
#
# ・解析
#   tmp/dills/npylm.dill をロード
#   tmp/dills/encoded.dill で log の全部の符号列をロード
#   全部を分かち書き
#   それを dill.dump
