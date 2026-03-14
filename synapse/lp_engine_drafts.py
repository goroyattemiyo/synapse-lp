"""
Synapse - LP生成エンジン Phase B
二段構成: HTMLパースで素材テキスト抽出 -> AIでプラットフォーム最適化
"""

import json
from typing import Any

from synapse.agents import run_agent
from synapse.config import LP_CODER_MODEL, LP_MAX_TOKENS, LP_REVIEWER_MODEL
from synapse.draft_generator import (
    generate_brain_draft,
    generate_note_draft,
    generate_posting_guide,
)
from synapse.image_pipeline import extract_sections
from synapse.lp_prompts import LP_CODER_SYSTEM, LP_REVIEWER_SYSTEM
from synapse.sandbox import Sandbox
from synapse.tools import CODER_TOOLS, REVIEWER_TOOLS

LP_DRAFT_ROUNDS = 2


def run_phase_b(
    client: Any,
    sandbox: Sandbox,
    result: dict[str, Any],
    notify: Any,
    log: Any,
) -> None:
    """Phase B: HTMLパース -> 素材生成 -> AI最適化 -> Reviewer検証。"""
    notify("System", "=== Phase B: ドラフト生成（二段構成） ===")

    # Step 1: HTMLパースで素材テキスト生成
    html_content = sandbox.read_file("lp.html")
    sections = extract_sections(html_content)
    notify("System", f"HTMLパース完了: {len(sections)}セクション検出")

    raw_brain = generate_brain_draft(html_content, sections)
    raw_note = generate_note_draft(html_content, sections)
    posting_guide = generate_posting_guide(sections, raw_brain, raw_note)

    # posting_guide.md は決定論的生成（AI不経由）
    sandbox.write_file("posting_guide.md", posting_guide)
    notify("System", "posting_guide.md 生成完了（HTMLパースベース）")

    # Step 2: 素材テキストをAIに渡してプラットフォーム最適化
    reviewer_reply = ""
    for draft_round in range(1, LP_DRAFT_ROUNDS + 1):
        notify("System", f"--- Phase B Round {draft_round}/{LP_DRAFT_ROUNDS} ---")

        if draft_round == 1:
            instruction = _build_optimization_prompt(raw_brain, raw_note)
        else:
            instruction = "以下の指摘を修正してください:" + chr(10) * 2 + reviewer_reply

        coder_messages = [{"role": "user", "content": instruction}]
        coder_reply, _ = run_agent(
            client,
            LP_CODER_MODEL,
            LP_CODER_SYSTEM,
            coder_messages,
            CODER_TOOLS,
            sandbox,
            log,
            max_tokens=LP_MAX_TOKENS,
        )
        notify("Coder", coder_reply)

        files = sandbox.list_files()
        review_instruction = _build_review_prompt(files)
        reviewer_messages = [{"role": "user", "content": review_instruction}]
        reviewer_reply, _ = run_agent(
            client,
            LP_REVIEWER_MODEL,
            LP_REVIEWER_SYSTEM,
            reviewer_messages,
            REVIEWER_TOOLS,
            sandbox,
            log,
            max_tokens=LP_MAX_TOKENS,
        )
        notify("Reviewer", reviewer_reply)

        if "APPROVED" in reviewer_reply:
            notify("System", f"Phase B: Round {draft_round} でドラフト承認!")
            result["phase_b_approved"] = True
            break
    else:
        notify("System", f"Phase B: {LP_DRAFT_ROUNDS}ラウンドでドラフト承認に至らず")
        # フォールバック: AI最適化失敗時は素材テキストをそのまま使用
        _write_fallback(sandbox, raw_brain, raw_note, notify)


def _build_optimization_prompt(raw_brain: str, raw_note: str) -> str:
    """AI最適化用のプロンプトを構築する。"""
    return (
        "以下の素材テキストをプラットフォーム向けに最適化してください。"
        + chr(10) * 2
        + "【重要ルール】"
        + chr(10)
        + "- セクション順序・画像プレースホルダー・有料境界の位置は絶対に変更しない"
        + chr(10)
        + "- 構造はそのまま維持し、テキストのコピーライティングのみ改善する"
        + chr(10)
        + "- brain_draft.md として write_file で保存すること"
        + chr(10)
        + "- note_draft.md として write_file で保存すること"
        + chr(10)
        + "- posting_guide.md は既に生成済みなので触らないこと"
        + chr(10) * 2
        + "=== Brain素材テキスト ==="
        + chr(10)
        + raw_brain[:6000]
        + chr(10) * 2
        + "=== Note素材テキスト ==="
        + chr(10)
        + raw_note[:6000]
    )


def _build_review_prompt(files: list[str]) -> str:
    """Reviewer用のプロンプトを構築する。"""
    return (
        "以下のファイルを検証してください。"
        + chr(10)
        + json.dumps(files, ensure_ascii=False)
        + chr(10) * 2
        + "検証項目:"
        + chr(10)
        + "1. brain_draft.md が存在し、見出し/太字/引用/画像のみ使用しているか"
        + chr(10)
        + "2. note_draft.md が存在し、見出し/太字/箇条書き/引用/画像のみ使用しているか"
        + chr(10)
        + "3. posting_guide.md が存在するか"
        + chr(10)
        + "4. 有料境界マーカーが存在するか"
        + chr(10)
        + "5. 画像プレースホルダーが存在するか"
        + chr(10)
        + "全て問題なければ APPROVED"
    )


def _write_fallback(
    sandbox: Sandbox,
    raw_brain: str,
    raw_note: str,
    notify: Any,
) -> None:
    """AI最適化失敗時に素材テキストをフォールバックとして書き込む。"""
    notify("System", "フォールバック: 素材テキストをそのまま使用")
    sandbox.write_file("brain_draft.md", raw_brain)
    sandbox.write_file("note_draft.md", raw_note)
