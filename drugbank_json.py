import lxml.etree as etree
import os
import json

# Defina o caminho para o seu arquivo DrugBank XML
xml_file_path = 'Projeto\drugbank.xml'  
output_json_path = 'antibiotics_dataset.json'  

# Namespace do DrugBank
DB_NAMESPACE = "http://www.drugbank.ca"
NS_MAP = {'db': DB_NAMESPACE}

# Lista de termos para identificar antibióticos
ANTIBIOTIC_KEYWORDS = [
    "Antibacterial", "Antibiotics", "Antibiotic", "Anti-Bacterial Agents",
    "Anti-Bacterial", "Penicillins", "Tetracyclines", "Macrolides",
    "Cephalosporins", "Fluoroquinolones", "Sulfonamides", "Aminoglycosides",
    "Carbapenems", "Monobactams",
]


def safe_extract_text(element, xpath, namespace_map):
    """Extrai texto de um elemento usando XPath, retornando None se não encontrado."""
    found_element = element.find(xpath, namespace_map)
    if found_element is not None and found_element.text:
        return found_element.text.strip()
    return None


def extract_antibiotic_data(drug_element):
    """Extrai os dados relevantes de um elemento <drug>."""
    drug_data = {}

    # 1. Informações Essenciais
    # Encontrar o drugbank-id primário
    primary_id_elem = drug_element.find('{%s}drugbank-id[@primary="true"]' % DB_NAMESPACE)
    drug_data['drugbank_id'] = primary_id_elem.text.strip() if primary_id_elem is not None and primary_id_elem.text else None
    if not drug_data['drugbank_id']:  # Se não encontrou primário, pega o primeiro disponível
        any_id_elem = drug_element.find('{%s}drugbank-id' % DB_NAMESPACE)
        drug_data['drugbank_id'] = any_id_elem.text.strip() if any_id_elem is not None and any_id_elem.text else None

    drug_data['name'] = safe_extract_text(drug_element, '{%s}name' % DB_NAMESPACE, NS_MAP)
    drug_data['description'] = safe_extract_text(drug_element, '{%s}description' % DB_NAMESPACE, NS_MAP)
    drug_data['cas_number'] = safe_extract_text(drug_element, '{%s}cas-number' % DB_NAMESPACE, NS_MAP)
    drug_data['unii'] = safe_extract_text(drug_element, '{%s}unii' % DB_NAMESPACE, NS_MAP)
    drug_data['indication'] = safe_extract_text(drug_element, '{%s}indication' % DB_NAMESPACE, NS_MAP)
    drug_data['toxicity'] = safe_extract_text(drug_element, '{%s}toxicity' % DB_NAMESPACE, NS_MAP)

    # Grupos
    groups = []
    groups_elem = drug_element.find('{%s}groups' % DB_NAMESPACE)
    if groups_elem is not None:
        for group_elem in groups_elem.findall('{%s}group' % DB_NAMESPACE):
            if group_elem.text:
                groups.append(group_elem.text.strip())
    drug_data['groups'] = groups

    # Categorias
    categories = []
    categories_elem = drug_element.find('{%s}categories' % DB_NAMESPACE)
    if categories_elem is not None:
        for category_elem in categories_elem.findall('{%s}category' % DB_NAMESPACE):
            cat_name_elem = category_elem.find('{%s}category' % DB_NAMESPACE)
            if cat_name_elem is not None and cat_name_elem.text:
                categories.append(cat_name_elem.text.strip())
    drug_data['categories'] = categories

    # Organismos Afetados
    affected_organisms = []
    affected_organisms_elem = drug_element.find('{%s}affected-organisms' % DB_NAMESPACE)
    if affected_organisms_elem is not None:
        for organism_elem in affected_organisms_elem.findall('{%s}affected-organism' % DB_NAMESPACE):
            if organism_elem.text:
                affected_organisms.append(organism_elem.text.strip())
    drug_data['affected_organisms'] = affected_organisms

    # 2. Informações para Interações (ADME, Mecanismo)
    drug_data['pharmacodynamics'] = safe_extract_text(drug_element, '{%s}pharmacodynamics' % DB_NAMESPACE, NS_MAP)
    drug_data['mechanism_of_action'] = safe_extract_text(drug_element, '{%s}mechanism-of-action' % DB_NAMESPACE, NS_MAP)
    drug_data['metabolism'] = safe_extract_text(drug_element, '{%s}metabolism' % DB_NAMESPACE, NS_MAP)
    drug_data['absorption'] = safe_extract_text(drug_element, '{%s}absorption' % DB_NAMESPACE, NS_MAP)
    drug_data['half_life'] = safe_extract_text(drug_element, '{%s}half-life' % DB_NAMESPACE, NS_MAP)
    drug_data['protein_binding'] = safe_extract_text(drug_element, '{%s}protein-binding' % DB_NAMESPACE, NS_MAP)
    drug_data['route_of_elimination'] = safe_extract_text(drug_element, '{%s}route-of-elimination' % DB_NAMESPACE, NS_MAP)
    drug_data['volume_of_distribution'] = safe_extract_text(drug_element, '{%s}volume-of-distribution' % DB_NAMESPACE, NS_MAP)
    drug_data['clearance'] = safe_extract_text(drug_element, '{%s}clearance' % DB_NAMESPACE, NS_MAP)

    # 3. Interações Diretas
    # Interações Medicamentosas
    drug_interactions = []
    drug_interactions_elem = drug_element.find('{%s}drug-interactions' % DB_NAMESPACE)
    if drug_interactions_elem is not None:
        for interaction_elem in drug_interactions_elem.findall('{%s}drug-interaction' % DB_NAMESPACE):
            interacting_id_elem = interaction_elem.find('{%s}drugbank-id' % DB_NAMESPACE)
            interacting_name_elem = interaction_elem.find('{%s}name' % DB_NAMESPACE)
            description_elem = interaction_elem.find('{%s}description' % DB_NAMESPACE)

            interaction_detail = {
                'drugbank_id': interacting_id_elem.text.strip() if interacting_id_elem is not None and interacting_id_elem.text else None,
                'name': interacting_name_elem.text.strip() if interacting_name_elem is not None and interacting_name_elem.text else None,
                'description': description_elem.text.strip() if description_elem is not None and description_elem.text else None,
            }
            if any(interaction_detail.values()):  # Adiciona apenas se tiver pelo menos um campo preenchido
                drug_interactions.append(interaction_detail)
    drug_data['drug_interactions'] = drug_interactions

    # Interações com Alimentos
    food_interactions = []
    food_interactions_elem = drug_element.find('{%s}food-interactions' % DB_NAMESPACE)
    if food_interactions_elem is not None:
        for fi_elem in food_interactions_elem.findall('{%s}food-interaction' % DB_NAMESPACE):
            if fi_elem.text:
                food_interactions.append(fi_elem.text.strip())
    drug_data['food_interactions'] = food_interactions

    # 4. Alvos
    targets = []
    targets_elem = drug_element.find('{%s}targets' % DB_NAMESPACE)
    if targets_elem is not None:
        for target_elem in targets_elem.findall('{%s}target' % DB_NAMESPACE):
            # A estrutura interna de target pode ser complexa, aqui pegamos apenas o ID UniProt se existir
            polypeptide_elem = target_elem.find('{%s}polypeptide' % DB_NAMESPACE)
            if polypeptide_elem is not None:
                uniprot_id_elem = polypeptide_elem.find(
                    '{%s}external-identifiers/{%s}external-identifier[{%s}resource="UniProtKB"]/{%s}identifier' % (
                        DB_NAMESPACE, DB_NAMESPACE, DB_NAMESPACE, DB_NAMESPACE))
                name_elem = polypeptide_elem.find('{%s}name' % DB_NAMESPACE)
                target_detail = {
                    'uniprot_id': uniprot_id_elem.text.strip() if uniprot_id_elem is not None and uniprot_id_elem.text else None,
                    'name': name_elem.text.strip() if name_elem is not None and name_elem.text else None
                }
                if any(target_detail.values()):
                    targets.append(target_detail)
    drug_data['targets'] = targets

    # 5. Dosagens
    dosages = []
    dosages_elem = drug_element.find('{%s}dosages' % DB_NAMESPACE)
    if dosages_elem is not None:
        for dosage_elem in dosages_elem.findall('{%s}dosage' % DB_NAMESPACE):
            form = safe_extract_text(dosage_elem, '{%s}form' % DB_NAMESPACE, NS_MAP)
            route = safe_extract_text(dosage_elem, '{%s}route' % DB_NAMESPACE, NS_MAP)
            strength = safe_extract_text(dosage_elem, '{%s}strength' % DB_NAMESPACE, NS_MAP)
            dosage_detail = {'form': form, 'route': route, 'strength': strength}
            if any(dosage_detail.values()):
                dosages.append(dosage_detail)
    drug_data['dosages'] = dosages
    
    # 6. Produtos - Incluindo labeller
    products = []
    products_elem = drug_element.find('{%s}products' % DB_NAMESPACE)
    if products_elem is not None:
        for product_elem in products_elem.findall('{%s}product' % DB_NAMESPACE):
            product_detail = {
                'name': safe_extract_text(product_elem, '{%s}name' % DB_NAMESPACE, NS_MAP),
                'labeller': safe_extract_text(product_elem, '{%s}labeller' % DB_NAMESPACE, NS_MAP), 
                'dosage_form': safe_extract_text(product_elem, '{%s}dosage-form' % DB_NAMESPACE, NS_MAP),
                'strength': safe_extract_text(product_elem, '{%s}strength' % DB_NAMESPACE, NS_MAP),
                'route': safe_extract_text(product_elem, '{%s}route' % DB_NAMESPACE, NS_MAP),
                'generic': safe_extract_text(product_elem, '{%s}generic' % DB_NAMESPACE, NS_MAP),
                'approved': safe_extract_text(product_elem, '{%s}approved' % DB_NAMESPACE, NS_MAP),
                'country': safe_extract_text(product_elem, '{%s}country' % DB_NAMESPACE, NS_MAP)
            }
            if any(product_detail.values()):
                products.append(product_detail)
    drug_data['products'] = products

    # 7. Sinônimos
    synonyms = []
    synonyms_elem = drug_element.find('{%s}synonyms' % DB_NAMESPACE)
    if synonyms_elem is not None:
        for synonym_elem in synonyms_elem.findall('{%s}synonym' % DB_NAMESPACE):
            if synonym_elem.text:
                synonyms.append(synonym_elem.text.strip())
    drug_data['synonyms'] = synonyms

    # 8. Classificação
    classification = {}
    classification_elem = drug_element.find('{%s}classification' % DB_NAMESPACE)
    if classification_elem is not None:
        classification['subclass'] = safe_extract_text(classification_elem, '{%s}subclass' % DB_NAMESPACE, NS_MAP)
        classification['alternative_parent'] = safe_extract_text(classification_elem,
                                                                 '{%s}alternative-parent' % DB_NAMESPACE, NS_MAP)
        classification['substituent'] = safe_extract_text(classification_elem, '{%s}substituent' % DB_NAMESPACE,
                                                           NS_MAP)
    if any(classification.values()):
        drug_data['classification'] = classification
    else:
         drug_data['classification'] = None # Or an empty dict {} if you prefer


    # 9. IDs Externos 
    external_identifiers = []
    ext_ids_elem = drug_element.find('{%s}external-identifiers' % DB_NAMESPACE)
    if ext_ids_elem is not None:
        for ext_id_elem in ext_ids_elem.findall('{%s}external-identifier' % DB_NAMESPACE):
            resource = safe_extract_text(ext_id_elem, '{%s}resource' % DB_NAMESPACE, NS_MAP)
            identifier = safe_extract_text(ext_id_elem, '{%s}identifier' % DB_NAMESPACE, NS_MAP)
            if resource and identifier:
                external_identifiers.append({'resource': resource, 'identifier': identifier})
    drug_data['external_identifiers'] = external_identifiers

    return drug_data


print(f"Iniciando o parse, identificação e extração de dados de antibióticos: {xml_file_path}")

if not os.path.exists(xml_file_path):
    print(f"Erro: Arquivo não encontrado em {xml_file_path}")
else:
    count_drugs = 0
    count_antibiotics = 0
    antibiotic_data = []  # Lista para armazenar os dados dos antibióticos encontrados

    try:
        context = etree.iterparse(xml_file_path, events=('end',), tag='{%s}drug' % DB_NAMESPACE)

        print("Iterando sobre os elementos <drug>...")

        for event, elem in context:
            count_drugs += 1
            is_antibiotic = False

            # --- Lógica para Identificar Antibióticos (da Etapa 2) ---
            categories_elem = elem.find('{%s}categories' % DB_NAMESPACE)
            if categories_elem is not None:
                for category_elem in categories_elem.findall('{%s}category' % DB_NAMESPACE):
                    cat_name_elem = category_elem.find('{%s}category' % DB_NAMESPACE)
                    if cat_name_elem is not None and cat_name_elem.text:
                        category_text = cat_name_elem.text.strip()
                        if any(keyword.lower() in category_text.lower() for keyword in ANTIBIOTIC_KEYWORDS):
                            is_antibiotic = True
                            break  # Encontrou, não precisa verificar as outras categorias deste drug

            # --- Se for um antibiótico, extraia e armazene os dados ---
            if is_antibiotic:
                count_antibiotics += 1
                data = extract_antibiotic_data(elem)
                antibiotic_data.append(data)
                print(f"  Extraído dados para {data.get('name', 'N/A')} (ID: {data.get('drugbank_id', 'N/A')})")

            # --- Gerenciamento de Memória ---
            # Crucial para liberar a memória após processar cada elemento <drug>
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getprevious().getparent()[0]
            # --- Fim Gerenciamento de Memória ---

        print(f"\nParse concluído. Total de elementos <drug> encontrados: {count_drugs}")
        print(f"Total de antibióticos identificados e dados extraídos: {count_antibiotics}")
        print(f"Preparando para salvar {len(antibiotic_data)} registros no arquivo JSON...")

        # --- Salvar os Dados Extraídos ---
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(antibiotic_data, f, indent=4, ensure_ascii=False)
            print(f"Dados salvos com sucesso em {output_json_path}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")

    except Exception as e:
        print(f"Ocorreu um erro durante o parse: {e}")
        print("Verifique o arquivo XML e a lógica de extração.")