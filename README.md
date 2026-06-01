# 🏦 PAYSYS - Payment Gaming System

Um sistema completo de banco e pagamentos integrado com um jogo de apostas.

## 🎮 Características

### Sistema Bancário
- ✅ Registro e login de usuários
- ✅ Múltiplas contas bancárias por usuário
- ✅ Transferências entre contas
- ✅ Histórico de transações
- ✅ QR Code para pagamentos
- ✅ Integração com múltiplas moedas (KZA, USD, EUR, etc)

### Sistema de Jogo
- 🎲 Jogo de números pares
- 💰 Multiplicador: Número x 1.000.000 KZA
- 🎯 50% de chance de vitória
- 📊 Estatísticas de jogos
- 🏆 Histórico de prêmios

### Pagamentos
- 💳 Pagamentos via QR Code
- 🌍 Transferências internacionais
- 📱 Carteira virtual
- 🔐 Criptografia de dados sensíveis
- 📈 Relatórios de pagamentos

## 🚀 Como Começar no Termux

### PASSO 1: Instalar Dependências

```bash
# Atualizar pacotes
pkg update && pkg upgrade -y

# Instalar Python, Git e outras ferramentas
pkg install python git curl wget -y

# Verificar instalação
python --version
```

### PASSO 2: Clonar o Repositório

```bash
# Criar diretório para o projeto
mkdir -p ~/projects
cd ~/projects

# Clonar repositório
git clone https://github.com/boychan668-sudo/paysys-bank.git
cd paysys-bank
```

### PASSO 3: Criar Ambiente Virtual

```bash
# Entrar no diretório backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

### PASSO 4: Instalar Dependências Python

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt
```

### PASSO 5: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env (usando nano ou vi)
nano .env

# Mudanças necessárias (deixar como está para SQLite local):
# - FLASK_ENV=development (já está)
# - DATABASE_URL=sqlite:///payment_system.db (já está)
```

### PASSO 6: Inicializar o Banco de Dados

```bash
# Criar arquivo do banco de dados
python << 'EOF'
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
EOF
```

### PASSO 7: Iniciar o Servidor

```bash
# Iniciar API Flask
python app.py

# Ou com Gunicorn (em outra aba do Termux)
gunicorn --bind 0.0.0.0:5000 app:create_app('development')
```

**O servidor estará disponível em:** `http://localhost:5000`

---

## 📡 Testando a API

### Em outro terminal do Termux:

```bash
# 1. REGISTRAR NOVO USUÁRIO
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jogador@paysys.com",
    "phone": "244923456789",
    "full_name": "João Silva",
    "password": "senha123"
  }'

# Resposta:
# {"message": "User registered successfully", "user": {...}}
```

```bash
# 2. LOGIN
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jogador@paysys.com",
    "password": "senha123"
  }'

# Resposta:
# {"access_token": "seu_token_aqui", "refresh_token": "...", "user": {...}}

# Salvar o access_token para próximas requisições
export TOKEN="seu_token_aqui"
```

```bash
# 3. CRIAR CONTA BANCÁRIA
curl -X POST http://localhost:5000/api/v1/accounts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "account_type": "checking",
    "currency": "KZA",
    "initial_balance": 10000000
  }'

# Resposta:
# {"message": "Account created successfully", "account": {...}}

# Salvar o account_id
export ACCOUNT_ID="seu_account_id_aqui"
```

```bash
# 4. VER SALDO
curl -X GET "http://localhost:5000/api/v1/accounts/$ACCOUNT_ID/balance" \
  -H "Authorization: Bearer $TOKEN"

# Resposta:
# {"account_number": "ACC...", "balance": 10000000, "currency": "KZA"}
```

```bash
# 5. JOGAR - Apostar em número par
curl -X POST http://localhost:5000/api/v1/game/play \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"account_id\": \"$ACCOUNT_ID\",
    \"even_number\": 4,
    \"bet_amount\": 1000
  }"

# Resposta (se ganhar):
# {
#   "message": "Game completed",
#   "result": "WON",
#   "game_session": {
#     "even_number": 4,
#     "bet_amount": 1000,
#     "potential_winnings": 4000000000,
#     "actual_winnings": 4000000000,
#     "is_won": true
#   },
#   "account_balance": 4000009000
# }
```

```bash
# 6. VER ESTATÍSTICAS DO JOGO
curl -X GET http://localhost:5000/api/v1/game/stats \
  -H "Authorization: Bearer $TOKEN"

# Resposta:
# {
#   "total_games": 5,
#   "total_wins": 3,
#   "total_losses": 2,
#   "win_rate": "60.00%",
#   "total_winnings": 12000000000,
#   "total_bets": 5000,
#   "net_profit": 11999995000
# }
```

---

## 💰 Cálculo de Ganhos

**Fórmula:** Aposta × (Número × 1.000.000)

| Número | Multiplicador | Aposta 1000 KZA | Ganho Potencial |
|--------|---------------|-----------------|------------------|
| 2      | 2.000.000     | 1.000           | 2.000.000.000   |
| 4      | 4.000.000     | 1.000           | 4.000.000.000   |
| 6      | 6.000.000     | 1.000           | 6.000.000.000   |
| 8      | 8.000.000     | 1.000           | 8.000.000.000   |
| 10     | 10.000.000    | 1.000           | 10.000.000.000  |

**Exemplo:**
- Você aposta 5.000 KZA no número 6
- Se ganhar: 5.000 × 6 × 1.000.000 = **30.000.000.000 KZA**
- Chance: 50% de ganhar

---

## 📱 Endpoints Disponíveis

### Autenticação
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Renovar token
- `GET /api/v1/auth/me` - Perfil atual

### Contas
- `POST /api/v1/accounts/` - Criar nova conta
- `GET /api/v1/accounts/` - Listar contas
- `GET /api/v1/accounts/<id>` - Detalhes da conta
- `GET /api/v1/accounts/<id>/balance` - Saldo da conta

### Transações
- `POST /api/v1/transactions/transfer` - Transferir dinheiro
- `GET /api/v1/transactions/history/<account_id>` - Histórico

### Jogo
- `POST /api/v1/game/play` - Jogar (número par)
- `GET /api/v1/game/sessions` - Sessões do usuário
- `GET /api/v1/game/stats` - Estatísticas

### QR Code
- `POST /api/v1/qrcode/generate` - Gerar QR Code
- `POST /api/v1/qrcode/decode` - Decodificar QR Code

### Pagamentos
- `POST /api/v1/payments/request` - Solicitar pagamento
- `POST /api/v1/payments/confirm` - Confirmar pagamento

---

## 🐛 Troubleshooting

### Erro: "No module named 'app'"
```bash
# Certifique-se de estar no diretório backend
cd backend

# Ativar ambiente virtual
source venv/bin/activate
```

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Resetar banco de dados
```bash
rm payment_system.db
python << 'EOF'
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
EOF
```

### Verificar se porta 5000 está em uso
```bash
lsof -i :5000

# Se estiver em uso, matar processo
kill -9 <PID>
```

---

## 📝 Estrutura do Projeto

```
paysys-bank/
├── backend/
│   ├── app.py                 # Aplicação principal
│   ├── config.py              # Configurações
│   ├── requirements.txt        # Dependências
│   ├── models/
│   │   ├── user.py            # Modelo de usuário
│   │   ├── account.py         # Modelo de conta
│   │   ├── transaction.py     # Modelo de transação
│   │   └── game.py            # Modelo de jogo
│   └── routes/
│       ├── auth.py            # Autenticação
│       ├── accounts.py        # Contas
│       ├── transactions.py    # Transações
│       ├── game.py            # Jogo
│       ├── qrcode.py          # QR Code
│       ├── payments.py        # Pagamentos
│       └── admin.py           # Admin
└── README.md
```

---

## 🔐 Segurança

- JWT para autenticação
- Bcrypt para hash de senhas
- HTTPS obrigatório em produção
- Validação de entrada em todos os endpoints
- Rate limiting de requisições
- Logs de auditoria de transações

---

## 📞 Suporte

Para problemas ou dúvidas, abra uma [issue](https://github.com/boychan668-sudo/paysys-bank/issues).

---

**Desenvolvido por:** boychan668-sudo  
**Versão:** 1.0.0  
**Data:** 2026
