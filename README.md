# YuchoMailOutput

## What This Is

ゆうちょ銀行のクレジットカードを使った際に送られてくるメールを全て取得し、今までカードで使った金額をGoogleスプレッドシートに出力してくれるPython。  
CSVにも対応してます。

## How To Use

### 起動してみよう

必要なパッケージを`req.txt`からインストールしてください。

```text
pip -r req.txt
```

次に`credentials.json`を取得しよう！（csvだけ使用する場合はいらない）  
[Google APIのクライアント認証情報を取得する](https://qiita.com/alpacanako/items/e130b199eec5b2758c18)というqiitaがわかりやすいと思います！  
必要になるのは

- Google SpreadSheet API
- Google Drive API

です！
ダウンロードしたファイルを`req.txt`、`main.py`と同じ場所に置いてください。  
後は実行！  
一応ダブルクリックでも実行はできますが…

```text
python main.py
```

で行うのが確実だと思います。  
実行すると、スプレッドシートでの出力か、CSVでの出力か聞かれます。  
自分の好みを方を選んでください。

もし、スプレッドシートで出力の場合、`spreadsheet_id`が必要になります。  
サービスアカウントも必要になると思います。  
サービスアカウントについては[サービスアカウントを利用したGoogleスプレッドシートの連携設定](https://docs.biztex.co.jp/cobit-docs/google_spreadsheet_settings/for_serviceaccount.html)こちらが参考になると思います。  
`spreadsheet_id`についてはサービスアカウントを追加したスプレッドシートのURL、`https://docs.google.com/spreadsheets/d/{12ysa4UFkPYQfDhKUhZ4Y489AdoLK_IrPQAv9rHVqawo}/edit?gid=0#gid=0`の{}の部分を入れてください。

### Let'GO!!!!!!!!!!

ここまでできたら後は待つだけ！  
何かわからないことがあったらお気楽に白深やよいの[Twitter](https://x.com/shirafukayayoi)、またはDiscord(shirafukayayoi)にDMしてください！
