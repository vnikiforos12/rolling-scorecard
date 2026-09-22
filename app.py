# -*- coding: utf-8 -*-
"""
Rolling Scorecard & Email Automation - Streamlit Cloud Edition
Πλήρης εφαρμογή υπολογισμού Scorecard και αποστολής Emails (10 Πρότυπα)
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

# Ρύθμιση Σελίδας Streamlit
st.set_page_config(
    page_title="Rolling Scorecard App",
    page_icon="🚚",
    layout="wide"
)

# ==============================================================================
# ΡΥΘΜΙΣΕΙΣ EMAIL
# ==============================================================================
SENDER_EMAIL    = "VASILEIOS.NIKIFOROS@LAFARGE.COM"
# Ανάγνωση από τα Streamlit Secrets ή χρήση προεπιλογής
SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "ilfkvjxuyiffjefs")
SMTP_SERVER     = "smtp.gmail.com"
SMTP_PORT       = 587
DEFAULT_TEST    = "VASILEIOS.NIKIFOROS@LAFARGE.COM"

# ==============================================================================
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ΚΑΘΑΡΙΣΜΟΥ
# ==============================================================================
def create_match_key(text):
    if pd.isna(text): return ""
    return " ".join(str(text).split()).upper()

def clean_number(val):
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    val_str = str(val).replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def clean_percentage(val):
    if pd.isna(val): return np.nan
    if isinstance(val, str):
        val = val.replace('%', '').strip()
        try:
            val = float(val)
        except ValueError:
            return np.nan
    if 0 < val <= 1.0:
        return val * 100.0
    return float(val)

# ==============================================================================
# ΠΡΟΤΥΠΑ EMAIL (10 ΠΡΟΤΥΠΑ)
# ==============================================================================
def generate_email_content(row):
    transporter = row['Transporter']
    category = row['Category']
    last_score = row['Last Score']
    final_score = int(round(row['Final Score']))
    is_relapse = row['Is_Relapse']
    times_60 = row['Times Score 60']
    tablet_pct = row['Tablet_Use_Pct']

    subject = f'Ειδοποίηση Scorecard: "{transporter}"'

    # 1. Πρότυπο 7: Υποτροπή
    if is_relapse:
        subject = f'Ειδοποίηση Scorecard: "{transporter}" - ΑΥΣΤΗΡΗ ΠΟΙΝΗ ΥΠΟΤΡΟΠΗΣ'
        body = (
            f"Αγαπητέ Συνεργάτη,\n\n"
            f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς, "
            f"οδήγησε το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα Πόντων) εκ νέου στο {final_score}.\n\n"
            f"Διαπιστώνεται ΥΠΟΤΡΟΠΗ ({times_60}η φορά με βαθμολογία στο όριο ανάληψης διορθωτικών ενεργειών του 60).\n\n"
            f"Ως εκ τούτου, ενεργοποιείται άμεσα η διαδικασία Επιβολής Αυστηρών Διορθωτικών Κυρώσεων και Ποινών, "
            f"σύμφωνα με την Πολιτική Επιβραβεύσεων και Συνεπειών του Ομίλου.\n\n"
            f"Παρακαλούμε για τις άμεσες ενέργειές σας και τον προγραμματισμό έκτακτης συνάντησης με τη Διοίκηση και το Τμήμα Υγείας & Ασφάλειας.\n\n"
            f"Με εκτίμηση,\n"
            f"Τμήμα Υγείας & Ασφάλειας"
        )
        return "Πρότυπο 7 (Υποτροπή)", subject, body

    # 2. Πρότυπα 5 & 6: Ποινή 1ης φοράς
    if final_score <= 60:
        cat_greek = "ΚΙΤΡΙΝΗ" if category == 'Yellow' else "ΚΟΚΚΙΝΗ"
        p_name = "Πρότυπο 5 (Ποινή Κίτρινη)" if category == 'Yellow' else "Πρότυπο 6 (Ποινή Κόκκινη)"
        body = (
            f"Αγαπητέ Συνεργάτη,\n\n"
            f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
            f"Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι {final_score}.\n\n"
            f"Με την απόδοση αυτή το σκορ σας βρίσκεται ήδη κάτω από το όριο ανάληψης διορθωτικών ενεργειών του 60. \n\n"
            f"Ως εκ τούτου, θα σας επιβληθεί η αντίστοιχη ποινή βάσει της Πολιτικής Επιβραβεύσεων και Συνεπειών του Ομίλου. \n\n"
            f"Με εκτίμηση,\n"
            f"Τμήμα Υγείας & Ασφάλειας"
        )
        return p_name, subject, body

    # 3. Πρότυπα 3 & 4: Πτώση κάτω από 80
    if last_score > 80.0 and final_score <= 80:
        cat_greek = "ΚΙΤΡΙΝΗ" if category == 'Yellow' else "ΚΟΚΚΙΝΗ"
        p_name = "Πρότυπο 3 (Πτώση Κίτρινη)" if category == 'Yellow' else "Πρότυπο 4 (Πτώση Κόκκινη)"
        body = (
            f"Αγαπητέ Συνεργάτη,\n\n"
            f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
            f"Το σκορ της συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα Πόντων) είναι {final_score}.\n\n"
            f"Με την απόδοση αυτή το σκορ σας βρίσκεται ήδη κάτω από το προειδοποιητικό όριο του 80.\n\n"
            f"Ως εκ τούτου, σας εφιστούμε την προσοχή για την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας, με γνώμονα πάντα την Υγεία & Ασφάλεια. \n\n"
            f"Με εκτίμηση,\n"
            f"Τμήμα Υγείας & Ασφάλειας"
        )
        return p_name, subject, body

    # 4. Πρότυπα 9, 10 & 8: Tablet < 80%
    if pd.notna(tablet_pct) and tablet_pct < 80.0:
        if category == 'Yellow':
            body = (
                f"Αγαπητέ Συνεργάτη,\n\n"
                f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς είναι  ΚΙΤΡΙΝΗ.\n\n"
                f"Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι {final_score}.\n\n"
                f"Επίσης, αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του 80%. "
                f"Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας.\n\n"
                f"Ως εκ τούτου θα σας αφαιρεθούν 5 πόντοι από τη βαθμολογία της Συνολικής Κάρτας Πόντων.\n\n"
                f"Με εκτίμηση,\n"
                f"Τμήμα Υγείας & Ασφάλειας"
            )
            return "Πρότυπο 9 (Tablet < 80% & Κίτρινος)", subject, body

        elif category == 'Red':
            body = (
                f"Αγαπητέ Συνεργάτη,\n\n"
                f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς είναι  ΚΟΚΚΙΝΗ.\n\n"
                f"Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι {final_score}.\n\n"
                f"Επίσης, αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του 80%. "
                f"Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας.\n\n"
                f"Ως εκ τούτου θα σας αφαιρεθούν 12 πόντοι από τη βαθμολογία της Συνολικής Κάρτας Πόντων.\n\n"
                f"Με εκτίμηση,\n"
                f"Τμήμα Υγείας & Ασφάλειας"
            )
            return "Πρότυπο 10 (Tablet < 80% & Κόκκινος)", subject, body

        else:
            body = (
                f"Αγαπητέ Συνεργάτη,\n\n"
                f"Αυτό το μήνα καταγράφηκε χρήση tablet κάτω από το όριο του 80%. "
                f"Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας.\n\n"
                f"Ως εκ τούτου θα σας αφαιρεθούν 2 πόντοι από τη βαθμολογία της Συνολικής Κάρτας Πόντων.\n\n"
                f"Με εκτίμηση,\n"
                f"Τμήμα Υγείας & Ασφάλειας"
            )
            return "Πρότυπο 8 (Tablet < 80% Γενικό)", subject, body

    # 5. Πρότυπα 1 & 2: Γενική ενημέρωση
    if category in ['Yellow', 'Red']:
        cat_greek = "ΚΙΤΡΙΝΗ" if category == 'Yellow' else "ΚΟΚΚΙΝΗ"
        p_name = "Πρότυπο 1 (Γενικό Κίτρινο)" if category == 'Yellow' else "Πρότυπο 2 (Γενικό Κόκκινο)"
        body = (
            f"Αγαπητέ Συνεργάτη,\n\n"
            f"Η απόδοσή σας στο σύστημα της Μηνιαίας Κάρτας Πόντων, που καταγράφει τις επιδόσεις οδικής συμπεριφοράς είναι  {cat_greek}.\n\n"
            f"Το σκορ της Συνολικής Οδικής Συμπεριφοράς (Συνολική Κάρτα πόντων) είναι {final_score}.\n\n"
            f"Παρακαλούμε, όπως προβείτε στην ενημέρωση των οδηγών σας με σκοπό την άμεση βελτίωση της απόδοσής σας αναφορικά με την οδική συμπεριφορά του στόλου σας.\n\n"
            f"Με εκτίμηση,\n"
            f"Τμήμα Υγείας & Ασφάλειας"
        )
        return p_name, subject, body

    return "Ενημερωτικό", subject, f"Ενημέρωση Scorecard για τον μεταφορέα {transporter}. Τρέχον Σκορ: {final_score}."

# ==============================================================================
# ΕΠΕΞΕΡΓΑΣΙΑ SCORECARD & ΔΗΜΙΟΥΡΓΙΑ EXCEL
# ==============================================================================
def process_data(df_prev_file, df_curr_file):
    df_curr = pd.read_excel(df_curr_file)
    
    col_trans = 'Μεταφορέας' if 'Μεταφορέας' in df_curr.columns else df_curr.columns[1]
    col_facil = 'Εγκατάσταση' if 'Εγκατάσταση' in df_curr.columns else df_curr.columns[0]
    col_dist  = 'Απόσταση' if 'Απόσταση' in df_curr.columns else 'Distance'
    col_score = 'Score' if 'Score' in df_curr.columns else 'Score'
    col_tab   = 'Χρήση Tablet' if 'Χρήση Tablet' in df_curr.columns else 'Tablet'

    df_curr['MatchKey'] = df_curr[col_trans].apply(create_match_key)
    df_curr['Distance_Clean'] = df_curr[col_dist].apply(clean_number)
    df_curr['Score_Clean'] = df_curr[col_score].apply(clean_number)
    df_curr['Tablet_Clean'] = df_curr[col_tab].apply(clean_percentage)

    if df_prev_file is not None:
        df_prev = pd.read_excel(df_prev_file)
        df_prev = df_prev.drop(columns=['MatchKey'], errors='ignore')
        trans_col_prev = 'Transporter' if 'Transporter' in df_prev.columns else df_prev.columns[0]
        df_prev['MatchKey'] = df_prev[trans_col_prev].apply(create_match_key)

        if 'Final Score' in df_prev.columns:
            prev_score_col = 'Final Score'
        elif 'Last Score Next Month' in df_prev.columns:
            prev_score_col = 'Last Score Next Month'
        else:
            prev_score_col = df_prev.columns[8]

        prev_times_col = None
        for cand in ['Times Score 60 Next Mont
