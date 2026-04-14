from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

app = FastAPI(title="API de Cashback")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Banco de Dados ──────────────────────────────────────────────────────────

def obter_conexao():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def inicializar_banco():
    with obter_conexao() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas (
                    id          SERIAL PRIMARY KEY,
                    ip_usuario  VARCHAR(50)    NOT NULL,
                    tipo_cliente VARCHAR(10)   NOT NULL,
                    valor_compra NUMERIC(10,2) NOT NULL,
                    cashback     NUMERIC(10,2) NOT NULL,
                    criado_em    TIMESTAMP     DEFAULT NOW()
                )
            """)
        conn.commit()

inicializar_banco()

# ── Lógica de Negócio ───────────────────────────────────────────────────────

CASHBACK_BASE_PERCENTUAL = 0.05
BONUS_VIP_PERCENTUAL     = 0.10
LIMITE_DOBRAR_CASHBACK   = 500.0

def calcular_cashback(tipo_cliente: str, valor_compra: float) -> float:
    """
    1. Cashback base = 5% do valor final
    2. Clientes VIP → +10% sobre o cashback base
    3. Compras acima de R$500 → dobra o cashback total
    """
    cashback = valor_compra * CASHBACK_BASE_PERCENTUAL

    if tipo_cliente.upper() == "VIP":
        cashback *= (1 + BONUS_VIP_PERCENTUAL)

    if valor_compra > LIMITE_DOBRAR_CASHBACK:
        cashback *= 2

    return round(cashback, 2)

# ── Schemas ─────────────────────────────────────────────────────────────────

class EntradaConsulta(BaseModel):
    tipo_cliente: str   # "VIP" ou "NORMAL"
    valor_compra: float

# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post("/calcular")
def calcular(entrada: EntradaConsulta, request: Request):
    ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

    tipo = entrada.tipo_cliente.upper()
    if tipo not in ("VIP", "NORMAL"):
        return {"erro": "tipo_cliente deve ser 'VIP' ou 'NORMAL'"}

    cashback = calcular_cashback(tipo, entrada.valor_compra)

    with obter_conexao() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO consultas (ip_usuario, tipo_cliente, valor_compra, cashback)
                VALUES (%s, %s, %s, %s)
                """,
                (ip, tipo, entrada.valor_compra, cashback),
            )
        conn.commit()

    return {
        "tipo_cliente": tipo,
        "valor_compra": entrada.valor_compra,
        "cashback":     cashback,
    }


@app.get("/historico")
def historico(request: Request):
    ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

    with obter_conexao() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT tipo_cliente, valor_compra, cashback, criado_em
                FROM consultas
                WHERE ip_usuario = %s
                ORDER BY criado_em DESC
                LIMIT 50
                """,
                (ip,),
            )
            linhas = cursor.fetchall()

    resultado = [
        {
            "tipo_cliente": linha[0],
            "valor_compra": float(linha[1]),
            "cashback":     float(linha[2]),
            "criado_em":    linha[3].replace(tzinfo=timezone.utc).astimezone(FUSO_BRASIL).strftime("%d/%m/%Y %H:%M"),
        }
        for linha in linhas
    ]

    return {"historico": resultado}


@app.get("/")
def raiz():
    return {"status": "API de Cashback no ar ✅"}