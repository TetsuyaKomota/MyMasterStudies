# coding = utf-8

# やること
# 単語列 → 境界列

# メソッド
# ・剪定
#   tmp/dills/parsed.dill をロード
#   tmp/log のデータと照らし合わせ，直前の状態と
#   hand 以外に変化がない境界は削除
#   剪定し終わった境界列は状態列に
