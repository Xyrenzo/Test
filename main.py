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
    1: {
        "title": {
            "en": "Hello World!", "ru": "Привет, мир!", "ja": "こんにちは世界！",
            "ko": "안녕하세요 세계!", "zh": "你好，世界！", "es": "¡Hola Mundo!", "pt": "Olá Mundo!"
        },
        "body": {
            "en": "This is the first post.", "ru": "Это первый пост.", "ja": "これは最初の投稿です。",
            "ko": "이것은 첫 번째 게시물입니다.", "zh": "这是第一篇帖子。", "es": "Esta es la primera publicación.", "pt": "Este é o primeiro post."
        },
        "images": [
            "/img/4057491150f2b43a0810764ddb241818.jpg"
        ]
    },
    2: {
        "title": {
            "en": "", "ru": "", "ja": "", "ko": "", "zh": "", "es": "", "pt": ""
        },
        "body": {
            "ru": "Трой Шумахер и его BalletCollective снова удивляют 👀 — на этот раз в проекте The Woods, который прошёл в Pioneer Works в Бруклине. Вместе с композитором Эллисом Людвиг-Леоне и группой San Fermin они создали микс из рок-концерта 🎸, танцевального шоу и иммерсивного театра...",
            "en": "Troy Schumacher and his BalletCollective surprise again 👀 — this time in the project The Woods, which took place at Pioneer Works in Brooklyn...",
            "ja": "トロイ・シューマッハーと彼のバレエコレクティブが再び驚きの連続👀...",
            "zh": "特洛伊·舒马赫和他的芭蕾集体再次带来惊喜👀...",
            "es": "Troy Schumacher y su BalletCollective vuelven a sorprender 👀...",
            "pt": "Troy Schumacher e o seu BalletCollective voltam a surpreender 👀..."
        },
        "images": [
            "/img/IMG_20250901_182647_527.jpg",
            "/img/IMG_20250901_182648_694.jpg"
        ]
    },
    3: {
        "title": {
            "en": "Hello World!", "ru": "Привет, мир!", "ja": "こんにちは世界！",
            "ko": "안녕하세요 세계!", "zh": "你好，世界！", "es": "¡Hola Mundo!", "pt": "Olá Mundo!"
        },
        "body": {
            "en": "Hello World!", "ru": "Привет, мир!", "ja": "こんにちは世界！",
            "ko": "안녕하세요 세계!", "zh": "你好，世界！", "es": "¡Hola Mundo!", "pt": "Olá Mundo!"
        },
        "images": [
            "/img/IMG_20250901_182650_107.jpg"
        ]
    }
}

comments = []

@app.get("/", response_class=HTMLResponse)
async def choose_language(request: Request):
    return templates.TemplateResponse("choose.html", {"request": request})

@app.post("/set_language")
async def set_language(language: str = Form(...)):
    first_post_id = min(posts.keys())
    return RedirectResponse(url=f"/post/{first_post_id}/{language}", status_code=303)

@app.get("/post/{post_id}/{lang}", response_class=HTMLResponse)
async def show_post(request: Request, post_id: int, lang: str):
    post = posts.get(post_id)
    if not post:
        return RedirectResponse("/")

    return templates.TemplateResponse("post.html", {
        "request": request,
        "lang": lang,
        "post": {
            "title": post["title"].get(lang, post["title"]["en"]),
            "body": post["body"].get(lang, post["body"]["en"]),
            "images": post["images"]
        },
        "post_id": post_id
    })

@app.get("/post/{post_id}/comments/{lang}", response_class=HTMLResponse)
async def show_comments(request: Request, post_id: int, lang: str):
    post = posts.get(post_id)
    if not post:
        return RedirectResponse("/")

    post_comments = []
    for c in comments:
        if c["post_id"] == post_id:
            if c["lang"] == lang:
                post_comments.append(c["text"])
            else:
                try:
                    tr = GoogleTranslator(source=c["lang"], target=lang).translate(c["text"])
                    post_comments.append(tr)
                except Exception:
                    post_comments.append(f"{c['text']} (ошибка перевода)")

    return templates.TemplateResponse("comments.html", {
        "request": request,
        "lang": lang,
        "post_id": post_id,
        "comments": post_comments,
        "post": {
            "title": post["title"].get(lang, post["title"]["en"])
        }
    })

@app.post("/post/{post_id}/comments/{lang}")
async def add_comment(post_id: int, lang: str, text: str = Form(...)):
    comments.append({"post_id": post_id, "text": text, "lang": lang})
    return RedirectResponse(url=f"/post/{post_id}/comments/{lang}", status_code=303)