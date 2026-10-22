# Icon distinctness review

The review of the icon family against Microsoft's icons and the owner's sign-off (D01 T02 §7). The side-by-side comparison, the per-rule results and the sign-off are still to come; this file records the decisions made so far.

## Symbol contrast

Decided 2026-10-22 by the owner. At the approved 15% darkening, the large (`lg`) app symbols crossed the blurred orb and dark block with too little contrast: the share of symbol pixels at 3:1 or more was Stage 46%, Mail 64%, Grid 75%, Plan 82%, Write 84% and Flow 100%, and the lowest pixel was 2.29:1.

The owner compared three versions on light and dark backgrounds, at 128 and 48 pixels:

| Version | Change | Lowest symbol pixel |
| --- | --- | --- |
| A | Approved: symbol 15% toward black, frost 42% white | 2.29:1 |
| B | Symbol 35% toward black | 3.31:1 |
| C | Frost 60% white | 3.17:1 |

The owner chose B. Every `lg` symbol pixel now reaches 3:1 or more (Stage lowest at 3.31:1), and the glass is unchanged. The `md` and `sm` drawings and the pixel-grid variants keep the 15% shade, which already met 3:1. The `Palette` tests in `scripts/tests/test_build_icons.py` now hold the `lg` tier to 3:1 too.
