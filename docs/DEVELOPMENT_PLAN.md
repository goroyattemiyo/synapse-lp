# Synapse LP Generator — 開発計画書

> **目的**: Synapseの3エージェント基盤を拡張し、Brain/Note向けの
> 「売れるLP品質コンテンツ」を一気通貫で生成するモードを実装する。
> **最終更新**: 2026-03-14

---

## 1. システム構成（現状）

`
synapse/
├── __init__.py          … run_synapse を公開
├── config.py            … モデル名・トークン上限・ループ上限
├── prompts.py           … Orchestrator / Coder / Reviewer のシステムプロンプト
├── lp_prompts.py        … LP用プロンプト3種 + セクションテンプレート
├── agents.py            … Anthropic Tool Use ループ管理（max_tokens可変対応）
├── tools.py             … write_file / read_file / run_command 定義 + 実行
├── sandbox.py           … 隔離ワークスペース（tmpdir）
├── engine.py            … 通常モード: Orchestrator→Coder→Reviewer ターン制御
├── lp_engine.py         … LPモード: 2フェーズ構成（HTML生成→ドラフト生成）
├── image_pipeline.py    … 画像化パイプライン（Playwright/手動ガイド）
├── draft_generator.py   … Brain/Note原稿生成 + 投稿ガイド
├── ui.py                … Streamlit チャットUI（通常モード）
└── lp_ui.py             … Streamlit LP生成UI（モード切替・プレビュー・ZIP DL）
`

### 主な定数（config.py）

| 定数 | 値 | 備考 |
|------|-----|------|
| MAX_ROUNDS | 3 | 通常モード: Coder-Reviewer最大往復 |
| MAX_TOOL_ITERATIONS | 20 | 1エージェント内ツール上限 |
| MAX_TOKENS | 4096 | 通常モード用 |
| LP_MAX_TOKENS | 16384 | LPモード用（HTML生成に十分） |
| LP_MAX_ROUNDS | 3 | LPモード: フェーズA/B各最大往復 |
| COMMAND_TIMEOUT | 60s | サンドボックスコマンドタイムアウト |

---

## 2. ゴール定義

### 最終成果物（1回の実行で出力）

| # | ファイル | 説明 |
|---|---------|------|
| 1 | lp.html | フルデザインの単一HTML（inline CSS） |
| 2 | sections/ | セクション画像群（PNG）※Playwright使用時 |
| 3 | brain_draft.md | Brain投稿用テキスト原稿 |
| 4 | note_draft.md | Note投稿用テキスト原稿 |
| 5 | posting_guide.md | 投稿手順ガイド |

### プラットフォーム制約

- Brain: 見出し(h2,h3), 太字, 引用, 画像, 動画のみ。文字色/サイズ不可
- Note: 見出し(h2,h3), 太字, 箇条書き, 引用, 画像。table不可, 文字色不可
- ビジュアル訴求部分はすべて画像化して回避する

---

## 3. 開発フェーズと進捗管理

### Phase 0: 基盤整備 ✅

| ID | タスク | 状態 |
|----|--------|------|
| 0-1 | tests/ ディレクトリ作成, pytest導入 | 完了 |
| 0-2 | 既存コードのユニットテスト作成 | 完了 |
| 0-3 | CI定義（GitHub Actions） | 完了 |
| 0-4 | 型ヒント追加 + mypy設定 | 完了 |
| 0-5 | ruff（linter/formatter）設定 | 完了 |

### Phase 1: LP生成プロンプト設計 ✅

| ID | タスク | 状態 |
|----|--------|------|
| 1-1 | lp_prompts.py に LP用プロンプト3種追加 | 完了 |
| 1-2 | LP構成テンプレート定義（12セクション） | 完了 |
| 1-3 | config.py に LP用定数追加（LP_MAX_TOKENS等） | 完了 |

### Phase 2: エンジン拡張 ✅

| ID | タスク | 状態 |
|----|--------|------|
| 2-1 | lp_engine.py に run_synapse_lp() 実装 | 完了 |
| 2-2 | LP用Orchestratorフロー | 完了 |
| 2-3 | LP用Coderフロー（2フェーズ: HTML生成→ドラフト生成） | 完了 |
| 2-4 | LP用Reviewerフロー（構造検証+コピー検証） | 完了 |
| 2-5 | agents.py に max_tokens パラメータ追加 | 完了 |

### Phase 3: 画像化パイプライン ✅

| ID | タスク | 状態 |
|----|--------|------|
| 3-1 | Playwright依存追加（オプショナル: try/import） | 完了 |
| 3-2 | セクション分割ロジック（data-section属性抽出） | 完了 |
| 3-3 | スクリーンショット撮影（Playwright使用時） | 完了 |
| 3-4 | 画像最適化（Pillow: リサイズ+圧縮） | 完了 |
| 3-5 | 手動スクリーンショットガイド生成（フォールバック） | 完了 |
| 3-6 | HTMLテキスト抽出（extract_text_from_html） | 完了 |

### Phase 4: プラットフォーム原稿生成 ✅

| ID | タスク | 状態 |
|----|--------|------|
| 4-1 | brain_draft.md 生成（有料境界マーカー付き） | 完了 |
| 4-2 | note_draft.md 生成（目次自動挿入付き） | 完了 |
| 4-3 | posting_guide.md 生成（Brain/Note手順+チェックリスト） | 完了 |
| 4-4 | セクション名→日本語タイトル変換辞書 | 完了 |

### Phase 5: UI統合 ✅

| ID | タスク | 状態 |
|----|--------|------|
| 5-1 | モード切替UI（通常/LP） | 完了 |
| 5-2 | 成果物プレビュー（HTML iframe + Markdownレンダリング） | 完了 |
| 5-3 | ZIPダウンロード | 完了 |
| 5-4 | 生成ステータス表示（進行中/完了/エラー） | 完了 |

---

## 4. バグ防止チェック体制

### 4-1. テスト戦略

- ユニットテスト（大量）: 関数単位で最も多く書く
- 結合テスト（中程度）: エージェント間の受け渡し検証
- E2Eテスト（少数）: 実API使用、手動トリガー

### 4-2. テストファイル一覧（78テスト通過、1スキップ）

`
tests/
├── __init__.py
├── conftest.py               … 共通fixture（Sandbox）
├── test_config.py            … 定数の型・範囲チェック（7件）
├── test_lp_config.py         … LP用定数チェック（3件）
├── test_prompts.py           … 通常プロンプト文字列検証（5件）
├── test_lp_prompts.py        … LPプロンプト文字列検証（8件）
├── test_sandbox.py           … Sandbox CRUD + コマンド実行（7件+1skip）
├── test_tools.py             … execute_tool 分岐（6件）
├── test_agents_extended.py   … run_agent max_tokens検証（2件）
├── test_lp_engine.py         … LP生成エンジン mock検証（5件）
├── test_image_pipeline.py    … セクション抽出・テキスト変換・ガイド（11件）
├── test_draft_generator.py   … Brain/Noteドラフト・投稿ガイド（17件）
└── test_lp_ui.py             … ZIP生成・UI関数（5件）
`

### 4-3. 静的解析（pushごとに自動実行）

| ツール | 目的 | 合格基準 |
|--------|------|----------|
| ruff | Lint + Format | エラー0 |
| mypy | 型チェック | エラー0 |
| bandit | セキュリティ | High/Medium 0 |

### 4-4. GitHub Actions CI

pushとPR時に自動実行:
- ruff check / ruff format --check
- mypy synapse/ --ignore-missing-imports
- bandit -r synapse/ -ll
- pytest tests/ -v --tb=short

### 4-5. コードレビュー規約

- 全変更は Pull Request 経由でマージ（推奨）
- CI 全Green 必須
- 新規関数には必ず対応テスト
- プロンプト変更時は出力比較をPRに記載

---

## 5. ブランチ戦略

- main: 安定版（現在ここで開発中）
- develop: 開発統合（今後分離予定）
- feature/*: 機能追加
- hotfix/*: 緊急修正

---

## 6. 各Phaseの完了条件と達成状況

| Phase | 完了条件 | 達成 |
|-------|----------|------|
| 0 | テスト全Green、CI動作、ruff/mypy/bandit全パス | ✅ |
| 1 | LP用プロンプト3種が存在しテスト済み | ✅ |
| 2 | run_synapse_lp() がmockで動作し lp.html を出力 | ✅ |
| 3 | lp.html から sections/*.png 自動変換が動作 | ✅ |
| 4 | brain/note_draft.md + posting_guide.md が生成される | ✅ |
| 5 | UIからLP生成、プレビュー、ZIPダウンロード完了 | ✅ |

---

## 7. リスク管理

| リスク | 対策 | 状況 |
|--------|------|------|
| HTMLがMAX_TOKENS超過 | LP_MAX_TOKENS=16384に引き上げ | 対応済 |
| Playwrightがsandboxで動かない | オプショナル依存+手動ガイドフォールバック | 対応済 |
| プラットフォーム仕様変更 | draft_generator.pyで分離設計 | 対応済 |
| AI出力品質ブレ | Reviewer構造検証+コピー検証の2段階 | 対応済 |
| 既存機能デグレ | 78テスト+CI自動実行 | 対応済 |

---

## 8. 依存パッケージ

### 本番
- anthropic>=0.40.0
- python-dotenv>=1.0.0
- streamlit>=1.30.0

### オプショナル（画像生成時）
- playwright>=1.40.0
- Pillow>=10.0.0

### 開発
- pytest>=8.0.0
- mypy>=1.8.0
- ruff>=0.4.0
- bandit>=1.7.0

---

## 9. 完了済スケジュール

| 期間 | Phase | 成果 |
|------|-------|------|
| Week 1 | Phase 0 | テスト基盤・CI・静的解析 |
| Week 1 | Phase 1 | LPプロンプト3種・セクションテンプレート |
| Week 1 | Phase 2 | LP生成エンジン（2フェーズ構成） |
| Week 1 | Phase 3 | 画像化パイプライン |
| Week 1 | Phase 4 | Brain/Noteドラフト・投稿ガイド |
| Week 1 | Phase 5 | Streamlit UI統合 |

---

## 10. 次のステップ

| # | タスク | 優先度 |
|---|--------|--------|
| 1 | 実APIでのLP生成テスト（E2E） | 高 |
| 2 | プロンプトチューニング（出力品質向上） | 高 |
| 3 | Playwright実環境での画像生成検証 | 中 |
| 4 | Brain/Noteへの実際の投稿テスト | 中 |
| 5 | Docker化（CI画像生成対応） | 低 |
| 6 | engine_base.py リファクタリング | 低 |