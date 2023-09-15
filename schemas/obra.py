from pydantic import BaseModel
from typing import Optional, List
from model.obra import Obra


class ObraSchema(BaseModel):
    """ Define como uma nova obra a ser inserida deve ser representada
    """
    nome: str = "Mona Lisa"
    artista: str = "Leonardo da Vinci"
    estilo: str = "Renascimento"
    tipo: str = "Pintura"
    link: str = "https://collections.louvre.fr/en/ark:/53355/cl010066723"


class ObraBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita com base na obra e artista.
    """
    nome: str = "Mona Lisa"
    artista: str = "Leonardo da Vinci"


class ListagemObrasSchema(BaseModel):
    """ Define como uma listagem de obras será retornada.
    """
    obras:List[ObraSchema]


def apresenta_obras(obras: List[Obra]):
    """ Retorna uma representação da obra seguindo o schema definido em
        ObraViewSchema.
    """
    result = []
    for obra in obras:
        result.append({
            "nome": obra.nome,
            "artista": obra.artista,
            "estilo": obra.estilo,
            "tipo": obra.tipo,
            "link": obra.link,
        })

    return {"obras": result}


class ObraViewSchema(BaseModel):
    """ Define como uma obra será retornada.
    """
    nome: str = "Mona Lisa"
    artista: str = "Leonardo da Vinci"
    estilo: str = "Renascimento"
    tipo: str = "Pintura"
    link: str = "https://collections.louvre.fr/en/ark:/53355/cl010066723"

class SmuseumSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma consulta de
        Artista e Obra de Arte.
    """
    link: str = "https://images.metmuseum.org/CRDImages/as/original/DP251139.jpg"
    obra: str = "Quail and Millet"
    artista: str = "Kiyohara Yukinobu" 
    total_obras: str = "4"
    qtde_msmnome: str = "1" 
    museu: str = "MET"

class SmuseumBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita com base na obra e artista.
    """
    nome: str = "Quail and Millet"
    artista: str = "Kiyohara Yukinobu"

class ObraDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str
    artista: str

def apresenta_obra(obra: Obra):
    """ Retorna uma representação da obra seguindo o schema definido em
        ObraViewSchema.
    """
    return {
        "nome": obra.nome,
        "artista": obra.artista,
        "estilo": obra.estilo,
        "tipo": obra.tipo,
        "link": obra.link,        
    }
