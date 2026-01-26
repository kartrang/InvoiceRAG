"""
Date stamp: 2026-01-26
"""
import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
import os
import requests

import datetime

st.set_page_config(page_title="Invoice Vector Storage", layout="wide")

css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.css")
if os.path.exists(css_path):
	with open(css_path) as f:
		st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Display the current date and day at the top of the UI
today = datetime.date.today()
current_date = today.strftime("%B %d, %Y")
current_day = today.strftime("%A")
st.markdown(f"<div style='text-align:right; color:gray; font-size:0.9em;'>Date: {current_date} ({current_day})</div>", unsafe_allow_html=True)
# Display the selected day below the date (if entered)
if invoice_day:
	st.markdown(f"<div style='text-align:right; color:gray; font-size:0.9em;'>Selected Day: {invoice_day}</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='sidebar-title'>⚙️ Qdrant Configuration</div>", unsafe_allow_html=True)
qdrant_url = st.sidebar.text_input("Qdrant URL")
qdrant_api_key = st.sidebar.text_input("Qdrant API Key", type="password")
collection_name = st.sidebar.text_input("Collection Name", value="invoices")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

st.markdown("<h1>📄 Invoice Upload & Vector Storage</h1>", unsafe_allow_html=True)

account_name = st.text_input("Account Name")
account_number = st.text_input("Account Number")
invoice_date = st.date_input("Invoice Date")
invoice_day = st.text_input("Day (e.g. Monday)")
invoice_file = st.file_uploader("Upload Invoice (PDF only)", type=["pdf"])

def extract_text_from_pdf(pdf_file):
	from PyPDF2 import PdfReader
	reader = PdfReader(pdf_file)
	text = ""
	for page in reader.pages:
		text += page.extract_text() or ""
	return text

def get_embedding(text, openai_api_key):
	url = "https://api.openai.com/v1/embeddings"
	headers = {
		"Authorization": f"Bearer {openai_api_key}",
		"Content-Type": "application/json"
	}
	data = {
		"input": text,
		"model": "text-embedding-ada-002"
	}
	response = requests.post(url, headers=headers, json=data)
	response.raise_for_status()
	embedding = response.json()["data"][0]["embedding"]
	return embedding

if st.button("🚀 Store Invoice in Qdrant"):
	if not all([account_name, account_number, invoice_date, invoice_day, invoice_file, qdrant_url, qdrant_api_key, openai_api_key]):
		st.error("All fields and credentials are required.")
	else:
		client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
		existing = [c.name for c in client.get_collections().collections]
		if collection_name not in existing:
			client.create_collection(
				collection_name=collection_name,
				vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
			)
		text = extract_text_from_pdf(invoice_file)
		embedding = get_embedding(text, openai_api_key)
		point = PointStruct(
			id=str(uuid.uuid4()),
			vector=embedding,
			payload={
				"account_name": account_name,
				"account_number": account_number,
				"invoice_date": invoice_date.isoformat(),
				"invoice_day": invoice_day,
				"file_name": invoice_file.name,
				"content": text[:3000]
			}
		)
		client.upsert(collection_name=collection_name, points=[point])
		st.success("Invoice stored in Qdrant!")

# --- Always Display Table of Stored Invoices ---
if all([qdrant_url, qdrant_api_key, collection_name]):
	try:
		client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
		# Get all points (invoices) from the collection
		points = client.scroll(collection_name=collection_name, limit=100)[0]
		if points:
			import pandas as pd
			st.markdown("<h2>Stored Invoices</h2>", unsafe_allow_html=True)
			data = []
			ids = []
			for p in points:
				payload = p.payload
				data.append({
					"File Name": payload.get("file_name", ""),
					"Account Name": payload.get("account_name", ""),
					"Account Number": payload.get("account_number", ""),
					"Invoice Date": payload.get("invoice_date", ""),
				})
				ids.append(p.id)
			df = pd.DataFrame(data)
			# Render table headers
			header_cols = st.columns([2,2,2,2,2,1])
			header_cols[0].markdown("**File Name**")
			header_cols[1].markdown("**Account Name**")
			header_cols[2].markdown("**Account Number**")
			header_cols[3].markdown("**Invoice Date**")
			header_cols[4].markdown("**Day**")
			header_cols[5].markdown("**Action**")
			# Add Day to DataFrame
			df["Day"] = [payload.get("invoice_day", "") for payload in points]
			# Render each row with a delete button
			for i, row in df.iterrows():
				cols = st.columns([2,2,2,2,2,1])
				cols[0].write(row["File Name"])
				cols[1].write(row["Account Name"])
				cols[2].write(row["Account Number"])
				cols[3].write(row["Invoice Date"])
				cols[4].write(row["Day"])
				if cols[5].button("Delete", key=f"delete_{ids[i]}"):
					try:
						client.delete(collection_name=collection_name, points_selector={"points": [ids[i]]})
						st.success(f"Deleted invoice: {row['File Name']}")
						st.experimental_rerun()
					except Exception as e:
						st.error(f"Failed to delete: {e}")
		else:
			st.info("No invoices found in the collection.")
	except Exception as e:
		st.warning(f"Could not fetch invoices: {e}")

# --- RAG: Ask Questions about Invoices ---
st.markdown("<h2>🔎 Ask Questions about Invoices (RAG)</h2>", unsafe_allow_html=True)
question = st.text_input("Ask a question about your invoices:")
if question and all([qdrant_url, qdrant_api_key, openai_api_key, collection_name]):
	try:
		# Get embedding for the question
		question_embedding = get_embedding(question, openai_api_key)
		# Search Qdrant for most relevant invoice(s)
		search_result = client.search(
			collection_name=collection_name,
			query_vector=question_embedding,
			limit=3
		)
		if search_result:
			# Concatenate the content of the top results
			context = "\n\n".join([hit.payload.get("content", "") for hit in search_result])
			# Compose prompt for OpenAI
			prompt = f"You are an assistant for answering questions about invoices. Use the following invoice content to answer the question.\n\nInvoice Content:\n{context}\n\nQuestion: {question}\nAnswer:"
			headers = {
				"Authorization": f"Bearer {openai_api_key}",
				"Content-Type": "application/json"
			}
			data = {
				"model": "gpt-3.5-turbo",
				"messages": [
					{"role": "system", "content": "You are an assistant for answering questions about invoices."},
					{"role": "user", "content": prompt}
				]
			}
			response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
			response.raise_for_status()
			answer = response.json()["choices"][0]["message"]["content"]
			st.markdown(f"**Answer:** {answer}")
		else:
			st.info("No relevant invoices found to answer your question.")
	except Exception as e:
		st.warning(f"Could not answer question: {e}")
