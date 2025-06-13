import streamlit as st
import os
import csv
from datetime import datetime

st.title("CSV Combiner App")

folder = st.text_input("Enter the folder path containing CSV files:", "Files/outs")

if st.button("Combine CSV Files"):
    folder = folder.replace("\\", "/")
    if not os.path.isdir(folder):
        st.error(f"Folder not found: {folder}")
    else:
        csv_files = [f for f in os.listdir(folder) if f.lower().endswith('.csv')]
        if not csv_files:
            st.warning("No CSV files found in the folder.")
        else:
            combined_rows = []
            headers = ["file_name"]
            header_set = set(headers)
            for file in csv_files:
                file_path = os.path.join(folder, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Update headers if new columns are found
                        for key in row.keys():
                            if key not in header_set:
                                headers.append(key)
                                header_set.add(key)
                        # Add file_name to row
                        row_with_file = {"file_name": file}
                        row_with_file.update(row)
                        combined_rows.append(row_with_file)
            # Fill missing columns with ''
            for row in combined_rows:
                for h in headers:
                    if h not in row:
                        row[h] = ''
            # Write combined CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            out_path = os.path.join(folder, f'combined_{timestamp}.csv')
            with open(out_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(combined_rows)
            st.success(f"Combined CSV saved to: {out_path}")
            st.write(f"Headers: {headers}")
            st.write(f"Total rows: {len(combined_rows)}")
