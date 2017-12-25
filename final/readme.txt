実行順



GenerateModel
↓
↓   log(csv ファイル)
↓
EncodeModel
↓
↓   符号列(dict(str(csvファイル名):[int(符号)]))
↓       冗長のまま (長さ 500 のまま)
↓
ParsingModel
↓
↓   文字列(dict(str(csvファイル名):[str(符号)]))
↓
↓   縮小文字列(dict(str(csvファイル名):[str(符号)]))
↓       冗長部分削除
↓
↓   縮小単語列(dict(str(csvファイル名):[str(符号)]))
↓
↓   境界列(dict(str(csvファイル名):[int(境界ステップ数)]))
↓
PrunningModel
↓
↓   境界列(dict(str(csvファイル名):[int(剪定済み境界ステップ数)]))
↓
MatchingModel
↓
↓   モデル列([[(model(各ステップに対応するモデル), w(重み))]])
↓



<<やること>>
・グリッドサーチの実装
	・これ動かしてあとは結果出るまで待ち
・nonGPU 環境 (研究室環境)で動作するように調整

