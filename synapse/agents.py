"""
Synapse - エージェント呼び出し
Anthropic Tool Use API のループを管理する
"""

import json

from synapse.config import MAX_TOKENS, MAX_TOOL_ITERATIONS
from synapse.tools import execute_tool


def run_agent(client, model, system, messages, tools, sandbox, log_fn, max_iterations=None):
    if max_iterations is None:
        max_iterations = MAX_TOOL_ITERATIONS

    kwargs = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": list(messages),
    }
    if tools:
        kwargs["tools"] = tools

    for i in range(max_iterations):
        response = client.messages.create(**kwargs)

        if response.stop_reason == "end_turn":
            text = _extract_text(response)
            return text, kwargs["messages"]

        if response.stop_reason == "tool_use":
            kwargs["messages"].append(
                {
                    "role": "assistant",
                    "content": response.content,
                }
            )

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    input_preview = json.dumps(block.input, ensure_ascii=False)[:200]
                    log_fn(f"  [Tool] {block.name}({input_preview})")

                    result = execute_tool(sandbox, block.name, block.input)
                    log_fn(f"  [Result] {str(result)[:500]}")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )

            kwargs["messages"].append(
                {
                    "role": "user",
                    "content": tool_results,
                }
            )
        else:
            text = _extract_text(response)
            return text, kwargs["messages"]

    return "Error: max tool iterations reached", kwargs["messages"]


def _extract_text(response) -> str:
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return text
