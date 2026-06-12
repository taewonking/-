import streamlit as st
import math

st.set_page_config(page_title="Calculator", page_icon="🧮", layout="centered")

st.title("🧮 Calculator")
st.markdown("사칙연산 · 모듈러 · 지수 · 로그 연산을 지원합니다.")

# ── 연산 선택 ──────────────────────────────────────────────
operation = st.selectbox(
    "연산 선택",
    [
        "➕ 덧셈 (a + b)",
        "➖ 뺄셈 (a - b)",
        "✖️ 곱셈 (a × b)",
        "➗ 나눗셈 (a ÷ b)",
        "🔢 모듈러 (a mod b)",
        "📈 지수 (a ^ b)",
        "📉 로그 (log_b(a))",
    ],
)

st.divider()

# ── 입력 ──────────────────────────────────────────────────
is_log = "로그" in operation

if is_log:
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("진수 (a)", value=100.0, format="%.6f")
    with col2:
        b = st.number_input("밑 (b)", value=10.0, format="%.6f")
else:
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("a", value=0.0, format="%.6f")
    with col2:
        b = st.number_input("b", value=1.0, format="%.6f")

# ── 계산 ──────────────────────────────────────────────────
if st.button("계산", use_container_width=True, type="primary"):
    result = None
    error = None

    try:
        if "덧셈" in operation:
            result = a + b
            expr = f"{a} + {b}"
        elif "뺄셈" in operation:
            result = a - b
            expr = f"{a} - {b}"
        elif "곱셈" in operation:
            result = a * b
            expr = f"{a} × {b}"
        elif "나눗셈" in operation:
            if b == 0:
                error = "0으로 나눌 수 없습니다."
            else:
                result = a / b
                expr = f"{a} ÷ {b}"
        elif "모듈러" in operation:
            if b == 0:
                error = "모듈러의 제수는 0이 될 수 없습니다."
            else:
                result = math.fmod(a, b)
                expr = f"{a} mod {b}"
        elif "지수" in operation:
            result = a ** b
            expr = f"{a} ^ {b}"
        elif "로그" in operation:
            if a <= 0:
                error = "진수(a)는 양수여야 합니다."
            elif b <= 0 or b == 1:
                error = "밑(b)은 양수이고 1이 아니어야 합니다."
            else:
                result = math.log(a, b)
                expr = f"log_{b}({a})"
    except OverflowError:
        error = "결과값이 너무 커서 표현할 수 없습니다."
    except Exception as e:
        error = f"오류: {e}"

    st.divider()
    if error:
        st.error(f"❌ {error}")
    else:
        st.success(f"**{expr} = {result:g}**")
        st.metric(label="결과", value=f"{result:g}")

# ── 도움말 ────────────────────────────────────────────────
with st.expander("연산 설명"):
    st.markdown(
        """
| 연산 | 설명 | 예시 |
|------|------|------|
| 덧셈 | a + b | 3 + 4 = 7 |
| 뺄셈 | a - b | 10 - 3 = 7 |
| 곱셈 | a × b | 3 × 4 = 12 |
| 나눗셈 | a ÷ b | 10 ÷ 4 = 2.5 |
| 모듈러 | a를 b로 나눈 나머지 | 10 mod 3 = 1 |
| 지수 | a의 b제곱 | 2 ^ 8 = 256 |
| 로그 | 밑이 b인 a의 로그 | log₁₀(100) = 2 |
"""
    )
