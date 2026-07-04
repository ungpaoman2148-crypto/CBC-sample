# dashboard.py — แดชบอร์ดผู้สมัครชมรม (สร้างด้วย Streamlit)
# วิธีรัน:  python -m streamlit run dashboard.py
# ต้องลงก่อน: python -m pip install streamlit pandas plotly

import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(page_title="แดชบอร์ดผู้สมัครชมรม", layout="wide")

PRIMARY = "#1D9E75"
PURPLE  = "#534AB7"
BLUE    = "#378ADD"
PALETTE = ["#1D9E75", "#534AB7", "#378ADD", "#D85A30"]

@st.cache_data
def load_data():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    res = supabase.table("applicants").select("*").execute()
    return pd.DataFrame(res.data)

df = load_data()

# ---------- 3) หัวเรื่อง ----------
st.title("ภาพรวมผู้สมัครชมรม")
st.caption("ข้อมูลตัวอย่าง · แดชบอร์ดสร้างด้วย Streamlit + Plotly")

# ---------- 4) Sidebar: ตัวกรองข้อมูล ----------
st.sidebar.header("ตัวกรองข้อมูล")

all_faculties = sorted(df["faculty"].unique())
sel_fac = st.sidebar.multiselect("เลือกคณะ", all_faculties, default=all_faculties)

YEAR_ORDER = ["ปี 1", "ปี 2", "ปี 3", "ปี 4"]
all_years = [y for y in YEAR_ORDER if y in df["year"].unique()]
sel_year = st.sidebar.multiselect("เลือกชั้นปี", all_years, default=all_years)

st.sidebar.caption("เลือกตัวกรองแล้วกราฟทุกอันจะอัปเดตตามทันที")

# ---------- 5) กรองข้อมูลตามที่เลือก ----------
dff = df[df["faculty"].isin(sel_fac) & df["year"].isin(sel_year)]

# ถ้ากรองจนไม่เหลือข้อมูล ให้แจ้งเตือนแล้วหยุด
if dff.empty:
    st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก — ลองเลือกใหม่อีกครั้ง")
    st.stop()

# ---------- 6) แถวตัวเลขสรุป (KPI) ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("ผู้สมัครทั้งหมด", f"{len(dff)} คน")
k2.metric("จำนวนคณะ", dff["faculty"].nunique())
k3.metric("อายุเฉลี่ย", f'{dff["age"].mean():.1f} ปี')
k4.metric("ปรึกษาบ่อยสุด", dff["topic"].value_counts().idxmax())

st.divider()

# ---------- 7) แถวกราฟที่ 1: คณะ + ชั้นปี ----------
c1, c2 = st.columns(2)

with c1:
    st.subheader("ผู้สมัครแยกตามคณะ")
    d = dff["faculty"].value_counts().reset_index()
    d.columns = ["คณะ", "จำนวน"]
    fig = px.bar(d, x="จำนวน", y="คณะ", orientation="h",
                 text="จำนวน", color_discrete_sequence=[PRIMARY])
    fig.update_layout(yaxis={"categoryorder": "total ascending"},
                      height=360, margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("สัดส่วนตามชั้นปี")
    present_years = [y for y in YEAR_ORDER if y in dff["year"].unique()]
    d = dff["year"].value_counts().reindex(present_years).reset_index()
    d.columns = ["ชั้นปี", "จำนวน"]
    fig = px.pie(d, names="ชั้นปี", values="จำนวน", hole=0.5,
                 color_discrete_sequence=PALETTE)
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ---------- 8) แถวกราฟที่ 2: เรื่องที่ปรึกษา + ช่องทาง ----------
c3, c4 = st.columns(2)

with c3:
    st.subheader("เรื่องที่อยากปรึกษา")
    d = dff["topic"].value_counts().reset_index()
    d.columns = ["เรื่อง", "จำนวน"]
    fig = px.bar(d, x="จำนวน", y="เรื่อง", orientation="h",
                 text="จำนวน", color_discrete_sequence=[PURPLE])
    fig.update_layout(yaxis={"categoryorder": "total ascending"},
                      height=360, margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("ช่องทางที่รู้จักชมรม")
    d = dff["channel"].value_counts().reset_index()
    d.columns = ["ช่องทาง", "จำนวน"]
    fig = px.bar(d, x="ช่องทาง", y="จำนวน",
                 text="จำนวน", color_discrete_sequence=[BLUE])
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ---------- 9) กราฟแนวโน้มยอดสมัครรายเดือน ----------
st.subheader("ยอดสมัครรายเดือน")
d = dff["apply_month"].value_counts().sort_index().reset_index()
d.columns = ["เดือน", "จำนวน"]
fig = px.line(d, x="เดือน", y="จำนวน", markers=True,
              color_discrete_sequence=[PRIMARY])
fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)

# ---------- 10) ตารางข้อมูลดิบ (ซ่อนไว้ กดเปิดได้) ----------
with st.expander("ดูตารางข้อมูลทั้งหมด"):
    st.dataframe(dff, use_container_width=True)

st.caption("สร้างโดย [ใส่ชื่อคุณ] · สมัครทีม Data — Coach by CBAF")
