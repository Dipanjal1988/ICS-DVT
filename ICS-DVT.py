import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

from fpdf import FPDF

import io



# CONFIG

PASSWORD = "icsdvt2025"

LOGO_URL = "https://raw.github.com/Dipanjal1988/ICS-DVT/blob/main/Infinite_Computer_Solutions_Logo.jpg"



# SESSION STATE

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False

if "password_attempt" not in st.session_state:

    st.session_state.password_attempt = ""



# LOGIN PAGE

if not st.session_state.authenticated:

    col1, col2 = st.columns([6, 1])

    with col1:

        st.title("ICS Data Validation Tool")

    with col2:

        st.title(":rocket:")



    with st.form("login_form"):

        password_input = st.text_input("Enter Password:", type="password")

        submit_button = st.form_submit_button("Submit")



        if submit_button:

            if password_input == PASSWORD:

                st.session_state.authenticated = True


            else:

                st.session_state.password_attempt = "Invalid"



    if st.session_state.password_attempt == "Invalid":

        st.error("Incorrect password. Please try again.")

    st.stop()



# MAIN APP HEADER

col1, col2 = st.columns([6, 1])

with col1:

    st.title("ICS Data Validation Tool")

with col2:

    st.title(":rocket:")



# FILE UPLOAD

file1 = st.file_uploader("Upload Source CSV", type=["csv"])

file2 = st.file_uploader("Upload Target CSV", type=["csv"])



if file1 and file2:

    df1 = pd.read_csv(file1)

    df2 = pd.read_csv(file2)



    st.subheader("Validation Summary")

    details = {}



    # Schema Validation

    schema_match = df1.columns.equals(df2.columns)

    schema_diff = list(set(df1.columns).symmetric_difference(set(df2.columns)))

    schema_mismatch_pct = 0 if schema_match else round(len(schema_diff) / max(len(df1.columns), 1) * 100, 2)

    st.markdown(f"- **Schema Mismatch**: {schema_mismatch_pct}%")

    details["Schema Details"] = {

        "Matching Columns Count": len(set(df1.columns).intersection(set(df2.columns))),

        "Mismatched Columns Count": len(schema_diff),

        "Mismatched Columns List": schema_diff if schema_diff else ["No schema mismatch"]

    }



    # Row Count Validation

    row_diff = abs(df1.shape[0] - df2.shape[0])

    row_mismatch_pct = round(row_diff / max(df1.shape[0], 1) * 100, 2)

    missing_in_target = pd.concat([df1, df2, df2]).drop_duplicates(keep=False)

    st.markdown(f"- **Row Count Difference**: {row_mismatch_pct}%")

    details["Row Details"] = {

        "Source Rows": df1.shape[0],

        "Target Rows": df2.shape[0],

        "Sample Missing Rows (in Target)": missing_in_target.head(5).to_dict(orient="records")

    }



    # Data Match Validation

    primary_key = df1.iloc[0,0]



    # Inner join on primary key

    df1_indexed = df1.set_index(primary_key)

    df2_indexed = df2.set_index(primary_key)



    # Keep only rows with matching keys

    common_keys = df1_indexed.index.intersection(df2_indexed.index)

    df1_common = df1_indexed.loc[common_keys].sort_index()

    df2_common = df2_indexed.loc[common_keys].sort_index()



    # Align columns

    common_cols = df1_common.columns.intersection(df2_common.columns)

    df1_final = df1_common[common_cols]
 
    df2_final = df2_common[common_cols]



   # Compare values

    comparison_result = df1_final.eq(df2_final)

    total_cells = comparison_result.size

    mismatched_cells = total_cells - comparison_result.values.sum()

    data_diff_pct = round((mismatched_cells / max(total_cells, 1)) * 100, 2)



    st.markdown(f"**Data Mismatch (Cell-wise, Key-based)**: {mismatch_pct}%")



    # Optional: show first 5 mismatches

    diff_mask = ~comparison_result

    mismatch_preview = df1_final[diff_mask].dropna(how='all').head(5)



    details["Data Details"] = {

    "Total Compared Rows": len(common_keys),

    "Compared Columns": list(common_cols),

    "Cell-wise Mismatch %": mismatch_pct,

    "Sample Mismatched Cells": mismatch_preview.to_dict(orient="index")

}
  
    # Null Check

    nulls_source = df1.isnull().sum().sum()

    nulls_target = df2.isnull().sum().sum()

    total_cells = df1.size + df2.size

    null_pct = round((nulls_source + nulls_target) / max(total_cells, 1) * 100, 2)

    st.markdown(f"- **Null Values**: {null_pct}%")

    details["Null Details"] = {

        "Source Nulls": int(nulls_source),

        "Target Nulls": int(nulls_target)

    }



    # Duplicate Check

    dups_source = df1.duplicated().sum()

    dups_target = df2.duplicated().sum()

    total_records = len(df1) + len(df2)

    dup_pct = round((dups_source + dups_target) / max(total_records, 1) * 100, 2)

    st.markdown(f"- **Duplicate Records**: {dup_pct}%")

    details["Duplicate Details"] = {

        "Source Duplicates": int(dups_source),

        "Target Duplicates": int(dups_target)

    }



    # Assistant Insights

    st.subheader("AI Assistant Insights")

    with st.expander("Click for observations and suggestions"):

        if schema_mismatch_pct > 0:

            st.markdown(f"- Schema mismatch in columns: `{', '.join(schema_diff)}`")

        if row_mismatch_pct > 0:

            st.markdown("- Row count difference suggests filtering or load issues.")

        if data_diff_pct > 0:

         st.markdown("- Row-level data mismatch found. Verify joins and transformations.")

        if null_pct > 0:

            st.markdown("- Nulls detected. Suggest `.fillna()` or data cleanup.")

        if dup_pct > 0:

            st.markdown("- Duplicates found. Recommend `.drop_duplicates()`.")

        if all(pct == 0 for pct in [schema_mismatch_pct, row_mismatch_pct, null_pct, dup_pct]):

            st.markdown("All validations passed successfully!")



    # Detailed Validation Views

    st.subheader("Detailed Validation Views")

    for key, val in details.items():

        with st.expander(key):

            for subkey, subval in val.items():

                st.markdown(f"**{subkey}:**")

                if isinstance(subval, list):

                    for item in subval:

                        st.json(item)

                else:

                    st.write(subval)



    # Visual Diagnostics

    st.subheader("Visual Diagnostics")

    if st.button("Show Null Heatmaps"):

        st.markdown("**Null Heatmap - Source**")

        fig1, ax1 = plt.subplots()

        sns.heatmap(df1.isnull(), cbar=False, ax=ax1)

        st.pyplot(fig1)



        st.markdown("**Null Heatmap - Target**")

        fig2, ax2 = plt.subplots()

        sns.heatmap(df2.isnull(), cbar=False, ax=ax2)

        st.pyplot(fig2)



    # Export Summary

    st.subheader("Export Summary")

    summary_df = pd.DataFrame({

        "Check": ["Schema", "Row Count", "Data Match", "Nulls", "Duplicates"],

        "Mismatch %": [schema_mismatch_pct, row_mismatch_pct, data_diff_pct, null_pct, dup_pct]

    })



    # CSV Export

    expanded_rows = []

    for section, data in details.items():

        for key, value in data.items():

            expanded_rows.append({"Section": section, "Detail": key, "Value": str(value)})

    detail_df = pd.DataFrame(expanded_rows)



    csv_buf = io.StringIO()

    detail_df.to_csv(csv_buf, index=False)

    st.download_button("Download CSV", csv_buf.getvalue(), "validation_detailed_report.csv", "text/csv")



    # PDF Export (fixed indentation on wrapped lines)

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=14)

    pdf.cell(190, 10, txt="ICS Data Validation Report", ln=True, align='C')

    pdf.ln(5)



    pdf.set_font("Arial", size=12)

    for idx, row in summary_df.iterrows():

        pdf.set_text_color(0, 0, 128)

        pdf.set_x(10)

        pdf.cell(190, 10, txt=f"{row['Check']} Check", ln=True)

        pdf.set_text_color(0, 0, 0)

        pdf.set_x(10)

        pdf.multi_cell(180, 8, txt=f"Mismatch %: {row['Mismatch %']}%")

        pdf.ln(1)



    pdf.set_font("Arial", size=12)

    for section, data in details.items():

        pdf.set_text_color(0, 0, 128)

        pdf.set_x(10)

        pdf.cell(190, 10, txt=section, ln=True)

        pdf.set_text_color(0, 0, 0)

        pdf.set_font("Arial", size=10)

        for key, val in data.items():

            text = f"{key}: {str(val)}"

            lines = [text[i:i+100] for i in range(0, len(text), 100)]

            for line in lines:

                pdf.set_x(15)

                pdf.multi_cell(175, 7, txt=line)

            pdf.ln(1)



    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    st.download_button("Download PDF", pdf_bytes, "validation_detailed_report.pdf", "application/pdf")
