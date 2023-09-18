# =============================================================================
""" 1 - Carga Inicial.
"""
# =============================================================================
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

# ===============================================================================
""" 2 - Inicializa variáveis de Informações gerais de identificação do serviço.
"""
#  ==============================================================================
info = Info(title="API Search in Museum", version="1.0.0")
app = OpenAPI(__name__, info=info)

home_tag = Tag(name="Documentação", description="Apresentação da documentação via Swagger.")
obra_tag = Tag(name="Rota em smuseum", description="Realiza busca de link de imagem de obra de arte")
doc_tag = Tag(name="Rota em Search in Museum", description="Documentação da API Search in Museum no github")

# ==============================================================================
""" 3 - Inicializa "service_name" para fins de geração de arquivo de log.
"""
# ==============================================================================
service_name = "smuseum"
logger = setup_logger(service_name)

# ==============================================================================
""" 4 - Configurações de "Cross-Origin Resource Sharing" (CORS).
# Foi colocado "supports_credentials=False" para evitar possíveis conflitos com
# algum tipo de configuração de browser. Mas não é a melhor recomendação por 
# segurança. Para melhorar a segurança desta API, o mais indicado segue nas 
# linhas abaixo comentadas.
#> origins_permitidas = ["Obras de Arte"]
#> Configurando o CORS com suporte a credenciais
#> CORS(app, origins=origins_permitidas, supports_credentials=True)
#> CORS(app, supports_credentials=True, expose_headers=["Authorization"])
#> Adicionalmente utilizar da biblioteca PyJWT
"""
# ==============================================================================
CORS(app, supports_credentials=False)

# ================================================================================
""" 5.1 - DOCUMENTAÇÂO: Rota "/" para geração da documentação via Swagger.
"""
# ================================================================================
@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi/swagger.
    """
    return redirect('/openapi/swagger')

# ================================================================================
""" 5.2 - DOCUMENTAÇÂO: Rota "/doc" para documentação via github.
"""
# ================================================================================
@app.get('/doc', tags=[doc_tag])
def doc():
    """Redireciona para documentação no github.
    """
    return redirect('https://github.com/Moriblo/smuseum')

# ==============================================================================++
""" 6.1 - Rota "/smuseum" para tratar o fetch de `GET`.
"""
# ==============================================================================++
@app.get('/smuseum', methods=['GET'], tags=[obra_tag],
            responses={"200": SmuseumSchema, "500": ErrorSchema})

def link(query: SmuseumBuscaSchema):
    """Busca link de imagem de obra de arte a partir do nome do Artista e Obra.
    """
    
    # ==============================================================================
    """ 6.1.1 - Lê pela chamada na rota /smuseum os valores para realização da 
        consulta.
    """
    # ==============================================================================
    busca_obra = request.args.get('nome')
    busca_artista = request.args.get('artista')

    # ==============================================================================
    """ 6.1.2 - Inicialização de Variáveis.

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
    contador_obras = 0
    error_code = "200"

    # Inicia as variáveis para o MET
    museu = "MET"
    museum_url_search = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&artistOrCulture=true&q="
    museum_url_object = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

    campo_obra = "title"
    campo_total = "total"
    campo_ID = "objectIDs"
    campo_result = "primaryImage"

    # ==============================================================================
    """ 6.1.3 - Define URL para a realização da consulta.
    """
    # ==============================================================================
    search_url = f'{museum_url_search}{busca_artista}'

    # ==============================================================================
    """ 6.1.4 - Retorna os IDs e total de objetos, CASO HAJA ARTISTA, e trata erro 
    caso não exista o artista na BD do museu.
    """
    # ==============================================================================
    try:
        response = requests.get(search_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if (err):
            error_msg = err
            error_code = "500"
            print(f'Erro HTTP: {err}')
            return {"mesage": error_msg}, error_code

    total_objetos = response.json()[campo_total]
    object_ids = response.json()[campo_ID]
    
    # ==============================================================================
    """ 6.1.5 - Coleta o nome de cada obra, a partir dos IDs associados ao artista,
        e verifica se esse nome corresponde a obra procurada.
    """
    # ==============================================================================
    if (total_objetos != 0):

        # Obtém informações sobre cada objeto (obra)
        artworks = []
        for object_id in object_ids:
            object_url = f"{museum_url_object}{object_id}"
            response = requests.get(object_url)
            artwork = response.json()
            artworks.append(artwork)

        # Armazena os resultados em uma "base de dados" JSON
        with open("artworks.json", "w") as f:
            json.dump(artworks, f)

        # Abre o arquivo para posicionar a leitura no início do arquivo e 
        # converte-lo em uma lista.
        with open("artworks.json", "r") as f:
            data = json.load(f)

        # Inicializa um contador de vezes em que uma dada obra aparece para 
        # um dado artista. Inicializa um vetor "índices" que vai coletar os números 
        # dos índices dos registros encontrados na lista 'data'.
        indices = []

        # Percorre a lista 'data'
        for i, DB in enumerate(data):

            # Verifica se o conteúdo da variável 'campo_obra' é um campo dentro 
            # do dicionário.
            if (campo_obra in DB):

                # Verifica se, dado um título de uma obra ('busca_obra'), este 
                # título consta, total ou parcialmente (str(DB[campo_obra]), na 
                # lista 'DB' para o campo 'campo_obra', considerando ambos em
                # low case (No Caps)
                if busca_obra and DB[campo_obra] and busca_obra.lower() in \
                    str(DB[campo_obra]).lower():

                    # Incrementa o contador e coleta o número do índice do 
                    # registro na lista.
                    contador_obras += 1
                    indices.append(i)

        # Verifica se foram encontradas obras para o artista informado
        if (indices):
            # Havendo obra(s) para o artista informado, coleta a informação do 
            # link de imagem para a primeira ocorrência
            busca_link = data[indices[0]][campo_result]
            logger.warning(f"Msg[1] Dados para registro: Lnk: {busca_link}, Obr: {busca_obra}, Art: {busca_artista}")
        else:
            # Trata erro por não ter encontrado A OBRA para o artista.
            busca_link = f'Erro_[1]: Existem {total_objetos} obras deste artista no museu {museu}. Porém nenhuma como {busca_obra}'
            logger.warning(f"Erro_[1]: Existem {total_objetos} obras deste artista no museu {museu}. Porém nenhuma como {busca_obra}")
    else:
        #Trata erro quando não encontra NENHUMA obra para o artista.
        busca_link = f'Erro_[2]: Não há obras do artista {busca_artista} no museu {museu}")'
        logger.warning(f"Erro_[2]: Não há obras do artista {busca_artista} no museu {museu}")
        error_code = "404"

    # ==============================================================================
    """ 6.1.6 - "Monta" o JSON" e retorna o resultado da busca ou a tratativa do erro.
    """
    # ==============================================================================
    json_response = ujson.dumps({
        "link": busca_link,
        "obra": busca_obra,
        "artista": busca_artista,
        "total_obras":  total_objetos,
        "qtde_msmnome": contador_obras,
        "museu": museu
    })

    return Response(json_response, content_type='application/json'), error_code

# ===============================================================================
""" 7 - Garante a disponibilidade da API em "suspenso".
"""
# ===============================================================================
if __name__ == '__main__':
    app.run(port=5002, debug=True)
