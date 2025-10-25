# 📄 Google Docs + DocTR Hybrid PDF OCR Script

This script performs Optical Character Recognition (OCR) on large PDF files by leveraging a hybrid approach:
1.  **DocTR** is used for **layout analysis** (detecting text blocks/columns).
2.  **Google Docs OCR** is used for the high-quality **text recognition** on the cropped blocks.
3.  The process chunks the PDF, performs OCR column-by-column, and reassembles the text into a single output file.

## 🚀 How to Run

The script is executed via the command line, taking the path to your PDF file as the sole argument. The output will be a text file with the same name as the PDF, but with a `.txt` extension.

### Command Example

```bash
python your_script_name.py my_document.pdf

If your input is my_document.pdf, the output will be saved as my_document.txt.

🛠️ Setup and Prerequisites

1. Python Dependencies

You'll need to install the required libraries using pip.
Bash

pip install PyPDF2 doctr google-api-python-client google-auth-oauthlib pillow numpy

2. Google Drive API Authentication

This script requires access to your Google Drive to perform the OCR via the Google Docs conversion feature.

    Enable the Google Drive API in your Google Cloud Project.

    Download a client secrets file (credentials.json) for a Desktop App OAuth 2.0 Client ID.

    Run the script once (it will fail, but prompt you for authorization) or manually run an OAuth flow to generate a token.json file.

        The script requires the scope: https://www.googleapis.com/auth/drive.

        The generated token.json file must be in the same directory as the script.

💡 Script Details

Key Features

    Hybrid OCR: Combines the excellent layout detection of DocTR with the superior text recognition quality of Google's OCR engine.

    Column/Block Support: Uses DocTR to detect text blocks and processes them individually, preserving the reading order (left-to-right columns).

    Large File Handling: Splits large PDFs into 5-page chunks to prevent processing issues and ensure stability.

    Automatic Cleanup: All uploaded files and temporary image crops are automatically deleted from Google Drive and your local filesystem upon completion.

Processing Workflow

    The input PDF is loaded and split into small PDF chunks.

    Each chunk is processed by DocTR to detect the bounding boxes for all text blocks/columns.

    Each detected block is cropped into a separate image file (PNG).

    The cropped image is uploaded to Google Drive and converted into a Google Doc (which performs the OCR).

    The Google Doc is exported as plain text and saved locally.

    The text from all blocks is collected, ordered by page and column, and written to the final .txt output file.

⚠️ Notes

    API Quota: Be mindful of Google API usage limits if processing a very large number of files.

    Rate Limiting: If you encounter errors, Google Drive may be rate-limiting your requests.

    token.json: Ensure your authentication token is kept secure and valid. If the token expires, you will need to re-authenticate.
