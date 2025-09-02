from fastapi import FastAPI, Request, Form, Query, Path
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")


def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS post_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('read','unread')) NOT NULL,
    UNIQUE(user_id, post_id)
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    lang TEXT NOT NULL DEFAULT 'en'
)
""")

    conn.commit()
    conn.close()


def mark_post_as_read(user_id: int, post_id: int):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        """ INSERT INTO post_status (user_id, post_id, status) 
            VALUES (?, ?, 'read') 
            ON CONFLICT(user_id, post_id) 
            DO UPDATE SET status='read' """,
        (user_id, post_id),
    )
    conn.commit()
    conn.close()


def get_user_read_ids(user_id: int):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT post_id FROM post_status WHERE user_id=? AND status='read'",
        (user_id,),
    )
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def get_user_lang(user_id: int) -> str:
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM user_settings WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_user_lang(user_id: int, lang: str):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        """ INSERT INTO user_settings (user_id, lang) 
            VALUES (?, ?) 
            ON CONFLICT(user_id) 
            DO UPDATE SET lang=excluded.lang """,
        (user_id, lang),
    )
    conn.commit()
    conn.close()


init_db()


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
            "en": "The Woods Project",
            "ru": "Проект The Woods",
            "ja": "ザ・ウッズ・プロジェクト",
            "ko": "더 우즈 프로젝트",
            "zh": "《树林》项目",
            "es": "El Proyecto The Woods",
            "pt": "O Projeto The Woods"
        },
        "body": {
            "ru": "Трой Шумахер и его BalletCollective снова удивляют 👀 — на этот раз в проекте The Woods, который прошёл в Pioneer Works в Бруклине. Вместе с композитором Эллисом Людвиг-Леоне и группой San Fermin они создали микс из рок-концерта 🎸, танцевального шоу и иммерсивного театра. Пространство бывшей фабрики превратилось в мистический лес 🌲, где зрители могли свободно перемещаться и становились частью представления.",
            "en": "Troy Schumacher and his BalletCollective surprise again 👀 — this time with The Woods project, which took place at Pioneer Works in Brooklyn. Together with composer Ellis Ludwig-Leone and the band San Fermin, they created a mix of rock concert 🎸, dance show, and immersive theater. The former factory space turned into a mystical forest 🌲, where the audience could freely move around and become part of the performance.",
            "ja": "トロイ・シューマッハーと彼のバレエコレクティブが再び驚きの演出を披露👀。今回はブルックリンのパイオニア・ワークスで開催された『ザ・ウッズ』プロジェクト。作曲家エリス・ルートヴィヒ＝レオーネやバンドのサン・フェルミンと共に、ロックコンサート🎸、ダンスショー、イマーシブシアターを融合させた。元工場の空間は神秘的な森🌲に変わり、観客は自由に移動しながら舞台の一部となった。",
            "zh": "特洛伊·舒马赫和他的芭蕾集体再次带来惊喜👀——这次是在布鲁克林先锋工厂举办的《树林》项目。与作曲家埃利斯·路德维希-莱昂和乐队 San Fermin 合作，他们创造了一场融合摇滚音乐会🎸、舞蹈表演和沉浸式戏剧的演出。旧工厂空间变成了一个神秘的森林 🌲，观众可以自由移动，成为表演的一部分。",
            "es": "Troy Schumacher y su BalletCollective vuelven a sorprender 👀 — esta vez con el proyecto The Woods, que tuvo lugar en Pioneer Works en Brooklyn. Junto al compositor Ellis Ludwig-Leone y la banda San Fermin, crearon una mezcla de concierto de rock 🎸, espectáculo de danza y teatro inmersivo. El antiguo espacio fabril se transformó en un bosque místico 🌲, donde el público podía moverse libremente y convertirse en parte del espectáculo.",
            "pt": "Troy Schumacher e o seu BalletCollective voltam a surpreender 👀 — desta vez com o projeto The Woods, que aconteceu no Pioneer Works, no Brooklyn. Juntamente com o compositor Ellis Ludwig-Leone e a banda San Fermin, criaram uma mistura de concerto de rock 🎸, espetáculo de dança e teatro imersivo. O antigo espaço fabril transformou-se numa floresta mística 🌲, onde o público podia mover-se livremente e tornar-se parte da performance."
        },
        "images": [
            "/img/IMG_20250901_182647_527.jpg",
            "/img/IMG_20250901_182648_694.jpg",
            "/img/IMG_20250901_182650_107.jpg"
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
async def choose_language(request: Request, user_id: int = Query(...)):
    lang = get_user_lang(user_id)
    if lang:
        return RedirectResponse(url=f"/post/{lang}/all?user_id={user_id}", status_code=303)
    return templates.TemplateResponse("choose.html", {"request": request, "user_id": user_id})


@app.post("/set_language")
async def set_language(language: str = Form(...), user_id: int = Form(...)):
    set_user_lang(user_id, language)
    return RedirectResponse(url=f"/post/{language}/all?user_id={user_id}", status_code=303)


@app.get("/post/{lang}/{filter}", response_class=HTMLResponse)
async def show_posts(request: Request, lang: str, filter: str = Path(default = "all"), user_id: int = Query(...)):
    user_lang = get_user_lang(user_id) or "en"

    if lang != user_lang:
        return RedirectResponse(f"/post/{user_lang}/{filter}?user_id={user_id}", status_code=303)

    read_ids = get_user_read_ids(user_id)
    if filter == "read":
        ids = read_ids
    elif filter == "unread":
        ids = set(posts.keys()) - read_ids
    else:
        ids = set(posts.keys())

    filtered_posts = []
    for pid in ids:
        if pid in posts:
            post = posts[pid]
            filtered_posts.append({
                "id": pid,
                "title": post["title"].get(user_lang, post["title"]["en"]),
                "body": post["body"].get(user_lang, post["body"]["en"]),
                "images": post["images"]
            })

    return templates.TemplateResponse("post.html", {
        "request": request,
        "lang": user_lang,
        "posts": filtered_posts,
        "filter": filter,
        "user_id": user_id
    })


@app.post("/mark_read/{post_id}")
async def mark_read(post_id: int, user_id: int = Form(...)):
    mark_post_as_read(user_id, post_id)
    return JSONResponse({"status": "ok"})


@app.post("/change_language")
async def change_language(language: str = Form(...), user_id: int = Form(...)):
    set_user_lang(user_id, language)
    return RedirectResponse(f"/post/{language}/all?user_id={user_id}", status_code=303)