# Cashback App — Desafio Nology

## Estrutura

```
cashback-app/
├── backend/
│   ├── main.py           # API FastAPI
│   ├── requirements.txt
│   └── Procfile
└── frontend/
    └── index.html        # App estático
```

---

## Passo a Passo para Hospedar

### 1. Subir o código no GitHub

```bash
git init
git add .
git commit -m "primeiro commit"
# Crie um repositório no github.com e siga as instruções para push
```

---

### 2. Criar banco PostgreSQL gratuito (Neon.tech)

1. Acesse https://neon.tech e crie uma conta gratuita
2. Crie um novo projeto → anote a **DATABASE_URL** (formato: `postgresql://user:pass@host/db`)

---

### 3. Hospedar o backend no Render.com (gratuito)

1. Acesse https://render.com → New → **Web Service**
2. Conecte seu repositório GitHub
3. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment Variables**, adicione:
   - `DATABASE_URL` = (a URL copiada do Neon)
5. Clique em **Deploy** → aguarde → copie a URL gerada (ex: `https://cashback-api.onrender.com`)

---

### 4. Configurar o frontend

No arquivo `frontend/index.html`, linha:

```javascript
const URL_API = 'https://SEU-BACKEND.onrender.com';
```

Substitua pela URL real do seu backend.

---

### 5. Hospedar o frontend no Vercel (gratuito)

1. Acesse https://vercel.com → New Project → importe o repositório
2. Em **Root Directory**, selecione `frontend`
3. Clique em **Deploy** → pronto!

Ou use o **Netlify** arrastando a pasta `frontend` em https://app.netlify.com/drop

---

## Regras de Negócio Implementadas

| Documento | Regra |
|-----------|-------|
| Doc 1 | Cashback base = 5% do valor final |
| Doc 1 | Cliente VIP ganha +10% sobre o cashback base |
| Doc 2 | Compras acima de R$500 = dobro do cashback (todos) |
| Doc 3 | Ordem: calcular base → dobrar (se >500) → aplicar bônus VIP |

### Exemplos

**VIP, R$600, cupom 20%** → valor final = R$480 → cashback = 480×5% = R$24 (não dobra pois 480<500) → VIP: 24×1.1 = **R$26,40**

**Normal, R$600, cupom 10%** → valor final = R$540 → cashback = 540×5% = R$27 × 2 = **R$54,00**

**VIP, R$600, cupom 15%** → valor final = R$510 → cashback = 510×5% = R$25,50 × 2 = R$51 → VIP: 51×1.1 = **R$56,10 ≈ R$56** ✅ (confirma item 4)
