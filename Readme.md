# My new dashboard terminal

Dashboard simples de investimentos que roda no terminal lendo dados de um CSV.

## Como usar

```bash
python3 main.py data/investimentos.csv
```

Os preços atuais são buscados automaticamente no Google Finance.
Se nenhum caminho for informado, o script tenta `~/investimentos.csv`, `~/.investimentos.csv`
e depois `data/investimentos.csv`.

## Instalação rápida

Edite o `REPO_URL` dentro de `install.sh` com o repositório correto e execute:

```bash
bash install.sh
```

O script clona o repositório em `~/term-dash-invest` e usa `~/investimentos.csv` ou `~/.investimentos.csv`
caso existam. Se nenhum deles existir, ele copia o CSV de exemplo para `~/investimentos.csv`.

## Instalação via script remoto

Você pode copiar direto do GitHub e rodar em uma linha (substitua o repositório):

```bash
curl -fsSL https://raw.githubusercontent.com/seu-usuario/term-dash-invest/main/install-remote.sh \\
  | REPO_URL=https://github.com/seu-usuario/term-dash-invest.git bash
```

### Formato esperado do CSV

Campos obrigatórios:

- `ativo`
- `preco_medio`
- `quantidade`

Campo opcional:

- `categoria`
- `ticker` (ex: `PETR4:BVMF`, usado para buscar preços no Google Finance)
