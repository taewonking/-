import streamlit as st
import google.generativeai as genai
import base64
import json
from PIL import Image
import io

# ── 페이지 설정 ────────────────────────────────────────────
st.set_page_config(page_title="메뉴지니 🍜", page_icon="🍜", layout="centered")

st.markdown("""
<style>
.header { background: linear-gradient(135deg,#ea580c,#f97316); padding: 20px; border-radius: 12px; color: white; margin-bottom: 16px; }
.header h1 { margin: 0; font-size: 28px; }
.header p { margin: 4px 0 0; opacity: 0.9; font-size: 14px; }
.top-pick { background: linear-gradient(135deg,#fff7ed,#fef3c7); border: 2px solid #fcd34d; border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; }
.menu-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; margin-bottom: 8px; background: white; }
.menu-card-rec { border: 1.5px solid #fb923c; border-radius: 12px; padding: 14px; margin-bottom: 8px; background: linear-gradient(135deg,#fff7ed,#fff); }
.tag { display: inline-block; background: #f3f4f6; color: #4b5563; border-radius: 20px; padding: 2px 9px; font-size: 12px; margin: 2px; }
.allergy-warn { background: #fef2f2; border-radius: 8px; padding: 6px 10px; color: #dc2626; font-size: 13px; margin-top: 6px; }
.rec-reason { background: #fff7ed; border-radius: 8px; padding: 6px 10px; color: #92400e; font-size: 13px; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

LANGS = {
    "🇰🇷 한국어": "Korean",
    "🇺🇸 English": "English",
    "🇯🇵 日本語": "Japanese",
    "🇨🇳 中文": "Chinese",
    "🇫🇷 Français": "French",
    "🇪🇸 Español": "Spanish",
    "🇩🇪 Deutsch": "German",
}
DIETS = ["없음", "채식 (Vegetarian)", "비건 (Vegan)", "할랄 (Halal)", "글루텐프리 (Gluten-free)"]
ALLERGIES = ["견과류", "해산물", "유제품", "계란", "밀", "콩"]
SPICE = ["상관없음", "약하게", "보통", "맵게"]

st.markdown("""
<div class="header">
  <h1>🍜 메뉴지니</h1>
  <p>메뉴판 사진 한 장으로 나에게 딱 맞는 메뉴를</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ 내 취향 설정")
    lang_key = st.selectbox("🌍 언어", list(LANGS.keys()))
    lang_label = LANGS[lang_key]
    diet = st.selectbox("🥗 식단 유형", DIETS)
    allergies = st.multiselect("⚠️ 알레르기", ALLERGIES)
    spice = st.select_slider("🌶️ 매운맛", options=SPICE)
    st.divider()
    st.caption("Powered by Gemini AI")

uploaded = st.file_uploader("📷 메뉴판 사진 업로드", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    st.image(uploaded, use_column_width=True)

    if st.button("🔍 메뉴 분석하기", type="primary", use_container_width=True):
        with st.spinner("분석 중... 잠시만 기다려주세요 🍜"):
            try:
                # Gemini 설정
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.0-flash")

                # 이미지 로드
                img = Image.open(uploaded)

                prompt = f"""You are MenuGenie, an expert food and menu analysis AI.

Analyze the menu photo and respond ONLY with a valid JSON object.
No markdown, no backticks, no explanation — just raw JSON.

User preferences:
- Language for response: {lang_label}
- Diet type: {diet}
- Allergies: {', '.join(allergies) if allergies else 'none'}
- Spice preference: {spice}

Return exactly this JSON structure:
{{
  "restaurantType": "brief description of cuisine type",
  "items": [
    {{
      "name": "translated name in {lang_label}",
      "originalName": "original name on menu",
      "price": "price as shown",
      "emoji": "single most relevant food emoji",
      "description": "2-3 sentences about ingredients, taste, texture in {lang_label}",
      "tags": ["tag1", "tag2"],
      "allergyWarning": "warning if relevant to user allergies, or null",
      "recommended": true,
      "recommendReason": "why this suits the user"
    }}
  ],
  "topPick": "single best recommendation name",
  "localSpecialty": "most iconic local dish name if visible"
}}

Rules:
- recommended must be true for 2-4 best matching items, false for others
- If no allergy conflict, set allergyWarning to null
- recommendReason only if recommended is true, else null"""

                response = model.generate_content([prompt, img])
                raw = response.text.strip()

                # backtick 제거
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()

                result = json.loads(raw)

                st.divider()

                if result.get("topPick"):
                    st.markdown(f"""
<div class="top-pick">
  🏆 <strong>TOP PICK</strong><br>
  <span style="font-size:18px;font-weight:800">{result['topPick']}</span>
</div>
""", unsafe_allow_html=True)

                items = result.get("items", [])
                rec_items = [i for i in items if i.get("recommended")]
                tab_rec, tab_all = st.tabs([f"✨ 추천 메뉴 ({len(rec_items)})", f"📋 전체 메뉴 ({len(items)})"])

                def render_items(item_list):
                    for item in item_list:
                        is_rec = item.get("recommended", False)
                        card_class = "menu-card-rec" if is_rec else "menu-card"
                        rec_badge = ' <span style="background:#fb923c;color:white;border-radius:20px;padding:2px 8px;font-size:11px;font-weight:700">추천</span>' if is_rec else ""
                        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in item.get("tags", [])])
                        allergy_html = f'<div class="allergy-warn">⚠️ {item["allergyWarning"]}</div>' if item.get("allergyWarning") else ""
                        reason_html = f'<div class="rec-reason">💡 {item["recommendReason"]}</div>' if is_rec and item.get("recommendReason") else ""

                        st.markdown(f"""
<div class="{card_class}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <span style="font-weight:700;font-size:16px">{item.get('name','')}</span>{rec_badge}<br>
      <span style="color:#6b7280;font-size:12px">{item.get('originalName','')}</span><br>
      <span style="color:#6b7280;font-size:13px">{item.get('price','')}</span>
    </div>
    <span style="font-size:28px">{item.get('emoji','🍽️')}</span>
  </div>
  <p style="font-size:13.5px;color:#374151;margin:10px 0 6px;line-height:1.6">{item.get('description','')}</p>
  <div>{tags_html}</div>
  {allergy_html}
  {reason_html}
</div>
""", unsafe_allow_html=True)

                with tab_rec:
                    if rec_items:
                        render_items(rec_items)
                    else:
                        st.info("추천 항목이 없습니다. 전체 메뉴를 확인해보세요.")

                with tab_all:
                    render_items(items)

            except json.JSONDecodeError as e:
                st.error(f"응답 파싱 오류: {e}")
            except Exception as e:
                st.error(f"오류: {e}")
else:
    st.info("👆 메뉴판 사진을 업로드하면 AI가 분석해드립니다.")
