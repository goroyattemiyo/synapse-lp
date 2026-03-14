"""E2Eテスト: 実APIでLP生成を実行する。"""

import os


def main():
    product_info = os.environ.get(
        "PRODUCT_INFO",
        "AI活用ガイド。ターゲットは副業初心者。価格1000円。",
    )
    print(f"Product: {product_info}")

    from synapse.lp_engine import run_synapse_lp

    result = run_synapse_lp(product_info)
    files = result.get("files", {})

    print(f"Files: {list(files.keys())}")
    print(
        f"Approved: {result.get(chr(39) + chr(97) + chr(112) + chr(112) + chr(114) + chr(111) + chr(118) + chr(101) + chr(100) + chr(39), False)}"
    )
    print(
        f"Rounds: {result.get(chr(39) + chr(114) + chr(111) + chr(117) + chr(110) + chr(100) + chr(115) + chr(39), 0)}"
    )

    assert "lp.html" in files, "lp.html not generated"
    assert len(files["lp.html"]) > 100, "lp.html too small"
    print("E2E test passed!")


if __name__ == "__main__":
    main()
