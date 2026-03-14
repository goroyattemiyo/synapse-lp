# PostCraft

HTMLからBrain/Note投稿素材を一括生成する変換ツール。

## 概要

LPのHTMLを貼り付けるだけで、Brain/Note用のセクション画像・投稿原稿・投稿ガイドを自動生成します。

## 主な機能

- セクション画像自動生成: HTMLの各セクションをPNG画像として切り出し（Playwright使用）
- Brain/Note原稿生成: 有料境界マーカー・画像プレースホルダー付きの投稿原稿を自動作成
- 投稿ガイド生成: Brain/Noteへの投稿手順・チェックリストを自動生成
- 配色テーマ選択: 7種のプリセット＋カスタム配色でLP生成プロンプトを最適化
- ZIP一括ダウンロード: HTML・画像・原稿・ガイドをまとめてダウンロード

## セットアップ

    git clone https://github.com/goroyattemiyo/postcraft.git
    cd postcraft
    pip install -r requirements.txt
    playwright install chromium

## 使い方

    streamlit run synapse/ui.py

1. 商品情報を入力（配色テーマを選択）
2. 生成されたプロンプトをAIチャットに貼り付けてHTMLを生成
3. 完成したHTMLをStep 3に貼り付け
4. Brain/Note素材が自動生成、ZIPでダウンロード

## 出力ファイル

- lp.html: LP本体
- sections/*.png: セクション画像
- brain_draft.md: Brain投稿用原稿
- note_draft.md: Note投稿用原稿
- posting_guide.md: 投稿手順ガイド

## 開発

    pip install -r requirements-dev.txt
    ruff format . && ruff check . && mypy synapse/ --ignore-missing-imports
    pytest tests/ -v

## テスト状況

116テスト合格 / 1スキップ

## ライセンス

MIT