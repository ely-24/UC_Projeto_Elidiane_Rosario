# Automated Prescription Recommendation System using RAG and Drug Interaction Data

This repository contains the resources and code developed for the academic project **"Construction of a Dataset for Automated Prescription Recommendations: A Focus on Antibiotic Drug Interactions using Retrieval-Augmented Generation (RAG)"**.

## 🧠 Overview

The main goal of this project is to build a dataset and prototype system capable of enhancing clinical prescription recommendations, with a particular emphasis on:
- Antibiotic drug interactions
- Semantic retrieval of biomedical knowledge
- Integration of Retrieval-Augmented Generation (RAG) with Large Language Models (LLMs)

## 📂 Repository Structure

- `chroma_db/`: Local vector store used for semantic search via ChromaDB.
- `drugbank_chunks.py`: Script for parsing and chunking DrugBank data into structured text units.
- `drugbank_json.py`: Extracts and formats relevant antibiotic data from DrugBank XML.
- `drugbank_vetor.py`: Converts extracted chunks into embeddings for use in RAG-based search.
- `ollama_pure.py`: Basic LLM query execution (without retrieval).
- `ollama_rag.py`: Retrieval-Augmented Generation pipeline implementation using RAG + LLM.
- `antibiotics_chunks.zip`: Preprocessed semantic chunks of antibiotics-related knowledge.
- `antibiotics_dataset.zip`: Main dataset archive built from DrugBank with antibiotic focus.
- `Apresentação do Projeto.pdf`: Project presentation slides.
- `UC_Projeto_Elidiane_Do_Rosário_Final.pdf`: Final report of the academic project.

## 🔍 Methodology

1. **Data Extraction**: Used DrugBank XML as the primary source, extracting fields related to antibiotic properties and interactions.
2. **Data Transformation**: Parsed relevant data into readable chunks and embedded using sentence-transformers.
3. **Semantic Search**: Used ChromaDB for vector similarity search.
4. **RAG Pipeline**: Queries are encoded, matched semantically, and passed along with context to a local LLM via Ollama.
5. **Evaluation**: Use cases focused on verifying how well the system handles complex drug interaction queries.

