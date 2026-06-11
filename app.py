import io
import json
import os
import re
import sys
import tempfile
import base64
from datetime import datetime, date
from pathlib import Path
import base64
import pandas as pd
import streamlit as st

logo_path = "assets/favicon.png"
with open(logo_path, "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode()

# page config
st.set_page_config(
    page_title="AFPL CXM Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Brand Colors
BRAND = {
    "primary": "#ef4444",      
    "primary_dark": "#dc2626",
    "primary_light": "#fef2f2",
    "secondary": "#1A2533",
    "secondary_light": "#243141",
    "accent": "#ef4444",
    "surface": "#FFFFFF",
    "surface_dark": "#F8F9FC",
    "text": "#1E293B",
    "text_light": "#64748B",
    "text_lighter": "#94A3B8",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#ef4444",
    "border": "#E2E8F0",
}

# inline CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap');

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

/* Main container */
.main .block-container {{
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1400px;
}}

/* Hide default Streamlit branding */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{background: transparent !important;}}

/* Custom header */
.afpl-header-new {{
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
}}

.afpl-brand {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.afpl-logo-new {{
    width: 250px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 20px;
    color: white;
    object-fit: contain;
}}

.afpl-title-new {{
    font-size: 22px;
    font-weight: 700;
    color: white;
    letter-spacing: -0.01em;
}}

.afpl-sub-new {{
    font-size: 13px;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
}}

.afpl-badge {{
    background: rgba(255,107,26,0.15);
    padding: 8px 16px;
    border-radius: 40px;
    font-size: 12px;
    font-weight: 500;
    color: {BRAND['primary']};
    border: 1px solid rgba(255,107,26,0.3);
}}

/* Sidebar styling */
section[data-testid="stSidebar"] {{
    background: {BRAND['surface']};
    border-right: 1px solid {BRAND['border']};
    padding: 1.5rem 0;
}}

section[data-testid="stSidebar"] .stMarkdown, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox div,
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stCheckbox label {{
    color: {BRAND['text']} !important;
}}

section[data-testid="stSidebar"] .stTextInput input {{
    border: 1px solid {BRAND['border']};
    border-radius: 10px;
    background: {BRAND['surface']};
}}

.sidebar-header {{
    padding: 0 1rem 0.5rem 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid {BRAND['border']};
}}

.sidebar-header h3 {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: {BRAND['text_light']};
    margin: 0;
}}

.step-badge {{
    display: inline-block;
    width: 24px;
    height: 24px;
    background: {BRAND['primary']};
    color: white;
    border-radius: 8px;
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    line-height: 24px;
    margin-right: 10px;
}}

/* Cards and containers */
.custom-card {{
    background: {BRAND['surface']};
    border: 1px solid {BRAND['border']};
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}

.custom-card:hover {{
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    border-color: {BRAND['primary_light']};
}}

/* Metric styling */
.metric-container {{
    background: linear-gradient(135deg, {BRAND['surface']} 0%, {BRAND['surface_dark']} 100%);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    border: 1px solid {BRAND['border']};
}}

.metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {BRAND['secondary']};
    margin: 0;
    letter-spacing: -0.02em;
}}

.metric-label {{
    font-size: 12px;
    font-weight: 500;
    color: {BRAND['text_light']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Button styling */
.stButton > button {{
    background: linear-gradient(135deg, {BRAND['primary']} 0%, {BRAND['primary_dark']} 100%) !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    color: white !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(255,107,26,0.2) !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(255,107,26,0.25) !important;
}}

/* Dataframe styling */
.stDataFrame {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid {BRAND['border']};
}}

.stDataFrame th {{
    background: {BRAND['surface_dark']};
    font-weight: 600;
    font-size: 12px;
    color: {BRAND['text']};
}}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: {BRAND['surface_dark']};
    padding: 6px;
    border-radius: 14px;
    margin-bottom: 1rem;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    color: {BRAND['text_light']};
}}

.stTabs [aria-selected="true"] {{
    background: {BRAND['surface']};
    color: {BRAND['primary']};
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}

/* File uploader */
div[data-testid="stFileUploader"] > div:first-child {{
    border: 2px dashed {BRAND['border']};
    border-radius: 16px;
    background: {BRAND['surface_dark']};
}}

div[data-testid="stFileUploader"] > div:first-child:hover {{
    border-color: {BRAND['primary']};
    background: rgba(255,107,26,0.02);
}}

/* Selectbox styling */
div[data-baseweb="select"] > div {{
    border-radius: 10px;
    border: 1px solid {BRAND['border']};
}}

div[data-baseweb="select"] > div:hover {{
    border-color: {BRAND['primary']};
}}

/* Checkbox */
.stCheckbox label span {{
    font-size: 13px;
    color: {BRAND['text']};
}}

/* Info/Warning/Success boxes */
.stAlert {{
    border-radius: 12px;
    border-left-width: 4px;
}}

.stAlert > div {{
    font-size: 13px;
}}

/* Divider */
hr {{
    margin: 1rem 0;
    border-color: {BRAND['border']};
    opacity: 0.5;
}}

/* Download buttons */
[data-testid="stDownloadButton"] button {{
    background: {BRAND['surface']} !important;
    color: {BRAND['primary']} !important;
    border: 1px solid {BRAND['border']} !important;
    box-shadow: none !important;
}}

[data-testid="stDownloadButton"] button:hover {{
    background: {BRAND['primary']} !important;
    color: white !important;
    border-color: {BRAND['primary']} !important;
}}

/* Expander */
.streamlit-expanderHeader {{
    font-size: 13px;
    font-weight: 500;
    color: {BRAND['text']};
    background: {BRAND['surface_dark']};
    border-radius: 12px;
}}

/* Progress bar */
.stProgress > div > div {{
    background-color: {BRAND['primary']};
}}

</style>
""", unsafe_allow_html=True)

# constants
HERE = Path(__file__).resolve().parent
TEMPLATE_PATH = HERE / "template.html"
CHARTJS_PATH  = HERE / "chart.umd.min.js"

# helpers from generator
def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [" ".join(str(c).replace("\n", " ").split()) for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    return df

def to_num(v):
    try:
        n = float(v)
        return 0 if pd.isna(n) else n
    except Exception:
        return 0

def to_date_str(v) -> str:
    if pd.isna(v):
        return ""
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    if not s or s == "nan":
        return ""
    # Handle Excel serial numbers (integers like 45974, 46154, etc.)
    try:
        n = float(s)
        if 30000 < n < 60000:  # Reasonable Excel date serial range (1982–2064)
            return (pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(n))).strftime("%Y-%m-%d")
    except Exception:
        pass
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return ""

SHEET_SIGNATURES = {
    "active_po": {
        "must_have": ["PO DATE"],
        "should_have": ["PO NO.", "Value", "PO Approval Status", "Person Name", "Status/ Wo No"],
    },
    "dispatch": {
        "must_have": ["PO Number", "PO Date"],
        "should_have": ["LAST INVOICE STATUS", "Payment due on", "Dispatch Status", "Delivered to Customer"],
    },
    "items": {
        "must_have": ["PO Item Name"],
        "should_have": ["MATERIAL", "ORDER QTY.", "BAL. QTY.", "VALUE", "DISPATCH DATE", "KAM Name"],
    },
    "survey": {
        "must_have": ["Date", "customer"],
        "should_have": ["Promoters", "Passives", "Detractors", "Percentage"],
    },
}

def classify_sheet(df: pd.DataFrame):
    cols = set(df.columns)
    best_kind, best_score = None, 0
    for kind, sig in SHEET_SIGNATURES.items():
        if not all(m in cols for m in sig["must_have"]):
            continue
        score = sum(1 for s in sig["should_have"] if s in cols)
        if score > best_score:
            best_score, best_kind = score, kind
    return best_kind

def _try_read_sheet(xl, name) -> 'pd.DataFrame':
    """Read a sheet, auto-detecting whether the real header is on row 0 or row 1.

    Some sheets (e.g. Active PO) have a blank/aggregate row above the true
    column headers. We try header=0 first; if classify_sheet fails we retry
    with header=1 so the second row becomes the column header.
    """
    df = clean_cols(pd.read_excel(xl, name, header=0))
    if classify_sheet(df) is not None:
        return df
    df2 = clean_cols(pd.read_excel(xl, name, header=1))
    if classify_sheet(df2) is not None:
        return df2
    return df  # fall back even if unclassifiable


def load_workbook_sheets(path) -> dict:
    xl = pd.ExcelFile(path)
    classified = {}
    log = []

    # First pass: try to classify all sheets
    for name in xl.sheet_names:
        df = _try_read_sheet(xl, name)
        # Convert any object columns with mixed types to string to avoid Arrow issues
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)

        kind = classify_sheet(df)

        # Special handling for survey/satisfaction sheets
        if kind is None:
            cols_lower = [c.lower() for c in df.columns]
            if 'date' in cols_lower and 'customer' in cols_lower:
                has_ratings = any('promoter' in c or 'passive' in c or 'detractor' in c or 'percentage' in c for c in cols_lower)
                if has_ratings:
                    kind = "survey"
                    log.append(f"Sheet **{name}** → `{kind}` (identified as survey sheet)")

        if kind is None:
            log.append(f"Sheet **{name}** - could not classify, skipped")
            continue

        if kind in classified and len(classified[kind]) >= len(df):
            continue

        classified[kind] = df
        if kind != "survey":
            log.append(f"Sheet **{name}** → `{kind}` ({len(df)} rows)")

    return classified, log

def extract_customers(sheets: dict) -> list[str]:
    customers = set()
    if "active_po" in sheets and "Customer" in sheets["active_po"].columns:
        customers.update(
            sheets["active_po"]["Customer"].dropna().astype(str)
            .str.strip().unique().tolist()
        )
    if "dispatch" in sheets and "Customer Name" in sheets["dispatch"].columns:
        customers.update(
            sheets["dispatch"]["Customer Name"].dropna().astype(str)
            .str.strip().unique().tolist()
        )
    if "items" in sheets and "CUSTOMER NAME" in sheets["items"].columns:
        customers.update(
            sheets["items"]["CUSTOMER NAME"].dropna().astype(str)
            .str.strip().unique().tolist()
        )
    return sorted(c for c in customers if c and c.lower() != "nan")

def extract_kam(sheets: dict, customer_filter: str) -> str:
    """Extract KAM name from items sheet if available"""
    if "items" not in sheets:
        return ""
    
    df = sheets["items"]
    kam_col_candidates = ["KAM Name", "KAM", "KAM NAME", "kam name", "Key Account Manager"]
    
    kam_col = None
    for col in kam_col_candidates:
        if col in df.columns:
            kam_col = col
            break
    
    if kam_col and "CUSTOMER NAME" in df.columns:
        # Filter for customer and get first non-null KAM
        cust_df = df[df["CUSTOMER NAME"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]
        kam_values = cust_df[kam_col].dropna().astype(str).str.strip()
        kam_values = kam_values[kam_values != ""]
        if len(kam_values) > 0:
            # Return the most common KAM name
            return kam_values.mode().iloc[0] if len(kam_values) > 0 else kam_values.iloc[0]
    
    return ""

def build_active_pos(df, customer_filter, today):
    if "Customer" in df.columns:
        df = df[df["Customer"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)].copy()
    df = df[df.get("PO NO.", pd.Series(dtype=object)).notna()].copy()
    rows = []
    for _, r in df.iterrows():
        po_date = r.get("PO DATE"); cdd = r.get("Delivery Time (Req. By Cust.) CDD")
        edd = r.get("Delivery Time (Given By PPC) EDD")
        approval_s = str(r.get("PO Approval Status", "") or "")
        remarks_s  = str(r.get("Reason/Remarks", "") or "")
        age = (today - po_date).days if pd.notna(po_date) else 0
        if "Hold" in approval_s or "Hold" in remarks_s: status = "On Hold"
        elif "Under Approval" in remarks_s or ("Pending" in approval_s and "W.O." not in approval_s): status = "PO Received"
        elif age >= 15: status = "In Production"
        elif age >= 7:  status = "WO Released"
        else:           status = "PO Received"
        is_delayed = False; delay_days = 0
        if pd.notna(edd) and edd < today and status not in ("Delivered", "On Hold"):
            delay_days = (today - edd).days; is_delayed = True
        rows.append({
            "po_no": r.get("PO NO.", ""), "po_date": to_date_str(po_date),
            "po_month": to_date_str(r.get("Month")),
            "value": to_num(r.get("Value")), "value_lac": to_num(r.get("Value In Lac")),
            "wo_no": str(r.get("W.O. Number", "") or ""),
            "cdd": to_date_str(cdd), "edd": to_date_str(edd),
            "approval": approval_s, "remarks": remarks_s, "status": status,
            "age_days": int(age), "delay_days": int(delay_days), "is_delayed": is_delayed,
            "kam": str(r.get("Person Name", "") or ""), "quarter": str(r.get("Quarter", "") or ""),
        })
    return rows

def build_dispatch_history(df, customer_filter, today):
    if "Customer Name" in df.columns:
        df = df[df["Customer Name"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)].copy()
    diff_col_candidates = [c for c in df.columns if "Diff in AFPL" in c]
    diff_col = diff_col_candidates[0] if diff_col_candidates else None
    rows = []
    for _, r in df.iterrows():
        inv_status = r.get("LAST INVOICE STATUS"); delivered = r.get("Delivered to Customer")
        dispatched = r.get("Dispatch Status")
        diff_days = r.get(diff_col) if diff_col and pd.notna(r.get(diff_col)) else 0
        if delivered == "Yes": status = "Delivered"
        elif dispatched == "Yes": status = "In Transit"
        elif pd.notna(inv_status) and "Complete" in str(inv_status): status = "Invoiced"
        else: status = "Pending"
        pay_due = r.get("Payment due on")
        inv_value_col = next((c for c in df.columns if c.startswith("Due payment")), None)
        inv_value = to_num(r.get(inv_value_col)) if inv_value_col else 0
        inv_no = r.get("LAST INVOICE NO.")
        pay_status = "Not Invoiced"; aging = 0
        if pd.notna(pay_due) and isinstance(pay_due, (pd.Timestamp, datetime)):
            if inv_value > 0:
                if pay_due < today: pay_status = "Overdue"; aging = (today - pay_due).days
                else: pay_status = "Due"
            else: pay_status = "Paid"
        elif inv_value == 0 and pd.notna(inv_no): pay_status = "Paid"
        on_time_flag = ("On time" in str(inv_status)) if pd.notna(inv_status) else None
        rows.append({
            "po_no": r.get("PO Number", ""), "po_date": to_date_str(r.get("PO Date")),
            "wo_no": str(r.get("WO Number", "") or ""),
            "cdd": to_date_str(r.get("Delivery Time (Req. By Cust.) CDD")),
            "edd": to_date_str(r.get("Delivery Time (Given By PPC) EDD")),
            "inv_no": str(int(inv_no)) if pd.notna(inv_no) and isinstance(inv_no, (int, float)) else (str(inv_no) if pd.notna(inv_no) else ""),
            "inv_date": to_date_str(r.get("LAST INVOICE DATE")), "inv_status": str(inv_status) if pd.notna(inv_status) else "",
            "inv_value": inv_value, "dispatch_date": to_date_str(r.get("Dispatch date")),
            "actual_delivery": to_date_str(r.get("Actual Delivery Date")),
            "dispatch_status": str(dispatched) if pd.notna(dispatched) else "",
            "delivered": str(delivered) if pd.notna(delivered) else "",
            "pay_due": to_date_str(pay_due), "pay_status": pay_status, "aging": int(aging),
            "delay_days": int(diff_days) if not pd.isna(diff_days) and -1000 < diff_days < 1000 else 0,
            "on_time": on_time_flag, "status": status, "kam": str(r.get("KAM", "") or ""),
            "dispatch_month": to_date_str(r.get("Month")),
        })
    return rows

def build_items(df, customer_filter):
    if "CUSTOMER NAME" in df.columns:
        df = df[df["CUSTOMER NAME"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)].copy()
    rows = []
    for _, r in df.iterrows():
        po = r.get("PO"); item_name = r.get("PO Item Name")
        if pd.isna(po) and pd.isna(item_name): continue
        order_qty = to_num(r.get("ORDER QTY.")); bal_qty = to_num(r.get("BAL. QTY."))
        forging_done = to_num(r.get("FRGN. DONE")); forging_pending = to_num(r.get("FORGING PENDING"))
        value = to_num(r.get("VALUE")); dispatch_date = to_date_str(r.get("DISPATCH DATE"))
        completion_pct = 1.0 if dispatch_date else (((order_qty - bal_qty) / order_qty) if order_qty > 0 else 0.0)
        exec_status = r.get("EXECUTABLE/NON- EXECUTABLE") or r.get("EXECUTABLE/NON-EXECUTABLE")
        if dispatch_date: item_status = "Dispatched"
        elif str(exec_status).upper().strip() == "NON-EXE": item_status = "Non-Executable"
        elif bal_qty == 0 and order_qty > 0: item_status = "Ready"
        elif forging_done >= order_qty and order_qty > 0: item_status = "Forging Complete"
        elif forging_done > 0: item_status = "In Production"
        else: item_status = "Pending"
        rows.append({
            "po": str(po) if pd.notna(po) else "", "item_name": str(item_name) if pd.notna(item_name) else "",
            "item_sr": to_num(r.get("PO SR.NO. / PO Item")), "wo": str(r.get("Work Order (W.O.)", "") or ""),
            "product_code": str(r.get("Product Code", "") or ""), "material": str(r.get("MATERIAL", "") or ""),
            "sch": str(r.get("SCH.", "") or ""), "po_date": to_date_str(r.get("PO DATE")),
            "wo_date": to_date_str(r.get("W/O DATE")), "cdd": to_date_str(r.get("CDD")),
            "edd": to_date_str(r.get("EDD")), "dispatch_date": dispatch_date,
            "order_qty": order_qty, "bal_qty": bal_qty, "forging_done": forging_done,
            "forging_pending": forging_pending, "rate": to_num(r.get("RATE")), "value": value,
            "gross_wt": to_num(r.get("GROSS WT.")), "completion_pct": round(completion_pct, 3),
            "status": item_status, "executable": str(exec_status) if pd.notna(exec_status) else "",
        })
    return rows

def extract_nps_csat_data(sheets: dict, customer_filter: str) -> dict:
    """Extract NPS/CSAT data from survey sheet"""
    
    # Look for sheet with survey/satisfaction data
    survey_df = None
    
    # Check for sheet names that might contain survey data
    for sheet_name, df in sheets.items():
        if any(keyword in sheet_name.lower() for keyword in ['survey', 'satisfaction', 'nps', 'csat', 'feedback']):
            survey_df = df
            break
    
    if survey_df is None:
        # Try to find by column names
        for df in sheets.values():
            cols = [c.lower() for c in df.columns]
            if any(word in str(cols) for word in ['promoter', 'detractor', 'passive', 'percentage']):
                survey_df = df
                break
    
    if survey_df is None:
        return {"feedback": [], "nps_score": 0, "csat_score": 0, "total_responses": 0, "promoters": 0, "passives": 0, "detractors": 0}
    
    # Clean column names
    survey_df = clean_cols(survey_df)
    
    # Find relevant columns (case insensitive)
    col_mapping = {}
    for col in survey_df.columns:
        col_lower = col.lower()
        if 'date' in col_lower:
            col_mapping['date'] = col
        elif 'customer' in col_lower:
            col_mapping['customer'] = col
        elif 'promoter' in col_lower:
            col_mapping['promoters'] = col
        elif 'passive' in col_lower:
            col_mapping['passives'] = col
        elif 'detractor' in col_lower:
            col_mapping['detractors'] = col
        elif 'total' in col_lower and 'responses' not in col_lower.lower():
            col_mapping['total'] = col
        elif 'percentage' in col_lower or 'score' in col_lower:
            col_mapping['percentage'] = col
    
    feedback_list = []
    total_promoters = 0
    total_passives = 0
    total_detractors = 0
    total_responses = 0
    
    for _, row in survey_df.iterrows():
        # Get values
        promoters = to_num(row.get(col_mapping.get('promoters', ''))) if 'promoters' in col_mapping else 0
        passives = to_num(row.get(col_mapping.get('passives', ''))) if 'passives' in col_mapping else 0
        detractors = to_num(row.get(col_mapping.get('detractors', ''))) if 'detractors' in col_mapping else 0
        percentage = to_num(row.get(col_mapping.get('percentage', ''))) if 'percentage' in col_mapping else 0
        total = to_num(row.get(col_mapping.get('total', ''))) if 'total' in col_mapping else (promoters + passives + detractors)
        
        # Calculate NPS score for this survey (-100 to +100)
        if total > 0:
            nps_score = round(((promoters - detractors) / total) * 100)
        else:
            nps_score = 0
        
        # Get date
        survey_date = ""
        if 'date' in col_mapping:
            survey_date = to_date_str(row.get(col_mapping['date']))
        
        feedback_list.append({
            "date": survey_date,
            "nps": nps_score,
            "csat": percentage,
            "promoters": int(promoters),
            "passives": int(passives),
            "detractors": int(detractors),
            "total": int(total),
            "theme": "Customer Satisfaction Survey",
            "sentiment": "Positive" if nps_score > 0 else "Neutral" if nps_score == 0 else "Negative"
        })
        
        total_promoters += promoters
        total_passives += passives
        total_detractors += detractors
        total_responses += total
    
    # Calculate overall NPS
    overall_nps = 0
    overall_csat = 0
    if total_responses > 0:
        overall_nps = round(((total_promoters - total_detractors) / total_responses) * 100)
        if feedback_list:
            overall_csat = sum(f['csat'] for f in feedback_list) / len(feedback_list)
    
    return {
        "feedback": feedback_list,
        "nps_score": overall_nps,
        "csat_score": round(overall_csat, 1),
        "total_responses": int(total_responses),
        "promoters": int(total_promoters),
        "passives": int(total_passives),
        "detractors": int(total_detractors)
    }

def get_total_quantity(sheets: dict, customer_filter: str) -> float:
    """Get total order quantity for the customer"""
    if "items" not in sheets:
        return 0
    
    df = sheets["items"]
    if "CUSTOMER NAME" in df.columns:
        df = df[df["CUSTOMER NAME"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]
    
    if "ORDER QTY." in df.columns:
        # Convert to numeric, coercing errors to NaN, then sum
        quantity_series = pd.to_numeric(df["ORDER QTY."], errors='coerce')
        return quantity_series.sum()
    return 0

def extract_available_dates(sheets: dict, customer_filter: str) -> dict:
    """Extract min and max dates from active_po and dispatch sheets"""
    min_date = None
    max_date = None
    
    # Check active_po sheet — prefer Month column (always clean dates)
    if "active_po" in sheets:
        df = sheets["active_po"]
        if "Customer" in df.columns:
            df = df[df["Customer"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]

        date_col = "Month" if "Month" in df.columns else ("PO DATE" if "PO DATE" in df.columns else None)
        if date_col:
            po_dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if len(po_dates) > 0:
                if min_date is None or po_dates.min() < min_date:
                    min_date = po_dates.min()
                if max_date is None or po_dates.max() > max_date:
                    max_date = po_dates.max()
    
    # Check dispatch sheet — use Month column (always a proper date) first, fall back to PO Date
    if "dispatch" in sheets:
        df = sheets["dispatch"]
        if "Customer Name" in df.columns:
            df = df[df["Customer Name"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]

        date_col = "Month" if "Month" in df.columns else ("PO Date" if "PO Date" in df.columns else None)
        if date_col:
            po_dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if len(po_dates) > 0:
                if min_date is None or po_dates.min() < min_date:
                    min_date = po_dates.min()
                if max_date is None or po_dates.max() > max_date:
                    max_date = po_dates.max()
    
    return {
        "min_date": min_date,
        "max_date": max_date,
        "has_data": min_date is not None and max_date is not None
    }

def generate_dynamic_quarters(min_date, max_date):
    """Generate quarter options based on actual data date range"""
    if not min_date or not max_date:
        return []
    
    quarters = []
    current = min_date.replace(day=1)
    end = max_date
    
    while current <= end:
        year = current.year
        quarter_num = (current.month - 1) // 3 + 1
        
        # Calculate quarter start and end months
        if quarter_num == 1:
            start_month = "Apr"
            end_month = "Jun"
            fy_start_year = year
            fy_end_year = year + 1
        elif quarter_num == 2:
            start_month = "Jul"
            end_month = "Sep"
            fy_start_year = year
            fy_end_year = year + 1
        elif quarter_num == 3:
            start_month = "Oct"
            end_month = "Dec"
            fy_start_year = year
            fy_end_year = year + 1
        else:  # Q4 (Jan-Mar)
            start_month = "Jan"
            end_month = "Mar"
            fy_start_year = year - 1
            fy_end_year = year
        
        quarter_label = f"Q{quarter_num} FY{fy_start_year}-{str(fy_end_year)[-2:]} ({start_month}–{end_month} {year})"
        quarters.append(quarter_label)
        
        # Move to next quarter
        if quarter_num == 1:
            current = current.replace(month=7, day=1)
        elif quarter_num == 2:
            current = current.replace(month=10, day=1)
        elif quarter_num == 3:
            current = current.replace(month=1, day=1, year=year + 1)
        else:  # Q4
            current = current.replace(month=4, day=1, year=year + 1)
    
    return quarters

def extract_available_years(sheets: dict, customer_filter: str) -> list:
    """Extract unique years from the data for year filter"""
    years = set()
    
    if "active_po" in sheets:
        df = sheets["active_po"]
        if "Customer" in df.columns:
            df = df[df["Customer"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]

        date_col = "Month" if "Month" in df.columns else ("PO DATE" if "PO DATE" in df.columns else None)
        if date_col:
            po_years = pd.to_datetime(df[date_col], errors="coerce").dt.year.dropna()
            years.update(po_years.astype(int).tolist())
    
    if "dispatch" in sheets:
        df = sheets["dispatch"]
        if "Customer Name" in df.columns:
            df = df[df["Customer Name"].astype(str).str.contains(customer_filter, case=False, na=False, regex=False)]

        date_col = "Month" if "Month" in df.columns else ("PO Date" if "PO Date" in df.columns else None)
        if date_col:
            po_years = pd.to_datetime(df[date_col], errors="coerce").dt.year.dropna()
            years.update(po_years.astype(int).tolist())

    return sorted(list(years))

def filter_active_by_date(active_rows, start_date, end_date, filter_type=None):
    """Filter active POs by date range.

    Uses 'po_month' (the Month column) as the primary filter key when available,
    falling back to po_date. Rows with no usable date are always included.
    """
    if not start_date or not end_date:
        return active_rows

    filtered = []
    for row in active_rows:
        date_str = row.get("po_month") or row.get("po_date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if start_date <= date_obj <= end_date:
                    filtered.append(row)
            except Exception:
                filtered.append(row)
        else:
            filtered.append(row)
    return filtered

def filter_history_by_date(hist_rows, start_date, end_date, filter_type=None):
    """Filter dispatch history by date range.

    Uses dispatch_month (the Month column) as the primary filter key because
    PO Date may be stored as Excel serial integers. Falls back to po_date,
    and includes the row unconditionally if neither date is available.
    """
    if not start_date or not end_date:
        return hist_rows

    filtered = []
    for row in hist_rows:
        date_str = row.get("dispatch_month") or row.get("po_date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if start_date <= date_obj <= end_date:
                    filtered.append(row)
            except Exception:
                filtered.append(row)
        else:
            filtered.append(row)
    return filtered

def filter_items_by_date(items_rows, start_date, end_date, filter_type=None):
    """Filter items by PO date range"""
    if not start_date or not end_date:
        return items_rows
    
    filtered = []
    for row in items_rows:
        po_date = row.get("po_date")
        if po_date:
            try:
                po_date_obj = datetime.strptime(po_date, "%Y-%m-%d").date()
                if start_date <= po_date_obj <= end_date:
                    filtered.append(row)
            except:
                # If date parsing fails, include the row
                filtered.append(row)
    return filtered

def filter_nps_by_date(feedback_data, start_date, end_date):
    """Filter NPS/CSAT feedback by MONTH (not exact dates)"""
    if not start_date or not end_date:
        return feedback_data
    
    # Get the months that fall within the date range
    months_to_include = set()
    current = start_date.replace(day=1)
    while current <= end_date:
        months_to_include.add((current.year, current.month))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    filtered_feedback = []
    for item in feedback_data.get("feedback", []):
        survey_date = item.get("date")
        if survey_date:
            try:
                survey_date_obj = None
                if isinstance(survey_date, str):
                    survey_date_obj = datetime.strptime(survey_date, "%Y-%m-%d").date()
                elif isinstance(survey_date, date):
                    survey_date_obj = survey_date
                
                if survey_date_obj and (survey_date_obj.year, survey_date_obj.month) in months_to_include:
                    filtered_feedback.append(item)
            except Exception as e:
                filtered_feedback.append(item)
    
    # Recalculate aggregates for filtered data
    total_promoters = sum(f.get("promoters", 0) for f in filtered_feedback)
    total_passives = sum(f.get("passives", 0) for f in filtered_feedback)
    total_detractors = sum(f.get("detractors", 0) for f in filtered_feedback)
    total_responses = sum(f.get("total", 0) for f in filtered_feedback)
    
    overall_nps = 0
    overall_csat = 0
    if total_responses > 0:
        overall_nps = round(((total_promoters - total_detractors) / total_responses) * 100)
        if filtered_feedback:
            overall_csat = sum(f.get("csat", 0) for f in filtered_feedback) / len(filtered_feedback)
    
    return {
        "feedback": filtered_feedback,
        "nps_score": overall_nps,
        "csat_score": round(overall_csat, 1),
        "total_responses": int(total_responses),
        "promoters": int(total_promoters),
        "passives": int(total_passives),
        "detractors": int(total_detractors)
    }


def build_hist_from_items(df: pd.DataFrame, customer_filter: str) -> list:
    """Build dispatch history records from the PPC items sheet.

    Each dispatched line item becomes one history record.  Payment fields
    (pay_status, inv_value, aging) are intentionally left blank/zero because
    accounts data is not sourced here.
    """
    if "CUSTOMER NAME" in df.columns:
        df = df[df["CUSTOMER NAME"].astype(str).str.contains(
            customer_filter, case=False, na=False, regex=False
        )].copy()

    rows = []
    for _, r in df.iterrows():
        dispatch_date = to_date_str(r.get("DISPATCH DATE"))
        if not dispatch_date:
            continue  # only completed/dispatched items go into hist

        edd = to_date_str(r.get("EDD"))
        cdd = to_date_str(r.get("CDD"))
        po_date = to_date_str(r.get("PO DATE"))

        # on-time: compare dispatch date vs EDD
        on_time = None
        delay_days = 0
        if dispatch_date and edd:
            try:
                from datetime import datetime as _dt
                diff = (_dt.strptime(dispatch_date, "%Y-%m-%d") -
                        _dt.strptime(edd, "%Y-%m-%d")).days
                delay_days = int(diff)
                on_time = diff <= 0
            except Exception:
                pass

        rows.append({
            "po_no":          str(r.get("PO", "") or ""),
            "po_date":        po_date,
            "wo_no":          str(r.get("Work Order (W.O.)", "") or ""),
            "cdd":            cdd,
            "edd":            edd,
            "inv_no":         "",
            "inv_date":       "",
            "inv_status":     "",
            "inv_value":      0,           # payment data not available from PPC
            "dispatch_date":  dispatch_date,
            "actual_delivery": dispatch_date,
            "dispatch_status": "Yes",
            "delivered":      "Yes",
            "pay_due":        "",
            "pay_status":     "Not Invoiced",  # neutral — accounts data pending
            "aging":          0,
            "delay_days":     delay_days,
            "on_time":        on_time,
            "status":         "Delivered",
            "kam":            str(r.get("KAM Name", "") or ""),
            "dispatch_month": dispatch_date[:7] + "-01" if dispatch_date else "",
        })
    return rows

def render_html(data: dict, meta: dict) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    chartjs  = CHARTJS_PATH.read_text(encoding="utf-8") if CHARTJS_PATH.exists() else ""
    cust_short = " ".join(meta["customer"].split()[:2]).rstrip(",.")
    
    # Load and encode the logo
    logo_path = HERE / "assets" / "favicon.png"
    logo_base64 = ""
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
            logo_base64 = f"data:image/png;base64,{logo_base64}"
    
    replacements = {
        "{{COMPANY}}":          "Anandmayee Forgings",
        "{{COMPANY_INITIAL}}":  "A",
        "{{COMPANY_LOGO}}":     logo_base64,  # Add this line
        "{{CUSTOMER}}":         meta["customer"],
        "{{CUSTOMER_SHORT}}":   cust_short,
        "{{CUSTOMER_DISPLAY}}": meta.get("customer_display", meta["customer"]),
        "{{KAM}}":              meta["kam"],
        "{{PERIOD}}":           meta["period"],
        "{{HERO_SUB}}":         meta["hero_sub"],
        "{{ITEM_COUNT}}":       str(len(data.get("items", []))),
        "{{GEN_DATE}}":         meta["gen_date"],
        "{{BODY_CLASS}}":       meta.get("body_class", ""),
        "{{DATA_JSON}}":        json.dumps(data, separators=(",", ":")),
        "{{CHARTJS}}":          chartjs,
        "{{CATEGORY}}":         meta.get("category", ""),
        "{{INDUSTRY}}":         meta.get("industry", ""),
        "{{PLANT}}":            meta.get("plant", ""),
        "{{ACTIVE_SINCE}}":     meta.get("active_since", ""),
    }
    html = template
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html

# STREAMLIT UI
# Header
st.markdown(f"""
<div class="afpl-header-new">
    <div class="afpl-brand">
        <div class="afpl-logo-new">
            <img src="data:image/png;base64,{encoded_logo}" 
                 width="250">
        </div>
    </div>
    <div class="afpl-badge">
        Customer Experience Management · Dashboard Generator
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar: file upload & customer selection
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0; border-bottom: 1px solid {BRAND['border']}; margin-bottom: 1rem;">
        <div style="height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto;">
            <img src="data:image/png;base64,{encoded_logo}" width="210";>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-header"><h3><span class="step-badge">1</span> Data Source</h3></div>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Upload Excel Workbook", 
        type=["xlsx", "xls"],
        help="Upload your Excel file containing Active PO, Dispatch, and Items sheets"
    )

    sheets, customers, sheet_log = {}, [], []

    if uploaded:
        with st.spinner("🔍 Reading workbook..."):
            try:
                sheets, sheet_log = load_workbook_sheets(uploaded)
                customers = extract_customers(sheets)
                st.success(f"Loaded {len(sheets)} sheets, {len(customers)} customers")
            except Exception as e:
                st.error(f"Error: {e}")

        if sheet_log:
            with st.expander("Sheet Classification Log"):
                for msg in sheet_log:
                    st.caption(msg)

    st.markdown('<div class="sidebar-header"><h3><span class="step-badge">2</span> Select Customer</h3></div>', unsafe_allow_html=True)

    if customers:
        search = st.text_input("Filter ⌕", placeholder="Type customer name...", key="customer_search")
        filtered = [c for c in customers if search.lower() in c.lower()] if search else customers
        selected_customer = st.selectbox("Customer", filtered, index=0 if filtered else None, key="customer_select")
        
        # Show customer count
        st.caption(f"📊 {len(filtered)} customers available")
    else:
        selected_customer = st.text_input("Customer Name (Manual)", placeholder="e.g. MICON ENGINEERS", key="customer_manual")

    st.markdown('<div class="sidebar-header"><h3><span class="step-badge">3</span> Reporting Period</h3></div>', unsafe_allow_html=True)

    # Get available date ranges from data if sheets are loaded
    available_years = []
    date_range_info = {"has_data": False, "min_date": None, "max_date": None}

    if sheets and selected_customer:
        date_range_info = extract_available_dates(sheets, selected_customer)
        available_years = extract_available_years(sheets, selected_customer)
        
        # Show data range info
        if date_range_info["has_data"]:
            st.info(f"Data Range: {date_range_info['min_date'].strftime('%b %Y')} - {date_range_info['max_date'].strftime('%b %Y')}")

    # Create dynamic filter options
    filter_options = ["All Data", "Yearly", "Quarterly", "Monthly", "Weekly Report", "Custom Range"]

    dynamic_quarters = []
    if date_range_info["has_data"]:
        dynamic_quarters = generate_dynamic_quarters(date_range_info["min_date"], date_range_info["max_date"])

    filter_type = st.selectbox("Filter Type", filter_options, index=0, key="filter_type")

    show_date_range = False
    start_date = None
    end_date = None
    period_label = ""

    if filter_type == "Yearly" and available_years:
        selected_year = st.selectbox("Select Year", available_years, key="year_select")
        start_date = date(selected_year, 1, 1)
        end_date = date(selected_year, 12, 31)
        period_label = f"Year {selected_year}"

    elif filter_type == "Quarterly" and dynamic_quarters:
        selected_quarter = st.selectbox("Select Quarter", dynamic_quarters, key="quarter_select")
        period_label = selected_quarter
        
        import re
        match = re.search(r'Q(\d) FY(\d{4})-(\d{2})', selected_quarter)
        if match:
            quarter_num = int(match.group(1))
            year = int(match.group(2))
            
            if quarter_num == 1:
                start_date = date(year, 4, 1)
                end_date = date(year, 6, 30)
            elif quarter_num == 2:
                start_date = date(year, 7, 1)
                end_date = date(year, 9, 30)
            elif quarter_num == 3:
                start_date = date(year, 10, 1)
                end_date = date(year, 12, 31)
            else:
                start_date = date(year + 1, 1, 1)
                end_date = date(year + 1, 3, 31)

    elif filter_type == "Monthly" and date_range_info["has_data"]:
        months = []
        current = date_range_info["min_date"].replace(day=1)
        while current <= date_range_info["max_date"]:
            months.append(current.strftime("%B %Y"))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        selected_month = st.selectbox("Select Month", months, key="month_select")
        period_label = selected_month
        
        month_date = datetime.strptime(selected_month, "%B %Y")
        start_date = date(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            end_date = date(month_date.year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = date(month_date.year, month_date.month + 1, 1) - pd.Timedelta(days=1)

    elif filter_type == "Weekly Report":
        st.markdown("### 📅 Weekly Report Date Range")
        st.caption("Note: End date can be at most 7 days after start date")
        
        col1, col2 = st.columns(2)
        with col1:
            default_start = date.today() - pd.Timedelta(days=7)
            if date_range_info.get("min_date"):
                default_start = max(date_range_info["min_date"].date(), default_start)
            start_date = st.date_input("Start Date", value=default_start, key="weekly_start")
        
        with col2:
            default_end = date.today()
            if date_range_info.get("max_date"):
                default_end = min(date_range_info["max_date"].date(), default_end)
            if start_date and default_end < start_date:
                default_end = start_date + pd.Timedelta(days=7)
            end_date = st.date_input("End Date", value=default_end, key="weekly_end")
        
        if start_date and end_date:
            if end_date > start_date + pd.Timedelta(days=7):
                st.error(f"⚠️ End date cannot be more than 7 days after start date!")
                st.stop()
            if end_date < start_date:
                st.error("⚠️ End date cannot be before start date!")
                st.stop()
            period_label = f"Weekly: {start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
        else:
            period_label = "Weekly Report"

    elif filter_type == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            default_start = date.today() - pd.Timedelta(days=30)
            if date_range_info.get("min_date"):
                default_start = max(date_range_info["min_date"].date(), default_start)
            start_date = st.date_input("Start Date", value=default_start, key="custom_start")
        
        with col2:
            default_end = date.today()
            if date_range_info.get("max_date"):
                default_end = min(date_range_info["max_date"].date(), default_end)
            if start_date and default_end < start_date:
                default_end = start_date
            end_date = st.date_input("End Date", value=default_end, key="custom_end")
        
        if start_date and end_date:
            if end_date < start_date:
                st.error("⚠️ End date cannot be before start date!")
                st.stop()
            period_label = f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
        else:
            period_label = "Custom Range"

    else:  # All Data
        if date_range_info["has_data"]:
            start_date = date_range_info["min_date"].date()
            end_date = date_range_info["max_date"].date()
            period_label = f"All Data ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})"
        else:
            period_label = "All Data"

    # Show selected period summary
    if period_label and period_label != "All Data":
        st.caption(f"› Selected: {period_label}")
    
    # Add reporting date picker - THIS WAS MISSING
    reporting_date = st.date_input("Reference Date", value=date.today(), key="reporting_date")
    
    st.markdown("---")
    
    # Add a status indicator
    if sheets and selected_customer:
        st.success(f"Ready to generate for {selected_customer.split()[0] if selected_customer else 'customer'}")
    else:
        st.info("Complete all steps above")
    
# Main panel
col_left, col_right = st.columns([2.5, 1])

with col_left:
    st.markdown("### ᯓ Data Preview")
    if sheets:
        tab_names = list(sheets.keys())
        if tab_names:
            tabs = st.tabs([f"🗂️ {k.title()}" for k in tab_names])
            for i, kind in enumerate(tab_names):
                df_preview = sheets[kind]
                if selected_customer:
                    cust_col = {"active_po": "Customer", "dispatch": "Customer Name", "items": "CUSTOMER NAME"}.get(kind)
                    if cust_col and cust_col in df_preview.columns:
                        mask = df_preview[cust_col].astype(str).str.contains(selected_customer, case=False, na=False, regex=False)
                        df_preview = df_preview[mask]
                with tabs[i]:
                    st.caption(f"{len(df_preview)} rows for **{selected_customer or 'all customers'}**")
                    st.dataframe(df_preview.head(20), use_container_width=True, height=280)
        else:
            st.info("No valid sheets found in the uploaded file.")
    else:
        st.info("📂 Upload an Excel file to preview data here.")

with col_right:
    st.markdown("### 三 Summary")
    if sheets and selected_customer:
        today_ts = pd.Timestamp(reporting_date)
        active_count  = len(build_active_pos(sheets.get("active_po", pd.DataFrame()), selected_customer, today_ts)) if "active_po" in sheets else 0
        hist_count    = len(build_dispatch_history(sheets.get("dispatch", pd.DataFrame()), selected_customer, today_ts)) if "dispatch" in sheets else 0
        total_qty     = get_total_quantity(sheets, selected_customer) if "items" in sheets else 0

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Active Purchase Orders</div>
            <div class="metric-value">{active_count}</div>
        </div>
        <div class="metric-container" style="margin-top: 12px;">
            <div class="metric-label">Dispatch Records</div>
            <div class="metric-value">{hist_count}</div>
        </div>
        <div class="metric-container" style="margin-top: 12px;">
            <div class="metric-label">Total Order Quantity</div>
            <div class="metric-value">{int(total_qty):,}</div>
        </div>
        """, unsafe_allow_html=True)

        if active_count + hist_count + total_qty == 0:
            st.warning("No records found. Check spelling or try partial name.")
    else:
        st.caption("Upload file and select customer to view metrics")

# Generate button
st.divider()

if not sheets:
    st.info("Upload an Excel file in the sidebar to get started.")
elif not selected_customer:
    st.warning("Select a customer in the sidebar.")
else:
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        go = st.button(f"Generate Dashboard for {selected_customer.split()[0]}", type="primary", use_container_width=True)

    if go:
        today_ts = pd.Timestamp(reporting_date)
        
        auto_kam = extract_kam(sheets, selected_customer)
        
        with st.spinner("Building dashboard..."):
            # Build data
            active = build_active_pos(sheets.get("active_po", pd.DataFrame()), selected_customer, today_ts) if "active_po" in sheets else []
            hist = build_hist_from_items(sheets.get("items", pd.DataFrame()), selected_customer) if "items" in sheets else []
            items = build_items(sheets.get("items", pd.DataFrame()), selected_customer) if "items" in sheets else []
            
            # Apply date filters if start_date and end_date are set
            if start_date and end_date:
                active = filter_active_by_date(active, start_date, end_date, filter_type)
                hist = filter_history_by_date(hist, start_date, end_date, filter_type)
                items = filter_items_by_date(items, start_date, end_date, filter_type)
            
            nps_data = extract_nps_csat_data(sheets, selected_customer)

            # Store original overall data for fallback
            original_nps_data = nps_data.copy()

            if start_date and end_date and nps_data.get("feedback"):
                filtered_nps_data = filter_nps_by_date(nps_data, start_date, end_date)
                
                # Check if filtered data has any responses
                if filtered_nps_data.get("total_responses", 0) == 0:
                    # No data for selected months - show overall data with warning message
                    st.warning(f"No NPS/CSAT survey data found for selected period ({period_label}). Showing overall data from all available surveys.")
                    nps_data = original_nps_data
                    # Add a flag to indicate this in the HTML
                    nps_data["showing_overall_fallback"] = True
                else:
                    nps_data = filtered_nps_data
                    nps_data["showing_overall_fallback"] = False
            else:
                nps_data["showing_overall_fallback"] = False
            
            data = {
                "active": active, 
                "hist": hist, 
                "items": items,
                "feedback_data": nps_data,
                "today": today_ts.strftime("%Y-%m-%d"),
                "customer": selected_customer, 
                "kam": auto_kam,
            }

            cust_display = selected_customer
            
            # Conditional hero text based on filter_type
            if filter_type == "Weekly Report" and start_date and end_date:
                hero_sub_text = (
                    f"Weekly performance snapshot for {' '.join(selected_customer.split()[:2])} from "
                    f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}. "
                    f"Real-time visibility on orders, dispatch, payments, and feedback."
                )
            elif filter_type == "Custom Range" and start_date and end_date:
                hero_sub_text = (
                    f"Custom period performance snapshot for {' '.join(selected_customer.split()[:2])} from "
                    f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}. "
                    f"Real-time visibility on orders, dispatch, payments, and feedback."
                )
            elif filter_type == "Yearly" and start_date and end_date:
                hero_sub_text = (
                    f"Yearly performance overview for {' '.join(selected_customer.split()[:2])} - {start_date.year}. "
                    f"Real-time visibility on orders, dispatch, payments, and feedback."
                )
            elif filter_type == "Quarterly":
                hero_sub_text = (
                    f"Quarterly performance snapshot for {' '.join(selected_customer.split()[:2])} - {period_label}. "
                    f"Real-time visibility on orders, dispatch, payments, and feedback."
                )
            elif filter_type == "Monthly":
                hero_sub_text = (
                    f"Monthly performance snapshot for {' '.join(selected_customer.split()[:2])} - {period_label}. "
                    f"Real-time visibility on orders, dispatch, payments, and feedback."
                )
            else:  # All Data
                hero_sub_text = (
                    f"Real-time visibility on orders, dispatch, payments, complaints and "
                    f"feedback for {' '.join(selected_customer.split()[:2])}. "
                    f"Built for proactive account management, operations review, and management dashboards."
                )

            meta = {
                "customer": selected_customer,
                "customer_display": cust_display,
                "kam": auto_kam,
                "period": period_label,  # Use the period_label from sidebar
                "hero_sub": hero_sub_text,
                "gen_date": today_ts.strftime("%d %b %Y"),
                "body_class": "",
            }

            if not TEMPLATE_PATH.exists():
                st.error(f"template.html not found at {TEMPLATE_PATH}. Place it in the same folder as app.py.")
                st.stop()

            html_content = render_html(data, meta)

        st.success(f"Dashboard generated - {len(active)} POs · {len(hist)} dispatches · {len(items)} items · KAM: {auto_kam or 'Not found'}")

        cust_slug = "_".join(selected_customer.split()[:2]).rstrip(",.")
        filename = f"CXM_{cust_slug}_{today_ts.strftime('%Y%m%d')}"

        # Create three columns for buttons
        dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 1])
        
        with dl_col1:
            st.download_button(
                label="Download HTML",
                data=html_content.encode("utf-8"),
                file_name=f"{filename}.html",
                mime="text/html",
                use_container_width=True,
            )

        with dl_col2:
            # Show PDF instructions instead of generating PDF
            with st.popover("How to get PDF", use_container_width=True):
                st.markdown("""
                ### Get PDF in 3 Simple Steps:
                
                1. **Download the HTML** using the button on the left
                2. **Open the file** in **Google Chrome** or **Microsoft Edge**
                3. **Press `Ctrl + P`** (Windows) or **`Cmd + P`** (Mac)
                
                ### For Best Results:
                - **Destination**: Select "Save as PDF"
                - **Margins**: Set to "None" or "Minimum"  
                - **Options**: Check "Background graphics"
                - **Scale**: 100%
                
                """)
            
            # Alternative: Add a "Generate PDF" button that opens HTML in new tab
            b64_html = base64.b64encode(html_content.encode()).decode()
            st.markdown(
                f'<a href="data:text/html;base64,{b64_html}" target="_blank" '
                f'style="display: block; width: 100%; text-align: center; '
                f'background: {BRAND["primary"]}; color: white; padding: 0.75rem 1.5rem; '
                f'border-radius: 12px; text-decoration: none; font-weight: 600; margin-top: 0.5rem;">'
                f'Open in Browser → Print as PDF</a>',
                unsafe_allow_html=True,
            )
