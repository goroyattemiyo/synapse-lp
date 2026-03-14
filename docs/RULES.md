# PostCraft - 開発ルール

最終更新: 2026-03-14

## 1. 絶対ルール

1. バイアス禁止: 技術選定・設計判断に個人的好みを持ち込まない
2. 品質妥協禁止: 動くが汚いコードは許可しない
3. 技術的異議の明示: 問題がある場合は根拠付きで反論する
4. エビデンスベース: 客観的指標（テスト結果・行数・CI）に基づいて判断
5. スコープ厳守: フェーズ外の要求は DEVELOPMENT_PLAN.md の Next Steps に追記

## 2. ファイルサイズ制限

| 種別 | 上限 | 分割検討 | 強制分割 |
|------|------|----------|----------|
| Python | 250行 | 200行超 | 250行超 |
| Markdown | 300行 | 250行超 | 300行超 |

AIが1回で読めるサイズを維持すること。

## 3. ワークフロールール

- push後は必ずリポジトリから直接ファイルを参照する
- 会話圧縮が発生したら RULES.md を再読み込みする
- 次フェーズ移行前に最新コードを取得する
- mainブランチで作業（ソロ開発）、CI green必須
- コミットメッセージ: eat:, ix:, docs:, 	est:, 
efactor: プレフィックス

## 4. テストルール

- 新規関数にはユニットテストを追加する
- CI (ruff, mypy, bandit, pytest) が全てパスすること
- 3層テスト: 純粋Python / Playwright (skip-if) / 手動E2E

## 5. 技術的負債台帳

| # | 内容 | 優先度 | 状態 |
|---|------|--------|------|
| 1 | LP用トークン上限分離 | 高 | ✅ 解消 (2026-03-14) |
| 2 | Playwright optional import | 高 | ✅ 解消 (2026-03-14) |
| 3 | engine共通処理抽出 (engine_base.py) | 低 | 🔲 保留 |
| 4 | 型ヒント追加 | 中 | ✅ 解消 (2026-03-14) |
| 5 | RULES.md ファイルサイズ更新 | 低 | ✅ 解消 (2026-03-14) |

## 6. ファイルサイズ監視 (現在値)

| ファイル | 行数 | 状態 |
|----------|------|------|
| synapse/lp_engine_drafts.py | 194 | ⚠️ 要注意 (200超で分割検討) |
| synapse/lp_ui_manual.py | 189 | ⚠️ 要注意 |
| synapse/lp_engine.py | 178 | OK |
| synapse/draft_generator.py | 178 | OK |
| synapse/image_pipeline.py | 157 | OK |
| synapse/engine.py | 155 | OK |
| synapse/lp_ui.py | 135 | OK |
| synapse/lp_manual_utils.py | 133 | OK |
| synapse/lp_prompts.py | 110 | OK |
| synapse/ui.py | 86 | OK |
| synapse/agents.py | 79 | OK |
| synapse/prompts.py | 64 | OK |
| synapse/sandbox.py | 65 | OK |
| synapse/tools.py | 56 | OK |
| synapse/config.py | 24 | OK |
| docs/DEVELOPMENT_PLAN.md | 255 | ⚠️ 要注意 (300上限) |

**テスト状況: 109件合格, 1件スキップ (run_command_timeout)**

## 7. ルール変更履歴

- 2026-03-14: 初版作成、技術的負債 #1,#2,#4 解消
- 2026-03-14: #5 解消、ファイルサイズ監視更新
- 2026-03-14: UI刷新後の全ファイル行数・テスト数109件反映
