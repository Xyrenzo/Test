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
            "ru": "Трой Шумахер и его BalletCollective снова удивляют 👀 — на этот раз в проекте The Woods, который прошёл в Pioneer Works в Бруклине. Вместе с композитором Эллисом Людвиг-Леоне и группой San Fermin они создали микс из рок-концерта 🎸, танцевального шоу и иммерсивного театра. Пространство бывшей фабрики превратилось в мистический лес 🌲, где публика ходила среди музыкантов и танцоров, будто сама становясь частью сюжета. Особая фишка — танцовщики поют 🎤! Например, Лесли Андреа Уильямс совмещает безумные танцевальные брейки с вокалом — прямо по-бейонсовски. В отличие от классики, здесь нет чёткой истории: зритель сам становится главным героем, а артисты лишь направляют атмосферу. Шумахер называет это «опытом сообщества», где танец возвращает живое ощущение быть вместе.\n\n✦ Автор: Pointe Magazine\n\n✨🌲🎶🩰",
            "en": "Troy Schumacher and his BalletCollective surprise again 👀 — this time in the project The Woods, which took place at Pioneer Works in Brooklyn. Together with composer Ellis Ludwig-Leone and the band San Fermin, they created a mix of a rock concert 🎸, a dance show, and immersive theater. The space of a former factory was transformed into a mystical forest 🌲, where the audience walked among the musicians and dancers, as if becoming part of the plot themselves. A special feature — the dancers sing 🎤! For example, Leslie Andrea Williams combines crazy dance breaks with vocals — just like Beyoncé. Unlike the classics, there is no clear story here: the viewer becomes the main character, and the artists only direct the atmosphere. Schumacher calls it a “community experience,” where dance brings back the living feeling of being together.\n\n✦ Author: Pointe Magazine\n\n✨🌲🎶🩰",
            "ja": "トロイ・シューマッハーと彼のバレエコレクティブが再び驚きの連続👀を披露しました。今回はブルックリンのパイオニア・ワークスで開催されたプロジェクト「The Woods」です。作曲家のエリス・ルートヴィヒ＝レオーネとバンド「サン・フェルミン」と共に、ロックコンサート🎸、ダンスショー、そして没入型シアターを融合させた作品を創り上げました。かつて工場だった空間は神秘的な森🌲へと変貌し、観客はまるで物語の一部になったかのように、ミュージシャンやダンサーの間を歩き回りました。\n\n特筆すべきは、ダンサーたちが歌うことです🎤！例えば、レスリー・アンドレア・ウィリアムズは、ビヨンセのように、クレイジーなダンスブレイクとボーカルを融合させています。古典作品とは異なり、明確なストーリーはありません。観客が主人公となり、アーティストは雰囲気を演出するだけです。シューマッハーはこれを「コミュニティ体験」と呼び、ダンスを通して共に生きる感覚を取り戻すことができると語っています。\n\n✦ 著者：Pointe Magazine\n\n✨🌲🎶🩰",
            "zh": "特洛伊·舒马赫和他的芭蕾集体再次带来惊喜👀——这次是在布鲁克林先锋工厂举办的“树林”项目。他们与作曲家埃利斯·路德维希-莱昂内和圣费尔明乐队携手，打造了一场融合摇滚音乐会🎸、舞蹈表演和沉浸式剧场的演出。昔日工厂的空间被改造成一片神秘的森林🌲，观众漫步于音乐家和舞者之间，仿佛置身于故事之中。\n\n一大亮点——舞者们还会唱歌🎤！例如，莱斯利·安德里亚·威廉姆斯将疯狂的舞步与人声融合在一起——就像碧昂丝一样。与经典作品不同，这里没有清晰的故事：观众成为主角，艺术家只是引导氛围。舒马赫称之为“社区体验”，舞蹈带回了那种鲜活的团聚感。\n\n✦作者：Pointe Magazine\n\n✨🌲🎶🩰",
            "es": "Troy Schumacher y su BalletCollective vuelven a sorprender 👀, esta vez con el proyecto The Woods, que tuvo lugar en Pioneer Works en Brooklyn. Junto con el compositor Ellis Ludwig-Leone y la banda San Fermin, crearon una mezcla de concierto de rock 🎸, espectáculo de danza y teatro inmersivo. El espacio de una antigua fábrica se transformó en un bosque místico 🌲, donde el público caminaba entre los músicos y bailarines, como si formara parte de la trama.\n\nUna característica especial: ¡los bailarines cantan 🎤! Por ejemplo, Leslie Andrea Williams combina alocados breaks de baile con voces, al estilo de Beyoncé. A diferencia de los clásicos, aquí no hay una historia clara: el espectador se convierte en el protagonista y los artistas solo dirigen la atmósfera. Schumacher lo llama una \"experiencia comunitaria\", donde la danza recupera la sensación de estar juntos.\n\n✦ Autor: Pointe Magazine\n\n✨🌲🎶🩰",
            "pt": "Troy Schumacher e o seu BalletCollective voltam a surpreender 👀 — desta vez no projeto The Woods, realizado no Pioneer Works, em Brooklyn. Juntamente com o compositor Ellis Ludwig-Leone e a banda San Fermin, criaram uma mistura de concerto de rock 🎸, espetáculo de dança e teatro imersivo. O espaço de uma antiga fábrica foi transformado numa floresta mística 🌲, onde o público caminhava entre músicos e bailarinos, como se fizesse parte do enredo.\n\nUm destaque especial — os bailarinos cantam 🎤! Por exemplo, Leslie Andrea Williams combina breaks de dança alucinantes com vozes — tal como Beyoncé. Ao contrário dos clássicos, não há aqui uma história clara: o espectador torna-se a personagem principal e os artistas apenas controlam a atmosfera. Schumacher chama-lhe \"experiência comunitária\", onde a dança traz de volta a sensação viva de estarmos juntos.\n\n✦ Autor: Revista Pointe\n\n✨🌲🎶🩰"
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
async def choose_language(request: Request):
    return templates.TemplateResponse("choose.html", {"request": request})

@app.post("/set_language")
async def set_language(language: str = Form(...)):
    return RedirectResponse(url=f"/post/{language}", status_code=303)

@app.get("/post/{lang}", response_class=HTMLResponse)
async def show_all_posts(request: Request, lang: str):
    all_posts = []
    for post_id, post in posts.items():
        all_posts.append({
            "id": post_id,
            "title": post["title"].get(lang, post["title"]["en"]),
            "body": post["body"].get(lang, post["body"]["en"]),
            "images": post["images"]
        })
    return templates.TemplateResponse("post.html", {
        "request": request,
        "lang": lang,
        "posts": all_posts
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