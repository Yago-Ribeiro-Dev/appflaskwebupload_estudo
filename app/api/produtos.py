from flask import Blueprint
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def configure(app):
    db.init_app(app)
    app.db = db


produtos = Blueprint("produtos",__name__)


def saldo_prazo_por_marca(page):
      with db.engine.connect() as conn:
        produtoprazo = (text("""
            DECLARE @PageNumber AS INT
            DECLARE @RowsOfPage AS INT
            SET @PageNumber= {}
            SET @RowsOfPage= 8
            SELECT pbasico.[SKU],pbasico.[NomeProduto],pbasico.[EAN]
            ,pbasico.[EstoqueLocal],pbasico.[SaldoAtual],pprazo.PrazoProducao,pbasico.EstoqueAtual
            ,CAST(psaldo.[DataAtualizado] as date) as dataatualizacao
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            JOIN [HauszMapa].[Produtos].[ProdutoDetalhe] as pdetalhe
            ON pdetalhe.IdProduto = pbasico.IdProduto
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] as psaldo
            ON psaldo.SKU = pbasico.SKU
            JOIN [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pprazo
            ON pprazo.SKU = pbasico.SKU
            JOIN [HauszMapa].[Estoque].[Estoque] as pestoq
            ON pestoq.IdEstoque = pbasico.EstoqueAtual
            WHERE pbasico.EstoqueAtual = 3
            ORDER BY [dataatualizado] DESC
            OFFSET (@PageNumber-1)*@RowsOfPage ROWS
            FETCH NEXT @RowsOfPage ROWS ONLY""".format(page)))
        exec_produtoprazo = conn.execute(produtoprazo).all()
        


