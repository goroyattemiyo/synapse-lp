# Synapse LP Generator — 開発計画書

> **目的**: Synapseの3エージェント基盤を拡張し、Brain/Note向けの
> 「売れるLP品質コンテンツ」を一気通貫で生成するモードを実装する。
> **最終更新**: 2026-03-13

---

## 1. 現状のシステム構成（As-Is）

synapse/
├── init.py      … run_synapse を公開
├── config.py        … モデル名・トークン上限・ループ上限
├── prompts.py       … Orchestrator / Coder / Reviewer のシステムプロンプト
├── agents.py        … Anthropic Tool Use ループ管理
├── tools.py         … write_file / read_file / run_command 定義 + 実行
├── sandbox.py       … 隔離ワークスペース（tmpdir）
├── engine.py        … Orchestrator→Coder→Reviewer ターン制御
└── ui.py            … Streamlit チャットUI
### 主な定数（config.py）

| 定数 | 現行値 | 備考 |
|------|--------|------|
| MAX_ROUNDS | 3 | Coder - Reviewer 最大往復 |
| MAX_TOOL_ITERATIONS | 20 | 1エージェント内ツール上限 |
| MAX_TOKENS | 4096 | LP用HTMLには不足 |
| COMMAND_TIMEOUT | 60s | |

---

## 2. ゴール定義（To-Be）

### 最終成果物（1回の実行で出力）

| # | ファイル | 説明 |
|---|---------|------|
| 1 | lp.html | フルデザインの単一HTML（inline CSS） |
| 2 | sections/ | セクション画像群（PNG） |
| 3 | brain_draft.md | Brain投稿用テキスト原稿 |
| 4 | note_draft.md | Note投稿用テキスト原稿 |
| 5 | posting_guide.md | 投稿手順ガイド |

### プラットフォーム制約

- Brain: 見出し(h2,h3), 太字, 引用, 画像, 動画のみ。文字色/サイズ不可
- Note: 見出し(h2,h3), 太字, 箇条書き, 引用, 画像。table不可, 文字色不可
- ビジュアル訴求部分はすべて画像化して回避する

---

## 3. 開発フェーズと進捗管理

### Phase 0: 基盤整備（バグ防止体制の構築）

| ID | タスク | 状態 |
|----|--------|------|
| 0-1 | tests/ ディレクトリ作成, pytest導入 | 完了 |
| 0-2 | 既存コードのユニットテスト作成 | 完了 |
| 0-3 | CI定義（GitHub Actions） | 完了 |
| 0-4 | 型ヒント追加 + mypy設定 | 完了 |
| 0-5 | ruff（linter/formatter）設定 | 完了 |

### Phase 1: LP生成プロンプト設計

| ID | タスク | 状態 |
|----|--------|------|
| 1-1 | prompts.py に LP用プロンプト3種追加 | 完了 |
| 1-2 | LP構成テンプレート定義 | 完了 |
| 1-3 | config.py に LP用定数追加 | 完了 |

### Phase 2: エンジン拡張

| ID | タスク | 状態 |
|----|--------|------|
| 2-1 | lp_engine.py に run_synapse_lp() 実装 | 完了 |
| 2-2 | LP用Orchestratorフロー | 完了 |
| 2-3 | LP用Coderフロー（HTML生成+ドラフト生成） | 完了 |
| 2-4 | LP用Reviewerフロー（構造+コピー検証） | 完了 |

### Phase 3: 画像化パイプライン

| ID | タスク | 状態 |
|----|--------|------|
| 3-1 | Playwright依存追加 | 未着手 |
| 3-2 | セクション分割ロジック | 未着手 |
| 3-3 | スクリーンショット撮影 | 未着手 |
| 3-4 | 画像最適化 | 未着手 |

### Phase 4: プラットフォーム原稿生成

| ID | タスク | 状態 |
|----|--------|------|
| 4-1 | brain_draft.md 生成ロジック | 未着手 |
| 4-2 | note_draft.md 生成ロジック | 未着手 |
| 4-3 | posting_guide.md 生成 | 未着手 |

### Phase 5: UI統合

| ID | タスク | 状態 |
|----|--------|------|
| 5-1 | モード切替UI追加 | 未着手 |
| 5-2 | 成果物プレビュー・DL | 未着手 |
| 5-3 | HTMLプレビュー | 未着手 |

---

## 4. バグ防止チェック体制

### 4-1. テスト戦略

- ユニットテスト（大量）: 関数単位で最も多く書く
- 結合テスト（中程度）: エージェント間の受け渡し検証
- E2Eテスト（少数）: Phase完了時に実施

### 4-2. ユニットテスト一覧（Phase 0 で作成）

tests/
├── conftest.py           … 共通fixture
├── test_sandbox.py       … Sandbox CRUD + コマンド実行
├── test_tools.py         … execute_tool の分岐
├── test_agents.py        … run_agent ループ制御（API mock）
├── test_prompts.py       … プロンプト文字列の検証
├── test_config.py        … 定数の型・範囲チェック
└── test_engine.py        … run_synapse_with_callback フロー

### 4-3. 結合テスト（Phase 2 以降で追加）

tests/
├── test_lp_flow.py       … LP生成の一気通貫テスト
├── test_image_pipeline.py … 画像化パイプライン
└── test_draft_generation.py … プラットフォーム原稿
### 4-4. 静的解析（pushごとに実行）

| ツール | 目的 | 合格基準 |
|--------|------|----------|
| ruff | Lint + Format | エラー0 |
| mypy | 型チェック | エラー0 |
| bandit | セキュリティ | High/Medium 0 |

### 4-5. GitHub Actions CI

pushとPR時に自動実行される:
- ruff check / ruff format --check
- mypy synapse/
- bandit -r synapse/
- pytest tests/ -v

### 4-6. コードレビュー規約

- 全変更は Pull Request 経由でマージ
- CI 全Green 必須
- 新規関数には必ず対応テスト
- プロンプト変更時は出力比較をPRに記載

---

## 5. ブランチ戦略

- main: 安定版
- develop: 開発統合
- feature/phase0-test-infra ~ feature/phase5-ui: 各Phase
- hotfix/*: 緊急修正

各 feature/* は develop へマージ。
Phase完了ごとに develop から main へリリースマージ。

---

## 6. 各Phaseの完了条件

| Phase | 完了条件 |
|-------|----------|
| 0 | 既存テスト全Green、CI動作、ruff/mypy/bandit全パス |
| 1 | LP用プロンプト3種が存在しテスト済み |
| 2 | run_synapse_lp() がmockで動作し lp.html を出力 |
| 3 | lp.html から sections/*.png 自動変換が動作 |
| 4 | brain/note_draft.md + posting_guide.md が生成される |
| 5 | UIからLP生成、プレビュー、ZIPダウンロード完了 |

---

## 7. リスク管理

| リスク | 対策 |
|--------|------|
| HTMLがMAX_TOKENS超過 | 段階的引き上げ + セクション分割生成 |
| Playwrightがsandboxで動かない | Docker化 or 手動スクショガイド |
| プラットフォーム仕様変更 | draft生成を差し替え可能に分離 |
| AI出力品質ブレ | Reviewer厳格化 + few-shot |
| 既存機能デグレ | Phase 0でテスト充実、全変更CI通す |

---

## 8. 追加パッケージ

- playwright>=1.40.0 (Phase 3)
- Pillow>=10.0.0 (Phase 3)
- pytest>=8.0.0 (Phase 0)
- mypy>=1.8.0 (Phase 0)
- ruff>=0.4.0 (Phase 0)
- bandit>=1.7.0 (Phase 0)

---

## 9. スケジュール

- Week 1: Phase 0（テスト基盤・CI）
- Week 2: Phase 1（LPプロンプト）
- Week 3: Phase 2（エンジン拡張）
- Week 4: Phase 3（画像化）
- Week 5: Phase 4（原稿生成）
- Week 6: Phase 5（UI統合）
