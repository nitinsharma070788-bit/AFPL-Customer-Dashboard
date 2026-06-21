import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set layout configurations matching the app ecosystem
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
    months_list = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Target Operation Month", months_list, index=datetime.datetime.now().month - 1)
with col_m2:
    client_name = st.text_input("Customer Account Identifier", placeholder="e.g., MICON ENGINEERS")
with col_m3:
    kam_name = st.text_input("Key Account Manager (KAM)", placeholder="e.g., John Doe")
with col_m4:
    report_date = st.date_input("Console Generation Date", datetime.date.today())
st.markdown('</div>', unsafe_allow_html=True)

# --- DATA STREAM FILE UPLOADER ---
uploaded_file = st.file_uploader("Drop operational business logs here (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("💡 Awaiting file upload. Showing live preview with demo metrics.")
    df_po = pd.DataFrame({
        'PO_Number': ['PO-001', 'PO-001', 'PO-002', 'PO-003', 'PO-004'],
        'Item_ID': ['ITM-101', 'ITM-102', 'ITM-103', 'ITM-104', 'ITM-105'],
        'QTY': [100, 150, 200, 50, 300],
        'Value': [1000, 1500, 4000, 500, 6000],
        'Status': ['Dispatched', 'Dispatched', 'Not Dispatched', 'Cancelled', 'Dispatched'],
        'Payment_Received': [1000, 1500, 0, 0, 4000],
        'Payment_Due': [0, 0, 4000, 0, 2000]
    })
    df_feedback = pd.DataFrame({
        'CSAT': ['Satisfied', 'Satisfied', 'Neutral', 'Unsatisfied', 'Satisfied'],
        'NPS_Group': ['Promoter', 'Promoter', 'Passive', 'Detractor', 'Promoter']
    })
else:
    try:
        xl = pd.ExcelFile(uploaded_file)
        # Always safely pull the very first sheet
        df_po = pd.read_excel(uploaded_file, sheet_name=0)
        
        # FIXED: Only pull sheet index 1 if it actually exists in the file!
        if len(xl.sheet_names) > 1:
            df_feedback = pd.read_excel(uploaded_file, sheet_name=1)
        else:
            df_feedback = pd.DataFrame(columns=['CSAT', 'NPS_Group'])
    except Exception as e:
        st.error(f"Error compiling stream parameters: {e}")
        st.stop()

# --- COMPUTATION METRIC ENGINES ---
total_po = df_po['PO_Number'].nunique() if 'PO_Number' in df_po.columns else 0
total_po_item = len(df_po)
total_po_qty = df_po['QTY'].sum() if 'QTY' in df_po.columns else 0
total_po_value = df_po['Value'].sum() if 'Value' in df_po.columns else 0

df_disp = df_po[df_po['Status'].str.lower() == 'dispatched'] if 'Status' in df_po.columns else pd.DataFrame()
total_disp_qty = df_disp['QTY'].sum() if not df_disp.empty else 0
total_disp_value = df_disp['Value'].sum() if not df_disp.empty else 0

df_not_disp = df_po[df_po['Status'].str.lower() == 'not dispatched'] if 'Status' in df_po.columns else pd.DataFrame()
not_disp_qty = df_not_disp['QTY'].sum() if not df_not_disp.empty else 0
not_disp_value = df_not_disp['Value'].sum() if not df_not_disp.empty else 0

total_payment_received = df_po['Payment_Received'].sum() if 'Payment_Received' in df_po.columns else 0
total_payment_due = df_po['Payment_Due'].sum() if 'Payment_Due' in df_po.columns else 0

# --- ACCOUNT METADATA ROW ---
st.write("### 📌 Account Overview Summary")
meta1, meta2, meta3 = st.columns(3)
with meta1:
    st.markdown(f'<div class="custom-card"><div class="card-label">Target Profile</div><div class="card-value">{client_name if client_name else "MICON ENGINEERS"}</div></div>', unsafe_allow_html=True)
with meta2:
    st.markdown(f'<div class="custom-card"><div class="card-label">Assigned Account Manager</div><div class="card-value">{kam_name if kam_name else "Unassigned Staff"}</div></div>', unsafe_allow_html=True)
with meta3:
    st.markdown(f'<div class="custom-card"><div class="card-label">Operational Window</div><div class="card-value">{selected_month} {report_date.year}</div></div>', unsafe_allow_html=True)

# --- LOGISTICS CORE TARGET MATRICES ---
st.write("### 📈 Core Enterprise Procurement KPIs")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="custom-card"><div class="card-label">Gross Purchase Orders</div><div class="card-value">{total_po}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="custom-card"><div class="card-label">Unique Components Logged</div><div class="card-value">{total_po_item}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="custom-card"><div class="card-label">Aggregated Volume Units</div><div class="card-value">{total_po_qty:,}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="custom-card"><div class="card-label">Gross Transacted Asset Value</div><div class="card-value">${total_po_value:,}</div></div>', unsafe_allow_html=True)

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
    st.write("**Fulfillment Stream Performance Metrics**")
    
    categories = ['Gross Balance', 'Dispatched Pipeline', 'Pending Allocations']
    qty_metrics = [total_po_qty, total_disp_qty, not_disp_qty]
    val_metrics = [total_po_value, total_disp_value, not_disp_value]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Units Qty', x=categories, y=qty_metrics, marker_color='#0284c7'))
    fig.add_trace(go.Bar(name='Financial Value ($)', x=categories, y=val_metrics, marker_color='#38bdf8'))
    
    fig.update_layout(barmode='group', **plotly_layout_defaults)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g_col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("**Collections Ledger & Working Capital Metrics**")
    
    fig_fin = go.Figure(data=[
        go.Bar(name='Settled Capital Assets', x=['Liquid Portfolio'], y=[total_payment_received], marker_color='#10b981', width=0.4),
        go.Bar(name='Outstanding Capital Portions', x=['Liquid Portfolio'], y=[total_payment_due], marker_color='#f43f5e', width=0.4)
    ])
    fig_fin.update_layout(barmode='stack', **plotly_layout_defaults)
    st.plotly_chart(fig_fin, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- REVIEWS & FEEDBACK PIPELINES ---
if 'CSAT' in df_feedback.columns and not df_feedback['CSAT'].dropna().empty:
    st.write("### 💬 Operations Sentiment Framework")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("**Customer Satisfaction Allocation Index (CSAT)**")
        csat_counts = df_feedback['CSAT'].value_counts()
        fig_p1 = px.pie(names=csat_counts.index, values=csat_counts.values, hole=0.4, color_discrete_sequence=['#0f172a', '#38bdf8', '#cbd5e1'])
        fig_p1.update_layout(**plotly_layout_defaults)
        st.plotly_chart(fig_p1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with f_col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write("**Net Promoter Alignment Index (NPS)**")
        nps_counts = df_feedback['NPS_Group'].value_counts()
        fig_p2 = px.pie(names=nps_counts.index, values=nps_counts.values, color_discrete_sequence=['#10b981', '#f1f5f9', '#f43f5e'])
        fig_p2.update_layout(**plotly_layout_defaults)
        st.plotly_chart(fig_p2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
