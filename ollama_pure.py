# ollama_pure.py

import ollama

# --- Configurações ---
llm_model_name = 'mistral' #'llama2'  ou  'phi', etc. 

# --- Função: Consulta ao LLM PURO (SEM RAG) ---
def pure_ollama_query(query_text: str):
    """
    Consulta o LLM diretamente sem contexto externo.
    """
    print(f"\n--- Consulta ao LLM PURO (Sem RAG) para: '{query_text}' ---")

    # Prompt de sistema mais genérico para o LLM puro
    system_prompt_pure = (
        "Você é um assistente de inteligência artificial útil e informativo. "
        "Responda à pergunta do usuário da melhor maneira possível com base no seu conhecimento geral. "
        "Se não souber a resposta ou a pergunta for muito específica e exigir dados especializados que você não possui, "
        "diga que não tem essa informação ou que o conhecimento é limitado."
    )

    try:
        response = ollama.chat(model=llm_model_name, messages=[
            {'role': 'system', 'content': system_prompt_pure},
            {'role': 'user', 'content': query_text},
        ])
        llm_response = response['message']['content']
        print("\n--- Resposta do LLM PURO ---")
        print(llm_response)
        return llm_response
    except Exception as e:
        print(f"Erro ao chamar o Ollama: {e}")
        print("Verifique se o Ollama está rodando e se o modelo especificado está disponível.")
        return "Desculpe, houve um erro ao processar sua solicitação com o LLM puro."

# --- Loop de Interação ---
if __name__ == "__main__":
    print("\n--- Teste de LLM Puro (Sem RAG) ---")
    print(f"Modelo LLM utilizado: {llm_model_name}")
    print("Este sistema responde usando apenas o conhecimento inerente ao modelo.")
    print("Digite sua pergunta (ou 'sair' para encerrar).")

    while True:
        user_query = input("\nSua pergunta: ")
        if user_query.lower() == 'sair':
            print("Encerrando o teste. Adeus!")
            break
        
        pure_ollama_query(user_query)