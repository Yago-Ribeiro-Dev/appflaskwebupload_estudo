from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def configure(app):
    db.init_app(app)
    app.db = db

def select_pedidos_vendas_marcas():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
            SELECT  pmarca.Marca,SUM(pflexy.[Quantidade] *
            pflexy.[PrecoUnitario]) as total
            FROM [HauszMapa].[Pedidos].[ItensFlexy] as pflexy
            JOIN [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            ON pbasico.SKU = pflexy.SKU
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Pedidos].[PedidoFlexy] AS pitens
            ON pitens.CodigoPedido = pflexy.CodigoPedido
            where pitens.StatusPedido in ('Pago','NF Emitida','Em Trânsito')
            AND MONTH(pflexy.[DataInserido]) = MONTH(getdate())
            GROUP BY pmarca.Marca,MONTH(pflexy.[DataInserido])"""))
                
        sellers = conn.execute(exec).all()
        for seller in sellers:
            sellerproduto = {
                'Marca':seller['Marca'],
                'total':seller['total']
            }
            lista_marcas.append(sellerproduto)
    return lista_marcas


def select_grafico_marcas():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
        SELECT SUM(pbasico.[SaldoAtual]) AS TOTALESTOQ
            ,pmarca.Marca
            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Estoque].[Estoque] as estoque
            ON estoque.IdEstoque = PBASICO.EstoqueAtual
            JOIN [HauszMapa].[Produtos].[Marca] pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            WHERE estoque.NomeEstoque = 'Fisico'
            GROUP BY estoque.NomeEstoque,pmarca.Marca"""))
            
                
        sellers = conn.execute(exec).all()
        for seller in sellers:
            sellerproduto = {
                'Marca':seller['Marca'],
                'total':seller['TOTALESTOQ']
            }
            lista_marcas.append(sellerproduto)
    return lista_marcas


def select_media_prazo_marcas():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
            SELECT AVG(prazo.[PrazoTotal]) AS 'MEDIAPRAZO',pmarca.Marca
            FROM [HauszMapa].[Produtos].[ProdutoPrazoProducFornec]  as prazo
            JOIN [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            ON pbasico.SKU = prazo.SKU
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca

            GROUP BY pmarca.Marca"""))
        prazos_marcas = conn.execute(exec).all()
        for prazos in prazos_marcas:
            prazo = {
                "PrazoTotal":prazos['MEDIAPRAZO'],
                "Marca":prazos['Marca']
            }
            lista_marcas.append(prazo)
    return lista_marcas
        

def select_marcas_perdas():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
            SELECT  count(sprice.[nomeseller]) AS TOTALANUNCIO
            ,sprice.[marcaprodutoseller]
            FROM [HauszMapaDev2].[dbo].[SellersPrices] as sprice
            WHERE diferenciapreco < 0 
            GROUP BY sprice.[marcaprodutoseller]"""))
        marcas = conn.execute(exec).all()
        for marca in marcas:
            items = {
                'TOTALANUNCIO':marca['TOTALANUNCIO'],
                'marcaprodutoseller':marca['marcaprodutoseller']
            }
            lista_marcas.append(items)
    return lista_marcas

        