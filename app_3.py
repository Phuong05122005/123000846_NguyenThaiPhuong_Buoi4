import re
from collections import Counter

import streamlit as st

# ========= CẤU HÌNH TỪ VỰNG MẪU =========

PREFIX_MEANINGS = {
    "bất": "phủ định / không",
    "phi": "trái với / không theo",
    "tái": "lặp lại / làm lại",
    "siêu": "rất / vượt trội",
    "phụ": "thêm / phụ trợ",
}

POSITIVE_PHRASES = [
    "chạy nhanh", "chạy_nhanh", "chơi game mượt", "chơi_game_mượt",
    "màn hình đẹp", "màn_hình_đẹp", "đẹp quá", "rất đẹp",
    "đẹp_lung_linh", "siêu đẹp", "hài lòng", "rất hài lòng",
]

NEGATIVE_PHRASES = [
    "chạy chậm", "chạy_chậm", "lag", "giật lag", "giật_lag",
    "lâu kinh", "pin yếu", "pin_yếu", "tụt pin", "tụt_pin",
    "hao pin", "hao_pin", "tụt kinh khủng", "tụt_kinh_khủng",
    "máy nóng", "máy_hơi_nóng", "camera chụp xấu", "camera_chụp_xấu",
    "xấu quá",
]

EXAMPLE_TEXT = (
    "Máy chạy nhanh, chơi game mượt, màn hình đẹp nhưng pin tụt kinh khủng, "
    "sạc hoài luôn. Thỉnh thoảng hơi lag nữa. Mình khá hài lòng nhưng pin yếu quá."
)


# ========= HÀM TIỆN ÍCH =========

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def simple_tokenize(text: str):
    return text.split()


def detect_prefixes(tokens, prefixes: dict) -> Counter:
    counts = Counter()
    for tok in tokens:
        t = re.sub(
            r"[^\w_áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệ"
            r"íìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữự"
            r"ýỳỷỹỵđ]",
            "",
            tok.lower(),
        )
        for pref in prefixes:
            if t.startswith(pref):
                counts[pref] += 1
    return counts


def detect_phrases(text: str, phrases: list) -> Counter:
    counts = Counter()
    for p in phrases:
        if not p:
            continue
        matches = re.findall(re.escape(p), text)
        if matches:
            counts[p] = len(matches)
    return counts


def overall_sentiment(pos_count: int, neg_count: int) -> str:
    if pos_count == 0 and neg_count == 0:
        return "KHÔNG RÕ / TRUNG TÍNH"
    if pos_count > neg_count:
        return "TÍCH CỰC"
    elif neg_count > pos_count:
        return "TIÊU CỰC"
    return "TRUNG TÍNH / LẪN LỘN"


# ========= GIAO DIỆN STREAMLIT =========

st.set_page_config(
    page_title="Morphology & Sentiment tiếng Việt",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 Demo Morphology & Sentiment tiếng Việt")

st.markdown(
    """
**Mục tiêu demo:**
- Tokenize đơn giản và phát hiện **từ ghép / cụm từ** tiếng Việt.
- Phát hiện **yếu tố Hán‑Việt** dạng tiền tố nghĩa (`bất`, `phi`, `tái`, `siêu`, `phụ`).
- Sentiment rule-based theo cụm tích cực / tiêu cực.
"""
)

col_left, col_right = st.columns([1.1, 1.6])

with col_left:
    st.subheader("Nhập review / comment tiếng Việt")

    def _paste_example():
        st.session_state["input_text"] = EXAMPLE_TEXT

    st.button("Dán ví dụ gợi ý", on_click=_paste_example)

    text = st.text_area(
        "Văn bản",
        key="input_text",
        height=200,
        placeholder="Ví dụ: Máy chạy nhanh, chơi game mượt, màn hình đẹp nhưng pin tụt kinh khủng...",
    )

    analyze_btn = st.button("Phân tích Morphology & Sentiment")

with col_right:
    st.subheader("Kết quả")

    if not text.strip():
        st.info("Hãy nhập một đoạn văn rồi bấm **Phân tích**.")
    elif analyze_btn:
        norm_text = normalize_text(text)
        tokens = simple_tokenize(norm_text)

        # 1) Tokenization
        st.markdown("### 1️⃣ Tokenization (split đơn giản)")
        st.code(" | ".join(tokens))

        # 2) Tiền tố Hán-Việt
        st.markdown("### 2️⃣ Yếu tố Hán‑Việt dạng 'tiền tố nghĩa'")
        prefix_counts = detect_prefixes(tokens, PREFIX_MEANINGS)
        if prefix_counts:
            for pref, c in prefix_counts.items():
                meaning = PREFIX_MEANINGS.get(pref, "")
                st.write(f"- `{pref}`: **{c}** lần – nghĩa: *{meaning}*")
        else:
            st.write("_Chưa thấy tiền tố mẫu. Thử thêm từ như `bất_cẩn`, `phi_lý`, `siêu_rẻ`._")

        # 3) Sentiment rule-based — từng bước
        st.markdown("### 3️⃣ Sentiment (rule-based) — Mô phỏng từng bước")

        pos_counts = detect_phrases(norm_text, POSITIVE_PHRASES)
        neg_counts = detect_phrases(norm_text, NEGATIVE_PHRASES)
        pos_total = sum(pos_counts.values())
        neg_total = sum(neg_counts.values())
        total_phrases = pos_total + neg_total

        # --- Bước 1: Liệt kê cụm phát hiện ---
        st.markdown("#### Bước 1 — Phát hiện cụm cảm xúc trong văn bản")

        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown("🟢 **Cụm tích cực**")
            if pos_counts:
                for p, c in pos_counts.items():
                    st.write(f"- `{p}` × {c}")
            else:
                st.write("_Không tìm thấy_")
        with col_neg:
            st.markdown("🔴 **Cụm tiêu cực**")
            if neg_counts:
                for p, c in neg_counts.items():
                    st.write(f"- `{p}` × {c}")
            else:
                st.write("_Không tìm thấy_")

        # --- Bước 2: Thống kê ---
        st.markdown("#### Bước 2 — Thống kê số lượng")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric("Σ Tích cực (P)", pos_total)
        stat_col2.metric("Σ Tiêu cực (N)", neg_total)
        stat_col3.metric("Tổng cụm", total_phrases)

        # --- Bước 3: Tính score & công thức ---
        st.markdown("#### Bước 3 — Tính Sentiment Score")

        if total_phrases > 0:
            score = (pos_total - neg_total) / total_phrases
            st.latex(
                r"\text{Score} = \frac{P - N}{P + N} = "
                rf"\frac{{{pos_total} - {neg_total}}}{{{pos_total} + {neg_total}}} = "
                rf"{score:+.2f}"
            )
            st.caption("Score ∈ [−1, +1]. Gần +1 → tích cực, gần −1 → tiêu cực, quanh 0 → trung tính.")
        else:
            score = 0.0
            st.latex(r"\text{Score} = 0 \quad (\text{không phát hiện cụm nào})")

        # --- Bước 4: Quy tắc phân loại ---
        st.markdown("#### Bước 4 — Quy tắc phân loại")
        st.markdown(
            r"""
| Điều kiện | Nhãn |
|---|---|
| $P = 0$ và $N = 0$ | KHÔNG RÕ / TRUNG TÍNH |
| $P > N$ (Score > 0) | TÍCH CỰC |
| $N > P$ (Score < 0) | TIÊU CỰC |
| $P = N$ (Score = 0) | TRUNG TÍNH / LẪN LỘN |
"""
        )

        label = overall_sentiment(pos_total, neg_total)

        # --- Bước 5: Kết luận ---
        st.markdown("#### Bước 5 — Kết luận")
        if "TÍCH CỰC" in label:
            st.success(f"➡️ P ({pos_total}) > N ({neg_total})  →  **{label}**  (Score = {score:+.2f})")
        elif "TIÊU CỰC" in label:
            st.error(f"➡️ N ({neg_total}) > P ({pos_total})  →  **{label}**  (Score = {score:+.2f})")
        else:
            st.warning(f"➡️ P ({pos_total}) = N ({neg_total})  →  **{label}**  (Score = {score:+.2f})")
    else:
        st.info("Nhập văn bản và bấm **Phân tích** để bắt đầu demo.")
