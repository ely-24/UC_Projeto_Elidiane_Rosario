import json
import os

# Caminho para o arquivo JSON gerado na etapa anterior
json_file_path = 'antibiotics_dataset.json'
# Caminho para o arquivo onde salvaremos os chunks
output_chunks_path = 'antibiotics_chunks.json'

# Lista para armazenar todos os chunks gerados
all_chunks = []

print(f"Lendo dados do arquivo: {json_file_path}")

if not os.path.exists(json_file_path):
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
else:
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            antibiotics_data = json.load(f)

        print(f"Arquivo lido com sucesso. Processando {len(antibiotics_data)} antibióticos em chunks...")

        for drug in antibiotics_data:
            drugbank_id = drug.get('drugbank_id', 'N/A')
            name = drug.get('name', 'N/A')

            # --- Criar Chunks para cada tipo de informação ---

            # 1. Chunk de Resumo/Visão Geral
            summary_text = f"Nome: {name} (ID DrugBank: {drugbank_id})\n"
            if drug.get('description'): summary_text += f"Descrição: {drug['description']}\n"
            if drug.get('indication'): summary_text += f"Indicação: {drug['indication']}\n"
            if drug.get('groups'): summary_text += f"Grupos: {', '.join(drug['groups'])}\n"
            if drug.get('categories'): summary_text += f"Categorias: {', '.join(drug['categories'])}\n"
            if drug.get('affected_organisms'): summary_text += f"Organismos Afetados: {', '.join(drug['affected_organisms'])}\n"

            if summary_text.strip(): # Adiciona apenas se houver conteúdo relevante
                all_chunks.append({
                    'chunk_id': f"{drugbank_id}_summary", # ID consistente (um por droga)
                    'drugbank_id': drugbank_id,
                    'name': name,
                    'chunk_type': 'summary',
                    'content': summary_text.strip()
                })

            # 2. Chunk de Farmacologia
            pharmacology_text = ""
            if drug.get('pharmacodynamics'): pharmacology_text += f"Farmacodinâmica: {drug['pharmacodynamics']}\n"
            if drug.get('mechanism_of_action'): pharmacology_text += f"Mecanismo de Ação: {drug['mechanism_of_action']}\n"

            if pharmacology_text.strip():
                all_chunks.append({
                    'chunk_id': f"{drugbank_id}_pharmacology", 
                    'drugbank_id': drugbank_id,
                    'name': name,
                    'chunk_type': 'pharmacology',
                    'content': pharmacology_text.strip()
                })

            # 3. Chunk de Farmacocinética (ADME)
            adme_text = ""
            if drug.get('metabolism'): adme_text += f"Metabolismo: {drug['metabolism']}\n"
            if drug.get('absorption'): adme_text += f"Absorção: {drug['absorption']}\n"
            if drug.get('half_life'): adme_text += f"Meia-vida: {drug['half_life']}\n"
            if drug.get('protein_binding'): adme_text += f"Ligação Proteica: {drug['protein_binding']}\n"
            if drug.get('route_of_elimination'): adme_text += f"Via de Eliminação: {drug['route_of_elimination']}\n"
            if drug.get('volume_of_distribution'): adme_text += f"Volume de Distribuição: {drug['volume_of_distribution']}\n"
            if drug.get('clearance'): adme_text += f"Clearance: {drug['clearance']}\n"

            if adme_text.strip():
                all_chunks.append({
                    'chunk_id': f"{drugbank_id}_pharmacokinetics", 
                    'drugbank_id': drugbank_id,
                    'name': name,
                    'chunk_type': 'pharmacokinetics',
                    'content': adme_text.strip()
                })

            # 4. Chunk de Toxicidade
            if drug.get('toxicity'):
                all_chunks.append({
                    'chunk_id': f"{drugbank_id}_toxicity", 
                    'drugbank_id': drugbank_id,
                    'name': name,
                    'chunk_type': 'toxicity',
                    'content': f"Toxicidade/Efeitos Adversos: {drug['toxicity'].strip()}"
                })

            # 5. Chunks de Interações Medicamentosas 
            if drug.get('drug_interactions'):
                for i, interaction in enumerate(drug['drug_interactions']):
                    # Prioriza o drugbank_id da droga interaginete para unicidade, mas sempre inclui o índice
                    interaction_id_suffix = interaction.get('drugbank_id')
                    if interaction_id_suffix:
                        chunk_id_suffix = f"{interaction_id_suffix}_{i}"
                    else: # Se não houver drugbank_id para a interação
                        chunk_id_suffix = f"idx{i}"

                    interaction_text = f"Interação Medicamentosa de {name} (ID DrugBank: {drugbank_id}) com {interaction.get('name', 'N/A')} (ID DrugBank: {interaction.get('drugbank_id', 'N/A')}).\n"
                    if interaction.get('description'):
                        interaction_text += f"Descrição: {interaction['description'].strip()}"

                    if interaction_text.strip() != f"Interação Medicamentosa de {name} (ID DrugBank: {drugbank_id}) com N/A (ID DrugBank: N/A).":
                        all_chunks.append({
                            'chunk_id': f"{drugbank_id}_drug_interaction_{chunk_id_suffix}", # ID consistente e único
                            'drugbank_id': drugbank_id,
                            'name': name,
                            'chunk_type': 'drug_interaction',
                            'interacting_drug_id': interaction.get('drugbank_id'),
                            'interacting_drug_name': interaction.get('name'),
                            'content': interaction_text.strip()
                        })

            # 6. Chunks de Interações Alimentares 
            if drug.get('food_interactions'):
                for i, fi in enumerate(drug['food_interactions']):
                    if fi.strip():
                        all_chunks.append({
                            'chunk_id': f"{drugbank_id}_food_interaction_{i}", 
                            'drugbank_id': drugbank_id,
                            'name': name,
                            'chunk_type': 'food_interaction',
                            'content': f"Interação Alimentar de {name} (ID DrugBank: {drugbank_id}): {fi.strip()}"
                        })

            # 7. Chunks de Alvos Moleculares 
            if drug.get('targets'):
                for i, target in enumerate(drug['targets']):
                    # Prioriza o uniprot_id, mas sempre inclui o índice para unicidade
                    target_uniprot_id = target.get('uniprot_id')
                    if target_uniprot_id:
                        chunk_id_suffix = f"{target_uniprot_id}_{i}"
                    else:
                        chunk_id_suffix = f"idx{i}" # Fallback para índice se não houver UniProt ID

                    target_text = f"Alvo Molecular de {name} (ID DrugBank: {drugbank_id}).\n"
                    if target.get('name'): target_text += f"Nome do Alvo: {target['name']}\n"
                    if target_uniprot_id: target_text += f"ID UniProt: {target_uniprot_id}\n"
                    

                    if target_text.strip() != f"Alvo Molecular de {name} (ID DrugBank: {drugbank_id}).":
                        all_chunks.append({
                            'chunk_id': f"{drugbank_id}_target_{chunk_id_suffix}", 
                            'drugbank_id': drugbank_id,
                            'name': name,
                            'chunk_type': 'target',
                            'target_name': target.get('name'),
                            'target_uniprot_id': target_uniprot_id,
                            'content': target_text.strip()
                        })

            # 8. Chunks de Dosagens 
            if drug.get('dosages'):
                for i, dosage in enumerate(drug['dosages']):
                    dosage_text = f"Dosagem para {name} (ID DrugBank: {drugbank_id}) (Entrada {i+1}).\n"
                    if dosage.get('form'): dosage_text += f"Forma: {dosage['form']}\n"
                    if dosage.get('route'): dosage_text += f"Via: {dosage['route']}\n"
                    if dosage.get('strength'): dosage_text += f"Concentração/Força: {dosage['strength']}\n"

                    if dosage_text.strip() != f"Dosagem para {name} (ID DrugBank: {drugbank_id}) (Entrada {i+1}).":
                        all_chunks.append({
                            'chunk_id': f"{drugbank_id}_dosage_{i}", 
                            'drugbank_id': drugbank_id,
                            'name': name,
                            'chunk_type': 'dosage',
                            'dosage_form': dosage.get('form'),
                            'dosage_route': dosage.get('route'),
                            'content': dosage_text.strip()
                        })

            # 9. Chunk de Produtos 
            if drug.get('products'):
                products_text = f"Produtos que contêm {name} (ID DrugBank: {drugbank_id}):\n"
                for i, product in enumerate(drug['products']): # Adiciona loop para garantir a inclusão de todos os produtos
                    products_text += f"- Nome: {product.get('name', 'N/A')}\n"
                    if product.get('labeller'): products_text += f"  Fabricante: {product['labeller']}\n"
                    if product.get('ndc_id'): products_text += f"  NDC ID: {product['ndc_id']}\n"
                    if product.get('dosage_form'): products_text += f"  Forma de Dosagem: {product['dosage_form']}\n"
                
                if products_text.strip() != f"Produtos que contêm {name} (ID DrugBank: {drugbank_id}):":
                    all_chunks.append({
                        'chunk_id': f"{drugbank_id}_products", 
                        'drugbank_id': drugbank_id,
                        'name': name,
                        'chunk_type': 'products',
                        'content': products_text.strip()
                    })

            # 10. Chunk de Sinônimos
            if drug.get('synonyms'):
                synonyms_text = f"Sinônimos para {name} (ID DrugBank: {drugbank_id}):\n"
                synonyms_text += ", ".join(drug['synonyms'])
                
                if synonyms_text.strip() != f"Sinônimos para {name} (ID DrugBank: {drugbank_id}):":
                    all_chunks.append({
                        'chunk_id': f"{drugbank_id}_synonyms", 
                        'drugbank_id': drugbank_id,
                        'name': name,
                        'chunk_type': 'synonyms',
                        'content': synonyms_text.strip()
                    })

            # 11. Chunk de Classificação
            if drug.get('classification'):
                classification_text = f"Classificação para {name} (ID DrugBank: {drugbank_id}):\n"
                if drug['classification'].get('kingdom'): classification_text += f"  Reino: {drug['classification']['kingdom']}\n"
                if drug['classification'].get('superclass'): classification_text += f"  Superclasse: {drug['classification']['superclass']}\n"
                if drug['classification'].get('class'): classification_text += f"  Classe: {drug['classification']['class']}\n"
                if drug['classification'].get('subclass'): classification_text += f"  Subclasse: {drug['classification']['subclass']}\n"
                if drug['classification'].get('direct_parent'): classification_text += f"  Parentesco Direto: {drug['classification']['direct_parent']}\n"

                if classification_text.strip() != f"Classificação para {name} (ID DrugBank: {drugbank_id}):":
                    all_chunks.append({
                        'chunk_id': f"{drugbank_id}_classification", 
                        'drugbank_id': drugbank_id,
                        'name': name,
                        'chunk_type': 'classification',
                        'content': classification_text.strip()
                    })
                    
            # 12. Chunk de IDs Externos
            if drug.get('external_identifiers'):
                ext_ids_text = f"Identificadores Externos para {name} (ID DrugBank: {drugbank_id}):\n"
                for i, ext_id in enumerate(drug['external_identifiers']):
                    if ext_id.get('resource') and ext_id.get('identifier'):
                        ext_ids_text += f"- {ext_id['resource']}: {ext_id['identifier']}\n"

                if ext_ids_text.strip() != f"Identificadores Externos para {name} (ID DrugBank: {drugbank_id}):":
                    all_chunks.append({
                        'chunk_id': f"{drugbank_id}_external_identifiers", 
                        'drugbank_id': drugbank_id,
                        'name': name,
                        'chunk_type': 'external_identifiers',
                        'content': ext_ids_text.strip()
                    })
        # --- Fim do processamento ---

        print(f"Processamento concluído. Total de chunks criados: {len(all_chunks)}")

        # Salvar os chunks em um arquivo JSON
        try:
            with open(output_chunks_path, 'w', encoding='utf-8') as f:
                json.dump(all_chunks, f, indent=4, ensure_ascii=False)
            print(f"Chunks salvos (opcional) em {output_chunks_path}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo de chunks: {e}")

    except Exception as e:
        print(f"Ocorreu um erro durante o processamento do JSON: {e}")
        print("Certifique-se de que o arquivo JSON está bem formado.")