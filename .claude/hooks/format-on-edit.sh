#!/usr/bin/env bash
# format-on-edit.sh — PostToolUse(Edit|MultiEdit|Write) hook: 編集されたファイルだけ整形する。
# fail-open（常に exit 0）: 整形の失敗・formatter/jq 不在・root 解決失敗で編集を止めない。
# ただしパス正規化（realpath）は fail-closed: 不在・失敗なら「整形しない」に倒す（root 外への書込防止）
# （利便機能でありゲートではない）。FORMAT_HOOK_DEBUG=1 で診断を stderr に出す。
# 生成元: /scaffold-stack（formatter は実証済みのものだけ埋める）
set -u
dbg() { [ -n "${FORMAT_HOOK_DEBUG:-}" ] && echo "[format-hook] $*" >&2 || true; }
# jq / realpath は command -v で存在確認（生の command not found を出さず、静かに skip）。
# realpath は「root 配下か」の判定に必須: 無い・失敗したときは非正規化パスで続行せず整形しない
# （symlink 経由で root 外のファイルを触らない = パス正規化は fail-closed。セッションは止めない = exit 0）。
command -v jq >/dev/null 2>&1 || { dbg "jq 不在 — skip"; exit 0; }
command -v realpath >/dev/null 2>&1 || { dbg "realpath 不在 — skip（正規化できないパスは整形しない）"; exit 0; }
f="$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
[ -n "$f" ] || { dbg "file_path なし — skip"; exit 0; }
# root は CLAUDE_PROJECT_DIR（公式 env）を第一候補、無ければ hook 自身の位置から導出
root="${CLAUDE_PROJECT_DIR:-}"
[ -n "$root" ] || root="$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd || true)"
[ -n "$root" ] || { dbg "root 解決不能 — skip"; exit 0; }
# root も realpath で正規化: file_path 側だけ正規化すると symlink 成分のある root で全ファイルが root 外扱いになる（macOS /var↔/private/var 等）。
root="$(realpath "$root" 2>/dev/null)" || { dbg "root を正規化できない — skip"; exit 0; }
[ -n "$root" ] || { dbg "root を正規化できない — skip"; exit 0; }
# 相対 file_path を root 基準で絶対化し、realpath で正規化（symlink 経由の root 外を弾く）。失敗は skip
case "$f" in /*) : ;; *) f="$root/$f" ;; esac
f="$(realpath "$f" 2>/dev/null)" || { dbg "file_path を正規化できない — skip"; exit 0; }
[ -n "$f" ] && [ -f "$f" ] || { dbg "実在しない — skip"; exit 0; }
# root 配下でなければ整形しない（/tmp や別 workspace への書き込みイベントを触らない）
case "$f" in "$root"/*) : ;; *) dbg "root 外（$f）— skip"; exit 0 ;; esac
rel="${f#"$root"/}"
# 除外は root 相対の先頭一致のみ（パス全体 glob は並列 worktree の実ソースまで除外する — 実測済みの罠）
case "$rel" in
  .claude/*|.sbx/*) dbg "生成物/設定（$rel）— skip"; exit 0 ;;
esac
case "$f" in
  # ↓ スタックに応じて実証済みの apply コマンド行だけ残す（判断表の format apply 列と同源）。
  #   Node 系は npx --no-install（未導入時のネットワーク取得をさせない — hook は決定的に）
  #   ruff は .venv にあり PATH 外なので uv run --frozen（lockfile を書き換えない）で呼ぶ
  *.py)         uv run --frozen --project "$root" ruff format "$f" >/dev/null 2>&1 || dbg "ruff 失敗/不在" ;;
esac
exit 0
