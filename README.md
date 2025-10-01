# Email Classifier — Produtivo / Improdutivo

Uma aplicação web simples para **classificar emails** em categorias **Produtivo** ou **Improdutivo** e sugerir respostas automáticas, usando **FastAPI** e a **API OpenAI**.

---

## Funcionalidades

- Upload de arquivos `.txt` ou `.pdf` contendo emails.
- Colar texto de email diretamente na interface.
- Classificação automática:
  - **Produtivo**: emails que requerem ação ou resposta.
  - **Improdutivo**: emails que não requerem ação imediata.
- Sugestão de resposta automática baseada na classificação.
- Interface web simples e responsiva com **TailwindCSS**.

---

## Tecnologias

- **Python 3.11+**
- **FastAPI** — backend e API REST.
- **OpenAI GPT-3.5-Turbo** — classificação e geração de respostas.
- **pdfplumber** — leitura de PDFs.
- **TailwindCSS** — estilização da interface.
- **Uvicorn** — servidor ASGI para desenvolvimento.

---

## Instalação e execução

1. Clone o repositório:

```bash
git clone <HTTPS do repositório>
```

2. Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
3. Configure sua chave da OpenAI:
Vá no site https://platform.openai.com pegue sua chave e no PowerShell rode:
```bash
$env:OPENAI_API_KEY="SUA_CHAVE_AQUI"
```
Para Linux/MacOs:
```bash
export OPENAI_API_KEY="SUA_CHAVE_AQUI"
```
4. Rode a aplicação dentro do diretório email-classifier:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```
5. Acesse no navegador para testar:
```bash
http://localhost:8080
```

