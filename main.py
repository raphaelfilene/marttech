from fastapi import FastAPI
from pydantic import BaseModel
import traceback

from time import time, mktime
from datetime import datetime

from database import Database

app = FastAPI()

db = Database()

# uvicorn main:app

@app.get("/")
def raiz():
    return {"Ola": "Mundo"}

class Cadernos(BaseModel):
    ID_CADERNO: int
    NOME: str
    DESCRICAO: str

class Anotacoes(BaseModel):
    ID_ANOTACAO: int
    ID_CADERNO: int
    TITULO: str
    DATA_MODIFICACAO: str
    DATA_CRIACAO: str

class Tags(BaseModel):
    ID_ANOTACAO: int
    ID_CADERNO: int
    ID_TAG: int
    TAG: str

def criar_objeto(dado,tabela):
    if tabela == 'CADERNOS':
        return Cadernos(
            ID_CADERNO = dado['ID_CADERNO'],
            NOME = dado['NOME'],
            DESCRICAO = dado['DESCRICAO']
        )
    
    elif tabela == 'ANOTACOES':
        return Anotacoes(
            ID_ANOTACAO = dado['ID_ANOTACAO'],
            ID_CADERNO = dado['ID_CADERNO'],
            TITULO = dado['TITULO'],
            DATA_MODIFICACAO = timestamp_to_date(dado['TIMESTAMP_MODIFICACAO']),
            DATA_CRIACAO = timestamp_to_date(dado['TIMESTAMP_CRIACAO'])
        )

    elif tabela == 'TAGS':
        return Tags(
            ID_ANOTACAO = dado['ID_ANOTACAO'],
            ID_CADERNO = dado['ID_CADERNO'],
            ID_TAG = dado['ID_TAG'],
            TAG = dado['TAG']
        )

def timestamp_to_date(timestamp):
    try:
        date = datetime.fromtimestamp(timestamp)
        return "%s/%s/%s %sh %smin"%(date.day,date.month,date.year,date.hour,date.minute)
    except:
        print("Timestamp inválido!")
    return None

def date_to_timestamp(data):
    try:
        data_obj = datetime.strptime(data,'%d/%m/%Y %Hh %Mmin')
        return int(mktime(data_obj.timetuple()))
    except Exception:
        traceback.print_exc()

def pegar_pelo_titulo(titulo,tabela):
    dados = db.pegar_dados_por_titulo(titulo,tabela)
    if dados and len(dados):
        lista = []
        for dado in dados:
            lista.append(criar_objeto(dado,tabela))
        return lista
    return None

def pegar_tudo(tabela):
    dados = db.retornar_tudo(tabela)
    if dados and len(dados):
        lista = []
        for dado in dados:
            lista.append(criar_objeto(dado,tabela))
        return lista
    return None

@app.get("/cadernos")
def pegar_todos_os_cadernos():
    resposta = pegar_tudo('CADERNOS')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não há nenhum Caderno na nossa base de dados!"}

@app.get("/anotacoes")
def pegar_todas_as_anotacoes():
    resposta = pegar_tudo('ANOTACOES')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não há nenhuma Anotação na nossa base de dados!"}

@app.get("/tags")
def pegar_todas_as_tags():
    resposta = pegar_tudo('TAGS')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não há nenhuma Tag na nossa base de dados!"}

@app.get("/cadernos/{nome}")
def pegar_caderno_pelo_nome(nome: str):
    resposta =  pegar_pelo_titulo(nome,'CADERNOS')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não existe nenhum Caderno com esse nome!"}

@app.get("/anotacoes/{titulo}")
def pegar_anotacao_pelo_titulo(titulo: str):
    resposta = pegar_pelo_titulo(titulo,'ANOTACOES')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não existe nenhuma Anotação com esse título!"}

@app.get("/tags/{tag}")
def pegar_tag_pela_tag(tag: str):
    resposta = pegar_pelo_titulo(tag,'TAGS')
    if resposta:
        return resposta
    else:
        return {"Status": 404, "Mensagem": "Não existe nenhuma Tag com esse nome!"}

@app.post("/criar_caderno/{nome}/{descricao}")
def criar_caderno(nome: str, descricao: str):
    resposta =  pegar_pelo_titulo(nome,'CADERNOS')
    if resposta:
        return {"Status": 404, "Mensagem": "Já existe um Caderno com esse nome!"}
    else:
        try:
            db.criar_caderno({'NOME':nome,'DESCRICAO':descricao},commit=True)
            return {"Status": 200, "Mensagem": "Caderno criado com sucesso!"}
        except Exception:
            traceback.print_exc()
            return {"Status": 404, "Mensagem": "Erro inesperado! Cheque os logs!"}

@app.post("/criar_anotacao/{nome_do_caderno}/{titulo_da_anotacao}")
def criar_anotacao(nome_do_caderno: str, titulo_da_anotacao: str):
    resposta =  pegar_pelo_titulo(nome_do_caderno,'CADERNOS')
    if not resposta:
        return {"Status": 404, "Mensagem": "Não existe um Caderno com esse nome!"}
    else:
        id_caderno = resposta[0].ID_CADERNO
        resposta =  pegar_pelo_titulo(titulo_da_anotacao,'ANOTACOES')
        if resposta:
            return {"Status": 404, "Mensagem": "Já existe uma Anotação com este nome!"}
        
        else:
            try:
                db.criar_anotacao({'TITULO':titulo_da_anotacao,'ID_CADERNO':id_caderno},commit=True)
                return {"Status": 200, "Mensagem": "Anotação criada com sucesso!"}
            except Exception:
                traceback.print_exc()
                return {"Status": 404, "Mensagem": "Erro inesperado! Cheque os logs!"}
