import os
import shutil
import subprocess
import streamlit as st
import xlsxwriter
import time
import re

temp_folder = r"F:\University\Ki_8\DATN\data\data_upload"

# Function to delete all .jpg and .png files in a folder
def remove_image_files(folder_path):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.lower().endswith(('.jpg', '.png')) and os.path.isfile(file_path):
                os.remove(file_path)
        # print("JPEG and PNG files deleted successfully.")
    except Exception as e:
        print(f"Error deleting JPEG and PNG files: {e}")

# Function to handle image upload, batch file execution, and temporary image deletion
def process_uploaded_files(uploaded_files):
    # Temp folder to move the uploaded images
    processed_files = []
    try:
        # Move the uploaded files to the temp folder
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            processed_files.append(file_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        
def run_bat_file():
    bat_file_path = r"F:\University\Ki_8\DATN\run.bat"
    with st.spinner("Extracting Information..."):
        subprocess.call([bat_file_path])
    st.success("Extraction complete!")
    
def clear_uploaded_images():
    # Function to clear uploaded images
    # Clearing session_state to reset uploaded files
    st.session_state.uploaded_files = [] 
    

# Title of the web app
st.title("Upload images to extract information")

# File uploader widget with multiple file selection
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    # Save uploaded files to session_state
    st.session_state.uploaded_files = uploaded_files

import os
import xlsxwriter
import re

import os
import xlsxwriter
import re

def txt_to_excel(input_dir, output_excel):
    # Create a new Excel workbook
    workbook = xlsxwriter.Workbook(output_excel)
    worksheet = workbook.add_worksheet()

    # Add a bold format for headers
    bold = workbook.add_format({'bold': True})

    # Write the header row
    header = ['Ảnh', 'Nhà cung cấp', 'Địa chỉ', 'Thời gian', 'Tổng tiền']
    for col, header_label in enumerate(header):
        worksheet.write(0, col, header_label, bold)

    # Initialize a list to store the maximum width of content in each column
    max_widths = [len(header_label) for header_label in header]

    # Iterate through each text file in the input directory
    row = 1
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as txtfile:
                # Read the contents of the text file
                lines = txtfile.readlines()
                
                # Initialize variables to store data
                name = filename.split('.')[0]
                seller_list = []
                address_list = []
                timestamp_list = []
                total_cost_list = []

                # Parse each line to extract relevant information
                for line in lines:
                    parts = line.strip().split('\t')
                    if len(parts) == 3:
                        key = parts[1].lower()
                        value = parts[2]
                        if key == 'address':
                            address_list.append(value)
                            max_widths[2] = max(max_widths[2], len(value))
                        elif key == 'seller':
                            seller_list.append(value)
                            max_widths[1] = max(max_widths[1], len(value))
                        elif key == 'timestamp':
                            timestamp_list.append(value)
                            max_widths[3] = max(max_widths[3], len(value))
                        elif key == 'total_cost' and value[0].isdigit():
                            total_cost = re.sub(r'[^\d.]', '', value)
                            total_cost_list.append(total_cost)
                            max_widths[4] = max(max_widths[4], len(total_cost))
                
                # Concatenate multiple values of 'Seller', 'Address', and 'Timestamp' with semicolons
                seller_str = ' '.join(seller_list)
                address_str = ' '.join(address_list)
                timestamp_str = ' ; '.join(timestamp_list)

                # Update the maximum width for the "Name" column
                max_widths[0] = max(max_widths[0], len(name))
                max_widths[1] = max(max_widths[0], len(seller_str))
                max_widths[2] = max(max_widths[0], len(address_str))
                max_widths[3] = max(max_widths[0], len(timestamp_str))

                # Write the data to the Excel file
                worksheet.write(row, 0, name)
                worksheet.write(row, 1, seller_str)
                worksheet.write(row, 2, address_str)
                worksheet.write(row, 3, timestamp_str)
                worksheet.write(row, 4, ' ; '.join(total_cost_list))
                
                row += 1

    # Auto-adjust column widths to fit content
    for col, width in enumerate(max_widths):
        worksheet.set_column(col, col, width + 2)

    # Close the workbook
    workbook.close()

   
# START

output_path = r"F:\University\Ki_8\DATN\output"

# Output Excel (XLSX) file path
output_excel = r'F:\University\Ki_8\DATN\export_excel_file\output.xlsx'

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False

# Check if the data_upload folder is empty and delete files if not
if os.listdir(temp_folder):
    # If the folder is not empty, remove files
    if not st.session_state.processed:
        remove_image_files(temp_folder)
        st.session_state.processed = True
else:
    # If the folder is empty
    if uploaded_files:
        # Process uploaded files
        process_uploaded_files(uploaded_files)

# If the "Process Images" button is clicked
if st.button("Process Images", key="Extracting Information"):
    if os.listdir(temp_folder):
        # If temp_folder has images, run bat file
        run_bat_file()
        
        # Path to the directory containing the text files
        input_dir = r'F:\University\Ki_8\DATN\output\key_info_extraction\data_upload\txt'

        # Convert text files to Excel (XLSX)
        txt_to_excel(input_dir, output_excel)

        # st.success("Conversion completed. Excel file saved as: " + output_excel)

        # Delete folder after export
        try:
            shutil.rmtree(output_path)
            # st.success("Output folder and its contents deleted.")
        except Exception as e:
            st.error(f"An error occurred while deleting the output folder: {e}")
            
        # Download button for the Excel file
        if os.path.exists(output_excel):
            with open(output_excel, "rb") as file:
                btn_label = "Download Excel File"
                btn_id = "download_excel"
                st.download_button(label=btn_label, data=file, file_name="Output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=btn_id)
    else:
        # If temp_folder is empty, show a message
        st.write("No images uploaded")
        
remove_image_files(temp_folder)        

