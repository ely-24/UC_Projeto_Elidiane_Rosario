# ollama_rag.py (com cache de query embedding e sem mencionar DrugBank)

import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import os

# --- Configurações ---
chroma_db_path = r'C:\Users\elidi\OneDrive\Ambiente de Trabalho\Python\chroma_db'
chroma_collection_name = 'drugbank_antibiotics'
embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
llm_model_name = 'mistral'
n_results_to_retrieve = 15

# --- Cache de Embeddings de Query ---
# Este dicionário armazenará {query_text: query_embedding}
query_embedding_cache = {}

# --- Inicialização ---

print(f"Conectando ao ChromaDB em: {chroma_db_path}")
try:
    client = chromadb.PersistentClient(path=chroma_db_path)
    collection = client.get_collection(name=chroma_collection_name)
    print(f"Coleção '{chroma_collection_name}' carregada com sucesso. Total de itens: {collection.count()}")
    if collection.count() == 0:
        print("Atenção: A coleção está vazia. Certifique-se de ter indexado os dados.")
except Exception as e:
    print(f"Erro ao carregar a coleção '{chroma_collection_name}': {e}")
    print("Certifique-se de que o ChromaDB foi populado corretamente executando o script de indexação.")
    exit()

print(f"Carregando modelo de embedding: {embedding_model_name}")
embedding_model = SentenceTransformer(embedding_model_name)
print("Modelo de embedding carregado.")

# --- Função: RAG com Ollama (COM RAG) ---
def rag_with_ollama(query_text: str):
    """
    Executa o processo de Retrieval-Augmented Generation para auxiliar médicos.
    Inclui cache de embeddings para a query e não menciona "DrugBank".
    """
    print(f"\n--- Consulta RAG (Com Contexto do Dataset) para: '{query_text}' ---")

    # 1. Gerar embedding para a pergunta do usuário (com cache)
    if query_text in query_embedding_cache:
        query_embedding = query_embedding_cache[query_text]
        print("Usando embedding da query do cache.")
    else:
        print("Gerando novo embedding para a query...")
        query_embedding = embedding_model.encode(query_text).tolist()
        query_embedding_cache[query_text] = query_embedding # Armazena no cache

    # 2. Buscar chunks relevantes no ChromaDB
    print(f"Buscando os {n_results_to_retrieve} chunks mais relevantes no ChromaDB...")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results_to_retrieve,
        include=['documents', 'metadatas', 'distances']
    )

    retrieved_chunks = results['documents'][0]
    retrieved_metadatas = results['metadatas'][0]
    retrieved_distances = results['distances'][0]

    if not retrieved_chunks:
        print("Nenhum chunk relevante encontrado no ChromaDB.")
        return ("Desculpe, não consegui encontrar informações relevantes sobre este antibiótico "
                "com base nos dados do dataset que possuo. Por favor, reformule sua pergunta "
                "ou consulte outras fontes confiáveis.")

    print(f"Chunks recuperados (top {len(retrieved_chunks)}):")
    context_parts = []
    for i, chunk_content in enumerate(retrieved_chunks):
        metadata = retrieved_metadatas[i]
        distance = retrieved_distances[i]
        context_parts.append(f"### Informação do Dataset (Chunk {i+1} - Tipo: {metadata.get('chunk_type', 'N/A')}, ID DrugBank: {metadata.get('drugbank_id', 'N/A')}, Distância: {distance:.4f}):\n{chunk_content}\n")
        print(f"  - Chunk {i+1} (Tipo: {metadata.get('chunk_type')}, ID DrugBank: {metadata.get('drugbank_id')}, Distância: {distance:.4f}): {chunk_content[:100]}...")

    # 3. Construir o prompt para o LLM com o contexto
    context = "\n\n".join(context_parts)
    
    # Prompt de sistema para instruir o LLM como assistente médico
    system_prompt_rag = (
        "Você é um assistente de informação sobre antibióticos, projetado para auxiliar médicos com base nos dados do dataset." 
        "O contexto fornecido pode estar em inglês, mas deve responder em português, traduzindo e sintetizando as informações de forma clara e precisa. "
        "As suas respostas devem ser precisas, concisas e estritamente derivadas do 'Contexto' fornecido."
        "É CRÍTICO que não adicione informações que não estejam explicitamente presentes no contexto, para evitar alucinações. "
        "NUNCA forneça aconselhamento médico direto, faça diagnósticos ou prescreva tratamentos. A sua função é fornecer informações descritivas sobre os antibióticos. "
        "Comece a sua resposta afirmando claramente que a informação é baseada nos dados do dataset e que não substitui o julgamento clínico do médico."
        "Se o contexto fornecido não contiver a informação necessária para responder à pergunta, diga 'Não tenho informações suficientes nos dados do dataset fornecidos!"
        "para responder a esta pergunta."
        " Mantenha um tom profissional e objectivo."
    )

    user_prompt = f"Contexto:\n{context}\n\nPergunta do Médico: {query_text}\n\nResposta:"

    # 4. Chamar o LLM via Ollama
    print("\nEnviando pergunta e contexto para o LLM (Ollama)...")
    try:
        response = ollama.chat(model=llm_model_name, messages=[
            {'role': 'system', 'content': system_prompt_rag},
            {'role': 'user', 'content': user_prompt},
        ])
        llm_response = response['message']['content']
        print("\n--- Resposta do LLM RAG ---")
        print(llm_response)
        return llm_response
    except Exception as e:
        print(f"Erro ao chamar o Ollama: {e}")
        print("Verifique se o Ollama está rodando e se o modelo especificado está disponível.")
        return "Desculpe, houve um erro ao processar sua solicitação com o LLM."

# --- Loop de Interação ---
if __name__ == "__main__":
    print("\n--- Assistente de Informação sobre Antibióticos (RAG com Dataset) ---")
    print(f"Modelo LLM utilizado: {llm_model_name}")
    print("Este sistema fornece informações sobre antibióticos com base nos dados do dataset. ")
    print("Ele NÃO substitui o julgamento clínico do médico. As decisões de tratamento são de responsabilidade do profissional de saúde.")
    print("Digite sua pergunta sobre antibióticos (ou 'sair' para encerrar).")

    while True:
        user_query = input("\nSua pergunta: ")
        if user_query.lower() == 'sair':
            print("Encerrando o assistente. Adeus!")
            break
        
        rag_with_ollama(user_query)