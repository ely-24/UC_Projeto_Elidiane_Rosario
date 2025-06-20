import json
import os
import chromadb 
from sentence_transformers import SentenceTransformer


# Caminho para o arquivo JSON contendo os chunks (gerado na etapa anterior)
chunks_file_path = 'antibiotics_chunks.json'

# Nome da coleção no ChromaDB onde os chunks serão armazenados
chroma_collection_name = 'drugbank_antibiotics'

# Caminho para o diretório onde o ChromaDB vai armazenar os dados
chroma_db_path = './chroma_db'

print(f"Lendo chunks do arquivo: {chunks_file_path}")

if not os.path.exists(chunks_file_path):
    print(f"Erro: Arquivo de chunks não encontrado em {chunks_file_path}")
else:
    try:
        # Carregar os chunks do arquivo JSON
        with open(chunks_file_path, 'r', encoding='utf-8') as f:
            all_chunks = json.load(f)

        print(f"Arquivo de chunks lido com sucesso. Total de chunks: {len(all_chunks)}")

        # --- Configurar ChromaDB ---
        # Criar um cliente ChromaDB
        client = chromadb.PersistentClient(path=chroma_db_path)

        # Antes de obter/criar a coleção, exclua-a se ela já existe.
        # Isso garante que você sempre comece com uma coleção vazia e fresca
        # para refletir as últimas alterações no arquivo de chunks.
        print(f"Verificando e excluindo coleção existente (se houver): '{chroma_collection_name}'")
        try:
            client.delete_collection(name=chroma_collection_name)
            print(f"Coleção '{chroma_collection_name}' existente foi excluída com sucesso.")
        except Exception as e:
            # Esta exceção ocorrerá se a coleção não existir, o que é normal na primeira execução
            print(f"Coleção '{chroma_collection_name}' não existia ou erro ao excluir (ignorado para criação): {e}")

        # Agora, crie a coleção (ela será nova ou recém-excluída)
        print(f"Criando nova coleção no ChromaDB: {chroma_collection_name}")
        collection = client.create_collection(name=chroma_collection_name)

        # --- Carregar o Modelo de Embedding ---
        # Um bom modelo para começar, equilibrando tamanho e desempenho
        print("Carregando modelo de embedding (sentence-transformers/all-MiniLM-L6-v2)...")
        embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("Modelo de embedding carregado.")

        # --- Gerar Embeddings e Adicionar ao ChromaDB ---
        print("Gerando embeddings e adicionando chunks ao ChromaDB...")

        # Listas para armazenar dados em batch 
        batch_size = 100 # Número de chunks para processar por vez
        documents = []
        metadatas = []
        ids = [] # Agora vamos usar o 'chunk_id' do JSON
        embeddings = [] # Lista para armazenar os vetores

        for i, chunk in enumerate(all_chunks):
            chunk_content = chunk.get('content', '')
            if not chunk_content.strip(): # Pula chunks vazios
                continue

            chunk_id = chunk.get('chunk_id') # Pega o ID persistente do chunk
            if not chunk_id:
                print(f"Aviso: Chunk sem 'chunk_id' encontrado. Pulando este chunk. Conteúdo: {chunk_content[:50]}...")
                continue

            chunk_embedding = embedding_model.encode(chunk_content) # Gera o vetor!

            # Armazenar dados do chunk para o batch
            documents.append(chunk_content)

            # Os metadados ajudam a filtrar e contextualizar os resultados da busca
            # IMPORTANTE: Filtramos valores None dos metadados, pois ChromaDB não os permite
            chunk_metadata = {k: v for k, v in chunk.items() if k not in ['content', 'chunk_id'] and v is not None}
            metadatas.append(chunk_metadata)

            # Adicionar o ID persistente do chunk
            ids.append(chunk_id)

            # Adicionar o embedding gerado
            embeddings.append(chunk_embedding.tolist()) # ChromaDB espera listas de floats

            # Adicionar ao ChromaDB em batches
            if (i + 1) % batch_size == 0 or (i + 1) == len(all_chunks):
                print(f"Adicionando batch de chunks ({len(ids)} chunks, até chunk {i+1})...")
                collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                # Limpar as listas para o próximo batch
                documents = []
                metadatas = []
                ids = []
                embeddings = []

        print("\nProcesso de embedding e indexação concluído.")
        print(f"Total de chunks indexados na coleção '{chroma_collection_name}': {collection.count()}")


    except Exception as e:
        print(f"Ocorreu um erro durante o processo de embedding/indexação: {e}")
        print("Verifique se as bibliotecas estão instaladas e o arquivo de chunks existe.")