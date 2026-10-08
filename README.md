# Chain Pic Sort

チェーン検査カメラで撮影した画像を、目視で OK / NG / SKIP / END に振り分けるデスクトップツールです。
Windows 11 と Linux で動きます。

## できること

- 画像（2048x1200 の jpg）の中心 1200x1200 を切り出し、設定に応じて左右 90° 回転して表示します
- 画像と同じ名前の json（AI 判定結果）から、verdict・confidence・mahalanobis などを表示します
- キー 1 つで jpg と json をまとめて `OK/` `NG/` `SKIP/` `END/` フォルダへ移動し、次の画像を表示します
- 合計・残り・各フォルダの件数を表示し、振り分け結果を `sort_log.csv` に記録します

## 起動方法（開発環境）

[uv](https://docs.astral.sh/uv/) を使います。

```bash
uv sync
uv run chain-pic-sort
```

Linux では Qt の実行に `libxcb-cursor0` などの X11 ライブラリが必要です。
起動時に xcb プラグインのエラーが出たら、OS のパッケージマネージャで入れてください。

## 使い方

1. 「フォルダを開く…」（`Ctrl+O`）で、画像があるフォルダを選びます
2. 画像を見て、ボタンまたはキーで振り分けます
3. 全件を振り分けると完了メッセージが出ます

前回開いたフォルダと回転の設定は、次回起動時に引き継がれます。

### 操作キー

| キー | 動作 |
|---|---|
| `1` | OK へ移動 |
| `2` | NG へ移動 |
| `3` | SKIP へ移動 |
| `4` | END へ移動（ツールは終了しません） |
| `←` / `→` | 前 / 次の未仕分け画像を表示 |
| `F` | 切り出し表示と画像全体の表示を切り替え |
| マウスホイール | 拡大・縮小（次の画像でウィンドウに収まる表示に戻ります） |
| ドラッグ | 拡大中の表示位置を移動 |

テンキーの `1`〜`4` も使えます。回転は「表示 → 回転」メニューで「なし / 左 90° / 右 90°」から選びます。

### フォルダ構成

```text
<選んだフォルダ>/
├── 20260622_140710_144_000001.jpg   未仕分け
├── 20260622_140710_144_000001.json
├── OK/  NG/  SKIP/  END/            振り分け先（無ければ自動で作成）
└── sort_log.csv                     振り分けの記録
```

- 対象は選んだフォルダの直下にある jpg だけです（サブフォルダは見ません）
- json が無い jpg は jpg だけを移動します
- 振り分け先に同じ名前のファイルがあると、移動せずに警告を出します（上書きしません）
- `sort_log.csv` の列は `timestamp, filename, category, verdict, confidence, mahalanobis` です。
  Excel で開いても文字化けしないよう UTF-8（BOM 付き）で書きます。
  Excel で開いたままだと書き込めないことがあり、その場合は移動だけ行って警告を出します

## Windows 向け実行ファイルの作り方

Windows 上で次を実行します（Windows の exe は Windows 上でしか作れません）。

```powershell
uv sync --group build
uv run --group build pyinstaller --noconfirm chain_pic_sort.spec
```

`dist\ChainPicSort\` フォルダができます。中の `ChainPicSort.exe` をダブルクリックすると起動します。
配布するときは `dist\ChainPicSort\` フォルダごと ZIP にして渡してください（exe 単体では動きません）。

## 開発

| 用途 | コマンド |
|---|---|
| テスト | `uv run pytest` |
| lint | `uv run ruff check` |
| フォーマット確認 | `uv run ruff format --check` |
| 型チェック | `uv run mypy` |

画面を持たない処理は `src/chain_pic_sort/core/`、画面は `src/chain_pic_sort/ui/` にあります。
