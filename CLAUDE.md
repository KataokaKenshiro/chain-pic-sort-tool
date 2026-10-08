# Project Instructions for Claude Code

## このプロジェクトについて

チェーン検査カメラの画像（2048x1200 グレースケール jpg + AI 判定結果の json）を、目視で OK / NG / SKIP / END に
振り分けるデスクトップツール。Python 3.12+ / PySide6 / uv。Windows 11 と Linux の両対応（Windows は PyInstaller で exe 化）。
画面を持たない処理は `src/chain_pic_sort/core/`、画面は `src/chain_pic_sort/ui/` に分け、core は画面なしで pytest する。

- 既定ブランチ: `main`
- 実際の検査画像（`image/`）は git に含めない。テストは `tmp_path` に生成したダミー画像を使う
- Qt テストは `tests/conftest.py` で `QT_QPA_PLATFORM=offscreen` にして動かす。Linux の素の環境では
  `libglib2.0-0 libegl1 libgl1 libfontconfig1 libxkbcommon0 libdbus-1-3` が無いと PySide6 の import で落ちる

### コマンド

| 用途 | コマンド | 備考 |
|---|---|---|
| install | `uv sync` | |
| テスト | `uv run pytest` | pytest-qt（offscreen） |
| lint | `uv run ruff check` | |
| format check | `uv run ruff format --check` | 検証用（書き換えない） |
| format apply | `uv run ruff format` | 書き込み系。PostToolUse hook で自動適用 |
| 型チェック | `uv run mypy` | 非 strict |

> 重要: このテンプレートは **言語・スタック非依存** の AI ワークフロー基盤のみ提供します。Docker・パッケージマネージャ・ビルド構成・ディレクトリレイアウト等の技術スキャフォールドはユーザー or AI が個別プロジェクトで生成します（依頼すれば Claude が現状を見て提案します）。

> 開発ワークフロー・Git 運用・行動原則などのセッション規約は
> `.claude/rules/workflow.md`（テンプレ提供・起動毎に自動更新）にある。本ファイルには
> **このプロジェクト固有の情報だけ** を書く。/prepare-workspace 等による参照の追記先も
> 本ファイルの「## 参照」節（無ければ新設）であり、workflow.md には追記しない。

## プロジェクト固有の情報を書く場所

CLAUDE.md（このファイル）にスタック・コマンド・規約を集約してください。Claude は起動時にこれを読み込みます。テンプレ初期状態では空欄です。

例：
- 主要ビルドコマンド（`make build` / `npm run build` / `cargo build` 等）
- テスト実行コマンド（プロジェクト側のテストランナー）
- フォーマット・lint・型チェックコマンド
- ディレクトリレイアウトとその意味
- **既定ブランチ名**（merge 先。main/master 以外ならここに明記）
- ドメイン用語・略語の対応表
- 触ってはいけないファイル・ディレクトリ

<!-- テンプレ還元先 override（任意）: /retrospect のテンプレ改善 issue の送り先を上書きするには、
     行頭に `テンプレ還元先: <owner>/<repo>` の 1 行を（この注釈の外に）足す。既定は正本 retrospect.md の値。 -->

プロジェクト固有の規約は `.claude/rules/<topic>.md` に追加できます（git 追跡され並列 Claude 間で共有）。
特定のファイル種別にだけ効かせたい規約は frontmatter `paths:` を付けると、その編集時のみロードされ context を節約できます。
プロジェクト横断のポリシー（コミット規約・レビュー方針など）は `paths` 無しで常時ロードして構いません。

> **配備モデル（manifest）**: `.claude/` のうち**テンプレ提供ファイル**（`commands/`・`hooks/`・
> 汎用 `rules/{commit,code-review,markdown-docs,workflow}.md`・`settings.json`）は **起動毎にテンプレ最新版へ上書き同期**
> されるため、ここを直接編集しても次回起動で戻ります。恒久変更は `_shared/claude-template/` 側で行ってください。
> 一方、**あなたが足したもの**（プロジェクト固有 `rules/*.md`・`/prepare-workspace` 取り込み skill/agent・
> `settings.local.json`・`CLAUDE.md`・`requirements/`・`plans/`）は git 追跡され保持・共有されます。
> Claude Code 設定をプロジェクトで上書きしたい場合は `.claude/settings.local.json`（テンプレ `settings.json` にマージ）に書きます。
