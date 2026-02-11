import chromadb
import datetime
import os

# Define onde o banco de dados será salvo
# Usamos o 'os.path' para garantir que funciona no Windows e Mac
DB_PATH = os.path.join(os.getcwd(), "argus_db")

# Inicia o cliente do banco
client = chromadb.PersistentClient(path=DB_PATH)

# Cria a coleção
colecao = client.get_or_create_collection(name="historico_argus")

def salvar_memoria(texto: str, metadados: dict):
    """
    Salva uma informação no banco vetorial.
    """
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadados["timestamp"] = agora
    
    # Cria um ID único baseado no tempo para não dar erro de duplicidade
    id_unico = f"doc_{datetime.datetime.now().timestamp()}"
    
    colecao.add(
        documents=[texto],
        metadatas=[metadados],
        ids=[id_unico]
    )
    print(f"--- [MEMÓRIA] Guardado: {id_unico} ---")

def buscar_memoria(pergunta: str, n_resultados=2):
    """
    Recupera informações relevantes do passado.
    """
    resultados = colecao.query(
        query_texts=[pergunta],
        n_results=n_resultados
    )
    return resultados['documents'][0]