# Synapse LP Generator

Synapse マルチAIエージェント基盤を拡張し、Brain/Note向けの
LP品質コンテンツを自動生成するツール。

## 機能

- フルデザインHTML LP自動生成（inline CSS、レスポンシブ）
- セクション画像自動生成（Playwright、オプショナル）
- Brain投稿用ドラフト自動生成（有料境界マーカー付き）
- Note投稿用ドラフト自動生成（目次自動挿入）
- 投稿手順ガイド + チェックリスト自動生成
- Streamlit Web UI（モード切替・プレビュー・ZIP DL）

## アーキテクチャ

3エージェント構成: Orchestrator → Coder → Reviewer

LP生成は2フェーズ:
- Phase A: HTML生成（構造検証+コピー検証）
- Phase B: ドラフト生成（Brain/Note最適化）

## セットアップ

`ash
git clone https://github.com/goroyattemiyo/synapse-lp.git
cd synapse-lp
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-..." > .env
`

## 実行

`ash
# Web UI
streamlit run synapse/ui.py

# LP生成（CUI）
python -c "from synapse.lp_engine import run_synapse_lp; run_synapse_lp('商品情報をここに')"
`

## テスト

`ash
pip install -r requirements-dev.txt
pytest tests/ -v
`

## 開発ドキュメント

- [開発計画書](docs/DEVELOPMENT_PLAN.md)

## テスト状況

78テスト通過 / 1スキップ（Windows環境タイムアウトテスト）

## ライセンス

MIT