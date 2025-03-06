# PDF to TIFF Converter using Azure Functions

This project is an Azure Function that automatically converts PDF files to TIFF images when they are uploaded to a specified Azure Blob Storage container. The converted TIFF files are then saved to another blob container. The original PDF files are archived after conversion.

## Features

- **Blob Trigger:** Activates when a PDF file is uploaded to the input container.
- **PDF to TIFF Conversion:** Converts PDF pages to TIFF format with 300 DPI resolution using PyMuPDF and PIL.
- **Blob Management:**
  - Saves TIFF files to a specified output container.
  - Moves the original PDF files to an archive container.
  - Cleans up temporary files after processing.

---

## Project Structure

- **Function:**
  - Trigger: Azure Blob Storage (`docurefattachmenttest` container).
  - Output: TIFF files to `docurefattachmenttesttif` container.
  - Archive: Moves original PDFs to `docurefattachmenttestarchive` container.

---

## Requirements

- **Python 3.8+**
- **Azure Functions Core Tools**
- **Azure Storage Account**
- **Azure Blob Containers:**
  - `docurefattachmenttest` (Input container for PDFs)
  - `docurefattachmenttesttif` (Output container for TIFFs)
  - `docurefattachmenttestarchive` (Archive for original PDFs)

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Emmanuel-Adelabu/pdftotiff.git
   cd Emmanuel-Adelabu/pdftotiff
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:** Create a `.env` file and add your Azure Storage connection string:

   ```env
   stsamd365proto01_STORAGE=<your-azure-storage-connection-string>
   ```

---

## How It Works

1. **Upload a PDF:**

   - Place a PDF file in the `docurefattachmenttest` container.

2. **Trigger Activation:**

   - The function triggers, downloads the PDF, and starts the conversion.

3. **PDF to TIFF Conversion:**

   - Converts each PDF page to a TIFF image (300 DPI).
   - Saves the TIFF files in `docurefattachmenttesttif` container.

4. **Archiving:**

   - Moves the original PDF to the `docurefattachmenttestarchive` container.

5. **Cleanup:**

   - Deletes temporary files created during the process.

---

## License

This project is licensed under the MIT License.
