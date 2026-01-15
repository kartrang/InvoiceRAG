# Invoice Vector Storage

This app allows you to upload invoice PDFs, store their vector embeddings in Qdrant, view and delete stored invoices, and ask questions about your invoices using Retrieval-Augmented Generation (RAG) with OpenAI.

## Features
- Upload invoice PDFs and extract text
- Store invoice vectors in Qdrant
- View and delete stored invoices
- Ask questions about invoices (RAG Q&A)

## Requirements
- Python 3.8+
- See `requirements.txt`
- Qdrant instance (cloud or local)
- OpenAI API key

## Usage
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   streamlit run invoice_vector_storage.py
   ```
3. Fill in your Qdrant and OpenAI credentials in the sidebar.
4. Upload invoices, view/delete them, and ask questions!

## Docker
A sample Dockerfile is provided for containerized deployment.
