"""
Taiwan Weather Forecast - Streamlit Web Application
Based on the curriculum: 'AI 創新微課程 Taiwan Weather Forecast'
Features:
- CWA API integration with SQLite persistence (data.db)
- Interactive region selection & 7-day temperature trends (MinT / MaxT)
- Folium Taiwan temperature map with dynamic color coding
- Clear tabular presentation with export capabilities
- AI smart recommendations for clothing, travel, and health
- Complete 24-step learning roadmap integration
"""

import os
import datetime
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import folium
import streamlit.components.v1 as components
try:
    from streamlit_folium import st_folium
except Exception:
    st_folium = None

import database as db
import cwa_api

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Taiwan Weather Forecast | 台灣天氣預報",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and clean typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif;
    }
    
    /* Top Banner Gradient */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #0284C7 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.25);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #BAE6FD;
        margin-top: 0.35rem;
        font-weight: 500;
    }
    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.8rem;
    }
    .hero-tag {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
    }
    
    /* Metric Card Customization */
    .metric-container {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px -2px rgba(0, 0, 0, 0.06);
    }
    
    /* AI Card */
    .ai-card {
        background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
        border: 1px solid #BFDBFE;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Legend Pill */
    .legend-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Ensure Database Initialization
# ---------------------------------------------------------
def setup_initial_data_if_needed():
    """Ensure data.db exists with initial records."""
    db.init_db()
    if db.get_record_count() == 0:
        # Generate initial realistic data
        mock_df = cwa_api.generate_mock_forecast_data(days=7)
        db.insert_forecasts(mock_df)


setup_initial_data_if_needed()


# ---------------------------------------------------------
# Sidebar: Controls & API Settings
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/partly-cloudy-day.png", width=70)
    st.title("氣象設定與控制台")
    st.caption("CWA API × SQLite × Streamlit")
    
    st.markdown("---")
    st.subheader("📡 中央氣象署 (CWA) 串接")
    cwa_key_input = st.text_input(
        "CWA API Key (授權碼)",
        placeholder="例如: CWA-XXXXXXXX-XXXX",
        help="登入中央氣象署氣象資料開放平台即可免費取得授權碼"
    )
    
    dataset_option = st.selectbox(
        "選擇資料集",
        options=["F-C0032-001 (一般天氣預報-36小時)", "F-D0047-091 (全台一週天氣預報)"],
        index=0
    )
    dataset_code = dataset_option.split(" ")[0]

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🔄 同步 API", use_container_width=True, type="primary"):
            if cwa_key_input.strip():
                with st.spinner("正在連線中央氣象署 API..."):
                    raw_json = cwa_api.fetch_cwa_live_data(cwa_key_input.strip(), dataset_code)
                    if raw_json:
                        df_parsed = cwa_api.parse_cwa_json_to_df(raw_json)
                        if not df_parsed.empty:
                            count = db.insert_forecasts(df_parsed)
                            st.success(f"成功更新 {count} 筆 CWA 官方預報資料！")
                        else:
                            st.warning("API 回傳成功但無法解析對應欄位，使用示範資料同步。")
                            mock_df = cwa_api.generate_mock_forecast_data(days=7)
                            db.insert_forecasts(mock_df)
                    else:
                        st.error("API 連線失敗，請確認 API Key 是否正確。")
            else:
                st.info("尚未填寫 API Key，自動產生最新 7 天氣象示範資料。")
                mock_df = cwa_api.generate_mock_forecast_data(days=7)
                db.insert_forecasts(mock_df)
                st.success("已更新 7 天最新氣象資料！")

    with col_btn2:
        if st.button("🎲 重設示範資料", use_container_width=True):
            mock_df = cwa_api.generate_mock_forecast_data(days=7)
            db.insert_forecasts(mock_df)
            st.success("示範資料庫已重設！")

    st.markdown("---")
    st.subheader("🎯 查詢條件")
    
    # Region selector
    available_regions = db.get_regions()
    if not available_regions:
        available_regions = cwa_api.REGIONS
        
    selected_region = st.selectbox(
        "選擇地區 (Select Region)",
        options=available_regions,
        index=0
    )
    
    # Date selector
    available_dates = db.get_dates()
    if not available_dates:
        available_dates = [datetime.date.today().strftime("%Y-%m-%d")]
        
    selected_date = st.selectbox(
        "選擇日期 (Select Date)",
        options=available_dates,
        index=0
    )

    st.markdown("---")
    st.caption(f"💾 資料庫狀態: 已儲存 **{db.get_record_count()}** 筆預報紀錄")
    st.caption("💡 提示: 支援重疊日期自動覆蓋 (INSERT OR REPLACE)，重複執行不重複插入。")


# ---------------------------------------------------------
# Main Page Header (Hero Banner)
# ---------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">
        <span>🌤️ Taiwan Weather Forecast</span>
        <span style="font-size: 1.1rem; font-weight: 500; opacity: 0.9;">台灣互動式天氣預報</span>
    </div>
    <div class="hero-subtitle">
        從氣象資料到互動式天氣預報應用 | 用程式探索天氣，用資料看見台灣，用 AI 實現更多可能
    </div>
    <div class="hero-tags">
        <span class="hero-tag">⚡ CWA API</span>
        <span class="hero-tag">📦 JSON Parsing</span>
        <span class="hero-tag">🐍 Python 3</span>
        <span class="hero-tag">🗄️ SQLite (data.db)</span>
        <span class="hero-tag">🐼 Pandas</span>
        <span class="hero-tag">🗺️ Folium Map</span>
        <span class="hero-tag">🎈 Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# KPI Metric Row
# ---------------------------------------------------------
region_df = db.get_forecast_by_region(selected_region)
date_df = db.get_forecast_by_date(selected_date)

today_record = region_df[region_df["dataDate"] == selected_date]
if not today_record.empty:
    cur_min = today_record.iloc[0]["minT"]
    cur_max = today_record.iloc[0]["maxT"]
    cur_avg = today_record.iloc[0]["avgT"]
    cur_diff = round(cur_max - cur_min, 1)
else:
    cur_min = region_df["minT"].min() if not region_df.empty else 20.0
    cur_max = region_df["maxT"].max() if not region_df.empty else 28.0
    cur_avg = round((cur_min + cur_max) / 2.0, 1)
    cur_diff = round(cur_max - cur_min, 1)

# Highlights across all regions for the selected date
hottest_region = "無資料"
coldest_region = "無資料"
if not date_df.empty:
    hottest_row = date_df.loc[date_df["maxT"].idxmax()]
    coldest_row = date_df.loc[date_df["minT"].idxmin()]
    hottest_region = f"{hottest_row['regionName']} ({hottest_row['maxT']}°C)"
    coldest_region = f"{coldest_row['regionName']} ({coldest_row['minT']}°C)"

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric(label=f"📍 {selected_region} 最低溫", value=f"{cur_min} °C")
with kpi2:
    st.metric(label=f"📍 {selected_region} 最高溫", value=f"{cur_max} °C")
with kpi3:
    st.metric(label="🌡️ 當日預估平均溫", value=f"{cur_avg} °C")
with kpi4:
    st.metric(label="📊 日夜溫差", value=f"{cur_diff} °C")
with kpi5:
    st.metric(label="🔥 今日全台最高", value=hottest_region)


# ---------------------------------------------------------
# Layout: Left = Map (Folium), Right = Line Chart (Plotly)
# ---------------------------------------------------------
col_map, col_chart = st.columns([1.05, 1.2])

def get_temp_color(temp: float) -> str:
    """Step 17: Color scale mapping for temperatures."""
    if temp < 20.0:
        return "#2563EB"  # Blue (< 20°C)
    elif 20.0 <= temp < 25.0:
        return "#10B981"  # Green (20 - 25°C)
    elif 25.0 <= temp <= 30.0:
        return "#F59E0B"  # Orange (25 - 30°C)
    else:
        return "#EF4444"  # Red (> 30°C)


with col_map:
    st.subheader("🗺️ 台灣地圖視覺化")
    st.caption(f"📅 顯示日期：**{selected_date}** 全台 6 大區域氣象概況 (點擊地圖圓圈查看詳細資訊)")

    # Color Legend Badges
    st.markdown("""
    <div>
        <span class="legend-pill" style="background:#DBEAFE; color:#1E40AF;">🔵 &lt; 20°C 寒冷/偏涼</span>
        <span class="legend-pill" style="background:#D1FAE5; color:#065F46;">🟢 20 - 25°C 舒適宜人</span>
        <span class="legend-pill" style="background:#FEF3C7; color:#92400E;">🟠 25 - 30°C 溫暖微熱</span>
        <span class="legend-pill" style="background:#FEE2E2; color:#991B1B;">🔴 &gt; 30°C 炎熱高溫</span>
    </div>
    """, unsafe_allow_html=True)

    # Initialize Folium Map centered on Taiwan
    m = folium.Map(
        location=[23.75, 120.95],
        zoom_start=7,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Map markers for each region
    for region_name, coord in cwa_api.REGION_COORDINATES.items():
        row = date_df[date_df["regionName"] == region_name]
        if not row.empty:
            min_t = row.iloc[0]["minT"]
            max_t = row.iloc[0]["maxT"]
            avg_t = row.iloc[0]["avgT"]
        else:
            min_t, max_t, avg_t = 20.0, 26.0, 23.0

        marker_color = get_temp_color(avg_t)
        is_highlighted = (region_name == selected_region)

        popup_html = f"""
        <div style="font-family: sans-serif; width: 175px;">
            <h4 style="margin: 0 0 5px 0; color: #1E3A8A;">{region_name}</h4>
            <p style="margin: 2px 0; font-size: 13px;"><b>日期:</b> {selected_date}</p>
            <p style="margin: 2px 0; font-size: 13px;"><b>最低溫:</b> <span style="color:#2563EB;">{min_t}°C</span></p>
            <p style="margin: 2px 0; font-size: 13px;"><b>最高溫:</b> <span style="color:#EF4444;">{max_t}°C</span></p>
            <p style="margin: 2px 0; font-size: 13px;"><b>平均溫:</b> <b>{avg_t}°C</b></p>
            <p style="margin: 4px 0 0 0; font-size: 11px; color: #64748B;">{coord['desc']}</p>
        </div>
        """

        folium.CircleMarker(
            location=[coord["lat"], coord["lon"]],
            radius=16 if is_highlighted else 12,
            color="#0F172A" if is_highlighted else marker_color,
            weight=3 if is_highlighted else 2,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.88,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{region_name}: {avg_t}°C ({min_t}~{max_t}°C)"
        ).add_to(m)

        # Label icon above marker
        folium.Marker(
            location=[coord["lat"] + 0.16, coord["lon"]],
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 11px; font-weight: 700; color: #0F172A; text-shadow: 1px 1px 2px white; text-align: center; width: 70px; margin-left: -35px;">{region_name}</div>"""
            )
        ).add_to(m)

    # Render map using st_folium if available, otherwise fallback cleanly to standalone HTML
    rendered = False
    if st_folium is not None:
        try:
            st_folium(m, width="100%", height=460, returned_objects=[])
            rendered = True
        except Exception:
            rendered = False
    if not rendered:
        components.html(m.get_root().render(), height=460)


with col_chart:
    st.subheader(f"📈 {selected_region} 一週最高與最低氣溫")
    st.caption("紅色代表最高氣溫 (MaxT)，藍色代表最低氣溫 (MinT)")

    if not region_df.empty:
        # Plotly Line Chart
        fig = go.Figure()

        # Add MaxT Line (Red)
        fig.add_trace(go.Scatter(
            x=region_df["dataDate"],
            y=region_df["maxT"],
            mode="lines+markers+text",
            name="最高氣溫 (MaxT)",
            line=dict(color="#EF4444", width=3),
            marker=dict(size=8, color="#EF4444"),
            text=[f"{v}°C" for v in region_df["maxT"]],
            textposition="top center",
            hovertemplate="<b>日期:</b> %{x}<br><b>最高溫:</b> %{y}°C<extra></extra>"
        ))

        # Add MinT Line (Blue)
        fig.add_trace(go.Scatter(
            x=region_df["dataDate"],
            y=region_df["minT"],
            mode="lines+markers+text",
            name="最低氣溫 (MinT)",
            line=dict(color="#3B82F6", width=3),
            marker=dict(size=8, color="#3B82F6"),
            text=[f"{v}°C" for v in region_df["minT"]],
            textposition="bottom center",
            hovertemplate="<b>日期:</b> %{x}<br><b>最低溫:</b> %{y}°C<extra></extra>"
        ))

        # Layout styling
        min_y = max(0, int(region_df["minT"].min()) - 4)
        max_y = int(region_df["maxT"].max()) + 5

        fig.update_layout(
            margin=dict(l=20, r=20, t=25, b=20),
            height=460,
            hovermode="x unified",
            xaxis=dict(
                title="預報日期 (Date)",
                showgrid=True,
                gridcolor="#E2E8F0"
            ),
            yaxis=dict(
                title="氣溫 (°C)",
                range=[min_y, max_y],
                showgrid=True,
                gridcolor="#E2E8F0"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("尚無該地區之氣溫數據，請點擊側邊欄「同步 API」載入資料。")


# ---------------------------------------------------------
# Lower Section: Table & AI Assistant (Step 15 & 22)
# ---------------------------------------------------------
col_table, col_ai = st.columns([1.1, 1.1])

with col_table:
    st.subheader(f"📋 {selected_region} 預報詳細數據表")
    st.caption("從 SQLite 資料庫 `data.db` 讀取並透過 Pandas 格式化顯示")

    if not region_df.empty:
        display_df = region_df.copy()
        display_df["溫差 (°C)"] = (display_df["maxT"] - display_df["minT"]).round(1)
        display_df = display_df.rename(columns={
            "dataDate": "預報日期 (Date)",
            "minT": "最低氣溫 MinT (°C)",
            "maxT": "最高氣溫 MaxT (°C)",
            "avgT": "平均氣溫 AvgT (°C)"
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 下載預報資料 (CSV)",
            data=csv_data,
            file_name=f"{selected_region}_weather_forecast.csv",
            mime="text/csv"
        )
    else:
        st.warning("查無數據。")


with col_ai:
    st.subheader("🤖 AI 天氣顧問與生活提醒")
    st.caption("依據今日與一週預報溫差，智慧運算穿搭、出行與健康防護指南")

    # Generate smart recommendations based on current temperature metrics
    clothing_advice = ""
    activity_advice = ""
    health_advice = ""

    if cur_max >= 30.0:
        clothing_advice = "短袖、透氣吸汗衣物、遮陽帽與太陽眼鏡 ☀️"
        activity_advice = "白天紫外線強烈，中午時段盡量減少戶外曝曬，戶外活動建議於清晨或傍晚進行。"
        health_advice = "隨時補充水份與電解質，慎防熱傷害與中暑。"
    elif cur_avg >= 24.0:
        clothing_advice = "短袖搭配薄襯衫或薄防風外套，早晚溫差微涼時可披上 👕"
        activity_advice = "天氣舒適溫暖，非常適合各項戶外休閒運動與旅遊踏青。"
        health_advice = "天氣宜人，可多開窗保持室內空氣流通。"
    elif cur_avg >= 18.0:
        clothing_advice = "長袖上衣、針織衫、防風薄外套，洋蔥式穿搭尤佳 🧥"
        activity_advice = "適合室內外文藝活動或近郊步道健行。"
        health_advice = f"日夜溫差達 {cur_diff}°C，早出晚歸朋友請留意心血管與呼吸道保暖。"
    else:
        clothing_advice = "保暖毛衣、羽絨外套、圍巾與手套 🧣"
        activity_advice = "天候偏冷，建議安排室內溫泉、博物館或聚會行程。"
        health_advice = "注意室內外溫差，適時使用暖氣或電毯，長者與幼童需特別注意保暖。"

    st.markdown(f"""
    <div class="ai-card">
        <h4 style="margin-top:0; color:#1E3A8A;">🌤️ {selected_region} 本日智慧提醒 ({selected_date})</h4>
        <p><b>👔 穿搭指南：</b>{clothing_advice}</p>
        <p><b>🚶 出行建議：</b>{activity_advice}</p>
        <p><b>❤️ 健康護理：</b>{health_advice}</p>
        <hr style="border:0; border-top:1px dashed #CBD5E1; margin:0.8rem 0;">
        <small style="color:#64748B;">⚡ 結合氣象數據 × 智慧規則決策引擎，打造專屬您的個人化生活氣象助手。</small>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# Footer: Project Architecture Guide
# ---------------------------------------------------------
st.markdown("---")
with st.expander("📚 查看專案核心架構與技術功能說明", expanded=False):
    st.markdown("""
    **本專案技術架構與功能亮點：**
    
    - **開放資料串接**：支援中央氣象署 CWA Open Data API 即時擷取與擬真資料離線支援。
    - **資料結構解析**：定位 `locations`、`locationName` 與 `weatherElement` 精準提取氣溫數值。
    - **SQLite 資料庫持久化**：本地 `data.db` 儲存長期預報紀錄，具備防重複插入與去重約束。
    - **互動式前端儀表板**：Streamlit 現代化介面，即時切換地區與預報日期。
    - **雙軌氣溫趨勢折線圖**：繪製一週最高溫 (紅) 與最低溫 (藍) 趨勢曲線與數值標註。
    - **地理圖資視覺化**：整合 Folium 依據平均氣溫著色標記（藍、綠、橘、紅）與彈出詳情。
    - **AI 智慧生活助手**：依據氣象數值動態推估穿搭指南、戶外出行與健康提醒。
    """)

st.caption("✨ Developed with pair-programming assistance by Antigravity | Code Smarter, Build a Better Tomorrow!")
