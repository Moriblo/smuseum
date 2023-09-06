from flask import redirect, request, Flask, jsonify, make_response
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import Response

from urllib.parse import unquote
from model import Session
from schemas import *

import os, sys, json, ujson
import requests


from logger import setup_logger

# ==============================================================================
""" Inicializa service_name com o nome exclusivo do serviço para fins de geração
    de arquivo de log.
"""
# ==============================================================================
service_name = "smuseum"
logger = setup_logger(service_name)

# ==============================================================================
""" Informações de identificação, acesso e documentação do serviço
"""
# ==============================================================================
info = Info(title="Busca link de foto de obra em um dado museu", version="1.0.0")
app = OpenAPI(__name__, info=info)

# ==============================================================================
""" Configurações de "Cross-Origin Resource Sharing"
"""
# ==============================================================================
# Foi colocado "supports_credentials=False" para evitar possíveis conflitos com
# algum tipo de configuração de browser. Mas não é a melhor recomendação por 
# segurança. Para melhorar a segurança desta API, o mais indicado segue nas 
# linhas abaixo comentadas.
CORS(app, supports_credentials=False)

# origins_permitidas = ["Obras de Arte"]
# Configurando o CORS com suporte a credenciais
# CORS(app, origins=origins_permitidas, supports_credentials=True)
# CORS(app, supports_credentials=True, expose_headers=["Authorization"])
# Adicionalmente utilizar da biblioteca PyJWT

# ==============================================================================
""" Rota /tradutor para tratar o fetch de `GET` do script.js.
"""
# ==============================================================================
@app.route('/smuseum', methods=['GET'])
def link():
    
    # Lê o valor do parâmetro de consulta 'entrada' da solicitação
    busca_obra = request.args.get('obra')
    busca_artista = request.args.get('artista')

    # ==============================================================================
    """ Inicialização de Variáveis.

        <museu - Nome do museu>, <museum_url_search - Rota para busca Inicial>
        <museum_url_object - Rota de busca dos objetos retornados na busca inicial>
        <campo_obra - Nome do campo que contém o Título da Obra>, 
        <campo_total - Nome do campo que contém o Total de ocorrências de objeto>
        <campo_ID - Nome do campo que contém o "ID number" de cada objeto buscado>
        <campo_result - Nome do campo que contém o link da imagem>
        
        O objetivo desta inicialização de variáveis é permitir que esta API
        possa ser utilizada no futuro, recebendo todas estas variáveis pela rota 
        /smuseum, e com isso permitir buscas para qualquer museu registrado em 
        uma base externa. Como não foi possível achar outro museu sem restrições
        de "copyright" e acessibilidade de API, estamos utilizando:

        Metropolitan Museum of Art (The Met: https://www.metmuseum.org/pt)
        e todas as variáveis estão sendo inicializadas com os dados referentes a 
        este museu.
    """
    # ==============================================================================

    ### Inicia as variáveis para o MET
    museu = "MET"
    museum_url_search = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&artistOrCulture=true&q="
    museum_url_object = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

    campo_obra = "title"
    campo_total = "total"
    campo_ID = "objectIDs"
    campo_result = "primaryImage"

    # URL para a pesquisa
    search_url = f'{museum_url_search}{busca_artista}'
    
    # Realiza a pesquisa e retorna os IDs e total de objetos
    response = requests.get(search_url)
    total_objetos = response.json()[campo_total]
    object_ids = response.json()[campo_ID]

    # Verifica se foi encontrado o artista na base do museu
    if (total_objetos != 0):

        # Obtém informações sobre cada objeto em JSON
        artworks = []
        for object_id in object_ids:
            object_url = f"{museum_url_object}{object_id}"
            response = requests.get(object_url)
            artwork = response.json()
            artworks.append(artwork)

        # Armazena os resultados em uma "base de dados" JSON
        with open("artworks.json", "w") as f:
            json.dump(artworks, f)

        ## Abre o arquivo para posicionar a leitura no início do arquivo e 
        # converte o em uma lista.
        with open("artworks.json", "r") as f:
            data = json.load(f)

        ## Inicializa um contador de vezes em que uma dada obra aparece para 
        # um dado artista. Inicializa um vetor índices que vai coletar os números 
        # dos índices dos registros encontrados na lista 'data'.
        contador_obras = 0
        indices = []

        ## Percorre a lista 'data'
        for i, DB in enumerate(data):
            # Verifica se o conteúdo da variável 'campo_obra' é um campo dentro 
            # do dicionário.
            if (campo_obra in DB):

                # Verifica se, dado um título de uma obra ('busca_obra'), este 
                # título consta, total ou parcialmente (str(DB[campo_obra]), na 
                # lista 'DB' para o campo 'campo_obra'.
                if (busca_obra in str(DB[campo_obra])):

                    # Incrementa o contador e coleta o número do índice do 
                    # registro na lista.
                    contador_obras += 1
                    indices.append(i)

        # Verifica se foram encontradas obras para o artista informado
        if (indices):
            # Havendo obra(s) para o artista informado, coleta a informação do 
            # link de imagem para a primeira ocorrência
            busca_link = data[indices[0]][campo_result]
        else:
            # Registra no log o erro por não ter encontrado nenhuma obra para o 
            # artista
            busca_link = f'Erro: Não há essa obra no museu {museu}'
            logger.warning(f"Erro: Não foi possível encontrar a obra {busca_obra} para o artista {busca_artista} no museu {museu}")
        
        json_response = ujson.dumps({
            "link": busca_link,
            "obra": busca_obra,
            "artista": busca_artista, 
            "total_obras":  total_objetos, 
            "qtde_msmnome": contador_obras, 
            "museu": museu
        })
        print(f"Resposta: {json_response}")
        logger.debug(f"{json_response}")
        return Response(json_response, content_type='application/json')
    else:
        #Trata erro quando não encontra artista.
        busca_link = busca_link = f'Erro: Não há esse artista no museu {museu}'
        logger.warning(f"Erro: Não foram econtradas obras do artista {busca_artista} no museu {museu}")
    pass

if __name__ == '__main__':
    app.run(port=5002, debug=True)
