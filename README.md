# Nap York QR Check-in Automation

This Python script provides a simple web interface (using Gradio) to automate the guest check-in information process from Mews. It reads guest data and room access codes from CSV files, generates a personalized HTML page with essential check-in details for a specific guest, uploads this page to a web server, and generates a QR code linking directly to that guest's unique page.

<table>
<tr>
<td style="text-align:center;">
<!-- Operator View Image -->
<img src="https://dredyson.com/wp-content/uploads/2025/05/Screenshot-2025-05-08-at-3.25.56 PM.png" alt="Operator View (Gradio Interface)" width="400">
<br>
*Operator View (Gradio Interface)*
</td>
<td style="text-align:center;">
<!-- Client View Image -->
<img src="https://dredyson.com/wp-content/uploads/2025/05/Screenshot-2025-05-08-at-3.25.42 PM.png" alt="Client View (HTML Page)" width="400">
<br>
*Client View (Personalized HTML Page)*
</td>
</tr>
</table>


## Features

### Data Sync and Cleaning Script (`pull_reports.py`)

*   **Automated Report Retrieval:** Uses Selenium to log into the Mews system and navigate to the "Guests in house" report.
*   **Date Filtering:** Configures the report dates for the current day's guests.
*   **Report Export:** Triggers the export/download of the report from Mews.
*   **Data Cleaning & Structuring:** Reads the downloaded Excel report (Sheet 2) using pandas, restructuring rows to ensure each guest has all relevant details on a single row.
*   **Date Extraction:** Parses check-in and check-out dates from a specific column (currently assumes they are embedded within the 'Companions' column string).
*   **CSV Output:** Saves the cleaned and formatted data to a CSV file (`cleaned_guest_list.csv`), which serves as the input for the QR Check-in App.

### QR Check-in Web Application (`app.py`)

*   **Gradio Web Interface:** Provides an intuitive, browser-based interface for staff to trigger the process.
*   **Guest Data Integration:** Reads the `cleaned_guest_list.csv` file using pandas.
*   **Current Guest Identification:** Logic to find the currently checked-in guest for a specific bed number, handling potential overlaps based on dates.
*   **Personalized HTML Page Generation:** Dynamically creates a web page for each guest containing their name, room number, room access code, bed/locker number, and checkout date. (The HTML template is embedded within the script).
*   **Secure File Transfer:** Uploads the generated HTML page to a remote web server via SFTP (using paramiko).
*   **Local File Copy:** Also copies the generated HTML to a local web server directory (e.g., `/var/www/html`).
*   **QR Code Generation:** Creates a scannable QR code image linking to the guest's specific online check-in page. Includes error handling to generate a default QR even if guest lookup or balance check fails.
*   **Balance Alert:** Notifies the user (via a UI message and a system sound) and customizes the QR link if the guest has an outstanding balance above $1.
*   **Activity Logging:** Records each successful QR code generation event in a log file with timestamp, URL, bed number, and guest name. Logs errors as well.
*   **Integrated Wi-Fi Info:** Includes a static QR code for the Nap York Wi-Fi within the interface.
*   **Basic Authentication:** Protects the Gradio web interface with a simple username and password login.

## Prerequisites

*   Python 3.10 installed.
*   The Python libraries listed in the Dependencies section.
*   A Mews account with access to the "Guests in house" report.
*   A Chrome browser installed on the machine running the `pull_reports.py` script.
*   A web server configured to serve static files (e.g., Nginx, Apache). The `pull_reports.py` script is configured to copy files to a local web root (like `/var/www/html`) and upload via SFTP to a remote server.
*   SFTP access credentials (host, port, username, password, target directory) for the server hosting the public domain used in the QR code links (e.g., `napyorkguest.com`).
*   Appropriate directory structure on the server running the scripts and the target web server.

## Dependencies

Install the necessary libraries using pip:

```bash
pip install gradio pandas qrcode pillow paramiko pytz selenium webdriver-manager openpyxl requests beautifulsoup4
    ```
    The Gradio application will start, and its local URL (e.g., `http://127.0.0.1:7860`) and possibly an external URL will be displayed in the console output.
2.  **Access the Web UI:** Open a web browser and go to the URL provided by Gradio.
3.  **Authenticate:** Enter the configured username and password when prompted by the browser's basic authentication dialog.
4.  **Enter Bed Number:** In the web interface, type the guest's bed number (e.g., `201-1`) into the "Enter Room & Bed Number" textbox.
5.  **Submit:** Click the "submit" button.
6.  **View Results:**
    *   The script will process the request, look up the guest, check their balance, generate the HTML, copy/upload it, and create the QR code.
    *   If the guest has a balance over $1, an audible bell will sound from the server terminal, and an error message "Please take care of balance" will appear in the web interface outputs.
    *   If successful and the balance is acceptable, the generated QR code image, the public URL linking to the guest's check-in page, and the guest's name will be displayed in the output section of the web page.
7.  **Share Information:** Staff can show the displayed QR code for the guest to scan with their smartphone, or provide them with the generated QR link directly.
8.  **Review Logs:** The `activity_logs.txt` file will be updated with a record of the QR code generation event, including the timestamp, URL, bed number, and guest name.

## HTML Template

The personalized guest check-in page is generated using a fixed HTML template embedded as a large multi-line string within the `generate_html` function in the Python script. This template contains placeholders (`{}`) that are dynamically filled with the specific guest's information.

To modify the design or content of the guest page, you must directly **edit the large multi-line string inside the `generate_html` function** in the `app.py` file. Be aware that this template includes a significant amount of inline CSS and JavaScript, likely from a web design tool, and requires careful editing to avoid breaking the page layout or functionality.

## File Structure Expectation (Based on Linux Paths in Code)

The script expects data and will create output files in specific locations. **Ensure these directories exist and are writable before running the script.**

/home/ubuntu/qrCode/v2/data/cleaned_guest_list.csv
/home/ubuntu/qrCode/data/doorCodes.csv
/home/ubuntu/qrCode/v2/data/qrCode.png
/home/ubuntu/qrCode/v2/data/checkin_details.html
/home/ubuntu/qrCode/v2/data/activity_logs.txt
/home/ubuntu/qrCode/v2/webpages/ # Temporary directory where HTML is saved before local copy
/var/www/html/ # Standard local web server root - HTML is copied here by shutil.copy
[SFTP Target Directory on Remote Server] # Directory on the remote server where HTML is uploaded via SFTP

## Customization

*   **Guest Data & Door Codes:** Regularly update the CSV files (`cleaned_guest_list.csv` and `doorCodes.csv`).
*   **HTML Template:** Modify the embedded HTML string in the `generate_html` function (see **HTML Template** section above).
*   **Balance Threshold:** Change the numeric value in the balance check condition (`if html_info[5] > 1:`).
*   **Authentication:** Update the username/password in `demo.launch()`.
*   **QR Code URL:** Modify the domain or path in `qr.add_data()`.
*   **File Paths & Credentials:** Adjust file paths and SFTP details in the script as needed for your deployment.

## Licensing

This software is **proprietary and not open source**. It is provided under a commercial license.

Any use, modification, or distribution of this code requires obtaining a valid commercial license directly from Dre Dyson.

If you are interested in using this software, please contact Dre Dyson to inquire about licensing terms and costs.
