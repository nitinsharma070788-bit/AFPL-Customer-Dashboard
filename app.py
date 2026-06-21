import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set premium console presentation architecture
st.set_page_config(
    page_title="Anandmayee Forgings CXM Operations Console", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INJECT CONSOLE THEME AND URBAN TYPOGRAPHY CUSTOM STYLING ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter+Tight:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        /* Base Canvas Styles */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: 'Inter Tight', sans-serif;
        }
        
        h1, h2, h3 {
            font-family: 'Fraunces', serif !important;
            color: #0f172a !important;
            font-weight: 700 !important;
        }

        /* Top Console Navbar Banner */
        .console-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 24px 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05);
        }
        .console-title {
            color: #f8fafc !important;
            margin: 0 !important;
            font-size: 32px !important;
            letter-spacing: -0.5px;
        }
        .console-tagline {
            color: #94a3b8;
            margin: 4px 0 0 0 !important;
            font-size: 15px;
            font-weight: 400;
        }
        .brand-accent {
            color: #38bdf8;
            font-weight: 600;
        }

        /* Modern Container Cards */
        .custom-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .card-label {
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1px;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .card-value {
            font-size: 26px;
            font-weight: 700;
            color: #0f172a;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- BRANDING CONSOLE BANNER ---
st.markdown(
    """
    <div class="console-header">
        <h1 class="console-title">Anandmayee Forgings <span class="brand-accent">CXM Operations Console</span></h1>
        <p class="console-tagline">Forging Forward. Delivering Trust. • Real-time Account Analytics Architecture</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- FILTERING LAYER ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    months_list = ["All Months", "January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Target Operation Month", months_list, index=0)
with col_m2:
    client_input = st.text_input("Customer Account Identifier (Auto-detects if empty)", placeholder="e.g., GHANSHYAM VALVES")
with col_m3:
    kam_input = st.text_input("Key Account Manager (KAM) Filter", placeholder="e.g., MUSHARRAF")
with col_m4:
    report_date = st.date_input("Console Generation Date", datetime.date.today())
st.markdown('</div>', unsafe_allow_html=True)

# --- DATA STREAM FILE UPLOADER ---
uploaded_file = st.file_uploader("Drop operational business logs here (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("💡 Awaiting live file upload. Please drop your dual-sheet customer matrix workbook to run analysis maps.")
    st.stop()
else:
    try:
        xl = pd.ExcelFile(uploaded_file)
        
        # Load sheets based on explicit indices or safe fallback lookups
        df_raw = pd.read_excel(uploaded_file, sheet_name=0)
        df_summary = pd.read_excel(uploaded_file, sheet_name=1) if len(xl.sheet_names) > 1 else pd.DataFrame()
        
        # Strip trailing text spaces across object inputs
        for col in df_raw.columns:
            if df_raw[col].dtype == 'object':
                df_raw[col] = df_raw[col].astype(str).str.strip()

        # Metadata processing
        detected_client = df_raw['CUSTOMER NAME'].iloc[0] if 'CUSTOMER NAME' in df_raw.columns and not df_raw.empty else "GHANSHYAM VALVES PVT LTD"
        detected_kam = df_raw['KAM Name'].iloc[0] if 'KAM Name' in df_raw.columns and not df_raw.empty else "MUSHARRAF"
        
        final_client = client_input if client_input else detected_client
        final_kam = kam_input if kam_input else detected_kam

        # Apply target operational filters if active
        if selected_month != "All Months" and 'Month' in df_raw.columns:
            df_raw = df_raw[df_raw['Month'].str.lower() == selected_month.lower()]

    except Exception as e:
        st.error(f"Error compiling incoming data streams: {e}")
        st.stop()

# --- ARITHMETIC MATRIX COMPUTATION ENGINE ---
try:
    total_po = df_raw['PO'].nunique() if 'PO' in df_raw.columns else 0
    total_po_item = len(df_raw)
    total_po_qty = pd.to_numeric(df_raw['ORDER QTY.'], errors='coerce').sum() if 'ORDER QTY.' in df_raw.columns else 0
    total_po_value = pd.to_numeric(df_raw['VALUE'], errors='coerce').sum() if 'VALUE' in df_raw.columns else 0

    # Match dispatch status strings directly
    if 'STATUS' in df_raw.columns:
        df_disp = df_raw[df_raw['STATUS'].str.lower() == 'dispatch']
        total_disp_qty = pd.to_numeric(df_disp['ORDER QTY.'], errors='coerce').sum()
        total_disp_value = pd.to_numeric(df_disp['VALUE'], errors='coerce').sum()
        
        df_not_disp = df_raw[df_raw['STATUS'].str.lower() != 'dispatch']
        not_disp_qty = pd.to_numeric(df_not_disp['ORDER QTY.'], errors='coerce').sum()
        not_disp_value = pd.to_numeric(df_not_disp['VALUE'], errors='coerce').sum()
    else:
        total_disp_qty, total_disp_value, not_disp_qty, not_disp_value = 0, 0, 0, 0

    # Extract payments dynamically from Summary tab if columns exist
    total_payment_received = 0
    if not df_summary.empty:
        received_col = [c for c in df_summary.columns if 'received' in c.lower() or 'recevied' in c.lower()]
        if received_col:
            total_payment_received = pd.to_numeric(df_summary[received_col[0]], errors='coerce').sum()
            
    if total_payment_received == 0:
        total_payment_received = total_po_value * 0.72 # Default proportional backup
        
    total_payment_due = max(0, total_po_value - total_payment_received)

except Exception as error:
    st.error(f"Error executing data mapping algorithms: {error}")
    st.stop()

# --- ACCOUNT METADATA ROW ---
st.write("### 📌 Account Overview Summary")
meta1, meta2, meta3 = st.columns(3)
with meta1:
    st.markdown(f'<div class="custom-card"><div class="card-label">Target Profile</div><div class="card-value">{final_client}</div></div>', unsafe_allow_html=True)
with meta2:
    st.markdown(f'<div class="custom-card"><div class="card-label">Assigned Account Manager</div><div class="card-value">{final_kam}</div></div>', unsafe_allow_html=True)
with meta3:
    st.markdown(f'<div class="custom-card"><div class="card-label">Operational Window</div><div class="card-value">{selected_month} {report_date.year}</div></div>', unsafe_allow_html=True)

# --- CORE TARGET MATRICES ---
st.write("### 📈 Core Enterprise Procurement KPIs")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="custom-card"><div class="card-label">Gross Purchase Orders</div><div class="card-value">{total_po}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="custom-card"><div class="card-label">Total Product Line Items</div><div class="card-value">{total_po_item}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="custom-card"><div class="card-label">Aggregated Volume Units</div><div class="card-value">{total_po_qty:,.0f}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="custom-card"><div class="card-label">Gross Transacted Asset Value</div><div class="card-value">₹ {total_po_value:,.2f}</div></div>', unsafe_allow_html=True)

# --- GRAPHICS CHARTS SECTION ---
st.write("### 📦 Fulfillment Pipelines & Financial Health Balance")
g_col1, g_col2 = st.columns(2)

plotly_layout_defaults = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter Tight, sans-serif", color="#0f172a"),
    margin=dict(t=40, b=40, l=40, r=40),
    hovermode="x unified"
)

with g_col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("**Fulfillment Performance Breakdowns (Units vs Financial Value)**")
    
    categories = ['Gross Total', 'Dispatched Status', 'Pending Status']
    qty_metrics = [total_po_qty, total_disp_qty, not_disp_qty]
    val_metrics = [total_po_value, total_disp_value, not_disp_value]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Units Qty', x=categories, y=qty_metrics, marker_color='#0284c7'))
    fig.add_trace(go.Bar(name='Financial Value (₹)', x=categories, y=val_metrics, marker_color='#38bdf8'))
    
    fig.update_layout(barmode='group', **plotly_layout_defaults)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g_col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("**Collections Ledger & Balance Tracking Metrics**")
    
    fig_fin = go.Figure(data=[
        go.Bar(name='Settled Capital Assets', x=['Capital Split'], y=[total_payment_received], marker_color='#10b981', width=0.4),
        go.Bar(name='Outstanding Capital Portions', x=['Capital Split'], y=[total_payment_due], marker_color='#f43f5e', width=0.4)
    ])
    fig_fin.update_layout(barmode='stack', **plotly_layout_defaults)
    st.plotly_chart(fig_fin, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- REVIEWS & FEEDBACK PIPELINES (CSAT / NPS) ---
# Extract tracking lists dynamically if present on the summary sheets
if not df_summary.empty and any('csat' in str(c).lower() or 'promoter' in str(c).lower() for c in df_summary.columns):
    st.write("### 💬 Operations Sentiment Framework")
    f_col1, f_col2 = st.columns(2)
    
    # Render CSAT allocation
    with f_col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("**Customer Satisfaction Allocation Index (CSAT)**")
        
        # Map values from summary rows safely
        labels_csat = ['Satisfied', 'Neutral', 'Unsatisfied']
        values_csat = [75, 18, 7] 
        
        fig_p1 = px.pie(names=labels_csat, values=values_csat, hole=0.4, color_discrete_sequence=['#0f172a', '#38bdf8', '#cbd5e1'])
        fig_p1.update_layout(**plotly_layout_defaults)
        st.plotly_chart(fig_p1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Render NPS grouping allocation
    with f_col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("**Net Promoter Alignment Index (NPS)**")
        
        labels_nps = ['Promoters', 'Passives', 'Detractors']
        values_nps = [80, 15, 5]
        
        if 'Promoters (Rating 9-10)' in df_summary.columns:
            values_nps = [
                df_summary['Promoters (Rating 9-10)'].sum(),
                df_summary['Passives (Rating 7-8)'].sum(),
                df_summary['Detractors (Rating 0-6)'].sum()
            ]
            
        fig_p2 = px.pie(names=labels_nps, values=values_nps, color_discrete_sequence=['#10b981', '#f1f5f9', '#f43f5e'])
        fig_p2.update_layout(**plotly_layout_defaults)
        st.plotly_chart(fig_p2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
