import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Olist Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stAppFooter {display: none !important;}
    div[data-testid="stFooter"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ── Tokens ──────────────────────────────────────────────────────
NAVY  = "#0D1B2A"; PANEL = "#132336"; BORDER = "#1E3A52"
TEAL  = "#00C2CB"; AMBER = "#F5A623"; ROSE   = "#E8445A"
WHITE = "#F0F4F8"; MUTED = "#7A9BB5"; OK     = "#2DD4BF"

def apply_theme(fig, h=340, hovermode="closest", legend=False, leg=None):
    kw = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter,sans-serif", color=WHITE, size=13),
        title_font=dict(color=WHITE, size=15),
        margin=dict(l=10, r=10, t=38, b=10),
        height=h, hovermode=hovermode,
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER,
                   tickfont=dict(color=MUTED, size=12)),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER,
                   tickfont=dict(color=MUTED, size=12)),
        coloraxis_colorbar=dict(tickfont=dict(color=MUTED, size=11)),
        showlegend=legend,
    )
    if leg:
        kw["legend"] = {"bgcolor": "rgba(0,0,0,0)",
                        "font": dict(color=WHITE, size=12), **leg}
    fig.update_layout(**kw)
    return fig

def brl(v):
    if pd.isna(v): return "R$0"
    if v >= 1e6: return f"R${v/1e6:.1f}M"
    if v >= 1e3: return f"R${v/1e3:.0f}K"
    return f"R${v:.0f}"

def num(v):
    if pd.isna(v): return "0"
    if v >= 1e6: return f"{v/1e6:.1f}M"
    if v >= 1e3: return f"{v/1e3:.0f}K"
    return str(int(v))

# ── CSS ─────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: 'Inter', sans-serif !important;
  background-color: {NAVY} !important;
  color: {WHITE} !important;
  font-size: 15px;
}}
.main .block-container {{ padding: 2rem 2.5rem 4rem; max-width: 1440px; }}

/* hide sidebar toggle */
[data-testid="collapsedControl"] {{ display:none !important; }}

/* ── Header ── */
.hdr {{ padding-bottom:1.4rem; border-bottom:1px solid {BORDER}; margin-bottom:1.8rem; }}
.hdr-tag {{
  display:inline-block; background:rgba(0,194,203,.12);
  border:1px solid rgba(0,194,203,.3); color:{TEAL};
  font-size:.72rem; font-weight:600; letter-spacing:.09em;
  text-transform:uppercase; padding:3px 11px; border-radius:20px; margin-bottom:.6rem;
}}
.hdr-title {{
  font-family:'Space Grotesk',sans-serif; font-size:2.1rem;
  font-weight:700; color:{WHITE}; margin:0; letter-spacing:-.02em; line-height:1.1;
}}
.hdr-title span {{ color:{TEAL}; }}
.hdr-meta {{ font-size:.85rem; color:{MUTED}; margin:.4rem 0 0; }}

/* ── Filter bar ── */
.fbar {{
  background:{PANEL}; border:1px solid {BORDER}; border-radius:8px;
  padding:16px 20px 6px; margin-bottom:1.8rem;
}}
.fbar-label {{
  font-size:.7rem; font-weight:600; color:{TEAL};
  text-transform:uppercase; letter-spacing:.1em; margin-bottom:10px;
}}

/* fix slider + select colours */
[data-testid="stSelectbox"] > div > div {{
  background:{NAVY} !important; border:1px solid {BORDER} !important;
  border-radius:6px !important; color:{WHITE} !important; font-size:.88rem !important;
}}
[data-testid="stSelectbox"] label,
.stSlider label {{
  font-size:.72rem !important; font-weight:600 !important;
  color:{TEAL} !important; text-transform:uppercase !important; letter-spacing:.09em !important;
}}

/* ── Section label ── */
.slbl {{
  font-size:.72rem; font-weight:600; color:{TEAL};
  text-transform:uppercase; letter-spacing:.12em;
  margin:2rem 0 .9rem; display:flex; align-items:center; gap:8px;
}}
.slbl::after {{ content:''; flex:1; height:1px; background:{BORDER}; }}

/* ── KPI row ── */
.krow {{
  display:grid; gap:12px; margin-bottom:1.8rem;
}}
.krow-7  {{ grid-template-columns:repeat(7,1fr); }}
.krow-4  {{ grid-template-columns:repeat(4,1fr); }}

.kcard {{
  background:{PANEL}; border:1px solid {BORDER};
  border-radius:8px; padding:18px 16px 14px;
  min-height:114px; display:flex; flex-direction:column;
  position:relative; overflow:hidden;
  transition:border-color .2s, transform .2s;
}}
.kcard:hover {{ border-color:{TEAL}; transform:translateY(-2px); }}
.kcard::before {{
  content:''; position:absolute; top:0; left:0; right:0; height:2px; background:{TEAL};
}}
.kcard.amb::before {{ background:{AMBER}; }}
.kcard.ros::before {{ background:{ROSE};  }}

.ktop {{
  font-size:.7rem; font-weight:600; color:{MUTED};
  text-transform:uppercase; letter-spacing:.09em; margin-bottom:10px;
}}
.kval {{
  font-family:'Space Grotesk',sans-serif; font-size:1.65rem;
  font-weight:700; color:{WHITE}; line-height:1; margin-bottom:8px; white-space:nowrap;
}}
.ksub      {{ font-size:.72rem; color:{MUTED}; margin-top:auto; }}
.ksub.ok   {{ color:{OK};    }}
.ksub.warn {{ color:{AMBER}; }}
.ksub.bad  {{ color:{ROSE};  }}

/* ── Responsive KPI rows ── */
@media (max-width: 900px) {{
  .krow-7 {{ grid-template-columns:repeat(4,1fr); }}
  .krow-4 {{ grid-template-columns:repeat(2,1fr); }}
}}
@media (max-width: 600px) {{
  .krow-7 {{ grid-template-columns:repeat(2,1fr); }}
  .krow-4 {{ grid-template-columns:1fr 1fr; }}
  .kval {{ font-size:1.2rem; }}
  .kcard {{ min-height:90px; padding:14px 12px; }}
  .ktop {{ font-size:.65rem; }}
}}
@media (max-width: 400px) {{
  .krow-7, .krow-4 {{ grid-template-columns:1fr; }}
}}

/* ── Tabs ── */
div[data-baseweb="tab-list"] {{
  background:{PANEL}; border-radius:8px; border:1px solid {BORDER};
  padding:5px 6px; gap:4px; margin-bottom:1.4rem;
}}
div[data-baseweb="tab"] {{
  font-family:'Space Grotesk',sans-serif !important;
  font-size:.85rem !important; font-weight:500 !important;
  color:{MUTED} !important; border-radius:6px !important;
  padding:10px 24px !important;
  margin:0 4px !important;                 /* ← extra spacing between tabs */
  transition:all .18s ease !important; border:1px solid transparent !important;
}}
div[data-baseweb="tab"]:hover {{
  color:{WHITE} !important; background:rgba(0,194,203,.09) !important;
  border-color:{BORDER} !important;
}}
div[aria-selected="true"][data-baseweb="tab"] {{
  background:{TEAL} !important; color:{NAVY} !important;
  font-weight:700 !important; border-color:{TEAL} !important;
}}

/* ── Chart panel ── */
.cpanel {{
  background:{PANEL}; border:1px solid {BORDER}; border-radius:8px;
  padding:20px 18px 12px; margin-bottom:14px;
  transition:border-color .2s;
}}
.cpanel:hover {{ border-color:rgba(0,194,203,.35); }}
.ctitle {{
  font-family:'Space Grotesk',sans-serif; font-size:1rem;
  font-weight:600; color:{WHITE}; margin:0 0 3px;
}}
.ccap {{ font-size:.76rem; color:{MUTED}; margin:0 0 12px; line-height:1.45; }}

/* ── Insight boxes ── */
.ins {{
  border-radius:6px; padding:12px 16px;
  margin:4px 0 16px; font-size:.82rem; line-height:1.6; color:{WHITE};
}}
.ins.t {{ background:rgba(0,194,203,.07);  border:1px solid rgba(0,194,203,.22); border-left:3px solid {TEAL};  }}
.ins.a {{ background:rgba(245,166,35,.07); border:1px solid rgba(245,166,35,.22); border-left:3px solid {AMBER}; }}
.ins.r {{ background:rgba(232,68,90,.07);  border:1px solid rgba(232,68,90,.22);  border-left:3px solid {ROSE};  }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:{NAVY}; }}
::-webkit-scrollbar-thumb {{ background:{BORDER}; border-radius:10px; }}
::-webkit-scrollbar-thumb:hover {{ background:{MUTED}; }}

/* ── Footer ── */
.foot {{
  display:flex; justify-content:space-between;
  padding:12px 0; border-top:1px solid {BORDER};
  margin-top:3rem; font-size:.74rem; color:{MUTED};
}}
</style>
""", unsafe_allow_html=True)

# ── Data ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load():
    df = pd.read_csv("data/olist_master_clean.csv", low_memory=False)
    for c in ["order_purchase_timestamp","order_delivered_customer_date",
              "order_estimated_delivery_date","order_approved_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    if "delivery_days" not in df.columns:
        df["delivery_days"] = (df["order_delivered_customer_date"]
                               - df["order_purchase_timestamp"]).dt.days
    if "on_time" not in df.columns:
        df["on_time"] = (df["order_delivered_customer_date"]
                         <= df["order_estimated_delivery_date"])
    if "item_revenue" not in df.columns:
        df["item_revenue"] = df.get("price", 0) + df.get("freight_value", 0)
    if "order_month" not in df.columns:
        df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    # Always re-derive from timestamp — CSV may have saved these as day names
    df["order_hour"]      = df["order_purchase_timestamp"].dt.hour.astype(int)
    df["order_dayofweek"] = df["order_purchase_timestamp"].dt.dayofweek.astype(int)
    cc = "product_category_name_english"
    if cc not in df.columns:
        df[cc] = df.get("product_category_name", "unknown")
    df[cc] = df[cc].fillna("unknown")
    df["delivery_bucket"] = pd.cut(
        df["delivery_days"].clip(0, 100),
        bins=[0,7,14,21,30,100],
        labels=["≤ 1 week","1–2 weeks","2–3 weeks","3–4 weeks","4+ weeks"],
        include_lowest=True,
    )
    return df

with st.spinner("Loading…"):
    RAW = load()

# ── Header ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <div class="hdr-tag">E-Commerce Analytics · Brazil · 2016–2018</div>
  <p class="hdr-title">Olist <span>Intelligence</span> Dashboard</p>
  <p class="hdr-meta">{len(RAW):,} delivered orders &nbsp;·&nbsp; 9 merged datasets</p>
</div>""", unsafe_allow_html=True)

# ── Filters ─────────────────────────────────────────────────────
months = sorted(RAW["order_month"].dropna().unique())
states = ["All"] + sorted(RAW["customer_state"].dropna().unique().tolist())
cats   = ["All"] + sorted(RAW["product_category_name_english"].dropna().unique().tolist())

st.markdown(f'<div class="fbar"><div class="fbar-label">🎛 &nbsp;Filters — every chart updates instantly</div>', unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns([3, 2, 2])
with fc1:
    dr = st.select_slider("Date range", options=months, value=(months[0], months[-1]))
with fc2:
    ss = st.selectbox("Customer state", states)
with fc3:
    sc = st.selectbox("Product category", cats)
st.markdown("</div>", unsafe_allow_html=True)

# ── Apply filters ────────────────────────────────────────────────
df = RAW[(RAW["order_month"] >= dr[0]) & (RAW["order_month"] <= dr[1])].copy()
if ss != "All": df = df[df["customer_state"] == ss]
if sc != "All": df = df[df["product_category_name_english"] == sc]

# Drop rows with missing timestamps (these break many plots)
df = df.dropna(subset=["order_purchase_timestamp"])

if len(df) == 0:
    st.warning("No orders match these filters.")
    st.stop()

active = []
if dr != (months[0], months[-1]): active.append(f"{dr[0]} → {dr[1]}")
if ss != "All": active.append(ss)
if sc != "All": active.append(sc)
if active:
    pills = " · ".join(f'<span style="color:{TEAL}">{a}</span>' for a in active)
    st.markdown(
        f'<div style="font-size:.78rem;color:{MUTED};margin:-1rem 0 1.2rem 2px">'
        f'Filtered by {pills} — <strong style="color:{WHITE}">{len(df):,} orders</strong></div>',
        unsafe_allow_html=True)

# ── KPIs ────────────────────────────────────────────────────────
tot_rev  = df["item_revenue"].sum()
tot_ord  = df["order_id"].nunique()
aov      = df.groupby("order_id")["item_revenue"].sum().mean()
otr      = df["on_time"].mean() * 100
avr      = df["review_score"].mean()
med_del  = df["delivery_days"].median()
rc       = "customer_unique_id" if "customer_unique_id" in df.columns else "customer_id"
rpt      = (df.groupby(rc)["order_id"].nunique() > 1).mean() * 100

def kcard(label, value, sub, sub_cls="", variant=""):
    return (f'<div class="kcard {variant}">'
            f'<div class="ktop">{label}</div>'
            f'<div class="kval">{value}</div>'
            f'<div class="ksub {sub_cls}">{sub}</div>'
            f'</div>')

st.markdown('<div class="slbl">Platform Overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="krow krow-7">'
    + kcard("Total Revenue",   brl(tot_rev), "gross product revenue")
    + kcard("Total Orders",    num(tot_ord), "delivered & confirmed")
    + kcard("Avg Order Value", brl(aov),     "price + freight",          variant="amb")
    + kcard("On-Time Rate",    f"{otr:.1f}%",
            "above target" if otr >= 90 else "below 90% target",
            "ok" if otr >= 90 else "warn")
    + kcard("Avg Review",      f"{avr:.2f} ★",
            "above 4.0" if avr >= 4 else "below 4.0",
            "ok" if avr >= 4 else "bad",
            "" if avr >= 4 else "ros")
    + kcard("Median Delivery", f"{med_del:.0f} days",
            "to customer door",
            "warn" if med_del > 12 else "",
            "amb" if med_del > 12 else "")
    + kcard("Repeat Rate",     f"{rpt:.1f}%",
            "needs loyalty push" if rpt < 5 else "healthy retention",
            "bad" if rpt < 5 else "ok",
            "ros" if rpt < 5 else "")
    + '</div>',
    unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "📈  Revenue & Growth",
    "📦  Products",
    "🚚  Delivery & Satisfaction",
    "🏪  Sellers",
    "👤  Customers",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — REVENUE & GROWTH
# ════════════════════════════════════════════════════════════════
with t1:
    monthly = (df.groupby("order_month")
               .agg(revenue=("item_revenue","sum"), orders=("order_id","nunique"))
               .reset_index().sort_values("order_month"))
    monthly = monthly.dropna(subset=["order_month","revenue","orders"])

    st.markdown('<div class="cpanel">', unsafe_allow_html=True)
    st.markdown('<div class="ctitle">Monthly Revenue & Order Volume</div>', unsafe_allow_html=True)
    st.markdown('<div class="ccap">Bars = revenue (BRL) · Line = order count · Hover for exact values</div>', unsafe_allow_html=True)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["order_month"], y=monthly["revenue"],
        name="Revenue", marker_color=TEAL, opacity=.82,
        hovertemplate="<b>%{x}</b><br>Revenue: R$%{y:,.0f}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["orders"],
        name="Orders", line=dict(color=AMBER, width=2.5), mode="lines+markers",
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"), secondary_y=True)
    apply_theme(fig, h=320, hovermode="x unified", legend=True,
                leg={"orientation":"h","yanchor":"bottom","y":1.02,"x":0})
    fig.update_yaxes(gridcolor=BORDER, tickfont=dict(color=MUTED), secondary_y=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=MUTED), secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if "2017-11" in monthly["order_month"].values:
        bf  = monthly[monthly["order_month"]=="2017-11"]["revenue"].values[0]
        oct_v = monthly[monthly["order_month"]=="2017-10"]["revenue"].values[0] if "2017-10" in monthly["order_month"].values else None
        if oct_v and oct_v > 0:
            st.markdown(f'<div class="ins a">⚡ <strong>Black Friday 2017</strong> — revenue spiked '
                        f'<strong>{(bf/oct_v-1)*100:.0f}%</strong> MoM '
                        f'({brl(bf)} vs {brl(oct_v)} in October). '
                        f'Filter this month out when calculating baseline growth trends.</div>',
                        unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sr = (df.groupby("customer_state")
              .agg(revenue=("item_revenue","sum"), orders=("order_id","nunique"))
              .reset_index().sort_values("revenue", ascending=False).head(12))
        sr["avg_ticket"] = sr["revenue"] / sr["orders"].replace(0, 1)
        sr = sr.dropna(subset=["customer_state","revenue","avg_ticket"])
        st.markdown('<div class="cpanel"><div class="ctitle">Revenue by State</div>'
                    '<div class="ccap">Top 12 · color = average ticket value</div>', unsafe_allow_html=True)
        fig2 = px.bar(sr, x="customer_state", y="revenue",
            color="avg_ticket", color_continuous_scale=["#1E3A52", TEAL],
            labels={"revenue":"Revenue (BRL)","customer_state":"","avg_ticket":"Avg Ticket"})
        apply_theme(fig2, h=290)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        if "payment_type" in df.columns:
            pay = (df[df["payment_type"].notna() & (df["payment_type"] != "not_defined")]
                   .groupby("payment_type")["item_revenue"].sum().reset_index())
            pay.columns = ["type","rev"]
            pay = pay.dropna(subset=["type","rev"])
            st.markdown('<div class="cpanel"><div class="ctitle">Revenue by Payment Method</div>'
                        '<div class="ccap">Share of total platform revenue</div>', unsafe_allow_html=True)
            fig3 = px.pie(pay, values="rev", names="type", hole=.55,
                color_discrete_sequence=[TEAL, AMBER, ROSE, MUTED])
            fig3.update_traces(textposition="outside", textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>R$%{value:,.0f}<extra></extra>")
            apply_theme(fig3, h=290, legend=True, leg={"orientation":"v","x":1,"y":.5})
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Heatmap — force integer index and full hour range
    st.markdown('<div class="cpanel"><div class="ctitle">When Do Customers Shop?</div>'
                '<div class="ccap">Order count by day of week × hour · Brighter = more orders</div>',
                unsafe_allow_html=True)
    hmap = (df.groupby(["order_dayofweek","order_hour"])["order_id"]
            .count().reset_index())
    hmap.columns = ["day","hour","orders"]
    hmap["day"]  = pd.to_numeric(hmap["day"],  errors="coerce").astype(int)
    hmap["hour"] = pd.to_numeric(hmap["hour"], errors="coerce").astype(int)
    pivot = hmap.pivot(index="day", columns="hour", values="orders").fillna(0)
    # reindex both days and hours to ensure all present
    pivot = pivot.reindex(range(7), fill_value=0)
    pivot = pivot.reindex(columns=range(24), fill_value=0)  # all hours
    day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    pivot.index = day_names
    pivot.columns = [str(c) for c in pivot.columns]
    fig4 = px.imshow(pivot,
        color_continuous_scale=[[0,PANEL],[.35,BORDER],[1,TEAL]],
        aspect="auto", labels=dict(x="Hour of Day", y="", color="Orders"))
    apply_theme(fig4, h=230)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ════════════════════════════════════════════════════════════════
with t2:
    cc = "product_category_name_english"
    cs = (df.groupby(cc)
          .agg(revenue=("item_revenue","sum"), orders=("order_id","nunique"),
               avg_price=("price","mean"), avg_review=("review_score","mean"))
          .reset_index())
    cs = cs.dropna(subset=[cc, "revenue","orders"])

    c1, c2 = st.columns(2)
    with c1:
        top_r = cs.sort_values("revenue", ascending=False).head(12)
        top_r = top_r.dropna(subset=["revenue","avg_price"])
        st.markdown('<div class="cpanel"><div class="ctitle">Top 12 Categories by Revenue</div>'
                    '<div class="ccap">Color = average product price</div>', unsafe_allow_html=True)
        fig = px.bar(top_r, x="revenue", y=cc, orientation="h",
            color="avg_price", color_continuous_scale=["#1E3A52", TEAL],
            text=top_r["revenue"].apply(brl),
            labels={"revenue":"Revenue (BRL)", cc:""})
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        apply_theme(fig, h=390)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        top_v = cs.sort_values("orders", ascending=False).head(12)
        top_v = top_v.dropna(subset=["orders","avg_review"])
        st.markdown('<div class="cpanel"><div class="ctitle">Top 12 Categories by Volume</div>'
                    '<div class="ccap">Color = average review score — reveals satisfaction gaps</div>',
                    unsafe_allow_html=True)
        fig2 = px.bar(top_v, x="orders", y=cc, orientation="h",
            color="avg_review", color_continuous_scale=[ROSE, AMBER, OK],
            text=top_v["orders"].apply(lambda x: f"{x:,}"),
            labels={"orders":"Order Count", cc:"", "avg_review":"Avg Rating"})
        fig2.update_traces(textposition="outside")
        fig2.update_layout(yaxis={"categoryorder":"total ascending"})
        apply_theme(fig2, h=390)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    sc2 = cs[cs["orders"] >= 30].dropna(subset=["revenue","avg_review","avg_price"])
    if len(sc2) > 0:
        st.markdown('<div class="cpanel"><div class="ctitle">Category: Revenue vs Customer Satisfaction</div>'
                    '<div class="ccap">Bubble size = order count · Sweet spot = top-right · Dashed lines = medians</div>',
                    unsafe_allow_html=True)
        fig3 = px.scatter(sc2, x="revenue", y="avg_review",
            size="orders", color="avg_price", hover_name=cc,
            color_continuous_scale=["#1E3A52", TEAL], size_max=50,
            labels={"revenue":"Total Revenue (BRL)","avg_review":"Avg Review","avg_price":"Avg Price"})
        fig3.add_vline(x=sc2["revenue"].median(),    line_dash="dot", line_color=MUTED, opacity=.5)
        fig3.add_hline(y=sc2["avg_review"].median(), line_dash="dot", line_color=MUTED, opacity=.5)
        apply_theme(fig3, h=360)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if "freight_value" in df.columns and "price" in df.columns:
        fc = (df.groupby(cc)
              .agg(avg_freight=("freight_value","mean"), avg_price=("price","mean"))
              .reset_index())
        fc["freight_pct"] = fc["avg_freight"] / fc["avg_price"].replace(0, np.nan) * 100
        fc = fc.dropna(subset=["freight_pct", cc]).sort_values("freight_pct", ascending=False).head(15)
        if len(fc) > 0:
            st.markdown('<div class="cpanel"><div class="ctitle">Freight Cost as % of Product Price — Top 15</div>'
                        '<div class="ccap">High freight % suppresses conversions and perceived value</div>',
                        unsafe_allow_html=True)
            fig4 = px.bar(fc, x=cc, y="freight_pct",
                color="freight_pct", color_continuous_scale=[OK, AMBER, ROSE],
                labels={cc:"","freight_pct":"Freight % of Price"})
            fig4.update_layout(xaxis_tickangle=-35)
            apply_theme(fig4, h=310)
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 3 — DELIVERY & SATISFACTION
# ════════════════════════════════════════════════════════════════
with t3:
    c1, c2 = st.columns(2)
    with c1:
        cd = df[df["delivery_days"].between(0, 60)].dropna(subset=["delivery_days"])
        if len(cd) > 0:
            md, mn = cd["delivery_days"].median(), cd["delivery_days"].mean()
            st.markdown('<div class="cpanel"><div class="ctitle">Delivery Time Distribution</div>'
                        '<div class="ccap">Days between purchase and delivery</div>', unsafe_allow_html=True)
            fig = px.histogram(cd, x="delivery_days", nbins=55,
                color_discrete_sequence=[TEAL], opacity=.85,
                labels={"delivery_days":"Days to Deliver"})
            fig.add_vline(x=md, line_dash="dash", line_color=AMBER,
                annotation_text=f"Median {md:.0f}d", annotation_font_color=AMBER,
                annotation_position="top right")
            fig.add_vline(x=mn, line_dash="dot", line_color=ROSE,
                annotation_text=f"Mean {mn:.0f}d", annotation_font_color=ROSE)
            apply_theme(fig, h=290)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        sot = (df.groupby("customer_state")
               .agg(p=("on_time","mean"), n=("order_id","nunique"))
               .reset_index())
        sot["p"] *= 100
        sot = sot[sot["n"] >= 20].dropna(subset=["customer_state","p"])
        if len(sot) > 0:
            nat = df["on_time"].mean() * 100
            st.markdown(f'<div class="cpanel"><div class="ctitle">On-Time Delivery Rate by State</div>'
                        f'<div class="ccap">National average: {nat:.1f}%</div>', unsafe_allow_html=True)
            fig2 = px.bar(sot, x="customer_state", y="p",
                color="p", color_continuous_scale=[ROSE, AMBER, OK],
                labels={"customer_state":"","p":"On-Time %"})
            fig2.add_hline(y=nat, line_dash="dash", line_color=WHITE, opacity=.4,
                annotation_text=f"Avg {nat:.1f}%", annotation_font_color=MUTED)
            apply_theme(fig2, h=290)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cpanel"><div class="ctitle">How Delivery Speed Affects Customer Satisfaction</div>'
                '<div class="ccap">Average review score by delivery window — the business case for faster logistics</div>',
                unsafe_allow_html=True)
    bs = (df.groupby("delivery_bucket", observed=True)
          .agg(avg=("review_score","mean"), n=("order_id","nunique"))
          .reset_index())
    bs = bs.dropna(subset=["delivery_bucket","avg"])
    fig3 = px.bar(bs, x="delivery_bucket", y="avg",
        color="avg", color_continuous_scale=[ROSE, AMBER, OK],
        text=bs["avg"].apply(lambda x: f"{x:.2f} ★"),
        labels={"delivery_bucket":"Delivery Window","avg":"Avg Review Score"})
    fig3.update_traces(textposition="outside")
    fig3.update_layout(yaxis_range=[0,5.5], coloraxis_showscale=False)
    apply_theme(fig3, h=270)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    ls = bs[bs["delivery_bucket"]=="4+ weeks"]["avg"]
    fs = bs[bs["delivery_bucket"]=="≤ 1 week"]["avg"]
    if len(ls) and len(fs):
        st.markdown(f'<div class="ins r">📉 Orders taking 4+ weeks score '
                    f'<strong>{ls.values[0]:.2f}★</strong> vs '
                    f'<strong>{fs.values[0]:.2f}★</strong> for week-or-less deliveries — '
                    f'a <strong>{fs.values[0]-ls.values[0]:.2f}-point drop</strong>. '
                    f'Delivery speed is the single biggest satisfaction lever on this platform.</div>',
                    unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        sd = df["review_score"].value_counts().sort_index().reset_index()
        sd.columns = ["score","count"]
        sd["pct"] = sd["count"] / sd["count"].sum() * 100
        sd = sd.dropna(subset=["score","count"])
        st.markdown('<div class="cpanel"><div class="ctitle">Review Score Distribution</div>'
                    '<div class="ccap">% of all delivered orders</div>', unsafe_allow_html=True)
        fig4 = px.bar(sd, x="score", y="count",
            color="score", color_continuous_scale=[ROSE, AMBER, OK],
            text=sd["pct"].apply(lambda x: f"{x:.1f}%"),
            labels={"score":"★ Score","count":"Orders"})
        fig4.update_traces(textposition="outside")
        fig4.update_layout(coloraxis_showscale=False,
                           yaxis_range=[0, sd["count"].max()*1.15])
        apply_theme(fig4, h=280)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        if "order_estimated_delivery_date" in df.columns:
            df["est_days"] = (df["order_estimated_delivery_date"]
                              - df["order_purchase_timestamp"]).dt.days
            vv = df[df["est_days"].between(0,90) & df["delivery_days"].between(0,90)]
            vv = vv.dropna(subset=["est_days","delivery_days"])
            vv = vv.sample(min(3000, len(vv)), random_state=42)
            if len(vv) > 0:
                st.markdown('<div class="cpanel"><div class="ctitle">Actual vs Estimated Delivery</div>'
                            '<div class="ccap">Below diagonal = early · Above = late</div>',
                            unsafe_allow_html=True)
                fig5 = px.scatter(vv, x="est_days", y="delivery_days",
                    opacity=.2, color_discrete_sequence=[TEAL],
                    labels={"est_days":"Estimated Days","delivery_days":"Actual Days"})
                mx = int(max(vv["est_days"].max(), vv["delivery_days"].max()))
                fig5.add_trace(go.Scatter(x=[0,mx], y=[0,mx], mode="lines",
                    line=dict(color=AMBER, dash="dash", width=1.5),
                    showlegend=False))
                apply_theme(fig5, h=280)
                st.plotly_chart(fig5, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — SELLERS
# ════════════════════════════════════════════════════════════════
with t4:
    if "seller_id" not in df.columns:
        st.info("Seller data not in current view.")
    else:
        sl = (df.groupby("seller_id")
              .agg(revenue=("item_revenue","sum"), orders=("order_id","nunique"),
                   avg_rating=("review_score","mean"), avg_del=("delivery_days","mean"))
              .reset_index())
        sl = sl[sl["orders"] >= 5].dropna(subset=["seller_id","revenue","avg_rating"])
        if len(sl) == 0:
            st.info("Not enough seller data with ≥5 orders.")
        else:
            mr, ms = sl["revenue"].median(), sl["avg_rating"].median()

            def seg(r):
                h = r["revenue"] >= mr; g = r["avg_rating"] >= ms
                if h and g:      return "⭐ Star Sellers"
                if h and not g:  return "⚠️ High Rev / Low Sat"
                if not h and g:  return "💎 Hidden Gems"
                return "🔴 At Risk"
            sl["segment"] = sl.apply(seg, axis=1)
            sc = sl["segment"].value_counts()
            cm = {"⭐ Star Sellers":OK, "⚠️ High Rev / Low Sat":AMBER,
                  "💎 Hidden Gems":TEAL, "🔴 At Risk":ROSE}

            k1,k2,k3,k4 = st.columns(4)
            for col, sg, var in [(k1,"⭐ Star Sellers",""), (k2,"⚠️ High Rev / Low Sat","amb"),
                                  (k3,"💎 Hidden Gems",""),  (k4,"🔴 At Risk","ros")]:
                with col:
                    col.markdown(
                        f'<div class="kcard {var}">'
                        f'<div class="ktop">{sg}</div>'
                        f'<div class="kval">{sc.get(sg,0):,}</div>'
                        f'<div class="ksub">sellers</div></div>',
                        unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

            st.markdown('<div class="cpanel"><div class="ctitle">Seller Performance Quadrant</div>'
                        '<div class="ccap">Revenue vs satisfaction · Bubble = order count · Dashed = medians</div>',
                        unsafe_allow_html=True)
            fig = px.scatter(sl, x="revenue", y="avg_rating", color="segment", size="orders",
                hover_data={"seller_id":True,"avg_del":":.1f","orders":True},
                color_discrete_map=cm, size_max=35,
                labels={"revenue":"Total Revenue (BRL)","avg_rating":"Avg Review Score"})
            fig.add_vline(x=mr, line_dash="dot", line_color=MUTED, opacity=.4)
            fig.add_hline(y=ms, line_dash="dot", line_color=MUTED, opacity=.4)
            apply_theme(fig, h=400, legend=True,
                        leg={"orientation":"h","yanchor":"bottom","y":1.01,"x":0})
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            warn = sl[sl["segment"]=="⚠️ High Rev / Low Sat"]
            if len(warn):
                st.markdown(f'<div class="ins a">⚠️ <strong>{len(warn)} high-revenue sellers</strong> '
                            f'have below-median satisfaction, accounting for '
                            f'<strong>{brl(warn["revenue"].sum())}</strong> in revenue. '
                            f'These represent platform reputation risk — prioritise for seller support.</div>',
                            unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                ts = sl.sort_values("revenue", ascending=False).head(15)
                ts = ts.dropna(subset=["seller_id","revenue","avg_rating"])
                st.markdown('<div class="cpanel"><div class="ctitle">Top 15 Sellers by Revenue</div>'
                            '<div class="ccap">Color = average review score</div>', unsafe_allow_html=True)
                fig2 = px.bar(ts, x="revenue", y="seller_id", orientation="h",
                    color="avg_rating", color_continuous_scale=[ROSE, AMBER, OK],
                    text=ts["revenue"].apply(brl),
                    labels={"revenue":"Revenue (BRL)","seller_id":"","avg_rating":"Avg Rating"})
                fig2.update_traces(textposition="outside")
                fig2.update_layout(yaxis={"categoryorder":"total ascending"})
                apply_theme(fig2, h=380)
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                d2 = sl[sl["avg_del"].between(0,40)].dropna(subset=["avg_del","avg_rating"])
                if len(d2) > 0:
                    st.markdown('<div class="cpanel"><div class="ctitle">Delivery Speed vs Rating</div>'
                                '<div class="ccap">Faster sellers earn higher ratings</div>',
                                unsafe_allow_html=True)
                    fig3 = px.scatter(d2,
                        x="avg_del", y="avg_rating", color="segment",
                        color_discrete_map=cm, opacity=.7,
                        labels={"avg_del":"Avg Delivery Days","avg_rating":"Avg Rating"})
                    apply_theme(fig3, h=380, legend=True,
                                leg={"orientation":"h","yanchor":"bottom","y":1.01,"x":0})
                    st.plotly_chart(fig3, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 5 — CUSTOMERS
# ════════════════════════════════════════════════════════════════
with t5:
    rc2 = "customer_unique_id" if "customer_unique_id" in df.columns else "customer_id"
    cu = (df.groupby(rc2)
          .agg(n=("order_id","nunique"), spent=("item_revenue","sum"),
               first=("order_purchase_timestamp","min"),
               last=("order_purchase_timestamp","max"))
          .reset_index())
    cu = cu.dropna(subset=[rc2,"n","spent"])
    one   = (cu["n"]==1).sum()
    rep   = (cu["n"]>1).sum()
    rp    = rep/len(cu)*100
    la    = cu["spent"].mean()
    lr    = cu[cu["n"]>1]["spent"].mean() if rep > 0 else 0
    lo    = cu[cu["n"]==1]["spent"].mean()

    st.markdown(
        '<div class="krow krow-4">'
        + kcard("Total Customers",  num(len(cu)), "unique buyers")
        + kcard("One-Time Buyers",  num(one),     f"{one/len(cu)*100:.1f}% of all customers","warn","amb")
        + kcard("Repeat Buyers",    num(rep),     f"avg LTV {brl(lr)}","ok")
        + kcard("Repeat Rate",      f"{rp:.1f}%",
                "needs loyalty push" if rp<5 else "healthy",
                "bad" if rp<5 else "ok", "ros" if rp<5 else "")
        + '</div>',
        unsafe_allow_html=True)

    if rp < 5 and lr > 0:
        st.markdown(f'<div class="ins r">🔴 <strong>Critical retention gap:</strong> '
                    f'Only <strong>{rp:.1f}%</strong> of customers ever reorder. '
                    f'Repeat buyers have a <strong>{(lr/max(lo,1)-1)*100:.0f}% higher LTV</strong> '
                    f'({brl(lr)} vs {brl(lo)}). A post-purchase email flow could significantly close this gap.</div>',
                    unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fr = cu["n"].value_counts().sort_index().head(8).reset_index()
        fr.columns = ["orders","customers"]
        fr = fr.dropna()
        st.markdown('<div class="cpanel"><div class="ctitle">Purchase Frequency Distribution</div>'
                    '<div class="ccap">How many orders each customer has placed</div>',
                    unsafe_allow_html=True)
        fig = px.bar(fr, x="orders", y="customers",
            color_discrete_sequence=[TEAL],
            text=fr["customers"].apply(num),
            labels={"orders":"Orders Placed","customers":"Customers"})
        fig.update_traces(textposition="outside")
        apply_theme(fig, h=280)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        sc3 = cu[cu["spent"].between(0, cu["spent"].quantile(0.97))].dropna(subset=["spent"])
        if len(sc3) > 0:
            st.markdown('<div class="cpanel"><div class="ctitle">Customer Lifetime Spend Distribution</div>'
                        '<div class="ccap">Capped at 97th percentile</div>', unsafe_allow_html=True)
            fig2 = px.histogram(sc3, x="spent", nbins=60,
                color_discrete_sequence=[TEAL], opacity=.85,
                labels={"spent":"Total Spend (BRL)"})
            fig2.add_vline(x=la, line_dash="dash", line_color=AMBER,
                annotation_text=f"Avg {brl(la)}", annotation_font_color=AMBER)
            apply_theme(fig2, h=280)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">RFM Segmentation</div>', unsafe_allow_html=True)
    snap = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm  = (df.groupby(rc2)
            .agg(recency=("order_purchase_timestamp", lambda x: (snap-x.max()).days),
                 frequency=("order_id","nunique"),
                 monetary=("item_revenue","sum"))
            .reset_index())
    rfm = rfm.dropna(subset=["recency","monetary","frequency"])
    rs = rfm.sample(min(3000, len(rfm)), random_state=42)
    if len(rs) > 0:
        st.markdown('<div class="cpanel"><div class="ctitle">Recency vs Monetary Value</div>'
                    '<div class="ccap">Low recency + high spend = highest priority customers · Bubble = order count</div>',
                    unsafe_allow_html=True)
        fig3 = px.scatter(rs, x="recency", y="monetary", size="frequency", color="frequency",
            color_continuous_scale=["#1E3A52", TEAL], opacity=.55, size_max=20,
            labels={"recency":"Days Since Last Order","monetary":"Total Spend (BRL)","frequency":"Orders"})
        apply_theme(fig3, h=350)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    geo = (df.groupby("customer_state")
           .agg(orders=("order_id","nunique"), avg_spend=("item_revenue","mean"))
           .reset_index().sort_values("orders", ascending=False))
    geo = geo.dropna(subset=["customer_state","orders","avg_spend"])
    st.markdown('<div class="cpanel"><div class="ctitle">Customer Distribution by State</div>'
                '<div class="ccap">Bar = orders · Color = average spend per order</div>',
                unsafe_allow_html=True)
    fig4 = px.bar(geo, x="customer_state", y="orders",
        color="avg_spend", color_continuous_scale=["#1E3A52", TEAL],
        text=geo["orders"].apply(num),
        labels={"customer_state":"","orders":"Orders","avg_spend":"Avg Spend"})
    fig4.update_traces(textposition="outside")
    apply_theme(fig4, h=270)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────
st.markdown(
    f'<div class="foot">'
    f'<span>Olist Brazilian E-Commerce · Kaggle · 2016–2018</span>'
    f'<span>Python · Pandas · Plotly · Streamlit</span>'
    f'</div>',
    unsafe_allow_html=True)
