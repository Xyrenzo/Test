from fastapi import FastAPI, Request, Form, Query, Path, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends

DATABASE_URL = "postgresql+psycopg://xyrenzo:jTF8wn6fr2GxkIadpPbW4IGQB0JR9cpL@dpg-d37fp76mcj7s73fke010-a/maket"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")


# ---------- MODELS ----------
class PostStatus(Base):
    __tablename__ = "post_status"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "post_id"),
        CheckConstraint("status IN ('read','unread')"),
    )


class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    lang = Column(String, nullable=False, default="en")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


# ---------- INIT ----------
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- HELPERS ----------
def mark_post_as_read(user_id: int, post_id: int, db: Session):
    obj = db.query(PostStatus).filter_by(user_id=user_id, post_id=post_id).first()
    if obj:
        obj.status = "read"
    else:
        obj = PostStatus(user_id=user_id, post_id=post_id, status="read")
        db.add(obj)
    db.commit()


def get_user_read_ids(user_id: int, db: Session):
    rows = db.query(PostStatus).filter_by(user_id=user_id, status="read").all()
    return {row.post_id for row in rows}


def get_user_lang(user_id: int, db: Session) -> str | None:
    row = db.query(UserSettings).filter_by(user_id=user_id).first()
    return row.lang if row else None


def set_user_lang(user_id: int, lang: str, db: Session):
    row = db.query(UserSettings).filter_by(user_id=user_id).first()
    if row:
        row.lang = lang
    else:
        row = UserSettings(user_id=user_id, lang=lang)
        db.add(row)
    db.commit()


def get_comments(post_id: int, db: Session):
    rows = db.query(Comment).filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return [{"id": r.id, "user_id": r.user_id, "content": r.content, "created_at": r.created_at} for r in rows]


def add_comment(post_id: int, user_id: int, content: str, db: Session):
    db.add(Comment(post_id=post_id, user_id=user_id, content=content))
    db.commit()


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

# ---------- ROUTES ----------
@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def choose_language(request: Request, user_id: int = Query(...), db: Session = Depends(get_db())):
    lang = get_user_lang(user_id, db)
    if lang:
        return RedirectResponse(url=f"/post/{lang}/all?user_id={user_id}", status_code=303)
    return templates.TemplateResponse("choose.html", {"request": request, "user_id": user_id})


@app.post("/set_language")
async def set_language(language: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db())):
    set_user_lang(user_id, language, db)
    return RedirectResponse(url=f"/post/{language}/all?user_id={user_id}", status_code=303)


@app.get("/post/{lang}/{filter}", response_class=HTMLResponse)
async def show_posts(request: Request, lang: str, filter: str = "all", user_id: int = Query(...), db: Session = Depends(get_db())):
    user_lang = get_user_lang(user_id, db) or "en"

    if lang != user_lang:
        return RedirectResponse(f"/post/{user_lang}/{filter}?user_id={user_id}", status_code=303)

    read_ids = get_user_read_ids(user_id, db)
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

    return templates.TemplateResponse("post.html", {"request": request, "lang": user_lang, "posts": filtered_posts, "filter": filter, "user_id": user_id})


@app.post("/mark_read/{post_id}")
async def mark_read(post_id: int, user_id: int = Query(...), db: Session = Depends(get_db())):
    mark_post_as_read(user_id, post_id, db)
    return JSONResponse({"status": "ok"})


@app.post("/change_language")
async def change_language(language: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db())):
    set_user_lang(user_id, language, db)
    return RedirectResponse(f"/post/{language}/all?user_id={user_id}", status_code=303)


@app.get("/post/{post_id}/comments/{lang}", response_class=HTMLResponse)
async def post_comments(request: Request, post_id: int, lang: str, user_id: int = Query(...), db: Session = Depends(get_db())):
    user_lang = get_user_lang(user_id, db) or "en"
    if lang != user_lang:
        return RedirectResponse(f"/post/{user_lang}/all?user_id={user_id}", status_code=303)

    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    items = get_comments(post_id, db)

    return templates.TemplateResponse("comments.html", {"request": request, "post": {"id": post_id, "title": post["title"].get(user_lang, post["title"]["en"]), "body": post["body"].get(user_lang, post["body"]["en"])}, "lang": lang, "user_id": user_id, "comments": items})


@app.post("/post/{post_id}/comments/add")
async def post_comment_add(post_id: int, content: str = Form(...), user_id: int = Form(...), lang: str = Form(...), db: Session = Depends(get_db())):
    add_comment(post_id, user_id, content, db)
    return RedirectResponse(f"/post/{post_id}/comments/{lang}?user_id={user_id}", status_code=303)