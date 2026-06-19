import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

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

st.divider()

# ── 그래프 ────────────────────────────────────────────────
st.subheader("📊 함수 그래프")

PRESETS = {
    "직접 입력": "",
    "y = x²": "x**2",
    "y = x³": "x**3",
    "y = √x": "np.sqrt(x)",
    "y = |x|": "np.abs(x)",
    "y = sin(x)": "np.sin(x)",
    "y = cos(x)": "np.cos(x)",
    "y = tan(x)": "np.tan(x)",
    "y = eˣ": "np.exp(x)",
    "y = ln(x)": "np.log(x)",
    "y = log₁₀(x)": "np.log10(x)",
    "y = 1/x": "1/x",
}

preset = st.selectbox("프리셋 함수", list(PRESETS.keys()))

if preset == "직접 입력":
    func_input = st.text_input(
        "함수 입력 (x를 변수로 사용)",
        value="x**2",
        placeholder="예: x**2 + 2*x + 1, np.sin(x), np.exp(-x)"
    )
else:
    func_input = st.text_input(
        "함수 입력 (x를 변수로 사용)",
        value=PRESETS[preset],
    )

col1, col2 = st.columns(2)
with col1:
    x_min = st.number_input("x 최솟값", value=-10.0)
with col2:
    x_max = st.number_input("x 최댓값", value=10.0)

if st.button("그래프 그리기", use_container_width=True):
    if x_min >= x_max:
        st.error("❌ x 최솟값은 최댓값보다 작아야 합니다.")
    elif not func_input.strip():
        st.error("❌ 함수를 입력해주세요.")
    else:
        try:
            x = np.linspace(x_min, x_max, 1000)
            # 허용된 함수만 사용
            allowed = {
                "np": np, "x": x,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "exp": np.exp, "log": np.log, "log10": np.log10,
                "log2": np.log2, "sqrt": np.sqrt, "abs": np.abs,
                "pi": np.pi, "e": np.e,
            }
            y = eval(func_input, {"__builtins__": {}}, allowed)
            y = np.where(np.isfinite(y), y, np.nan)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(x, y, color="#ea580c", linewidth=2)
            ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
            ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title(f"y = {func_input}")
            ax.grid(True, alpha=0.3)
            ax.set_xlim(x_min, x_max)

            # y축 범위 자동 조정 (이상값 제외)
            y_finite = y[np.isfinite(y)]
            if len(y_finite) > 0:
                y_range = np.percentile(y_finite, [2, 98])
                margin = (y_range[1] - y_range[0]) * 0.1 or 1
                ax.set_ylim(y_range[0] - margin, y_range[1] + margin)

            st.pyplot(fig)
            plt.close(fig)

        except Exception as e:
            st.error(f"❌ 함수 오류: {e}\n\n힌트: numpy 함수는 np.sin(x) 형태로 입력하세요.")

st.caption("사용 가능: x, np.sin, np.cos, np.tan, np.exp, np.log, np.log10, np.sqrt, np.abs, np.pi, np.e")
