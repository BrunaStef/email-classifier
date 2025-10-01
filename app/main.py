import os
import io
import re
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import pdfplumber
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = FastAPI(title="Email Classifier")

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    stopwords = {
        'de','a','o','que','e','do','da','em','um','para','com','não','uma','os','no','se',
        'na','por','mais','as','dos','como','mas','foi','ao','ele','das','tem','à','seu','sua',
        'ou','ser','quando','muito','há','nos','já','está','eu','também','são','até','isso',
        'ela','entre','era','após','sem','sobre','ter','me','até'
    }
    tokens = [t for t in text.split() if t not in stopwords]
    return " ".join(tokens)

def rule_based_classifier(text: str):
    productive_keywords = [
        'erro','problema','suporte','ajuda','atualiza','atualização','status',
        'documento','anexo','anexado','fatura','pagamento','reclamação','reclamacao',
        'solicita','solicitação','prazo','entrega','contrato','assinado','assinar'
    ]
    for kw in productive_keywords:
        if kw in text:
            return {"category":"Produtivo"}
    return {"category":"Improdutivo"}

def build_openai_prompt(text: str):
    prompt = f"""
Você recebe o conteúdo de um e-mail. Classifique em UMA das categorias: "Produtivo" (requer ação/resposta) ou "Improdutivo" (não requer ação imediata).
Retorne **APENAS** um JSON válido com chaves:
- category: "Produtivo" ou "Improdutivo"
- suggested_response: uma resposta curta em português adequada ao e-mail.

O e-mail:
\"\"\"{text}\"\"\"
"""
    return prompt

def classify_with_openai(text: str):
    prompt = build_openai_prompt(text)
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role":"system", "content":"Você é um assistente que classifica e redige respostas curtas para e-mails de suporte/negócios."},
                {"role":"user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=350
        )
        content = resp['choices'][0]['message']['content']
        m = re.search(r'\{.*\}', content, re.S)
        if m:
            data = json.loads(m.group(0))
            return data
        else:
            return {"category":"Improdutivo", "suggested_response": content.strip()}
    except Exception as e:
        print("OpenAI error:", e)
        return None

@app.post("/analyze")
async def analyze(email_text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    text = ""
    if file:
        contents = await file.read()
        ctype = file.content_type
        if ctype == "text/plain":
            text = contents.decode('utf-8', errors='ignore')
        elif ctype == "application/pdf":
            text = extract_text_from_pdf_bytes(contents)
        else:
            try:
                text = contents.decode('utf-8', errors='ignore')
            except:
                text = ""
    if email_text:
        if text:
            text = text + "\n\n" + email_text
        else:
            text = email_text

    if not text or text.strip()=="":
        return JSONResponse({"error":"Nenhum texto recebido"}, status_code=400)

    raw = text.strip()
    processed = preprocess_text(raw)

    result = None
    if OPENAI_API_KEY:
        result = classify_with_openai(raw)
    if not result:
        result = rule_based_classifier(processed)

        if result["category"] == "Produtivo":
            suggested = ("Obrigado pelo contato. Recebemos seu e-mail e vamos analisar a solicitação. "
                         "Você pode enviar mais detalhes ou anexos se necessário. Abertura de chamado em andamento.")
        else:
            suggested = ("Agradecemos a mensagem. No momento não é necessária ação adicional. "
                         "Se precisar de ajuda, nos envie detalhes específicos.")
        result.update({"suggested_response": suggested})

    return JSONResponse({
        "category": result.get("category"),
        "suggested_response": result.get("suggested_response")
    })
