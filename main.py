# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from deep_translator import GoogleTranslator

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")

posts = {
    "en": {"title": "Hello World!", "body": "This is the first post.", "img": "/img/4057491150f2b43a0810764ddb241818.jpg "},
    "ru": {"title": "Привет, мир!", "body": "Это первый пост.", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
    "ja": {"title": "こんにちは世界！", "body": "これは最初の投稿です。", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
    "ko": {"title": "안녕하세요 세계!", "body": "이것은 첫 번째 게시물입니다.", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
    "zh": {"title": "你好，世界！", "body": "这是第一篇帖子。", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
    "es": {"title": "¡Hola Mundo!", "body": "Esta es la primera publicación.", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
    "pt": {"title": "Olá Mundo!", "body": "Este é o primeiro post.", "img": "/img/4057491150f2b43a0810764ddb241818.jpg"},
}

# комменты храним как список словарей {text, lang}
comments = []

@app.get("/", response_class=HTMLResponse)
async def choose_language(request: Request):
    return templates.TemplateResponse("choose.html", {"request": request})

@app.post("/set_language")
async def set_language(language: str = Form(...)):
    return RedirectResponse(url=f"/post/{language}", status_code=303)

@app.get("/post/{lang}", response_class=HTMLResponse)
async def show_post(request: Request, lang: str):
    post = posts.get(lang)
    if not post:
        return RedirectResponse("/")
    
    # переводим комментарии
    translated_comments = []
    for c in comments:
        if c["lang"] == lang:
            translated_comments.append(c["text"])
        else:
            try:
                tr = GoogleTranslator(source=c["lang"], target=lang).translate(c["text"])
                translated_comments.append(f"{tr}")
            except Exception:
                translated_comments.append(f"{c['text']} (ошибка перевода)")

    return templates.TemplateResponse("post.html", {
        "request": request,
        "lang": lang,
        "post": post,
        "comments": translated_comments
    })

@app.post("/comment/{lang}")
async def add_comment(lang: str, text: str = Form(...)):
    comments.append({"text": text, "lang": lang})
    return RedirectResponse(url = f"/post/{lang}", status_code=303)
