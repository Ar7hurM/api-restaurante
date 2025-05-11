from typing import Union
from fastapi import FastAPI, HTTPException, status
from fastapi import Request
from fastapi.responses import HTMLResponse
import mysql.connector

app = FastAPI()

# INICIAR BANCO
conexao = mysql.connector.connect(
    host="172.18.152.213",
    user="api",
    passwd = "123",
    database="restaurante"
)

cursor = conexao.cursor()


# CRIAR TABELA
@app.get("/criartabelas")
def criar_tabelas(request: Request):
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE usuarios (id int NOT NULL AUTO_INCREMENT,nome varchar(50) NOT NULL,email varchar(50) NOT NULL,senha varchar(50) NOT NULL,endereco varchar(50) NOT NULL,PRIMARY KEY (id),UNIQUE KEY nome (nome))")
    cursor.execute("CREATE TABLE produtos (id_produto int NOT NULL AUTO_INCREMENT,nome_produto varchar(60) NOT NULL,descricao varchar(100) DEFAULT NULL,valor float NOT NULL,PRIMARY KEY (id_produto),UNIQUE KEY nome_produto (nome_produto))")
    cursor.execute("CREATE TABLE pedidos (id_pedido int NOT NULL,nome_produto_fk varchar(100) NOT NULL,nome_fk varchar(100) NOT NULL,KEY nome_produto_fk (nome_produto_fk),KEY nome_fk (nome_fk),CONSTRAINT pedidos_ibfk_1 FOREIGN KEY (nome_produto_fk) REFERENCES produtos (nome_produto),CONSTRAINT pedidos_ibfk_2 FOREIGN KEY (nome_fk) REFERENCES usuarios (nome))")
    conexao.commit()
    return {"mensagem": "Tabelas criadas com suceso!"}

# TABELA USUARIOS
@app.post("/login")
def login(request: Request, email: str, password: str):
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, password))
    linha_user = cursor.fetchone()
    if linha_user != None:
        return f"Login com o email {email} realizado com sucesso!"
    else:
        raise HTTPException(status_code=404, detail="Email ou senha inválidos!")


@app.post("/register")
def register(request: Request, email: str, password: str, nome: str, endereco: str):
    cursor = conexao.cursor()    

    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha, endereco) VALUES (%s,%s,%s,%s)", (nome, email, password, endereco))
        conexao.commit()
        return f"Usuário {nome} cadastrado com sucesso!"
    finally:
        conexao.close()
        cursor.close()


@app.get("/esqueci-senha")
def esqueci_senha(request: Request, email: str, password: str):
    cursor = conexao.cursor()
    cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (password,email))
    linhas_afetadas = cursor.rowcount
    conexao.commit()
    if linhas_afetadas == 0:
        raise HTTPException(status_code=400, detail="E-mail não cadastrado")
    return {"Senha atualizada!"}



@app.post("/delete")
def deletar_user(request: Request, email: str, senha: str):
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM usuarios WHERE email = %s AND senha = %s",(email,senha))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="O email ou senha informados não coincidem!")
    else:
        return {"Usuário deletado"}


# TABELA PRODUTOS   
@app.get("/adicionarp")
def adicionar_produto(request: Request, nome_produto: str, descricao: str, valor: str):
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO produtos (nome_produto, descricao, valor) VALUES (%s, %s, %s)", (nome_produto, descricao, valor))
    conexao.commit()
    return {"Produto adicionado"}

@app.get("/deletep")
def deletar_produto(request: Request, nome_produto: str, valor: float):
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM produtos WHERE nome_produto = %s",(nome_produto,))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"O produto ou valor inseridos não coincidem!")
    else:
        return f"Produto {nome_produto} deletado!"

@app.get("/atualizarp")
def atualizar_produto(request: Request, nome_produto: str, valor_produto: float):
    cursor = conexao.cursor()
    cursor.execute("UPDATE produtos SET valor = %s WHERE nome_produto = %s", (valor_produto, nome_produto))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=400, detail="Não foi possível atualizar o produto, verifique os dados informados!")
    return {"Valor atualizado para:",valor_produto}

@app.post("/verproduto")
def visualizar_produto(request: Request, nome_produto: str):
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM produtos WHERE nome_produto = %s", (nome_produto,))
    resultado = cursor.fetchall()
    if resultado:
        return {"produtos": resultado}
    else:
        raise HTTPException(status_code=404, detail=f"O produto {nome_produto} não foi encontrado")

# TABELA PEDIDOS   
@app.get("/criarped")
def criar_pedido(request: Request, nome_produto: str, nome: str, id_pedido: str):
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO pedidos (id_pedido, nome_produto_fk, nome_fk) VALUES (%s, %s, %s)", (id_pedido, nome_produto, nome))
    conexao.commit()
    return {"Pedido realizado"}

@app.get("/deleteped")
def deletar_pedido(request: Request, id_pedido: int, nome_pedido: str):
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s AND nome_fk = %s", (id_pedido, nome_pedido))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"O pedido ou nome informado não coincidem!")
    else:
        return f"O pedido de id = {id_pedido} do cliente = {nome_pedido} foi deletado"

@app.get("/atualizarped")
def atualizar_pedido(request: Request, id_pedido: int, nome_produto: str, nome_produto_atual: str):
    cursor = conexao.cursor()
    cursor.execute("UPDATE pedidos SET nome_produto_fk = %s WHERE id_pedido = %s AND nome_produto_fk = %s", (nome_produto, id_pedido, nome_produto_atual))
    conexao.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=400, detail=f"Não foi possível atualizar o pedido, verifique os dados informados!")
    else:
        return f"O pedido de id = {id_pedido} com o produto = {nome_produto_atual} foi alterado para {nome_produto}"

@app.post("/visualizarped")
def visualizar_pedido(request: Request, id_pedido: int, nome: str):
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE id_pedido = %s AND nome_fk = %s", (id_pedido, nome))
    resultado = cursor.fetchall()
    if resultado:
        return {"pedidos": resultado}
    else:
        raise HTTPException(status_code=404, detail="O pedido informado não foi encontrado!")