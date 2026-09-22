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
        for cand in ['Times Score 60 Next Month', 'Times Score 60', 'Φορές Σκορ 60', 'Πλήθος Σκορ 60', 'Penalty Count']:
            if cand in df_prev.columns:
                prev_times_col = cand
                break

        cols_to_pull = [df_prev.columns[0], prev_score_col, 'MatchKey']
        if prev_times_col:
            cols_to_pull.append(prev_times_col)

        all_keys = pd.concat([df_prev['MatchKey'], df_curr['MatchKey']]).dropna().unique()
        all_keys = [k for k in all_keys if k != ""]
        df_merged = pd.DataFrame({'MatchKey': all_keys})

        prev_subset = df_prev[cols_to_pull].drop_duplicates(subset=['MatchKey'])
        rename_dict = {df_prev.columns[0]: 'Name_Orig_Prev', prev_score_col: 'Prev_Month_Final_Score'}
        if prev_times_col:
            rename_dict[prev_times_col] = 'Prev_Times_60'

        df_merged = df_merged.merge(prev_subset, on='MatchKey', how='left').rename(columns=rename_dict)
        if 'Prev_Times_60' not in df_merged.columns:
            df_merged['Prev_Times_60'] = df_merged['Prev_Month_Final_Score'].apply(
                lambda x: 1 if (pd.notna(x) and float(x) <= 60.0) else 0
            )
        else:
            df_merged['Prev_Times_60'] = df_merged['Prev_Times_60'].fillna(0).astype(int)
    else:
        all_keys = df_curr['MatchKey'].dropna().unique()
        df_merged = pd.DataFrame({'MatchKey': all_keys})
        df_merged['Name_Orig_Prev'] = np.nan
        df_merged['Prev_Month_Final_Score'] = np.nan
        df_merged['Prev_Times_60'] = 0

    curr_subset = df_curr[[col_trans, col_facil, 'Distance_Clean', 'Score_Clean', 'Tablet_Clean', 'MatchKey']].drop_duplicates(subset=['MatchKey'])
    df_merged = df_merged.merge(curr_subset, on='MatchKey', how='left').rename(columns={
        col_trans: 'Name_Original_Curr',
        col_facil: 'Facility',
        'Distance_Clean': 'Distance',
        'Score_Clean': 'Driving_Score',
        'Tablet_Clean': 'Tablet_Use_Pct'
    })

    df_merged['Transporter'] = df_merged['Name_Original_Curr'].fillna(df_merged['Name_Orig_Prev'])
    df_merged['Facility'] = df_merged['Facility'].fillna('-')
    df_merged['Distance'] = df_merged['Distance'].fillna(0.0)

    # 1 & 2. Χιλιόμετρα & Score
    def evaluate_driving(row):
        dist = row['Distance']
        raw_score = row['Driving_Score']
        if dist < 500.0:
            return 0.0, "Grey", 0
        if raw_score <= 5.0:
            return raw_score, "Green", 10
        elif raw_score < 9.0:
            return raw_score, "Yellow", -3
        else:
            return raw_score, "Red", -10

    eval_results = df_merged.apply(evaluate_driving, axis=1)
    df_merged['Score'] = [x[0] for x in eval_results]
    df_merged['Category'] = [x[1] for x in eval_results]
    df_merged['Category Points'] = [x[2] for x in eval_results]

    # 3. Tablet Points
    def get_tablet_points(row):
        cat = row['Category']
        pct = row['Tablet_Use_Pct']
        score = row['Score']
        if cat == "Grey" or pd.isna(pct):
            return 0
        if pct < 80.0:
            return -12 if score <= 5.0 else -2
        return 0

    df_merged['Tablet Use Points'] = df_merged.apply(get_tablet_points, axis=1)

    # 4. Last Score, Final Score & Floor/Cap
    df_merged['Last Score'] = df_merged['Prev_Month_Final_Score'].apply(
        lambda x: 100.0 if (pd.isna(x) or x <= 60.0) else float(x)
    )
    df_merged['Calculated_Score'] = df_merged['Last Score'] + df_merged['Category Points'] + df_merged['Tablet Use Points']
    df_merged['Final Score'] = df_merged['Calculated_Score'].apply(lambda x: max(60.0, min(160.0, x)))
    df_merged['Last Score Next Month'] = df_merged['Final Score'].apply(lambda x: 100.0 if x <= 60.0 else x)

    # 5. Times Score 60 & Relapse
    def calc_times_60(row):
        prev_cnt = int(row['Prev_Times_60']) if pd.notna(row['Prev_Times_60']) else 0
        return prev_cnt + 1 if row['Final Score'] <= 60.0 else prev_cnt

    df_merged['Times Score 60'] = df_merged.apply(calc_times_60, axis=1)
    df_merged['Times Score 60 Next Month'] = df_merged['Times Score 60'].apply(lambda x: 0 if x >= 2 else int(x))
    df_merged['Is_Relapse'] = df_merged['Times Score 60'] >= 2

    # Triggers
    def evaluate_mail_triggers(row):
        reasons = []
        is_relapse = row['Is_Relapse']
        times_60 = row['Times Score 60']
        final_score = row['Final Score']
        last_score = row['Last Score']
        cat = row['Category']
        dist = row['Distance']
        tab_pct = row['Tablet_Use_Pct']
        score = row['Score']

        if is_relapse:
            reasons.append(f"Υποτροπή - {times_60}η Φορά <= 60")
        elif final_score <= 60.0:
            reasons.append("Ποινή 1ης φοράς (Βαθμολογία <= 60)")

        if last_score > 80.0 and final_score <= 80.0:
            reasons.append("Προειδοποίηση (Πτώση <= 80)")

        if dist >= 500.0 and cat in ['Yellow', 'Red']:
            reasons.append(f"Κατηγορία {cat} (Score: {score:.2f})")

        if pd.notna(tab_pct) and tab_pct < 80.0 and dist >= 500.0:
            reasons.append(f"Χαμηλή Χρήση Tablet ({tab_pct:.1f}%)")

        return (len(reasons) > 0), ", ".join(reasons)

    mail_eval = df_merged.apply(evaluate_mail_triggers, axis=1)
    df_merged['WARNING MAIL'] = [x[0] for x in mail_eval]
    df_merged['REASON'] = [x[1] for x in mail_eval]
    df_merged['TEST MAIL'] = DEFAULT_TEST
    df_merged['EMAIL'] = ""

    # Τελικές στήλες (Τράμπα E & F)
    final_cols = [
        'Transporter', 'Facility', 'Distance', 'Last Score', 'Score', 'Category', 
        'Category Points', 'Tablet_Use_Pct', 'Tablet Use Points', 'Final Score', 
        'Last Score Next Month', 'Times Score 60', 'Times Score 60 Next Month', 
        'WARNING MAIL', 'REASON', 'TEST MAIL', 'EMAIL'
    ]

    df_final = df_merged[final_cols].copy()
    df_final['Distance'] = df_final['Distance'].round(1)
    df_final['Score'] = df_final['Score'].round(2)
    df_final['Tablet_Use_Pct'] = df_final['Tablet_Use_Pct'].fillna(0.0).round(1)

    # Δημιουργία Μορφοποιημένου Excel στη Μνήμη (In-Memory BytesIO)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, sheet_name='Scorecard', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Scorecard']
        max_row, max_col = len(df_final), len(final_cols) - 1

        fmt_center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        fmt_dec1   = workbook.add_format({'num_format': '#,##0.0', 'align': 'center'})
        fmt_dec2   = workbook.add_format({'num_format': '0.00', 'align': 'center'})
        fmt_pct    = workbook.add_format({'num_format': '0.0"%"', 'align': 'center'})

        fmt_green  = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'align': 'center'})
        fmt_yellow = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700', 'align': 'center'})
        fmt_red    = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'align': 'center'})
        fmt_grey   = workbook.add_format({'bg_color': '#D9D9D9', 'font_color': '#595959', 'align': 'center'})
        fmt_orange = workbook.add_format({'bg_color': '#FFC000', 'font_color': '#000000', 'align': 'center'})
        fmt_alert  = workbook.add_format({'bg_color': '#FF0000', 'font_color': '#FFFFFF', 'bold': True, 'align': 'center'})

        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, max_row, max_col)

        for i, col in enumerate(df_final.columns):
            col_len = max(df_final[col].astype(str).str.len().max(), len(col)) + 4
            if col == 'Distance':
                worksheet.set_column(i, i, col_len, fmt_dec1)
            elif col == 'Score':
                worksheet.set_column(i, i, col_len, fmt_dec2)
            elif col == 'Tablet_Use_Pct':
                worksheet.set_column(i, i, col_len, fmt_pct)
            elif col in ['Transporter', 'REASON']:
                worksheet.set_column(i, i, col_len, None)
            else:
                worksheet.set_column(i, i, col_len, fmt_center)

        c_cat = df_final.columns.get_loc('Category')
        worksheet.conditional_format(1, c_cat, max_row, c_cat, {'type': 'cell', 'criteria': '==', 'value': '"Green"', 'format': fmt_green})
        worksheet.conditional_format(1, c_cat, max_row, c_cat, {'type': 'cell', 'criteria': '==', 'value': '"Yellow"', 'format': fmt_yellow})
        worksheet.conditional_format(1, c_cat, max_row, c_cat, {'type': 'cell', 'criteria': '==', 'value': '"Red"', 'format': fmt_red})
        worksheet.conditional_format(1, c_cat, max_row, c_cat, {'type': 'cell', 'criteria': '==', 'value': '"Grey"', 'format': fmt_grey})

        c_score = df_final.columns.get_loc('Score')
        worksheet.conditional_format(1, c_score, max_row, c_score, {'type': 'cell', 'criteria': '<=', 'value': 5.0, 'format': fmt_green})
        worksheet.conditional_format(1, c_score, max_row, c_score, {'type': 'cell', 'criteria': 'between', 'minimum': 5.01, 'maximum': 8.99, 'format': fmt_yellow})
        worksheet.conditional_format(1, c_score, max_row, c_score, {'type': 'cell', 'criteria': '>=', 'value': 9.0, 'format': fmt_red})

        c_tab_pts = df_final.columns.get_loc('Tablet Use Points')
        worksheet.conditional_format(1, c_tab_pts, max_row, c_tab_pts, {'type': 'cell', 'criteria': '<', 'value': 0, 'format': fmt_alert})

        c_fin = df_final.columns.get_loc('Final Score')
        worksheet.conditional_format(1, c_fin, max_row, c_fin, {'type': 'cell', 'criteria': '<=', 'value': 60, 'format': fmt_alert})
        worksheet.conditional_format(1, c_fin, max_row, c_fin, {'type': 'cell', 'criteria': 'between', 'minimum': 61, 'maximum': 79, 'format': fmt_orange})

        c_times = df_final.columns.get_loc('Times Score 60')
        worksheet.conditional_format(1, c_times, max_row, c_times, {'type': 'cell', 'criteria': '==', 'value': 1, 'format': fmt_orange})
        worksheet.conditional_format(1, c_times, max_row, c_times, {'type': 'cell', 'criteria': '>=', 'value': 2, 'format': fmt_alert})

        c_warn = df_final.columns.get_loc('WARNING MAIL')
        worksheet.conditional_format(1, c_warn, max_row, c_warn, {'type': 'cell', 'criteria': '==', 'value': True, 'format': fmt_alert})

        c_reas = df_final.columns.get_loc('REASON')
        worksheet.conditional_format(1, c_reas, max_row, c_reas, {'type': 'text', 'criteria': 'containing', 'value': 'Υποτροπή', 'format': fmt_alert})

    excel_data = output.getvalue()
    return df_merged, df_final, excel_data

# ==============================================================================
# UI STREAMLIT
# ==============================================================================
st.title("🚚 Rolling Scorecard & Safety Email Automation")
st.markdown("### Αυτόματη Επεξεργασία Κάρτας Πόντων Οδικής Ασφάλειας & Αποστολή Ειδοποιήσεων")

if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

tab1, tab2 = st.tabs(["📊 1. Υπολογισμός & Εξαγωγή Excel", "📧 2. Έλεγχος & Αποστολή Emails"])

with tab1:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        # Νέο Label: Previous Rolling Scorecard
        prev_file = st.file_uploader("Previous Rolling Scorecard", type=["xlsx"])
    with col_in2:
        # Νέο Label: Current Preliminary Scorecard
        curr_file = st.file_uploader("Current Preliminary Scorecard", type=["xlsx"])

    if st.button("🚀 Υπολογισμός Scorecard", type="primary", use_container_width=True):
        if curr_file is None:
            st.error("⚠️ Παρακαλώ επιλέξτε το Current Preliminary Scorecard!")
        else:
            with st.spinner("Επεξεργασία και υπολογισμός scorecard..."):
                try:
                    df_merged, df_final, excel_bytes = process_data(prev_file, curr_file)
                    st.session_state.processed_data = {
                        'df_merged': df_merged,
                        'df_final': df_final,
                        'excel_bytes': excel_bytes
                    }
                    st.success("✅ Η επεξεργασία ολοκληρώθηκε με επιτυχία!")
                except Exception as e:
                    st.error(f"❌ Σφάλμα επεξεργασίας: {e}")

    if st.session_state.processed_data is not None:
        df_final = st.session_state.processed_data['df_final']
        excel_bytes = st.session_state.processed_data['excel_bytes']

        total_cnt = len(df_final)
        green_cnt = (df_final['Category'] == 'Green').sum()
        yellow_cnt = (df_final['Category'] == 'Yellow').sum()
        red_cnt = (df_final['Category'] == 'Red').sum()
        warn_cnt = (df_final['WARNING MAIL'] == True).sum()
        relapse_cnt = (df_final['Times Score 60'] >= 2).sum()

        st.markdown("---")
        st.subheader("📈 Σύνοψη Αποτελεσμάτων")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Σύνολο", total_cnt)
        m2.metric("🟢 Πράσινοι", green_cnt)
        m3.metric("🟡 Κίτρινοι", yellow_cnt)
        m4.metric("🔴 Κόκκινοι", red_cnt)
        m5.metric("⚠️ Warnings", warn_cnt)
        m6.metric("🚨 Υποτροπές", relapse_cnt)

        st.download_button(
            label="📥 Λήψη Έτοιμου Excel (Μορφοποιημένο)",
            data=excel_bytes,
            file_name="Rolling_Scorecard_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("### 📋 Προεπισκόπηση Τελικού Scorecard")
        st.dataframe(df_final, use_container_width=True, height=450)

with tab2:
    if st.session_state.processed_data is None:
        st.info("ℹ️ Πρέπει πρώτα να εκτελέσετε τον υπολογισμό στο Tab 1!")
    else:
        df_merged = st.session_state.processed_data['df_merged']
        flagged = df_merged[df_merged['WARNING MAIL'] == True]

        st.subheader(f"🔍 Μεταφορείς προς Ειδοποίηση ({len(flagged)})")

        preview_rows = []
        for _, r in flagged.iterrows():
            p_name, subj, _ = generate_email_content(r)
            preview_rows.append({
                'Μεταφορέας': r['Transporter'],
                'Κατηγορία': r['Category'],
                'Final Score': r['Final Score'],
                'Tablet %': r['Tablet_Use_Pct'],
                'Times 60': r['Times Score 60'],
                'Πρότυπο Email': p_name,
                'Αιτιολογία': r['REASON']
            })
        df_preview = pd.DataFrame(preview_rows) if preview_rows else pd.DataFrame(columns=['Μήνυμα', 'Δεν βρέθηκαν προειδοποιήσεις'])
        st.dataframe(df_preview, use_container_width=True)

        st.markdown("---")
        st.subheader("📤 Επιλογές Αποστολής")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            use_test_mode = st.checkbox("Δοκιμαστική Λειτουργία (Αποστολή στο VASILEIOS.NIKIFOROS@LAFARGE.COM)", value=True)
            confirm_send = st.checkbox("Επιβεβαιώνω ότι επιθυμώ την αποστολή των Emails", value=False)
            btn_send = st.button("📧 Αποστολή Emails Τώρα", type="primary")

        with col_m2:
            status_box = st.empty()

        if btn_send:
            if not confirm_send:
                st.warning("⚠️ Παρακαλώ επιβεβαιώστε πρώτα την αποστολή τσεκάροντας το σχετικό κουτάκι.")
            elif flagged.empty:
                st.info("ℹ️ Δεν υπάρχουν μεταφορείς για αποστολή.")
            else:
                log_messages = []
                with st.spinner("Αποστολή emails σε εξέλιξη..."):
                    try:
                        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        server.starttls()
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        log_messages.append(f"🔌 Σύνδεση SMTP Επιτυχής ({SENDER_EMAIL})")

                        for idx, (_, row) in enumerate(flagged.iterrows(), start=1):
                            p_name, subject, body = generate_email_content(row)
                            recipient = DEFAULT_TEST if use_test_mode else (row['EMAIL'] if str(row['EMAIL']).strip() != "" else DEFAULT_TEST)

                            msg = MIMEMultipart()
                            msg['From'] = SENDER_EMAIL
                            msg['To'] = recipient
                            msg['Subject'] = Header(subject, 'utf-8').encode()
                            msg.attach(MIMEText(body, 'plain', 'utf-8'))

                            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
                            log_messages.append(f"[{idx}/{len(flagged)}] Εστάλη για: {row['Transporter']} ({p_name}) -> {recipient}")
                            time.sleep(0.5)

                        server.quit()
                        log_messages.append("🎉 Η αποστολή ολοκληρώθηκε με απόλυτη επιτυχία!")
                        status_box.success("Τα emails εστάλησαν επιτυχώς!")
                    except Exception as e:
                        log_messages.append(f"❌ Σφάλμα: {e}")
                        status_box.error(f"Σφάλμα κατά την αποστολή: {e}")

                st.code("\n".join(log_messages))
