# Nap York QR Check-in Automation

This Python script provides a simple web interface (using Gradio) to automate the guest check-in information process from Mews. It reads guest data and room access codes from CSV files, generates a personalized HTML page with essential check-in details for a specific guest, uploads this page to a web server, and generates a QR code linking directly to that guest's unique page.

![Customer Facing]([URL_or_Path_to_Image](https://dredyson.com/wp-content/uploads/2025/05/Screenshot-2025-05-08-at-2.17.36%E2%80%AFPM.png)

## Features

*   **Gradio Web Interface:** Provides an intuitive, browser-based interface for staff to trigger the process.
*   **Guest Data Integration:** Reads guest lists and door codes from CSV files using the pandas library.
*   **Current Guest Identification:** Logic to find the currently checked-in guest for a specific bed number, handling potential overlaps based on dates.
*   **Personalized HTML Page Generation:** Dynamically creates a web page for each guest containing their name, room number, room access code, bed/locker number, and checkout date. (The HTML template is embedded within the script).
*   **Secure File Transfer:** Uploads the generated HTML page to a remote web server via SFTP (using paramiko).
*   **Local File Copy:** Also copies the generated HTML to a local web server directory (e.g., `/var/www/html`).
*   **QR Code Generation:** Creates a scannable QR code image linking to the guest's specific online check-in page.
*   **Balance Alert:** Notifies the user (via a UI message and a system sound) if the guest has an outstanding balance above $1.
*   **Activity Logging:** Records each successful QR code generation event in a log file with timestamp, URL, bed number, and guest name.
*   **Integrated Wi-Fi Info:** Includes a static QR code for the Nap York Wi-Fi within the interface.
*   **Basic Authentication:** Protects the Gradio web interface with a simple username and password login.

## Prerequisites

*   Python 3.x installed.
*   The Python libraries listed in the Dependencies section.
*   A CSV file containing guest details (`cleaned_guest_list.csv`) with columns like `bed_number`, `Customer`, `check_in_date`, `check_out_date`, and `Balance including preauthorizations`.
*   A CSV file containing room access codes (`doorCodes.csv`) with columns like `Room` and `Passcode`.
*   Access to a web server where the generated HTML files will be hosted and accessible via a public URL (like `napyorkguest.com`).
*   SFTP access credentials (host, port, username, password, target directory) for the server hosting the public domain.
*   Appropriate directory structure on the server running the script and the target web server.

## Dependencies

Install the necessary Python libraries using pip:

```bash
pip install gradio pandas qrcode pillow paramiko pytz

```

## Setup

1.  **Save the Code:** Save the provided Python code as a `.py` file (e.g., `napcheckin.py`).
2.  **Prepare Data Files:** Ensure your `cleaned_guest_list.csv` and `doorCodes.csv` files are correctly formatted and placed in the directories specified in the script.
3.  **Configure File Paths:**
    *   The script contains specific Linux paths. **You must edit the Python script (`napcheckin.py`)** to update the absolute paths to match your server environment for:
        *   `guest_list_path`
        *   `door_codes_path`
        *   `qrCode_path` (Output path for the temporary QR code image file)
        *   `checkin_html_path` (Output path for the temporary HTML file before copy/upload)
        *   `activity_logs_path` (Path for the activity log file)
        *   The local directory path used as the *destination* for `shutil.copy` (e.g., `/var/www/html/` in the code's copy operation).
    *   **Important:** Ensure the user account running the script has read and write permissions for these directories and files.
4.  **Configure SFTP Credentials:** **Edit the `generateQRCode` function in the Python script** to replace the placeholder SFTP details with your actual connection information (`sftp_host`, `sftp_port`, `sftp_username`, `sftp_password`, `sftp_directory`).
    *   **Security Warning:** Hardcoding credentials directly in the script is **not recommended for production environments**. Consider using environment variables or a separate configuration file for better security.
5.  **Configure Web Server:** Ensure your local web server (if using the local copy) is configured to serve files from the directory specified in the `shutil.copy` destination. Crucially, verify that the domain used in the QR code URL (e.g., `napyorkguest.com`) correctly points to the directory on the remote server specified in your SFTP configuration.
6.  **Update QR Link URL:** If you are not using `http://napyorkguest.com/`, **edit the `qr.add_data()` line in the `generateQRCode` function** to use your correct public domain or IP address. The UTM parameters can also be adjusted here.
7.  **Update Basic Auth:** **Edit the `auth` parameter in the `demo.launch()` line** near the end of the script to change the default username and password (`"Napyork", "napnow"`) used to access the Gradio interface.

## Usage

1.  **Run the Script:** Open your terminal or command prompt, navigate to the directory where you saved the script, and execute it:

    ```bash
    python napcheckin.py
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

To modify the design or content of the guest page, you must directly **edit the large multi-line string inside the `generate_html` function** in the `napcheckin.py` file. Be aware that this template includes a significant amount of inline CSS and JavaScript, likely from a web design tool, and requires careful editing to avoid breaking the page layout or functionality.

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
