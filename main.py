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
        "img": "/img/4057491150f2b43a0810764ddb241818.jpg"
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

    translated_comments = []
    for c in comments:
        if c["post_id"] == post_id:
            if c["lang"] == lang:
                translated_comments.append(c["text"])
            else:
                try:
                    tr = GoogleTranslator(source=c["lang"], target=lang).translate(c["text"])
                    translated_comments.append(tr)
                except Exception:
                    translated_comments.append(f"{c['text']} (ошибка перевода)")

    return templates.TemplateResponse("post.html", {
        "request": request,
        "lang": lang,
        "post": {
            "title": post["title"].get(lang, post["title"]["en"]),
            "body": post["body"].get(lang, post["body"]["en"]),
            "img": post["img"]
        },
        "comments": translated_comments,
        "post_id": post_id,
        "posts_list": posts
    })

@app.post("/comment/{post_id}/{lang}")
async def add_comment(post_id: int, lang: str, text: str = Form(...)):
    comments.append({"post_id": post_id, "text": text, "lang": lang})
    return RedirectResponse(url=f"/post/{post_id}/{lang}", status_code=303)

@app.get("/change_lang/{post_id}/{lang}")
async def change_language(post_id: int, lang: str = Form(...)):
    return RedirectResponse(url=f"/post/{post_id}/{lang}", status_code=303)