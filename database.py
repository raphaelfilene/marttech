# -*- coding: utf-8 -*-
import sqlite3
import os, traceback
from random import randint
from time import time


class Database:
    NOME_DB = 'dados.db'
    VALOR_MAX_IDS = 9999999999
    TABELAS = ['CADERNOS','ANOTACOES','TAGS']

    def __init__(self,testar=False):
        self.con = sqlite3.connect(self.NOME_DB,check_same_thread=False)
        self.con.text_factory=str
        self.cursor = self.con.cursor()

        if testar: # coloquei essa flag para poder testar com mais facilidades
            self.__teste()

    
    def __criar_tabelas(self, mostrar_logs=False):
        # criando a tabela CADERNOS
        try:
            self.cursor.execute("CREATE TABLE CADERNOS (ID_CADERNO INTEGER PRIMARY KEY, NOME TEXT UNIQUE, DESCRICAO TEXT);")
        except Exception:
            if mostrar_logs:
                traceback.print_exc()

        # criando a tabela ANOTACOES
        try:
            self.cursor.execute("CREATE TABLE ANOTACOES (ID_ANOTACAO INTEGER PRIMARY KEY, ID_CADERNO INTEGER NOT NULL, TITULO TEXT UNIQUE, TIMESTAMP_CRIACAO INTEGER, TIMESTAMP_MODIFICACAO INTEGER);")
        except Exception:
            if mostrar_logs:
                traceback.print_exc()
        
        # criando a tabela TAGS
        try:
            self.cursor.execute("CREATE TABLE TAGS (ID_TAG INTEGER PRIMARY KEY, ID_ANOTACAO INTEGER NOT NULL, ID_CADERNO INTEGER NOT NULL, TAG TEXT);")
        except Exception:
            if mostrar_logs:
                traceback.print_exc()
    
    def __criar_id_unico(self,tabela):
        id = randint(1,self.VALOR_MAX_IDS)
        
        if tabela == 'TAGS':
            self.cursor.execute("SELECT * FROM TAGS WHERE ID_TAG = %s"%id)
        
        elif tabela == 'ANOTACOES':
            self.cursor.execute("SELECT * FROM ANOTACOES WHERE ID_ANOTACAO= %s"%id)
        
        else:
            self.cursor.execute("SELECT * FROM CADERNOS WHERE ID_CADERNO= %s"%id)
        
        # garantindo que o ID seja único
        if len(self.cursor.fetchall()):
            return self.__criar_id_unico(tabela)

        return id
    
    def __deletar_tudo(self):
        try:
            for tabela in self.TABELAS:
                self.cursor.execute("DROP TABLE %s"%tabela)
            
            self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def __checando_dado(self,dado,tipo):
        # checando se o dado é válido
        if tipo == 'tabela':
            assert dado in self.TABELAS
        
        elif tipo == 'caderno':
            assert len({'NOME','DESCRICAO'}.difference(set(dado.keys()))) == 0
        
        elif tipo == 'anotacao':
            assert len({'ID_CADERNO','TITULO'}.difference(set(dado.keys()))) == 0
        
        elif tipo == 'tag':
            assert len({'ID_ANOTACAO','ID_CADERNO'}.difference(set(dado.keys()))) == 0
    
    def criar_caderno(self,caderno,commit=False):
        self.__checando_dado(caderno,'caderno')

        try:
            id_caderno = self.__criar_id_unico('CADERNOS')
            self.cursor.execute("INSERT INTO CADERNOS VALUES (%s,'%s','%s')"%(id_caderno,caderno['NOME'],caderno['DESCRICAO']))

            if commit: self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def criar_anotacao(self,anotacao,commit=False):
        self.__checando_dado(anotacao,'anotacao')

        try:
            id_anotacao = self.__criar_id_unico('ANOTACOES')
            timestamp = int(time())
            self.cursor.execute("INSERT INTO ANOTACOES VALUES (%s,%s,'%s',%s,%s)"%(id_anotacao,anotacao['ID_CADERNO'],anotacao['TITULO'],timestamp,timestamp))

            if commit: self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def criar_tag(self,tag,commit=False):
        self.__checando_dado(tag,'tag')

        try:
            id_tag = self.__criar_id_unico('TAGS')
            timestamp = int(time())
            self.cursor.execute("INSERT INTO TAGS VALUES (%s,%s,%s,'%s')"%(id_tag,tag['ID_ANOTACAO'],tag['ID_CADERNO'],tag['TAG']))

            if commit: self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def deletar_tabela(self,id_tabela,tabela,commit=False):
        self.__checando_dado(tabela,'tabela')

        try:
            if tabela == 'TAGS':
                self.cursor.execute("DELETE FROM TAGS WHERE ID_TAG = %s"%id_tabela)

                if commit: self.con.commit()
            
            elif tabela == 'ANOTACOES':
                self.cursor.execute("SELECT ID_TAG FROM TAGS WHERE ID_ANOTACAO = %s"%id_tabela)
                ids_tags = [i[0] for i in self.cursor.fetchall()]
                
                for id_tag in ids_tags:
                    self.deletar_tabela(id_tag,'TAGS')

                self.cursor.execute("DELETE FROM ANOTACOES WHERE ID_ANOTACAO = %s"%id_tabela)

                if commit: self.con.commit()
            
            else:
                self.cursor.execute("SELECT ID_ANOTACAO FROM ANOTACOES WHERE ID_CADERNO = %s"%id_tabela)
                ids_anotacoes = [i[0] for i in self.cursor.fetchall()]

                for id_anotacao in ids_anotacoes:
                    self.deletar_tabela(id_anotacao,'ANOTACOES')
                
                self.cursor.execute("DELETE FROM CADERNOS WHERE ID_CADERNO = %s"%id_tabela)

                if commit: self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def __formatar_dados(self,tabela,dados):
        self.__checando_dado(tabela,'tabela')
        
        # transforma os dados retornados do banco em dicionários mais organizados
        retorno = []

        if tabela == 'CADERNOS':
            for linha in dados:
                retorno.append({
                    'ID_CADERNO': linha[0],
                    'NOME': linha[1],
                    'DESCRICAO': linha[2]
                })
        
        elif tabela == 'ANOTACOES':
            for linha in dados:
                retorno.append({
                    'ID_ANOTACAO': linha[0],
                    'ID_CADERNO': linha[1],
                    'TITULO': linha[2],
                    'TIMESTAMP_CRIACAO': linha[3],
                    'TIMESTAMP_MODIFICACAO': linha[4]
                })
        
        else:
            for linha in dados:
                retorno.append({
                    'ID_TAG': linha[0],
                    'ID_ANOTACAO': linha[1],
                    'ID_CADERNO': linha[2],
                    'TAG': linha[3]
                })
        
        return retorno
    
    def pegar_dados_por_titulo(self,titulo,tabela):
        self.__checando_dado(tabela,'tabela')
        
        if tabela == 'CADERNOS':
            self.cursor.execute("SELECT * FROM CADERNOS WHERE NOME = '%s'"%titulo)
        
        elif tabela == 'ANOTACOES':
            self.cursor.execute("SELECT * FROM ANOTACOES WHERE TITULO = '%s'"%titulo)
        
        else:
            self.cursor.execute("SELECT * FROM TAGS WHERE TAG = '%s'"%titulo)
        
        retorno = self.cursor.fetchall()
        
        if retorno and len(retorno):
            return self.__formatar_dados(tabela,retorno)
        return None
    
    def pegar_dados_pelo_id(self,id_tabela,tabela):
        self.__checando_dado(tabela,'tabela')
        
        if tabela == 'CADERNOS':
            self.cursor.execute("SELECT * FROM CADERNOS WHERE ID_CADERNO = %s"%id_tabela)
        
        elif tabela == 'ANOTACOES':
            self.cursor.execute("SELECT * FROM ANOTACOES WHERE ID_ANOTACAO = %s"%id_tabela)
        
        else:
            self.cursor.execute("SELECT * FROM TAGS WHERE ID_TAG = %s"%id_tabela)
        
        return self.__formatar_dados(tabela,self.cursor.fetchall())
    
    def retornar_tudo(self,tabela):
        self.__checando_dado(tabela,'tabela')

        self.cursor.execute("SELECT * FROM %s"%tabela)
        return self.__formatar_dados(tabela,self.cursor.fetchall())
    
    def editar(self,tabela,dados_atualizados,commit=False):
        self.__checando_dado(tabela,'tabela')

        try:
            if tabela == 'CADERNOS':
                self.cursor.execute("UPDATE CADERNOS SET NOME='%s', DESCRICAO ='%s' WHERE ID_CADERNO=%s"%(dados_atualizados['NOME'],dados_atualizados['DESCRICAO'],dados_atualizados['ID_CADERNO']))
            
            elif tabela == 'ANOTACOES':
                timestamp = int(time())
                self.cursor.execute("UPDATE ANOTACOES SET TITULO='%s', TIMESTAMP_MODIFICACAO =%s WHERE ID_ANOTACAO=%s"%(dados_atualizados['TITULO'],timestamp,dados_atualizados['ID_ANOTACAO']))
            
            elif tabela == 'TAGS':
                timestamp = int(time())
                self.cursor.execute("UPDATE TAGS SET TAG='%s' WHERE ID_TAG=%s"%(dados_atualizados['TAG'],dados_atualizados['ID_TAG']))
            
            if commit: self.con.commit()
        
        except Exception:
            traceback.print_exc()
    
    def __teste(self):
        self.__criar_tabelas(mostrar_logs=True)

        commit = True
        
        deletar_tudo = False
        criar = False
        mostrar = False
        deletar = False
        editar = False

        if criar:
            self.criar_caderno({'NOME':'Caderno de Teste','DESCRICAO':'Descrição teste'},commit)

            cadernos = self.retornar_tudo('CADERNOS')
            self.criar_anotacao({'TITULO':'Título de Teste','ID_CADERNO':cadernos[0]['ID_CADERNO']},commit)

            anotacoes = self.retornar_tudo('ANOTACOES')
            self.criar_tag({'TAG':'Tag de Teste','ID_CADERNO':cadernos[0]['ID_CADERNO'], 'ID_ANOTACAO':anotacoes[0]['ID_ANOTACAO']},commit)
        

        if mostrar:

            print('\n\n\nCADERNOS...')
            cadernos = self.retornar_tudo('CADERNOS')
            for caderno in cadernos:
                print('\n')
                for key in caderno.keys():
                    print(key,caderno[key])

            print('\n\n\ANOTACOES...')
            anotacoes = self.retornar_tudo('ANOTACOES')
            for anotacao in anotacoes:
                print('\n')
                for key in anotacao.keys():
                    print(key,anotacao[key])

            print('\n\n\TAGS...')
            tags = self.retornar_tudo('TAGS')
            for tag in tags:
                print('\n')
                for key in tag.keys():
                    print(key,tag[key])
            print('\n\n')
        
        if editar:
            self.editar('CADERNOS',{'NOME':'Novo Nome','DESCRICAO':'Nova Descrição','ID_CADERNO':6499617474},commit)
            self.editar('ANOTACOES',{'TITULO':'Novo Titulo','ID_ANOTACAO':8277781654},commit)
            self.editar('TAGS',{'TAG':'Nova Tag','ID_TAG':3502659870},commit)

        if deletar:
            cadernos = self.retornar_tudo('CADERNOS')
            for caderno in cadernos:
                self.deletar_tabela(caderno['ID_CADERNO'],'CADERNOS',commit)
        
        if deletar_tudo:
            self.__deletar_tudo()
