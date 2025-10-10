# ============================================================
# EUR-Lex CELEX Downloader
# ------------------------------------------------------------

# What this script does:
# 1) Reads a CSV of proposals with a column named 'CELEX'.
#    A CELEX number is the stable identifier used by EUR-Lex for EU laws and related documents.
# 2) For each unique CELEX code (for example, '32019R0947'), it tries:
#    a) to fetch and save the HTML version of the act
#    b) if HTML is not available, to fetch the PDF version
#    Note: if a document is unavailable in one format, it may still exist in another.
#    c) if PDF is not available, to fetch the DOC/DOCX version
# 3) Saves any retrieved files to ../Data/Regulations
# 4) Records CELEX codes with no HTML (for diagnostics) in ../Data/not_found_celex_numbers.csv

# %%
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep

# %%
# Create the directory if it doesn't exist
output_dir = '../Data/Regulations'
os.makedirs(output_dir, exist_ok=True)

# List to store CELEX numbers for which the document does not exist
not_found_celex_numbers = []

# Function to download the HTML content for each CELEX number
def download_celex_html(celex_number, iteration):
    file_path_html = os.path.join(output_dir, f'{celex_number}.html')
    url_html = f'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:{celex_number}'

    try:
        response = requests.get(url_html)
        response.raise_for_status()  # Check if the request was successful
        html_content = response.text

        # Check if the "document does not exist" message is present in the HTML version
        if 'The requested document does not exist.' in html_content:
            print(f"[{iteration}/{total_celex_codes}] {celex_number} document does not exist in HTML.")
            not_found_celex_numbers.append(celex_number)
            return False

        # Save the HTML content if the document exists
        with open(file_path_html, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"[{iteration}/{total_celex_codes}] {celex_number} HTML document downloaded and saved.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[{iteration}/{total_celex_codes}] Failed to download HTML for {celex_number}. Error: {e}")
        not_found_celex_numbers.append(celex_number)
        return False

def download_celex_pdf(celex_number, iteration):
    pdf_found = False  # Flag to check if any PDF file was found
    url_pdf = f'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:{celex_number}'

    try:
        response_pdf = requests.get(url_pdf, stream=True)
        response_pdf.raise_for_status()

        # Check the content type of the response to determine if it's a direct file download
        content_type = response_pdf.headers.get('Content-Type', '')

        # If the content is a PDF file (based on the MIME type), save it directly
        if 'application/pdf' in content_type:
            file_path = os.path.join(output_dir, f'{celex_number}.pdf')
            download_and_save_file(response_pdf, file_path)
            print(f"[{iteration}/{total_celex_codes}] {celex_number} PDF file downloaded directly and saved.")
            pdf_found = True

        else:
            # Otherwise, treat the response as HTML and parse for PDF links
            soup = BeautifulSoup(response_pdf.text, 'html.parser')
            act_link = soup.find('a', href=lambda href: href and 'DOC_1' in href and 'format=PDF' in href)
            annex_link = soup.find('a', href=lambda href: href and 'DOC_2' in href and 'format=PDF' in href)

            if act_link:
                # Construct the full URL for the main act
                act_url = f"https://eur-lex.europa.eu{act_link['href'].replace('./../../../../', '/')}"
                download_and_save_file_from_url(act_url, os.path.join(output_dir, f'{celex_number}.pdf'))
                print(f"[{iteration}/{total_celex_codes}] {celex_number} main act (PDF) downloaded and saved.")
                pdf_found = True

            if annex_link:
                # Construct the full URL for the annex
                annex_url = f"https://eur-lex.europa.eu{annex_link['href'].replace('./../../../../', '/')}"
                download_and_save_file_from_url(annex_url, os.path.join(output_dir, f'{celex_number}_Annex.pdf'))
                print(f"[{iteration}/{total_celex_codes}] {celex_number} annex (PDF) downloaded and saved.")
                pdf_found = True

        return pdf_found

    except requests.exceptions.RequestException as e:
        print(f"[{iteration}/{total_celex_codes}] Failed to retrieve PDF page for {celex_number}. Error: {e}")
        return False


# Function to download DOC or DOCX content for each CELEX number
def download_celex_doc(celex_number, iteration):
    doc_found = False  # Flag to check if any DOC file was found
    url_doc = f'https://eur-lex.europa.eu/legal-content/EN/TXT/DOC/?uri=CELEX:{celex_number}'

    try:
        response_doc = requests.get(url_doc, stream=True)
        response_doc.raise_for_status()

        # Check the content type of the response to determine if it's a direct file download
        content_type = response_doc.headers.get('Content-Type', '')

        # If the content is a DOC file (based on the MIME type), save it directly
        if 'application/msword' in content_type or 'application/vnd.openxmlformats-officedocument' in content_type:
            file_extension = get_file_extension(content_type)
            file_path = os.path.join(output_dir, f'{celex_number}{file_extension}')
            download_and_save_file(response_doc, file_path)
            print(f"[{iteration}/{total_celex_codes}] {celex_number} DOC file downloaded directly and saved.")
            return True

        else:
            # Otherwise, treat the response as HTML and parse for DOC_1 and DOC_2 links
            soup = BeautifulSoup(response_doc.text, 'html.parser')
            act_link = soup.find('a', href=lambda href: href and 'DOC_1' in href)
            annex_link = soup.find('a', href=lambda href: href and 'DOC_2' in href)

            if act_link:
                # Download and save the main act
                act_url = f"https://eur-lex.europa.eu{act_link['href']}"
                download_and_save_file_from_url(act_url, os.path.join(output_dir, f'{celex_number}.doc'))
                print(f"[{iteration}/{total_celex_codes}] {celex_number} main act (DOC) downloaded and saved.")
                doc_found = True

            if annex_link:
                # Download and save the annex
                annex_url = f"https://eur-lex.europa.eu{annex_link['href']}"
                download_and_save_file_from_url(annex_url, os.path.join(output_dir, f'{celex_number}_Annex.doc'))
                print(f"[{iteration}/{total_celex_codes}] {celex_number} annex (DOC) downloaded and saved.")
                doc_found = True

        return doc_found

    except requests.exceptions.RequestException as e:
        print(f"[{iteration}/{total_celex_codes}] Failed to retrieve DOC page for {celex_number}. Error: {e}")
        return False

# Helper function to download and save a file from a direct response
def download_and_save_file(response, file_path):
    try:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except Exception as e:
        print(f"Failed to save file: {file_path}. Error: {e}")

# Helper function to download and save a file from a URL
def download_and_save_file_from_url(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download file from {url}. Error: {e}")

# Helper function to get the file extension from the Content-Type header
def get_file_extension(content_type):
    if 'application/msword' in content_type:
        return '.doc'
    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
        return '.docx'
    return '.doc'  # Default to .doc if unsure



# %%
# Load a webscrapped dataset
proposals_load = pd.read_csv('../Data/proposals_processed.csv')

#Get unique CELEX numbers
unique_celex_numbers = proposals_load['CELEX'].unique()

#Show total number of unique CELEX codes
total_celex_codes = len(unique_celex_numbers)
print(f"Total number of unique CELEX codes: {total_celex_codes}")

# %%
# Iterate over the provided CELEX numbers
for i, celex in enumerate(unique_celex_numbers, start=1):
    # First try downloading the HTML
    if not download_celex_html(celex, i):
        # If HTML doesn't exist, try downloading the PDF
        if not download_celex_pdf(celex, i):
            # If PDF doesn't exist, try downloading the DOC
            download_celex_doc(celex, i)

    sleep(1)  # To avoid overwhelming the server, add a delay between requests.

# Save the CELEX numbers for which the document does not exist as a DataFrame
if not_found_celex_numbers:
    not_found_df = pd.DataFrame(not_found_celex_numbers, columns=['CELEX'])
    not_found_df.to_csv('../Data/not_found_celex_numbers.csv', index=False)
    print(f"\nSaved the list of CELEX numbers for which the document does not exist to 'not_found_celex_numbers.csv'.")


