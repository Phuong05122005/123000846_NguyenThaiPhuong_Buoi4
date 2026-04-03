"""
BÀI TẬP: Morphology & Sentiment tiếng Việt với underthesea
Phiên bản tối ưu giao diện + hiển thị underthesea giống yêu cầu
"""

import re
from collections import Counter

import streamlit as st

# TODO 1: Import
from underthesea import word_tokenize, sentiment

# ========= CẤU HÌNH =========
PREFIX_MEANINGS = {
    "bất": "phủ định / không",
    "phi": "trái với / không theo",
    "tái": "lặp lại / làm lại",
    "siêu": "rất / vượt trội",
    "phụ": "thêm / phụ trợ",
}

POSITIVE_PHRASES = ["chạy nhanh", "chạy_nhanh", "chơi game mượt", "chơi_game_mượt",
                    "màn hình đẹp", "màn_hình_đẹp", "đẹp quá", "rất đẹp", "đẹp_lung_linh",
                    "siêu đẹp", "hài lòng", "rất hài lòng"]

NEGATIVE_PHRASES = ["chạy chậm", "chạy_chậm", "lag", "giật lag", "giật_lag", "lâu kinh",
                    "pin yếu", "pin_yếu", "tụt pin", "tụt_pin", "hao pin", "hao_pin",
                    "tụt kinh khủng", "máy nóng", "camera chụp xấu", "xấu quá"]

EXAMPLE_TEXT = (
    "Máy chạy nhanh, chơi game mượt, màn hình đẹp nhưng pin tụt kinh khủng, "
    "sạc hoài luôn. Thỉnh thoảng hơi lag nữa. Mình khá hài lòng nhưng pin yếu quá."
)

# ========= HÀM =========
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def simple_tokenize(text: str):
    return text.split()

def underthesea_tokenize(text: str):
    tokens_list = word_tokenize(text)
    tokens_text = word_tokenize(text, format="text")
    return tokens_list, tokens_text

def safe_sentiment(text: str) -> str:
    try:
        result = sentiment(text, domain='general')
        if isinstance(result, (list, tuple)) and len(result) > 0:
            label = str(result[0])
            if "#" in label:
                label = label.split("#")[-1]
            return label.lower().strip()
        if isinstance(result, str):
            return result.lower().strip()
        return "neutral"
    except Exception:
        return "neutral"

def detect_prefixes(tokens, prefixes):
    counts = Counter()
    for tok in tokens:
        t = re.sub(r"[^\w_áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]", "", tok.lower())
        for pref in prefixes:
            if t.startswith(pref):
                counts[pref] += 1
    return counts

def detect_phrases(text: str, phrases: list):
    counts = Counter()
    for p in phrases:
        if p:
            counts[p] = len(re.findall(re.escape(p), text))
    return counts

def overall_sentiment(pos: int, neg: int) -> str:
    if pos == 0 and neg == 0:
        return "TRUNG TÍNH"
    if pos > neg:
        return "TÍCH CỰC"
    elif neg > pos:
        return "TIÊU CỰC"
    return "TRUNG TÍNH / LẪN LỘN"

# ========= GIAO DIỆN =========
st.set_page_config(
    page_title="Morphology & Sentiment VN",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧬 Morphology & Sentiment Analysis tiếng Việt")
st.markdown("**Ứng dụng phân tích hình thái và cảm xúc với underthesea**")

# Sidebar
with st.sidebar:
    st.header("📝 Input")
    if st.button("📋 Dán ví dụ", use_container_width=True):
        st.session_state.input_text = EXAMPLE_TEXT

    text = st.text_area(
        "Nhập review/comment tiếng Việt",
        key="input_text",
        height=180,
        placeholder="Ví dụ: Máy chạy nhanh nhưng pin yếu quá...",
    )

    st.divider()
    analyze_btn = st.button("🚀 Phân tích ngay", type="primary", use_container_width=True)

# Main content
if not text.strip():
    st.info("👈 Hãy nhập văn bản vào sidebar và nhấn **Phân tích ngay**", icon="ℹ️")
elif analyze_btn:
    norm_text = normalize_text(text)

    tab1, tab2, tab3 = st.tabs(["🔤 Tokenization", "🔖 Tiền tố Hán-Việt", "❤️ Sentiment Analysis"])

    # Tab 1: Tokenization
    with tab1:
        st.subheader("So sánh hai phương pháp Tokenization")
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**Cách 1: split() đơn giản**")
            with st.container(border=True):
                st.code(" | ".join(simple_tokenize(norm_text)), language=None)

        with col2:
            st.markdown("**Cách 2: underthesea `word_tokenize`**")
            tokens_list, tokens_text = underthesea_tokenize(text)
            with st.container(border=True):
                st.code(" | ".join(tokens_list), language=None)
                st.caption(f"Dạng chuỗi: `{tokens_text}`")

    # Tab 2: Tiền tố
    with tab2:
        st.subheader("Phát hiện tiền tố Hán-Việt")
        prefix_counts = detect_prefixes(tokens_list, PREFIX_MEANINGS)
        if prefix_counts:
            for pref, cnt in prefix_counts.items():
                st.info(f"**{pref}** xuất hiện **{cnt}** lần → *{PREFIX_MEANINGS.get(pref)}*")
        else:
            st.write("Không phát hiện tiền tố mẫu trong văn bản này.")

    # Tab 3: Sentiment (Phần được sửa theo ảnh)
    with tab3:
        st.subheader("Phân tích Sentiment")

        col_rule, col_ut = st.columns(2, gap="large")

        # Rule-based
        with col_rule:
            st.markdown("#### 🔧 Cách 1 — Rule-based")
            pos_counts = detect_phrases(norm_text, POSITIVE_PHRASES)
            neg_counts = detect_phrases(norm_text, NEGATIVE_PHRASES)
            pos_total = sum(pos_counts.values())
            neg_total = sum(neg_counts.values())

            subcol1, subcol2 = st.columns(2)
            with subcol1:
                with st.container(border=True):
                    st.metric("Tích cực", pos_total)
                    if pos_counts:
                        for p, c in pos_counts.items():
                            st.caption(f"• {p} ×{c}")
            with subcol2:
                with st.container(border=True):
                    st.metric("Tiêu cực", neg_total)
                    if neg_counts:
                        for p, c in neg_counts.items():
                            st.caption(f"• {p} ×{c}")

            label_rule = overall_sentiment(pos_total, neg_total)
            if label_rule == "TÍCH CỰC":
                st.success(f"**Kết luận:** {label_rule}")
            elif label_rule == "TIÊU CỰC":
                st.error(f"**Kết luận:** {label_rule}")
            else:
                st.warning(f"**Kết luận:** {label_rule}")

        # === PHẦN underthesea ĐÃ SỬA GIỐNG ẢNH ===
        with col_ut:
            st.markdown("#### 👁️ Cách 2 — underthesea <span style='color:#00ff88'>sentiment()</span>", unsafe_allow_html=True)
            
            senti_label = safe_sentiment(text)
            
            # Khung giống hệt ảnh bạn gửi
            st.markdown(
                f"""
                <div style="background-color: #1e3a8a; padding: 16px; border-radius: 8px; margin-top: 10px;">
                    <strong style="color: white;">Nhãn underthesea:</strong> 
                    <span style="color: #60a5fa; font-weight: 500;">{senti_label}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # So sánh
        st.divider()
        st.markdown("#### 🔍 So sánh hai phương pháp")
        st.markdown("""
        | Tiêu chí              | Rule-based                          | underthesea                          |
        |-----------------------|-------------------------------------|--------------------------------------|
        | Phương pháp           | Dựa trên từ điển cố định            | Model NLP đã huấn luyện              |
        | Ưu điểm               | Minh bạch, dễ hiểu                  | Xử lý ngữ cảnh tốt hơn               |
        | Nhược điểm            | Dễ bỏ sót cụm mới                   | Khó giải thích (black-box)           |
        """)

else:
    st.info("Nhấn **Phân tích ngay** để xem kết quả", icon="👈")

st.caption("Bài tập Morphology & Sentiment tiếng Việt • Tối ưu giao diện")