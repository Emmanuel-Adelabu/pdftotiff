import azure.functions as func
import os
import logging
import tempfile
import fitz
from PIL import Image
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = func.FunctionApp()

@app.blob_trigger(arg_name="blob", path="docurefattachmenttest",
                               connection="stsamd365proto01_STORAGE") 

def pdftotiffconverter(blob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {blob.name}"
                f"Blob Size: {blob.length} bytes")
    
    # Connection string and container names
    connection_string = os.getenv("stsamd365proto01_STORAGE")
    output_container_name = "docurefattachmenttesttif"
    input_container_name = "docurefattachmenttest"
    archive_container_name = "docurefattachmenttestarchive"
    clean_blob = blob.name[len("docurefattachmenttest/"):]

    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    logging.info("BlobServiceClient created successfully.")

    # Download the PDF file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(blob.read())
        temp_pdf_path = temp_pdf.name
        logging.info(f"PDF file temporarily saved to: {temp_pdf_path}")

    try:
        # Convert PDF to images using PyMuPDF
        logging.info("Starting PDF to image conversion...")
        pdf_document = fitz.open(temp_pdf_path)
        for i in range(len(pdf_document)):
            page = pdf_document.load_page(i)
            # Increase the resolution by scaling the page (e.g., 300 DPI)
            zoom = 300 / 72  # Scale factor for 300 DPI
            mat = fitz.Matrix(zoom, zoom)  # Create a scaling matrix

            pix = page.get_pixmap(matrix=mat, alpha=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tiff") as temp_tiff:
                img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                img.save(temp_tiff, format="TIFF", dpi=(300, 300), compression="tiff_deflate")
                temp_tiff_path = temp_tiff.name
                logging.info(f"TIFF file temporarily saved to: {temp_tiff_path}")

                # Upload the TIFF file to the output container
                output_blob_name = f"{os.path.splitext(clean_blob)[0]}_page_{i+1}.tiff"
                output_blob_client = blob_service_client.get_blob_client(container=output_container_name, blob=output_blob_name)
                logging.info(f"Attempting to upload {output_blob_name} to {output_container_name}...")
                with open(temp_tiff_path, "rb") as tiff_file:
                    output_blob_client.upload_blob(tiff_file)
                logging.info(f"Successfully uploaded {output_blob_name} to {output_container_name}.")

        pdf_document.close()

        input_blob_client = blob_service_client.get_blob_client(container= input_container_name, blob=clean_blob)
        archive_blob_client = blob_service_client.get_blob_client(container=archive_container_name, blob=clean_blob)

        # Copy the blob to the archive container
        logging.info(f"Moving {blob.name} to archive container {archive_container_name}...")
        archive_blob_client.start_copy_from_url(input_blob_client.url)
        logging.info(f"Successfully copied {blob.name} to {archive_container_name}.")

        input_blob_client.delete_blob()
        logging.info(f"Deleted source blob: {blob.name}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise e

    finally:
        # Clean up temporary files
        logging.info("Cleaning up temporary files...")
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        for temp_tiff_path in [f for f in os.listdir(tempfile.gettempdir()) if f.endswith(".tiff")]:
            os.remove(os.path.join(tempfile.gettempdir(), temp_tiff_path))
        logging.info("Temporary files cleaned up.")
