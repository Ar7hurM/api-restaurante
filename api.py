from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from mysql.connector import IntegrityError
import mysql.connector

app = FastAPI()

# CONEXÃO COM BANCO
conexao = mysql.connector.connect(
    host="172.18.152.213",
    user="api",
    passwd="123",
    database="bancoapi"
)

cursor = conexao.cursor()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    nome: str
    endereco: str

class EsqueciSenhaRequest(BaseModel):
    email: str
    password: str

class DeletarUsuarioRequest(BaseModel):
    email: str
    senha: str

class ProdutoRequest(BaseModel):
    nome_produto: str
    descricao: str
    valor: float

class DeletarProdutoRequest(BaseModel):
    nome_produto: str

class AtualizarProdutoRequest(BaseModel):
    nome_produto: str
    valor_produto: float

class CriarPedidoRequest(BaseModel):
    id_pedido: int
    nome_produto: str
    nome: str

class DeletarPedidoRequest(BaseModel):
    id_pedido: int
    nome_pedido: str

class AtualizarPedidoRequest(BaseModel):
    id_pedido: int
    nome_produto: str
    nome_produto_atual: str

class MostrarUsuariosRequest(BaseModel):
    id: int
    nome: str
    email: str
    endereco: str


# ROTAS

@app.get("/criartabelas")
def criar_tabelas():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT NOT NULL AUTO_INCREMENT,
            nome VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL,
            senha VARCHAR(50) NOT NULL,
            endereco VARCHAR(50) NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY nome (nome)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INT NOT NULL AUTO_INCREMENT,
            nome_produto VARCHAR(60) NOT NULL,
            descricao VARCHAR(100) DEFAULT NULL,
            valor FLOAT NOT NULL,
            PRIMARY KEY (id_produto),
            UNIQUE KEY nome_produto (nome_produto)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido INT NOT NULL,
            nome_produto_fk VARCHAR(100) NOT NULL,
            nome_fk VARCHAR(100) NOT NULL,
            KEY nome_produto_fk (nome_produto_fk),
            KEY nome_fk (nome_fk),
            CONSTRAINT pedidos_ibfk_1 FOREIGN KEY (nome_produto_fk) REFERENCES produtos (nome_produto),
            CONSTRAINT pedidos_ibfk_2 FOREIGN KEY (nome_fk) REFERENCES usuarios (nome)
        )
    """)
    conexao.commit()
    return {"mensagem": "Tabelas criadas com sucesso!"}


@app.post("/login")
def login(data: LoginRequest):
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (data.email, data.password))
    linha_user = cursor.fetchone()
    if linha_user:
        return {"mensagem": f"Login com o email {data.email} realizado com sucesso!"}
    else:
        raise HTTPException(status_code=404, detail="Email ou senha inválidos!")


@app.post("/register")
def register(data: RegisterRequest):
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, endereco) VALUES (%s, %s, %s, %s)",
            (data.nome, data.email, data.password, data.endereco)
        )
        conexao.commit()

        return {"mensagem": f"Usuário {data.nome} cadastrado com sucesso!"}

    except IntegrityError as e:
        conexao.rollback()
        if "Duplicate entry" in str(e):
            return {"mensagem": "Usuário já cadastrado com este nome ou e-mail."}
        else:
            raise HTTPException(status_code=400, detail="Erro de integridade no banco de dados.")

    except Exception as e:
        conexao.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/esqueci-senha")
def esqueci_senha(data: EsqueciSenhaRequest):
    cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (data.password, data.email))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="E-mail não cadastrado")
    return {"mensagem": "Senha atualizada com sucesso!"}


@app.delete("/delete")
def deletar_user(data: DeletarUsuarioRequest):
    cursor.execute("DELETE FROM usuarios WHERE email = %s AND senha = %s", (data.email, data.senha))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="O email ou senha informados não coincidem!")
    return {"mensagem": "Usuário deletado com sucesso!"}

@app.get("/mostraruser")
def mostrar_usuarios():
    cursor.execute("SELECT * FROM usuarios")
    result = cursor.fetchall()
    if result:
        return {"usuarios" : result}
    else:
        raise HTTPException(status_code=404, detail="Ocorreu um erro, tente novamente mais tarde!")


@app.post("/adicionarp")
def adicionar_produto(data: ProdutoRequest):
    cursor.execute("INSERT INTO produtos (nome_produto, descricao, valor) VALUES (%s, %s, %s)",
                   (data.nome_produto, data.descricao, data.valor))
    conexao.commit()
    return {"mensagem": "Produto adicionado com sucesso!"}


@app.delete("/deletep")
def deletar_produto(data: DeletarProdutoRequest):
    cursor.execute("DELETE FROM produtos WHERE nome_produto = %s", (data.nome_produto,))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")
    return {"mensagem": f"Produto {data.nome_produto} deletado com sucesso!"}


@app.put("/atualizarp")
def atualizar_produto(data: AtualizarProdutoRequest):
    cursor.execute("UPDATE produtos SET valor = %s WHERE nome_produto = %s", (data.valor_produto, data.nome_produto))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Não foi possível atualizar o produto.")
    return {"mensagem": f"Valor do produto {data.nome_produto} atualizado para {data.valor_produto}!"}


@app.get("/verproduto")
def visualizar_produto(nome_produto: str):
    cursor.execute("SELECT * FROM produtos WHERE nome_produto = %s", (nome_produto,))
    resultado = cursor.fetchall()
    if resultado:
        return {"produtos": resultado}
    raise HTTPException(status_code=404, detail="Produto não encontrado!")


@app.post("/criarped")
def criar_pedido(data: CriarPedidoRequest):
    cursor.execute("INSERT INTO pedidos (id_pedido, nome_produto_fk, nome_fk) VALUES (%s, %s, %s)",
                   (data.id_pedido, data.nome_produto, data.nome))
    conexao.commit()
    return {"mensagem": "Pedido criado com sucesso!"}


@app.delete("/deleteped")
def deletar_pedido(data: DeletarPedidoRequest):
    cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s AND nome_fk = %s", (data.id_pedido, data.nome_pedido))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    return {"mensagem": f"Pedido de id {data.id_pedido} deletado com sucesso!"}


@app.put("/atualizarped")
def atualizar_pedido(data: AtualizarPedidoRequest):
    cursor.execute(
        "UPDATE pedidos SET nome_produto_fk = %s WHERE id_pedido = %s AND nome_produto_fk = %s",
        (data.nome_produto, data.id_pedido, data.nome_produto_atual)
    )
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Não foi possível atualizar o pedido.")
    return {"mensagem": f"Pedido {data.id_pedido} atualizado para produto {data.nome_produto}!"}


@app.get("/visualizarped")
def visualizar_pedido(id_pedido: int, nome_cliente: str):
    cursor.execute("SELECT * FROM pedidos WHERE id_pedido = %s AND nome_fk = %s", (id_pedido, nome_cliente))
    resultado = cursor.fetchall()
    if resultado:
        return {"pedidos": resultado}
    raise HTTPException(status_code=404, detail="Pedido não encontrado!")
