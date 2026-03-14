"""
Synapse - LP生成エンジン
エントリポイント + Phase A: HTML生成（Orchestrator -> Coder -> Reviewer）
"""

import json
import os
from datetime import datetime
from typing import Any

import anthropic
from dotenv import load_dotenv

from synapse.agents import run_agent
from synapse.config import (
    LP_CODER_MODEL,
    LP_MAX_ROUNDS,
    LP_MAX_TOKENS,
    LP_ORCHESTRATOR_MODEL,
    LP_REVIEWER_MODEL,
)
from synapse.lp_engine_drafts import run_phase_b
from synapse.lp_prompts import LP_CODER_SYSTEM, LP_ORCHESTRATOR_SYSTEM, LP_REVIEWER_SYSTEM
from synapse.sandbox import Sandbox
from synapse.tools import CODER_TOOLS, REVIEWER_TOOLS

load_dotenv()


def run_synapse_lp(product_info: str, callback: Any = None) -> dict[str, Any]:
    """LP生成のメインエントリポイント。"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    sandbox = Sandbox()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("logs", exist_ok=True)
    log_file = open(f"logs/lp_{timestamp}.txt", "w", encoding="utf-8")

    def log(text: str) -> None:
        print(text)
        log_file.write(text + chr(10))
        log_file.flush()

    def notify(agent: str, content: str) -> None:
        log(f"[{agent}]" + chr(10) + f"{content}" + chr(10))
        if callback:
            callback(agent, content)

    log("=" * 60)
    log("Synapse LP Generator v0.2.0")
    log(f"Product: {product_info[:100]}")
    log("=" * 60 + chr(10))

    result: dict[str, Any] = {
        "sandbox": sandbox,
        "files": {},
        "approved": False,
        "rounds": 0,
        "log_path": f"logs/lp_{timestamp}.txt",
        "phase_a_approved": False,
        "phase_b_approved": False,
    }

    try:
        run_phase_a(client, sandbox, product_info, result, notify, log)
        if result["phase_a_approved"]:
            run_phase_b(client, sandbox, result, notify, log)
        result["approved"] = result["phase_a_approved"] and result["phase_b_approved"]
        for file_path in sandbox.list_files():
            content = sandbox.read_file(file_path)
            result["files"][file_path] = content
            log(f"--- {file_path} ---")
            log(content)
    except Exception as e:
        notify("System", f"エラー: {str(e)}")
        result["error"] = str(e)
    finally:
        log_file.close()

    return result


def run_phase_a(
    client: Any,
    sandbox: Sandbox,
    product_info: str,
    result: dict[str, Any],
    notify: Any,
    log: Any,
) -> None:
    """Phase A: Orchestrator設計 -> Coder HTML生成 -> Reviewer検証。"""
    notify("System", "=== Phase A: LP HTML生成 ===")

    orch_messages = [
        {
            "role": "user",
            "content": (
                "以下の商品/サービス情報をもとに、"
                "売れるLPの構成を設計してください。" + chr(10) * 2 + product_info
            ),
        }
    ]
    orch_reply, _ = run_agent(
        client,
        LP_ORCHESTRATOR_MODEL,
        LP_ORCHESTRATOR_SYSTEM,
        orch_messages,
        None,
        sandbox,
        log,
        max_tokens=LP_MAX_TOKENS,
    )
    notify("Orchestrator", orch_reply)

    reviewer_reply = ""
    for round_num in range(1, LP_MAX_ROUNDS + 1):
        result["rounds"] = round_num
        notify("System", f"--- Phase A Round {round_num}/{LP_MAX_ROUNDS} ---")

        if round_num == 1:
            instruction = (
                "以下のLP設計に従って、lp.html を生成してください。"
                + chr(10)
                + "単一HTMLファイルにCSS inline で全て含めてください。"
                + chr(10)
                + "各セクションに data-section 属性を付与してください。"
                + chr(10) * 2
                + orch_reply
            )
        else:
            instruction = (
                "以下の指摘を修正してください。lp.html のみ修正:" + chr(10) * 2 + reviewer_reply
            )

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
        review_instruction = (
            "以下のファイルからlp.htmlを検証してください。"
            + chr(10)
            + json.dumps(files, ensure_ascii=False)
            + chr(10) * 2
            + "構造チェック: 12セクション, data-section属性, CTAボタン, レスポンシブ"
            + chr(10)
            + "コピーチェック: 致命的問題のみ指摘"
            + chr(10)
            + "構造チェック全パス AND コピーに致命的問題なし -> APPROVED"
        )
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
            notify("System", f"Phase A: Round {round_num} でHTML承認!")
            result["phase_a_approved"] = True
            break
    else:
        notify("System", f"Phase A: {LP_MAX_ROUNDS}ラウンドでHTML承認に至らず")
