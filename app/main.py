from datetime import date
import sqlite3
from sqlite3 import Error
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import List

app = FastAPI(
    title="API de Alunos",
    description="Esta API permite gerenciar dados de alunos, incluindo cadastro, listagem e consulta por CPF.",
    version="1.0.0"
)


# Modelo Pydantic
class User(BaseModel):
    cpf: int
    nome: str
    data_nascimento: date


# Conexão e criação de tabela
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('alunos.db', check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


def create_table(conn):
    try:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS alunos (
                                        cpf integer PRIMARY KEY,
                                        nome text NOT NULL,
                                        data_nascimento text NOT NULL
                                    ); """
        conn.execute(sql_create_table)
    except Error as e:
        print(e)


conn = create_connection()
if conn is not None:
    create_table(conn)
else:
    print("Falha ao criar a conexão com o DB!")


# Função para redirecionar para a documentação
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


# Endpoint para listar todos os alunos
@app.get("/alunos", response_model=List[User], description="Retorna todos os alunos cadastrados",
         summary="Listar alunos")
def get_alunos():
    cur = conn.cursor()
    cur.execute("SELECT * FROM alunos")
    rows = cur.fetchall()
    if rows:
        return [User(cpf=row[0], nome=row[1], data_nascimento=date.fromisoformat(row[2])) for row in rows]
    raise HTTPException(status_code=404, detail="Nenhum aluno encontrado")


# Endpoint para criar um novo aluno
@app.post("/alunos", description="Cria um novo aluno", summary="Criar aluno")
def create_aluno(user: User):
    sql = ''' INSERT INTO alunos(cpf,nome,data_nascimento)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (user.cpf, user.nome, user.data_nascimento.isoformat()))  # Convertendo para string no formato ISO
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    return {"message": "Usuário criado com sucesso"}


# Endpoint para obter um aluno pelo CPF
@app.get("/alunos/{cpf}", response_model=User, description="Retorna um aluno pelo CPF", summary="Obter aluno pelo cpf")
def get_aluno(cpf: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM alunos WHERE cpf=?", (cpf,))
    row = cur.fetchone()
    if row:
        return User(cpf=row[0], nome=row[1], data_nascimento=date.fromisoformat(row[2]))  # Convertendo de string para date
    raise HTTPException(status_code=404, detail="Usuário não encontrado")
