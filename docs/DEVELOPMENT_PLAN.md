# PostCraft - 開発計画書

最終更新: 2026-03-14

## 1. リポジトリ構成

postcraft/ ├── synapse/ │ ├── init.py │ ├── config.py # 定数定義 │ ├── prompts.py # 通常モード用プロンプト │ ├── lp_prompts.py # LP生成用プロンプト │ ├── agents.py # エージェント実行 │ ├── tools.py # ツール定義・実行 │ ├── sandbox.py # サンドボックス環境 │ ├── engine.py # 通常モードエンジン │ ├── lp_engine.py # LP生成エンジン (Phase A) │ ├── lp_engine_drafts.py # LP生成エンジン (Phase B + 画像) │ ├── image_pipeline.py # Playwright画像キャプチャ │ ├── draft_generator.py # Brain/Note原稿生成 │ ├── lp_manual_utils.py # 手動モード用ユーティリティ │ ├── ui.py # Streamlitエントリポイント │ ├── lp_ui.py # LP自動生成UI │ └── lp_ui_manual.py # 手動LP変換UI ├── tests/ # テストスイート (109件) ├── docs/ │ ├── RULES.md # 開発ルール │ └── DEVELOPMENT_PLAN.md # 本ファイル ├── pyproject.toml ├── requirements.txt └── requirements-dev.txt


## 2. 主要定数 (config.py)

MAX_ROUNDS=3, MAX_TOOL_ITERATIONS=20, MAX_TOKENS=4096,
LP_MAX_TOKENS=16384, LP_MAX_ROUNDS=3, COMMAND_TIMEOUT=60s

## 3. 最終成果物 (1回の実行で生成)

lp.html (単一HTMLファイル、インラインCSS), sections/*.png (セクション画像),
brain_draft.md (Brain投稿用原稿), note_draft.md (Note投稿用原稿),
posting_guide.md (投稿手順ガイド)

Brain制約: 見出し・太字・引用・画像のみ。Note制約: 見出し・太字・リスト・引用・画像（テーブル不可）。

## 4. 開発フェーズ (全完了)

**Phase 0 - 基盤整備**: テスト基盤、CI (GitHub Actions)、型ヒント、リンター設定 ✅

**Phase 1 - LPプロンプト**: LP_ORCHESTRATOR/CODER/REVIEWER/SECTION_TEMPLATE作成、プレースホルダールール、画像プレースホルダー仕様、CTA配置ルール、Reviewer検証強化 ✅

**Phase 2 - エンジン拡張**: run_postcraft (Phase A: Orchestrator→Coder→Reviewer)、トークン上限分離 (LP_MAX_TOKENS=16384) ✅

**Phase 3 - 画像パイプライン**: Playwright/Pillowによるセクション画像キャプチャ、800px幅・1MB以下に最適化、手動スクリーンショットガイド生成、Playwright optional import ✅

**Phase 4 - 原稿生成**: Brain/Note原稿自動生成 (有料境界マーカー、画像プレースホルダー、目次)、投稿ガイド生成、Phase B最適化ループ (Coder+Reviewer 2ラウンド) ✅

**Phase 5 - UI統合**: Streamlit 2モード構成 (手動LP変換 / LP自動生成API)、手動モード4ステップ (商品情報入力→プロンプト生成→HTML貼付→素材生成)、構造化入力フォーム、Playwright subprocess実行 (Streamlit非同期競合回避)、ZIP一括ダウンロード (HTML+画像+原稿+ガイド) ✅

## 5. UIモード構成

### モードA: 手動LP変換 (APIキー不要)
Step 1: 商品情報を構造化フォームに入力 (商品名・ターゲット・価格・内容・差別化・補足)
Step 2: 最適化プロンプト自動生成 → AIチャット (ChatGPT/Claude) に貼付してHTMLを生成・調整
Step 3: 最終版HTMLを貼り付け
Step 4: Brain/Note原稿・セクション画像・投稿ガイドを自動生成、ZIP一括ダウンロード

### モードB: LP自動生成 (APIキー必要)
サイドバーでAnthropicAPIキーを入力 → 商品情報入力 → 全自動でLP+原稿+画像を生成

## 6. テスト状況

**109件合格, 1件スキップ** (run_command_timeout)

テストファイル: test_agents_extended, test_config, test_draft_generator, test_image_integration, test_image_pipeline, test_lp_config, test_lp_engine, test_lp_prompts, test_lp_ui, test_prompts, test_sandbox, test_tools, test_ui_manual

静的解析: ruff (フォーマット+リント), mypy (型チェック), bandit (セキュリティ) 全てゼロエラー
CI: GitHub Actions で push/PR ごとに自動実行

## 7. リスクと対策

トークン上限超過 → LP_MAX_TOKENS=16384に拡張済み。Playwright環境依存 → optional import + 手動ガイドフォールバック + subprocess実行。プラットフォーム仕様変更 → モジュール分離で対応容易。AI出力品質 → 2段階Reviewerループ。リグレッション → 109件テスト + CI自動実行。

## 8. 依存関係

本番: anthropic>=0.40.0, python-dotenv>=1.0.0, streamlit>=1.30.0
画像 (任意): playwright>=1.40.0, Pillow>=10.0.0
開発: pytest>=8.0.0, mypy>=1.8.0, ruff>=0.4.0, bandit>=1.7.0

## 9. Next Steps (優先度順)

| # | タスク | 優先度 | 状態 |
|---|--------|--------|------|
| 1 | 実APIでのE2E LP生成テスト | 高 | 🔲 未着手 |
| 2 | プロンプトチューニング (実生成結果ベース) | 高 | 🔲 未着手 |
| 3 | Brain/Noteへの実投稿テスト | 中 | 🔲 未着手 |
| 4 | Docker CI画像生成環境 | 低 | 🔲 未着手 |
| 5 | engine_base.py リファクタリング | 低 | 🔲 未着手 |
| 6 | Streamlit Cloud デプロイ | 低 | 🔲 未着手 |
| 7 | インタラクティブ投稿チェックリスト (UI) | 低 | 🔲 未着手 |

開発ルールの詳細は docs/RULES.md を参照。
