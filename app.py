# -*- coding: utf-8 -*-
"""
Rolling Scorecard & Email Automation - Heracles / Holcim Group Edition
Streamlit Cloud Application with Exact Logo Rendering & Green Circle Icon
"""

import base64
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import os
import smtplib
import time
import numpy as np
import pandas as pd
import streamlit as st

# Streamlit Page Configuration (Πράσινος κύκλος αντί για λιοντάρι)
st.set_page_config(
    page_title="HERACLES Group | Road Safety Scorecard",
    page_icon="🟢",
    layout="wide",
)

# ==============================================================================
# LOGO HELPER FUNCTION (LOADS YOUR EXACT UPLOADED LOGO.PNG)
# ==============================================================================
def get_heracles_holcim_logo_html():
  """Loads the exact uploaded logo.png from the repository without distortion."""
  for fname in [
      "logo.png",
      "heracles.png",
      "holcim_logo.png",
      "holcim.png",
      "logo.jpg",
      "logo.jpeg",
  ]:
    if os.path.exists(fname):
      try:
        with open(fname, "rb") as f:
          encoded = base64.b64encode(f.read()).decode()
        ext = fname.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        return f'<img src="data:{mime};base64,{encoded}" alt="Heracles Holcim Logo" style="height: 50px; max-width: 360px; width: auto; object-fit: contain; display: block;">'
      except Exception:
        pass

  # Φιλική υπενθύμιση αν δεν έχει ανέβει ακόμα το αρχείο logo.png στο GitHub
  return """
    <div style="color: #0B1E36; font-weight: 700; font-size: 0.85rem; text-align: center; line-height: 1.3;">
        <span style="color: #005A9C; font-size: 1.15rem; font-weight: 900; letter-spacing: 1px;">HERACLES</span><br>
        <span style="font-size: 0.75rem; color: #64748B;">A MEMBER OF HOLCIM GROUP</span><br>
        <span style="font-size: 0.68rem; color: #E11D48; font-weight: 600;">(Ανέβασε το logo.png στο GitHub)</span>
    </div>
    """


# ==============================================================================
# HOLCIM / HERACLES CORPORATE STYLING (DARK & LIGHT MODE COMPATIBLE)
# ==============================================================================
st.markdown(
    """
<style>
    /* Holcim / Heracles Header Banner */
    .holcim-banner {
        background: linear-gradient(135deg, #07172B 0%, #102A4C 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 6px solid #00C067;
    }

    .holcim-logo-card {
        background-color: #FFFFFF !important;
        padding: 8px 18px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 60px !important;
    }
    
    .holcim-badge {
        background-color: rgba(0, 192, 103, 0.15) !important;
        color: #00D26A !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        display: inline-block;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(0, 192, 103, 0.4) !important;
        text-transform: uppercase;
    }

    .holcim-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
        line-height: 1.2;
    }

    .holcim-subtitle {
        font-size: 1.05rem;
        color: #94A3B8 !important;
        font-weight: 400;
        margin-top: 0.4rem;
    }

    /* Primary Action Buttons (Holcim Green) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00A859 0%, #00C067 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 3px 10px rgba(0, 192, 103, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #00934E 0%, #00A859 100%) !important;
        box-shadow: 0 5px 15px rgba(0, 192, 103, 0.45) !important;
        transform: translateY(-1px);
    }

    /* Download Button */
    div.stDownloadButton > button {
        background-color: var(--secondary-background-color, #102A4C) !important;
        color: var(--text-color, #FFFFFF) !important;
        border: 1.5px solid #00C067 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.3s ease !important;
    }

    div.stDownloadButton > button:hover {
        background-color: #00C067 !important;
        color: #07172B !important;
        border-color: #00C067 !important;
        box-shadow: 0 4px 14px rgba(0, 192, 103, 0.35) !important;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        border-radius: 10px !important;
        padding: 14px 18px !important;
        border-top: 3.5px solid #00C067 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] p {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] *,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        letter-spacing: -0.5px !important;
    }

    /* Dark Mode */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            background-color: #0E1E33 !important;
            border: 1px solid #1E3A5F !important;
            border-top: 3.5px solid #00D26A !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p {
            color: #94A3B8 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] *,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
            color: #FFFFFF !important;
        }
    }

    /* Light Mode */
    @media (prefers-color-scheme: light) {
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-top: 3.5px solid #00C067 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p {
            color: #475569 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] *,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
            color: #0B1E36 !important;
        }
    }

    /* File Upload Dropzones */
    [data-testid="stFileUploadDropzone"] {
        border: 1.5px dashed #00C067 !important;
        border-radius: 8px !important;
        background-color: var(--secondary-background-color) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px;
        font-weight: 700;
        color: var(--text-color);
        opacity: 0.7;
        border-radius: 6px 6px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #00D26A !important;
        border-bottom: 3px solid #00C067 !important;
        background-color: rgba(0, 192, 103, 0.1) !important;
        opacity: 1 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
SENDER_EMAIL = "VASILEIOS.NIKIFOROS@LAFARGE.COM"
SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "ilfkvjxuyiffjefs")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
DEFAULT_TEST = "VASILEIOS.NIKIFOROS@LAFARGE.COM"


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def create_match_key(text):
  if pd.isna(text):
    return ""
  return " ".join(str(text).split()).upper()


def clean_number(val):
  if pd.isna(val):
    return 0.0
  if isinstance(val, (int, float)):
    return float(val)
  val_str = str(val).replace(",", "").strip()
  try:
    return float(val_str)
  except ValueError:
    return 0.0


def clean_percentage(val):
  if pd.isna(val):
    return np.nan
  if isinstance(val, str):
    val = val.replace("%", "").strip()
    try:
      val = float(val)
    except ValueError:
      return np.nan
  if 0 < val <= 1.0:
    return val * 100.0
  return float(val)


# ==============================================================================
# 10 GREEK EMAIL TEMPLATES
# ==============================================================================
def generate_email_content(row):
  transporter = row["Transporter"]
  category = row["Category"]
  last_score = row["Last Score"]
  final_score = int(round(row["Final Score"]))
  is_relapse = row["Is_Relapse"]
  times_60 = row["Times Score 60"]
  tablet_pct = row["Tablet_Use_Pct"]

  subject = f'Ειδοποίηση Scorecard: "{transporter}"'

  # 1. Πρότυπο 7: Υποτροπή
  if is_relapse:
    subject = (
        f'Ειδοποίηση Scorecard: "{transporter}" - ΑΥΣΤΗΡΗ ΠΟΙΝΗ ΥΠΟΤΡΟΠΗΣ'
    )
    body = (
        "Αγαπητέ Συνεργάτη,\n\n"
        "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
        " τις επιδόσεις οδικής συμπεριφοράς, οδήγησε το σκορ της Συνολικής"
        " Οδικής Συμπεριφοράς (Συνολική Κάρτα Πόντων) εκ νέου στο"
        f" {final_score}.\n\n"
        f"Διαπιστώνεται ΥΠΟΤΡΟΠΗ ({times_60}η φορά με βαθμολογία στο όριο"
        " ανάληψης διορθωτικών ενεργειών του 60).\n\n"
        "Ως εκ τούτου, ενεργοποιείται άμεσα η διαδικασία Επιβολής Αυστηρών"
        " Διορθωτικών Κυρώσεων και Ποινών, σύμφωνα με την Πολιτική"
        " Επιβραβεύσεων και Συνεπειών του Ομίλου.\n\n"
        "Παρακαλούμε για τις άμεσες ενέργειές σας και τον προγραμματισμό"
        " έκτακτης συνάντησης με τη Διοίκηση και το Τμήμα Υγείας &"
        " Ασφάλειας.\n\n"
        "Με εκτίμηση,\n"
        "Τμήμα Υγείας & Ασφάλειας"
    )
    return "Πρότυπο 7 (Υποτροπή)", subject, body

  # 2. Πρότυπα 5 & 6: Ποινή 1ης φοράς
  if final_score <= 60:
    cat_greek = "ΚΙΤΡΙΝΗ" if category == "Yellow" else "ΚΟΚΚΙΝΗ"
    p_name = (
        "Πρότυπο 5 (Ποινή Κίτρινη)"
        if category == "Yellow"
        else "Πρότυπο 6 (Ποινή Κόκκινη)"
    )
    body = (
        "Αγαπητέ Συνεργάτη,\n\n"
        "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
        f" τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
        "Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι"
        f" {final_score}.\n\n"
        "Με την απόδοση αυτή το σκορ σας βρίσκεται ήδη κάτω από το όριο"
        " ανάληψης διορθωτικών ενεργειών του 60.\n\n"
        "Ως εκ τούτου, θα σας επιβληθεί η αντίστοιχη ποινή βάσει της Πολιτικής"
        " Επιβραβεύσεων και Συνεπειών του Ομίλου.\n\n"
        "Με εκτίμηση,\n"
        "Τμήμα Υγείας & Ασφάλειας"
    )
    return p_name, subject, body

  # 3. Πρότυπα 3 & 4: Πτώση κάτω από 80
  if last_score > 80.0 and final_score <= 80:
    cat_greek = "ΚΙΤΡΙΝΗ" if category == "Yellow" else "ΚΟΚΚΙΝΗ"
    p_name = (
        "Πρότυπο 3 (Πτώση Κίτρινη)"
        if category == "Yellow"
        else "Πρότυπο 4 (Πτώση Κόκκινη)"
    )
    body = (
        "Αγαπητέ Συνεργάτη,\n\n"
        "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
        f" τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
        "Το σκορ της συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα Πόντων) είναι"
        f" {final_score}.\n\n"
        "Με την απόδοση αυτή το σκορ σας βρίσκεται ήδη κάτω από το"
        " προειδοποιητικό όριο του 80.\n\n"
        "Ως εκ τούτου, σας εφιστούμε την προσοχή για την άμεση βελτίωση της"
        " απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας, με"
        " γνώμονα πάντα την Υγεία & Ασφάλεια.\n\n"
        "Με εκτίμηση,\n"
        "Τμήμα Υγείας & Ασφάλειας"
    )
    return p_name, subject, body

  # 4. Πρότυπα 9, 10 & 8: Tablet < 80%
  if pd.notna(tablet_pct) and tablet_pct < 80.0:
    if category == "Yellow":
      body = (
          "Αγαπητέ Συνεργάτη,\n\n"
          "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
          " τις επιδόσεις οδικής συμπεριφοράς είναι  ΚΙΤΡΙΝΗ.\n\n"
          "Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων)"
          f" είναι {final_score}.\n\n"
          "Επίσης, αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του"
          " 80%. Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με"
          " σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική"
          " συμπεριφορά του στόλου σας.\n\n"
          "Ως εκ τούτου θα σας αφαιρεθούν 5 πόντοι από τη βαθμολογία της"
          " Συνολικής Κάρτας Πόντων.\n\n"
          "Με εκτίμηση,\n"
          "Τμήμα Υγείας & Ασφάλειας"
      )
      return "Πρότυπο 9 (Tablet < 80% & Κίτρινος)", subject, body

    elif category == "Red":
      body = (
          "Αγαπητέ Συνεργάτη,\n\n"
          "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
          " τις επιδόσεις οδικής συμπεριφοράς είναι  ΚΟΚΚΙΝΗ.\n\n"
          "Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων)"
          f" είναι {final_score}.\n\n"
          "Επίσης, αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του"
          " 80%. Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με"
          " σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική"
          " συμπεριφορά του στόλου σας.\n\n"
          "Ως εκ τούτου θα σας αφαιρεθούν 12 πόντοι από τη βαθμολογία της"
          " Συνολικής Κάρτας Πόντων.\n\n"
          "Με εκτίμηση,\n"
          "Τμήμα Υγείας & Ασφάλειας"
      )
      return "Πρότυπο 10 (Tablet < 80% & Κόκκινος)", subject, body

    else:
      body = (
          "Αγαπητέ Συνεργάτη,\n\n"
          "Αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του 80%."
          " Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό"
          " την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική"
          " συμπεριφορά του στόλου σας.\n\n"
          "Ως εκ τούτου θα σας αφαιρεθούν 2 πόντοι από τη βαθμολογία της"
          " Συνολικής Κάρτας Πόντων.\n\n"
          "Με εκτίμηση,\n"
          "Τμήμα Υγείας & Ασφάλειας"
      )
      return "Πρότυπο 8 (Tablet < 80% Γενικό)", subject, body

  # 5. Πρότυπα 1 & 2: Γενική ενημέρωση
  if category in ["Yellow", "Red"]:
    cat_greek = "ΚΙΤΡΙΝΗ" if category == "Yellow" else "ΚΟΚΚΙΝΗ"
    p_name = (
        "Πρότυπο 1 (Γενικό Κίτρινο)"
        if category == "Yellow"
        else "Πρότυπο 2 (Γενικό Κόκκινο)"
    )
    body = (
        "Αγαπητέ Συνεργάτη,\n\n"
        "Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει"
        f" τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
        "Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι"
        f" {final_score}.\n\n"
        "Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό την"
        " άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του"
        " στόλου σας.\n\n"
        "Με εκτίμηση,\n"
        "Τμήμα Υγείας & Ασφάλειας"
    )
    return p_name, subject, body

  return (
      "Ενημερωτικό",
      subject,
      f"Ενημέρωση Scorecard για τον μεταφορέα {transporter}. Τρέχον Σκορ:"
      f" {final_score}.",
  )


# ==============================================================================
# SCORECARD CALCULATION
# ==============================================================================
def process_data(df_prev_file, df_curr_file):
  df_curr = pd.read_excel(df_curr_file)

  col_trans = (
      "Transporter"
      if "Transporter" in df_curr.columns
      else (
          "Μεταφορέας" if "Μεταφορέας" in df_curr.columns else df_curr.columns[1]
      )
  )
  col_facil = (
      "Facility"
      if "Facility" in df_curr.columns
      else (
          "Εγκατάσταση"
          if "Εγκατάσταση" in df_curr.columns
          else df_curr.columns[0]
      )
  )
  col_dist = (
      "Distance"
      if "Distance" in df_curr.columns
      else ("Απόσταση" if "Απόσταση" in df_curr.columns else "Distance")
  )
  col_score = "Score" if "Score" in df_curr.columns else "Score"
  col_tab = (
      "Tablet Usage"
      if "Tablet Usage" in df_curr.columns
      else (
          "Χρήση Tablet"
          if "Χρήση Tablet" in df_curr.columns
          else (
              "IdentityUsePercentage"
              if "IdentityUsePercentage" in df_curr.columns
              else "Tablet"
          )
      )
  )

  df_curr["MatchKey"] = df_curr[col_trans].apply(create_match_key)
  df_curr["Distance_Clean"] = df_curr[col_dist].apply(clean_number)
  df_curr["Score_Clean"] = df_curr[col_score].apply(clean_number)
  df_curr["Tablet_Clean"] = df_curr[col_tab].apply(clean_percentage)

  if df_prev_file is not None:
    df_prev = pd.read_excel(df_prev_file)
    df_prev = df_prev.drop(columns=["MatchKey"], errors="ignore")
    trans_col_prev = (
        "Transporter"
        if "Transporter" in df_prev.columns
        else (
            "Μεταφορέας"
            if "Μεταφορέας" in df_prev.columns
            else df_prev.columns[0]
        )
    )
    df_prev["MatchKey"] = df_prev[trans_col_prev].apply(create_match_key)

    if "Final Score" in df_prev.columns:
      prev_score_col = "Final Score"
    elif "Last Score Next Month" in df_prev.columns:
      prev_score_col = "Last Score Next Month"
    else:
      prev_score_col = df_prev.columns[8]

    prev_times_col = None
    for cand in [
        "Times Score 60 Next Month",
        "Times Score 60",
        "Φορές Σκορ 60",
        "Πλήθος Σκορ 60",
        "Penalty Count",
    ]:
      if cand in df_prev.columns:
        prev_times_col = cand
        break

    cols_to_pull = [df_prev.columns[0], prev_score_col, "MatchKey"]
    if prev_times_col:
      cols_to_pull.append(prev_times_col)

    all_keys = (
        pd.concat([df_prev["MatchKey"], df_curr["MatchKey"]]).dropna().unique()
    )
    all_keys = [k for k in all_keys if k != ""]
    df_merged = pd.DataFrame({"MatchKey": all_keys})

    prev_subset = df_prev[cols_to_pull].drop_duplicates(subset=["MatchKey"])
    rename_dict = {
        df_prev.columns[0]: "Name_Orig_Prev",
        prev_score_col: "Prev_Month_Final_Score",
    }
    if prev_times_col:
      rename_dict[prev_times_col] = "Prev_Times_60"

    df_merged = df_merged.merge(prev_subset, on="MatchKey", how="left").rename(
        columns=rename_dict
    )
    if "Prev_Times_60" not in df_merged.columns:
      df_merged["Prev_Times_60"] = df_merged["Prev_Month_Final_Score"].apply(
          lambda x: 1 if (pd.notna(x) and float(x) <= 60.0) else 0
      )
    else:
      df_merged["Prev_Times_60"] = (
          df_merged["Prev_Times_60"].fillna(0).astype(int)
      )
  else:
    all_keys = df_curr["MatchKey"].dropna().unique()
    df_merged = pd.DataFrame({"MatchKey": all_keys})
    df_merged["Name_Orig_Prev"] = np.nan
    df_merged["Prev_Month_Final_Score"] = np.nan
    df_merged["Prev_Times_60"] = 0

  curr_subset = df_curr[[
      col_trans,
      col_facil,
      "Distance_Clean",
      "Score_Clean",
      "Tablet_Clean",
      "MatchKey",
  ]].drop_duplicates(subset=["MatchKey"])
  df_merged = df_merged.merge(curr_subset, on="MatchKey", how="left").rename(
      columns={
          col_trans: "Name_Original_Curr",
          col_facil: "Facility",
          "Distance_Clean": "Distance",
          "Score_Clean": "Driving_Score",
          "Tablet_Clean": "Tablet_Use_Pct",
      }
  )

  df_merged["Transporter"] = df_merged["Name_Original_Curr"].fillna(
      df_merged["Name_Orig_Prev"]
  )
  df_merged["Facility"] = df_merged["Facility"].fillna("-")
  df_merged["Distance"] = df_merged["Distance"].fillna(0.0)

  # Distance (< 500 km) & Score
  def evaluate_driving(row):
    dist = row["Distance"]
    raw_score = row["Driving_Score"]
    if dist < 500.0:
      return 0.0, "Grey", 0
    if raw_score <= 5.0:
      return raw_score, "Green", 10
    elif raw_score < 9.0:
      return raw_score, "Yellow", -3
    else:
      return raw_score, "Red", -10

  eval_results = df_merged.apply(evaluate_driving, axis=1)
  df_merged["Score"] = [x[0] for x in eval_results]
  df_merged["Category"] = [x[1] for x in eval_results]
  df_merged["Category Points"] = [x[2] for x in eval_results]

  # Tablet Points
  def get_tablet_points(row):
    cat = row["Category"]
    pct = row["Tablet_Use_Pct"]
    score = row["Score"]
    if cat == "Grey" or pd.isna(pct):
      return 0
    if pct < 80.0:
      return -12 if score <= 5.0 else -2
    return 0

  df_merged["Tablet Use Points"] = df_merged.apply(get_tablet_points, axis=1)

  # Last Score & Final Score
  df_merged["Last Score"] = df_merged["Prev_Month_Final_Score"].apply(
      lambda x: 100.0 if (pd.isna(x) or x <= 60.0) else float(x)
  )
  df_merged["Calculated_Score"] = (
      df_merged["Last Score"]
      + df_merged["Category Points"]
      + df_merged["Tablet Use Points"]
  )
  df_merged["Final Score"] = df_merged["Calculated_Score"].apply(
      lambda x: max(60.0, min(160.0, x))
  )
  df_merged["Last Score Next Month"] = df_merged["Final Score"].apply(
      lambda x: 100.0 if x <= 60.0 else x
  )

  # Times Score 60 & Relapse
  def calc_times_60(row):
    prev_cnt = (
        int(row["Prev_Times_60"]) if pd.notna(row["Prev_Times_60"]) else 0
    )
    return prev_cnt + 1 if row["Final Score"] <= 60.0 else prev_cnt

  df_merged["Times Score 60"] = df_merged.apply(calc_times_60, axis=1)
  df_merged["Times Score 60 Next Month"] = df_merged["Times Score 60"].apply(
      lambda x: 0 if x >= 2 else int(x)
  )
  df_merged["Is_Relapse"] = df_merged["Times Score 60"] >= 2

  # Evaluation Triggers
  def evaluate_mail_triggers(row):
    reasons = []
    is_relapse = row["Is_Relapse"]
    times_60 = row["Times Score 60"]
    final_score = row["Final Score"]
    last_score = row["Last Score"]
    cat = row["Category"]
    dist = row["Distance"]
    tab_pct = row["Tablet_Use_Pct"]
    score = row["Score"]

    if is_relapse:
      reasons.append(f"Υποτροπή - {times_60}η Φορά <= 60")
    elif final_score <= 60.0:
      reasons.append("Ποινή 1ης φοράς (Βαθμολογία <= 60)")

    if last_score > 80.0 and final_score <= 80.0:
      reasons.append("Προειδοποίηση (Πτώση <= 80)")

    if dist >= 500.0 and cat in ["Yellow", "Red"]:
      reasons.append(f"Κατηγορία {cat} (Score: {score:.2f})")

    if pd.notna(tab_pct) and tab_pct < 80.0 and dist >= 500.0:
      reasons.append(f"Χαμηλή Χρήση Tablet ({tab_pct:.1f}%)")

    return (len(reasons) > 0), ", ".join(reasons)

  mail_eval = df_merged.apply(evaluate_mail_triggers, axis=1)
  df_merged["WARNING MAIL"] = [x[0] for x in mail_eval]
  df_merged["REASON"] = [x[1] for x in mail_eval]
  df_merged["TEST MAIL"] = DEFAULT_TEST
  df_merged["EMAIL"] = ""

  final_cols = [
      "Transporter",
      "Facility",
      "Distance",
      "Last Score",
      "Score",
      "Category",
      "Category Points",
      "Tablet_Use_Pct",
      "Tablet Use Points",
      "Final Score",
      "Last Score Next Month",
      "Times Score 60",
      "Times Score 60 Next Month",
      "WARNING MAIL",
      "REASON",
      "TEST MAIL",
      "EMAIL",
  ]

  df_final = df_merged[final_cols].copy()
  df_final["Distance"] = df_final["Distance"].round(1)
  df_final["Score"] = df_final["Score"].round(2)
  df_final["Tablet_Use_Pct"] = df_final["Tablet_Use_Pct"].fillna(0.0).round(1)

  # Generate Formatted Excel
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df_final.to_excel(writer, sheet_name="Scorecard", index=False)
    workbook = writer.book
    worksheet = writer.sheets["Scorecard"]
    max_row, max_col = len(df_final), len(final_cols) - 1

    fmt_center = workbook.add_format({"align": "center", "valign": "vcenter"})
    fmt_dec1 = workbook.add_format({"num_format": "#,##0.0", "align": "center"})
    fmt_dec2 = workbook.add_format({"num_format": "0.00", "align": "center"})
    fmt_pct = workbook.add_format({"num_format": '0.0"%"', "align": "center"})

    fmt_green = workbook.add_format(
        {"bg_color": "#C6EFCE", "font_color": "#006100", "align": "center"}
    )
    fmt_yellow = workbook.add_format(
        {"bg_color": "#FFEB9C", "font_color": "#9C5700", "align": "center"}
    )
    fmt_red = workbook.add_format(
        {"bg_color": "#FFC7CE", "font_color": "#9C0006", "align": "center"}
    )
    fmt_grey = workbook.add_format(
        {"bg_color": "#D9D9D9", "font_color": "#595959", "align": "center"}
    )
    fmt_orange = workbook.add_format(
        {"bg_color": "#FFC000", "font_color": "#000000", "align": "center"}
    )
    fmt_alert = workbook.add_format({
        "bg_color": "#FF0000",
        "font_color": "#FFFFFF",
        "bold": True,
        "align": "center",
    })

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, max_row, max_col)

    for i, col in enumerate(df_final.columns):
      col_len = max(df_final[col].astype(str).str.len().max(), len(col)) + 4
      if col == "Distance":
        worksheet.set_column(i, i, col_len, fmt_dec1)
      elif col == "Score":
        worksheet.set_column(i, i, col_len, fmt_dec2)
      elif col == "Tablet_Use_Pct":
        worksheet.set_column(i, i, col_len, fmt_pct)
      elif col in ["Transporter", "REASON"]:
        worksheet.set_column(i, i, col_len, None)
      else:
        worksheet.set_column(i, i, col_len, fmt_center)

    c_cat = df_final.columns.get_loc("Category")
    worksheet.conditional_format(
        1,
        c_cat,
        max_row,
        c_cat,
        {"type": "cell", "criteria": "==", "value": '"Green"', "format": fmt_green},
    )
    worksheet.conditional_format(
        1,
        c_cat,
        max_row,
        c_cat,
        {"type": "cell", "criteria": "==", "value": '"Yellow"', "format": fmt_yellow},
    )
    worksheet.conditional_format(
        1,
        c_cat,
        max_row,
        c_cat,
        {"type": "cell", "criteria": "==", "value": '"Red"', "format": fmt_red},
    )
    worksheet.conditional_format(
        1,
        c_cat,
        max_row,
        c_cat,
        {"type": "cell", "criteria": "==", "value": '"Grey"', "format": fmt_grey},
    )

    c_score = df_final.columns.get_loc("Score")
    worksheet.conditional_format(
        1,
        c_score,
        max_row,
        c_score,
        {"type": "cell", "criteria": "<=", "value": 5.0, "format": fmt_green},
    )
    worksheet.conditional_format(
        1,
        c_score,
        max_row,
        c_score,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": 5.01,
            "maximum": 8.99,
            "format": fmt_yellow,
        },
    )
    worksheet.conditional_format(
        1,
        c_score,
        max_row,
        c_score,
        {"type": "cell", "criteria": ">=", "value": 9.0, "format": fmt_red},
    )

    c_tab_pts = df_final.columns.get_loc("Tablet Use Points")
    worksheet.conditional_format(
        1,
        c_tab_pts,
        max_row,
        c_tab_pts,
        {"type": "cell", "criteria": "<", "value": 0, "format": fmt_alert},
    )

    c_fin = df_final.columns.get_loc("Final Score")
    worksheet.conditional_format(
        1,
        c_fin,
        max_row,
        c_fin,
        {"type": "cell", "criteria": "<=", "value": 60, "format": fmt_alert},
    )
    worksheet.conditional_format(
        1,
        c_fin,
        max_row,
        c_fin,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": 61,
            "maximum": 79,
            "format": fmt_orange,
        },
    )

    c_times = df_final.columns.get_loc("Times Score 60")
    worksheet.conditional_format(
        1,
        c_times,
        max_row,
        c_times,
        {"type": "cell", "criteria": "==", "value": 1, "format": fmt_orange},
    )
    worksheet.conditional_format(
        1,
        c_times,
        max_row,
        c_times,
        {"type": "cell", "criteria": ">=", "value": 2, "format": fmt_alert},
    )

    c_warn = df_final.columns.get_loc("WARNING MAIL")
    worksheet.conditional_format(
        1,
        c_warn,
        max_row,
        c_warn,
        {"type": "cell", "criteria": "==", "value": True, "format": fmt_alert},
    )

    c_reas = df_final.columns.get_loc("REASON")
    worksheet.conditional_format(
        1,
        c_reas,
        max_row,
        c_reas,
        {
            "type": "text",
            "criteria": "containing",
            "value": "Υποτροπή",
            "format": fmt_alert,
        },
    )

  excel_data = output.getvalue()
  return df_merged, df_final, excel_data


# ==============================================================================
# UI STREAMLIT
# ==============================================================================
logo_html = get_heracles_holcim_logo_html()

banner_html = (
    '<div class="holcim-banner">'
    '<div style="display: flex; justify-content: space-between; align-items:'
    ' center; flex-wrap: wrap; gap: 18px;">'
    '<div style="flex: 1; min-width: 280px;">'
    '<div class="holcim-badge">HERACLES GROUP | SAFETY EXCELLENCE</div>'
    '<div class="holcim-title">Rolling Scorecard & Safety Automation</div>'
    '<div class="holcim-subtitle">Fleet Road Safety Performance Evaluation &'
    ' Automated Notification Dispatch</div>'
    '</div>'
    f'<div class="holcim-logo-card">{logo_html}</div>'
    '</div>'
    '</div>'
)

st.markdown(banner_html, unsafe_allow_html=True)

if "processed_data" not in st.session_state:
  st.session_state.processed_data = None

tab1, tab2 = st.tabs(
    ["📊 1. Calculation & Excel Export", "📧 2. Review & Send Emails"]
)

with tab1:
  col_in1, col_in2 = st.columns(2)
  with col_in1:
    prev_file = st.file_uploader("Previous Rolling Scorecard", type=["xlsx"])
  with col_in2:
    curr_file = st.file_uploader(
        "Current Preliminary Scorecard", type=["xlsx"]
    )

  if st.button(
      "🚀 Calculate Scorecard", type="primary", use_container_width=True
  ):
    if curr_file is None:
      st.error("⚠️ Please select the Current Preliminary Scorecard!")
    else:
      with st.spinner("Processing and calculating scorecard..."):
        try:
          df_merged, df_final, excel_bytes = process_data(prev_file, curr_file)
          st.session_state.processed_data = {
              "df_merged": df_merged,
              "df_final": df_final,
              "excel_bytes": excel_bytes,
          }
          st.success("✅ Processing completed successfully!")
        except Exception as e:
          st.error(f"❌ Processing error: {e}")

  if st.session_state.processed_data is not None:
    df_final = st.session_state.processed_data["df_final"]
    excel_bytes = st.session_state.processed_data["excel_bytes"]

    total_cnt = len(df_final)
    green_cnt = (df_final["Category"] == "Green").sum()
    yellow_cnt = (df_final["Category"] == "Yellow").sum()
    red_cnt = (df_final["Category"] == "Red").sum()
    warn_cnt = (df_final["WARNING MAIL"] == True).sum()
    relapse_cnt = (df_final["Times Score 60"] >= 2).sum()

    st.markdown("---")
    st.subheader("📈 Results Summary")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total", total_cnt)
    m2.metric("🟢 Green", green_cnt)
    m3.metric("🟡 Yellow", yellow_cnt)
    m4.metric("🔴 Red", red_cnt)
    m5.metric("⚠️ Warnings", warn_cnt)
    m6.metric("🚨 Relapses", relapse_cnt)

    st.download_button(
        label="📥 Download Formatted Excel",
        data=excel_bytes,
        file_name="Rolling_Scorecard_Output.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    st.markdown("### 📋 Final Scorecard Preview")
    st.dataframe(df_final, use_container_width=True, height=450)

with tab2:
  if st.session_state.processed_data is None:
    st.info("ℹ️ Please calculate the scorecard in Tab 1 first!")
  else:
    df_merged = st.session_state.processed_data["df_merged"]
    flagged = df_merged[df_merged["WARNING MAIL"] == True]

    st.subheader(f"🔍 Transporters to Notify ({len(flagged)})")

    preview_rows = []
    for _, r in flagged.iterrows():
      p_name, subj, _ = generate_email_content(r)
      preview_rows.append({
          "Transporter": r["Transporter"],
          "Category": r["Category"],
          "Final Score": r["Final Score"],
          "Tablet %": r["Tablet_Use_Pct"],
          "Times 60": r["Times Score 60"],
          "Email Template": p_name,
          "Reason": r["REASON"],
      })
    df_preview = (
        pd.DataFrame(preview_rows)
        if preview_rows
        else pd.DataFrame(columns=["Message", "No warnings found"])
    )
    st.dataframe(df_preview, use_container_width=True)

    st.markdown("---")
    st.subheader("📤 Dispatch Options")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
      use_test_mode = st.checkbox(
          "Test Mode (Send only to VASILEIOS.NIKIFOROS@LAFARGE.COM)",
          value=True,
      )
      confirm_send = st.checkbox(
          "I confirm that I want to send the Emails", value=False
      )
      btn_send = st.button("📧 Send Emails Now", type="primary")

    with col_m2:
      status_box = st.empty()

    if btn_send:
      if not confirm_send:
        st.warning(
            "⚠️ Please confirm dispatch by checking the confirmation box"
            " first."
        )
      elif flagged.empty:
        st.info("ℹ️ No transporters found for email dispatch.")
      else:
        log_messages = []
        with st.spinner("Sending emails in progress..."):
          try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            log_messages.append(f"🔌 SMTP Connection Successful ({SENDER_EMAIL})")

            for idx, (_, row) in enumerate(flagged.iterrows(), start=1):
              p_name, subject, body = generate_email_content(row)
              recipient = (
                  DEFAULT_TEST
                  if use_test_mode
                  else (
                      row["EMAIL"]
                      if str(row["EMAIL"]).strip() != ""
                      else DEFAULT_TEST
                  )
              )

              msg = MIMEMultipart()
              msg["From"] = SENDER_EMAIL
              msg["To"] = recipient
              msg["Subject"] = Header(subject, "utf-8").encode()
              msg.attach(MIMEText(body, "plain", "utf-8"))

              server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
              log_messages.append(
                  f"[{idx}/{len(flagged)}] Sent to: {row['Transporter']}"
                  f" ({p_name}) -> {recipient}"
              )
              time.sleep(0.5)

            server.quit()
            log_messages.append("🎉 Email dispatch completed successfully!")
            status_box.success("Emails sent successfully!")
          except Exception as e:
            log_messages.append(f"❌ Error: {e}")
            status_box.error(f"Error during email dispatch: {e}")

        st.code("\n".join(log_messages))
