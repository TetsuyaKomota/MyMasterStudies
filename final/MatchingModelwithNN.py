# coding = utf-8

# やること
# 境界列(剪定済み) → 境界列(マッチング済み)

# 手順
# 0. 初期状態を before に入れる
# 1. before から十分離れた次の状態を after に入れる
# 2. 以下を複数回繰り返し，学習モデルを複数得る
#   2-1. before から重複サンプリング
#   2-2. サンプリング結果に対応した after を取得
#   2-3. 取得したデータセットでモデルを学習
#   2-4. 再代入で評価して評価値を得ておく
# 3. before それぞれに以下を行い，predict を取得
#   3-1. モデルで推定し，評価値で重みづけ
#   3-2. 和を predict に挿入
# 4. before を output に追加
# 5. before <- predict
# 6.1. に戻る
