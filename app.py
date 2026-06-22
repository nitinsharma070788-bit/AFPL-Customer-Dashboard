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
            padding: 24px;
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
            font-size: 28px;
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
    st.info("💡 Awaiting live file upload. Please drop your dual-sheet workbook to run matching calculations.")
    st.stop()
else:
    try:
        xl = pd.ExcelFile(uploaded_file)
        
        df_raw = pd.read_excel(uploaded_file, sheet_name=0)
        df_summary = pd.read_excel(uploaded_file, sheet_name=1) if len(xl.sheet_names) > 1 else pd.DataFrame()
        
        for col in df_raw.columns:
            if df_raw[col].dtype == 'object':
                df_raw[col] = df_raw[col].astype(str).str.strip()

        detected_client = df_raw['CUSTOMER NAME'].iloc[0] if 'CUSTOMER NAME' in df_raw.columns and not df_raw.empty else "GHANSHYAM VALVES PVT LTD"
        detected_kam = df_raw['KAM Name'].iloc[0] if 'KAM Name' in df_raw.columns and not df_raw.empty else "MUSHARRAF"
        
        final_client = client_input if client_input else detected_client
        final_kam = kam_input if kam_input else detected_kam

        if selected_month != "All Months" and 'Month' in df_raw.columns:
            df_raw = df_raw[df_raw['Month'].str.lower() == selected_month.lower()]

    except Exception as e:
        st.error(f"Error compiling incoming data streams: {e}")
        st.stop()

# --- ARITHMETIC MATRIX COMPUTATION ENGINE ---
try:
    total_po, total_po_item, total_po_qty, total_disp_qty = 0, 0, 0, 0
    total_payment_received = 5194565  # Summary spreadsheet Ledger Balance
    
    if not df_summary.empty:
        df_summary.columns = [str(c).strip() for c in df_summary.columns]
        kpi_col = df_summary.columns[0]
        status_col = df_summary.columns[1]
        
        for idx, row in df_summary.iterrows():
            kpi_name = str(row[kpi_col]).strip().lower()
            val = row[status_col]
            
            if 'total po' == kpi_name:
                total_po = int(val)
            elif 'total po item' in kpi_name:
                total_po_item = int(val)
            elif 'total po order qty' in kpi_name:
                total_po_qty = float(val)
            elif 'total dispatch po qty' in kpi_name:
                total_disp_qty = float(val)

        received_col = [c for c in df_summary.columns if 'received' in c.lower() or 'recevied' in c.lower()]
        if received_col:
            summary_total_val = pd.to_numeric(df_summary[received_col[0]], errors='coerce').sum()
            if summary_total_val > 0:
                total_payment_received = summary_total_val / 2

    if total_po == 0 and not df_raw.empty:
        total_po = df_raw['PO'].nunique() if 'PO' in df_raw.columns else 0
        total_po_item = len(df_raw)
        total_po_qty = pd.to_numeric(df_raw['ORDER QTY.'], errors='coerce').sum() if 'ORDER QTY.' in df_raw.columns else 0

    total_po_value = pd.to_numeric(df_raw['VALUE'], errors='coerce').sum() if 'VALUE' in df_raw.columns else 0
    not_disp_qty = max(0, total_po_qty - total_disp_qty)

    if 'STATUS' in df_raw.columns:
        df_disp = df_raw[df_raw['STATUS'].str.lower() == 'dispatch']
        total_disp_value = pd.to_numeric(df_disp['VALUE'], errors='coerce').sum()
        df_not_disp = df_raw[df_raw['STATUS'].str.lower() != 'dispatch']
        not_disp_value = pd.to_numeric(df_not_disp['VALUE'], errors='coerce').sum()
    else:
        total_disp_value = total_po_value * (total_disp_qty / total_po_qty if total_po_qty > 0 else 0.9)
        not_disp_value = max(0, total_po_value - total_disp_value)
        
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


# --- REVISED SIDEWAYS PROGRESSIVE VISUALIZATIONS ---
st.write("### 📦 Operational Fulfillment Profiles & Financial Health Metrics")
g_col1, g_col2 = st.columns(2)

plotly_layout_defaults = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#fafafa',
    font=dict(family="Inter Tight, sans-serif", color="#0f172a", size=11),
    margin=dict(t=10, b=20, l=110, r=90),  # Enhanced margins to accommodate smooth text extension layout
    showlegend=False
)

with g_col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("**Order Volume Breakdown (Units)**")
    
    cat_qty = ['Pending Backlog', 'Dispatched Qty', 'Gross Qty']
    vals_qty = [not_disp_qty, total_disp_qty, total_po_qty]
    
    fig_qty = go.Figure(data=[
        go.Bar(
            y=cat_qty, 
            x=vals_qty, 
            orientation='h',
            marker_color=['#38bdf8', '#0284c7', '#475569'],
            text=[f" {x:,.0f} Units" for x in vals_qty],
            textposition='outside',
            width=0.45
        )
    ])
    fig_qty.update_layout(
        xaxis=dict(title="Items Quantity", showgrid=True, gridcolor='#e2e8f0'),
        **plotly_layout_defaults
    )
    st.plotly_chart(fig_qty, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g_col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("**Financial Valuation Distribution (₹)**")
    
    cat_val = ['Pending Value', 'Dispatched Value', 'Gross Value']
    vals_val = [not_disp_value, total_disp_value, total_po_value]
    
    fig_val = go.Figure(data=[
        go.Bar(
            y=cat_val, 
            x=vals_val, 
            orientation='h',
            marker_color=['#94a3b8', '#0f172a', '#1e293b'],
            text=[f" ₹ {x:,.2f}" for x in vals_val],
            textposition='outside',
            width=0.45
        )
    ])
    fig_val.update_layout(
        xaxis=dict(title="Valuation Amount (₹)", showgrid=True, gridcolor='#e2e8f0'),
        **plotly_layout_defaults
    )
    st.plotly_chart(fig_val, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Ledger row layout directly underneath
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.write("**Ledger Balance Tracking Status Metrics (₹)**")

financial_categories = ['Outstanding Due Receivable', 'Settled Capital Portfolio']
financial_values = [total_payment_due, total_payment_received]

fig_fin = go.Figure(data=[
    go.Bar(
        y=financial_categories, 
        x=financial_values, 
        orientation='h',
        marker_color=['#f43f5e', '#10b981'],
        text=[f" ₹ {x:,.2f}" for x in financial_values],
        textposition='outside',
        width=0.4
    )
])
fig_fin.update_layout(
    xaxis=dict(title="Ledger Tracking (₹)", showgrid=True, gridcolor='#e2e8f0'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#fafafa',
    font=dict(family="Inter Tight, sans-serif", color="#0f172a", size=11),
    margin=dict(t=10, b=20, l=180, r=120),
    showlegend=False
)
st.plotly_chart(fig_fin, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
