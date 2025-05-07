# postcode-api
fastapi
playwright

## 公式doc
```
https://fastapi.tiangolo.com/ja/tutorial/first-steps/#api
```

## rye インストール
```
curl -sSf https://rye.astral.sh/get | bash
```

## rye パッケージ追加、変更時
```
rye sync

rye add パッケージ名
rye add --dev パッケージ名

rye remove パッケージ名
```

## playwright インストール（必須）
```
rye run playwright install    
```

## playwright 自動コード生成
```
rye run playwright codegen サイト名
```