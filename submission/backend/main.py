"""
文化基因库与时空地图 - Unified Backend API
Dynasty Filter . Silk Road . Story Generator

启动方式: 双击 start.bat 或运行 python main.py
"""

import os, re, uuid, json, webbrowser, threading
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

try:  # .env 可选，没有也能跑
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR / ".." / "frontend").resolve()
UPLOAD_DIR = BASE_DIR / "uploads"; RESULT_DIR = BASE_DIR / "results"
UPLOAD_DIR.mkdir(exist_ok=True); RESULT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Jade Culture Hub API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ========================================
# Credentials - bring your own key
# ========================================
# 仓库不内置任何 API Key。优先级：请求头（前端设置面板） > 环境变量 / .env

DEFAULT_IMAGE_BASE  = "https://api.siliconflow.cn/v1"
DEFAULT_IMAGE_MODEL = "Tongyi-MAI/Z-Image-Turbo"
DEFAULT_TEXT_BASE   = "https://api.openai.com/v1"
DEFAULT_TEXT_MODEL  = "gpt-4o-mini"

ENV_IMAGE_KEY   = os.getenv("SILICONFLOW_API_KEY", "").strip()
ENV_IMAGE_BASE  = (os.getenv("SILICONFLOW_BASE_URL", "").strip() or DEFAULT_IMAGE_BASE).rstrip("/")
ENV_IMAGE_MODEL = os.getenv("SILICONFLOW_IMAGE_MODEL", "").strip() or DEFAULT_IMAGE_MODEL
ENV_TEXT_KEY    = os.getenv("OPENAI_API_KEY", "").strip()
ENV_TEXT_BASE   = (os.getenv("OPENAI_BASE_URL", "").strip() or DEFAULT_TEXT_BASE).rstrip("/")
ENV_TEXT_MODEL  = os.getenv("OPENAI_TEXT_MODEL", "").strip() or DEFAULT_TEXT_MODEL

_PRIVATE_HOST_RE = re.compile(r"^(localhost|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|0\.0\.0\.0|\[?::1\]?)", re.I)


def _header(request: Request, name: str) -> str:
    return (request.headers.get(name) or "").strip()


def _client_base_url(request: Request, header_name: str, default: str) -> str:
    """客户端可覆盖 Base URL，但只接受公网 http(s) 地址（防 SSRF）。"""
    raw = _header(request, header_name)
    if not raw:
        return default
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return default
    if _PRIVATE_HOST_RE.match(parsed.hostname):
        return default
    return raw.rstrip("/")


def image_credentials(request: Request) -> dict:
    return {
        "key":   _header(request, "X-Image-Key") or ENV_IMAGE_KEY,
        "model": _header(request, "X-Image-Model") or ENV_IMAGE_MODEL,
        "base":  _client_base_url(request, "X-Image-Base", ENV_IMAGE_BASE),
    }


def text_credentials(request: Request) -> dict:
    return {
        "key":   _header(request, "X-Text-Key") or ENV_TEXT_KEY,
        "model": _header(request, "X-Text-Model") or ENV_TEXT_MODEL,
        "base":  _client_base_url(request, "X-Text-Base", ENV_TEXT_BASE),
    }


MISSING_IMAGE_KEY_MSG = (
    "未配置图片生成 API Key。请在前端「设置」中填写 SiliconFlow Key，"
    "或在 backend/.env 中设置 SILICONFLOW_API_KEY。"
)

# ========================================
# SHARED DATA - Dynasty Prompts
# ========================================
DYNASTY_PROMPTS = {
    "han": {"label":"汉代","period":"西汉-东汉 (202 BC-220 AD)",
        "positive_prompt":(
            "Transform this object into a Chinese Han dynasty ceremonial jade artifact, "
            "carved from archaic celadon-white jade with heavy brown patina and earth-calcification marks across the surface. "
            "Deeply carved chi-dragon spiraling across the body, dense cloud-scroll patterns filling the background, "
            "raised grain pattern dots in orderly rows. Thick heavy proportions, angular primitive carving, "
            "rough tool marks visible in raking light. The object should look like a 2000-year-old archaeological treasure "
            "freshly excavated from a Han nobleman's tomb. Murky celadon-green jade with dark brown veins and chalky white spots. "
            "Solemn, heavy, awe-inspiring. Museum artifact on pure black, dramatic raking light, ultra realistic 8K"
        ),
        "negative_prompt":(
            "smooth polished surface, modern minimalist design, thin delicate proportions, bright saturated colors, "
            "symmetrical machine-made precision, translucent, shiny gloss, gold inlay, gemstones, Tang or Qing style, "
            "cartoon, low quality, blurry, watermark, text, plastic, fake"
        ),
        "visual_features":["螭纹","云气纹","谷纹","蚕纹","古朴厚重"],"jade_types":["青白玉","黄玉"]},
    "tang": {"label":"唐代","period":"唐代 (618-907 AD)",
        "positive_prompt":(
            "Transform this object into a Chinese Tang dynasty jade ornament from the Silk Road golden age, "
            "carved from luminous warm white jade with a glass-smooth mirror polish and subtle golden-russet outer skin. "
            "Bold high-relief carving of Central Asian foreigner figures in flowing robes, lush blooming lotus scrolls, "
            "and ornate Baoxiang flower medallions in deep relief. Full rounded generous proportions, "
            "the carving style is confident cosmopolitan — Chinese and Persian artistic traditions fused together. "
            "The white jade glows with inner warmth, scattered natural russet inclusions adding character. "
            "Opulent, worldly, radiant. Museum photograph, warm directional light on black, ultra realistic 8K"
        ),
        "negative_prompt":(
            "rough primitive surface, thin austere proportions, monochrome muted colors, solemn heavy mood, "
            "simple minimal design, matte unpolished finish, thick clumsy carving, angular harsh lines, "
            "Han or Song style austerity, cartoon, low quality, blurry, watermark, text, plastic, fake"
        ),
        "visual_features":["胡人纹","莲花纹","宝相花纹","丰满圆润","西域风格"],"jade_types":["白玉","青玉"]},
    "song": {"label":"宋代","period":"宋代 (960-1279 AD)",
        "positive_prompt":(
            "Transform this object into a Chinese Song dynasty literati jade piece, "
            "carved from pale misty celadon jade with a soft matte surface that feels like touched silk. "
            "Delicate shallow relief carving just barely rising from the surface — flower-and-bird scenes, "
            "a sprig of plum blossom, or children at play rendered with the lightest touch. "
            "The aesthetic is poetic simplicity: much of the surface is left UNCARVED, negative space valued as deeply as detail. "
            "Thin elegant proportions, subtle openwork for airiness, the object feels weightless. "
            "Scholar's desk refinement, like a Song ink-wash painting rendered in jade. "
            "Understated, intellectual, serene. Soft diffuse lighting on pure black, ultra realistic 8K"
        ),
        "negative_prompt":(
            "thick heavy proportions, shiny polished surface, complex dense ornament covering everything, "
            "bold bright colors, imperial grandeur, dramatic carving, heavy patina, rough surface, "
            "Tang or Qing style opulence, cartoon, low quality, blurry, watermark, text, plastic, fake"
        ),
        "visual_features":["花鸟纹","童子纹","文人雅致","清淡素雅","镂雕"],"jade_types":["青玉","黄玉"]},
    "ming": {"label":"明代","period":"明代 (1368-1644 AD)",
        "positive_prompt":(
            "Transform this object into a Chinese Ming dynasty imperial jade carving, "
            "carved from rich golden-yellow jade with a mirror-smooth polish across every facet. "
            "Dense virtuosic multi-layer openwork relief carving in the famous Lu Zigang style — "
            "dragons coiling through ruyi clouds, phoenixes with individually defined feathers, "
            "every detail rendered with METICULOUS PRECISION and perfect symmetry. "
            "The composition is balanced and authoritative, proclaiming imperial power. "
            "Medium proportions, every square centimeter activated with intricate ornament, "
            "light passing through the pierced layers creating dramatic depth. "
            "Magnificent, precise, majestic. Dramatic spotlighting on pure black, ultra realistic 8K"
        ),
        "negative_prompt":(
            "rough unpolished surface, simple minimalist design, thin delicate proportions, muted subtle colors, "
            "primitive archaic style, partially carved, negative space, understated elegance, "
            "Han or Song style restraint, cartoon, low quality, blurry, watermark, text, plastic, fake"
        ),
        "visual_features":["镂雕透雕","工整细腻","陆子冈风格","龙凤纹","牌饰带板"],"jade_types":["黄玉","白玉"]},
    "qing": {"label":"清代","period":"清代 (1644-1912 AD)",
        "positive_prompt":(
            "Transform this object into a Chinese Qing dynasty Qianlong imperial Mughal-style jade treasure, "
            "carved from deep spinach-green jade with paper-thin translucent walls — LIGHT PASSES THROUGH the jade "
            "revealing glowing emerald depths within. Elaborate Islamic-inspired floral arabesque patterns cover every surface, "
            "accented with gold-wire inlay and inset rubies and turquoises catching the light. "
            "The Hindustan (痕都斯坦) style: semi-transparent thin-walled vessel with exquisite abundance of decoration, "
            "no surface left plain. Qianlong period peak craftsmanship — the apogee of Chinese jade art. "
            "The object appears to GLOW from within when lit. "
            "Exquisite, abundant, breathtaking. Museum photograph with careful translucency lighting on pure black, ultra realistic 8K"
        ),
        "negative_prompt":(
            "plain undecorated surface, thick heavy walls, matte rough finish, simple minimalist design, "
            "muted monochrome, subtle restraint, negative space, primitive carving, opaque jade, "
            "Han or Song style simplicity, cartoon, low quality, blurry, watermark, text, plastic, fake"
        ),
        "visual_features":["痕都斯坦风格","薄胎","乾隆工","繁缛精致","嵌宝石"],"jade_types":["碧玉","白玉","青玉"]},
}

# ========================================
# SHARED DATA - Preset Stories
# ========================================
PRESETS = [
    {"keyword":"君子佩玉","title":"君子佩玉","title_en":"A Gentleman Wears Jade","explanation":"古代君子以玉比德，佩玉于身以时刻自省。玉之温润象征仁，纹理象征义，声音象征智，不折象征勇。","source":"《礼记·玉藻》","source_text":"“君子无故，玉不去身，君子于玉比德焉。”"},
    {"keyword":"弄玉吹箫","title":"弄玉吹箫","title_en":"Nong Yu Plays the Flute","explanation":"秦穆公之女弄玉善吹玉箫，引来凤凰，后与仙人萧史乘凤飞升。玉箫成为仙乐与美好姻缘的象征。","source":"《列仙传》","source_text":"“萧史善吹箫，作凤鸣，秦穆公以女弄玉妻之，一旦皆随凤凰飞去。”"},
    {"keyword":"完璧归赵","title":"完璧归赵","title_en":"Return the Jade Intact","explanation":"蔺相如携和氏璧出使秦国，以智勇双全迫使秦王让步，将无价之宝完好归还赵国，成为外交智慧的典范。","source":"《史记·廉颇蔺相如列传》","source_text":"“城入赵而璧留秦；城不入，臣请完璧归赵。”"},
    {"keyword":"化干戈为玉帛","title":"化干戈为玉帛","title_en":"Swords into Jade and Silk","explanation":"化战争为和平——干戈为兵器，玉帛为礼仪之器。古代诸侯会盟时以玉帛为礼，象征放下兵戈、结为友好。","source":"《淮南子·原道训》","source_text":"“化干戈为玉帛，犹化虎狼为羔羊也。”"},
    {"keyword":"金玉满堂","title":"金玉满堂","title_en":"Hall of Gold and Jade","explanation":"金玉堆满厅堂，象征极致富贵。老子提出“金玉满堂，莫之能守”，提醒世人财富无常，德行方为长久之道。","source":"《老子·九章》","source_text":"“金玉满堂，莫之能守；富贵而骄，自遗其咎。”"},
    {"keyword":"冰清玉洁","title":"冰清玉洁","title_en":"Pure as Ice, Clean as Jade","explanation":"如冰之清澈、如玉之无瑕，比喻人的品格高洁。古人认为玉有九德，纯净无瑕的玉代表了最高尚的人格追求。","source":"《魏书·广陵王传》","source_text":"“冰清玉洁，有若寒松劲竹，虽经霜雪而不改其操。”"},
]

DYNASTY_LIST = [{"id":k,"label":v["label"],"period":v["period"],"features":v["visual_features"],"jade_types":v["jade_types"]} for k,v in DYNASTY_PROMPTS.items()]

# ========================================
# DESIGN OPTIONS — Multi-level jade design selector
# ========================================
DESIGN_OPTIONS = {
    "object": {
        "label": "器物类型", "icon": "🏺", "required": True,
        "options": [
            {"id":"bi","label":"玉璧","desc":"圆盘形礼器","prompt":"a ceremonial bi disc, flat circular form with a central hole"},
            {"id":"cong","label":"玉琮","desc":"方柱形礼器","prompt":"a cong tube, square outer section with a cylindrical bore"},
            {"id":"gui","label":"玉圭","desc":"长条形礼器","prompt":"a gui tablet, elongated flat blade shape with a pointed tip"},
            {"id":"pendant","label":"玉佩","desc":"随身配饰","prompt":"an ornate jade pendant for wearing, elegant flowing shape"},
            {"id":"bracelet","label":"玉镯","desc":"腕间美玉","prompt":"a smooth jade bracelet, circular and continuous"},
            {"id":"vase","label":"玉瓶","desc":"陈设赏器","prompt":"an elegant jade vase with a slender neck and full body"},
            {"id":"ruyi","label":"玉如意","desc":"吉祥如意","prompt":"a ruyi scepter with a lingzhi-shaped cloud head and curved handle"},
            {"id":"seal","label":"玉印","desc":"方寸权力","prompt":"a square jade seal with a carved knob finial on top"},
            {"id":"cup","label":"玉杯","desc":"饮器玲珑","prompt":"a delicate jade cup with subtle flared walls"},
            {"id":"mountain","label":"玉山子","desc":"山水意境","prompt":"a jade mountain carving with landscape scenes in deep relief"},
        ]
    },
    "material": {
        "label": "玉材选择", "icon": "💎", "required": True,
        "options": [
            {"id":"white","label":"白玉","color":"#f0efe8","prompt":"luminous white jade (白玉), glassy smooth with warm undertones"},
            {"id":"celadon-white","label":"青白玉","color":"#c5d5c0","prompt":"celadon-white jade (青白玉), pale greenish-grey with natural veining"},
            {"id":"celadon","label":"青玉","color":"#a8c4a0","prompt":"celadon jade (青玉), soft misty green like distant mountains"},
            {"id":"yellow","label":"黄玉","color":"#e8d5a0","prompt":"golden-yellow jade (黄玉), rich amber warmth like honey in sunlight"},
            {"id":"spinach","label":"碧玉","color":"#5a8a60","prompt":"deep spinach-green jade (碧玉), dark saturated forest depths"},
            {"id":"black","label":"墨玉","color":"#3a3a3a","prompt":"black jade (墨玉), deep inky darkness with subtle undertones"},
            {"id":"brown","label":"糖玉","color":"#b8916a","prompt":"brown sugar jade (糖玉), warm caramel-brown with russet streaks"},
        ]
    },
    "dynasty": {
        "label": "朝代风格", "icon": "🏛️", "required": True,
        "options": [
            {"id":"han","label":"汉代","desc":"古朴厚重，螭龙云气",
             "prompt":"Han dynasty (202 BC-220 AD) archaic solemn style: thick proportions, chi-dragon and cloud-scroll deep carving, rough tool marks, heavy brown patina and calcification — like a 2000-year-old excavated treasure"},
            {"id":"tang","label":"唐代","desc":"丰满圆润，宝相莲花",
             "prompt":"Tang dynasty (618-907 AD) cosmopolitan opulent style: full rounded forms, lotus and Baoxiang flower high-relief, Silk Road fusion of Chinese and Persian art, luminous mirror polish, golden-russet skin"},
            {"id":"song","label":"宋代","desc":"清淡素雅，花鸟童子",
             "prompt":"Song dynasty (960-1279 AD) literati elegant style: delicate shallow carving, flower-and-bird natural scenes, poetic negative space, thin light proportions, soft matte finish — like ink-wash painting in jade"},
            {"id":"ming","label":"明代","desc":"工整大气，镂雕龙凤",
             "prompt":"Ming dynasty (1368-1644 AD) Lu Zigang imperial style: dense multi-layer openwork, dragons and phoenixes with individually defined details, perfect symmetry, mirror-smooth polish, authoritative composition"},
            {"id":"qing","label":"清代","desc":"繁缛精致，痕都斯坦",
             "prompt":"Qing dynasty (1644-1912 AD) Qianlong imperial Mughal style: paper-thin translucent walls, Hindustan floral arabesques, gold-wire inlay, inset rubies and turquoises, breathtaking exquisite craftsmanship"},
        ]
    },
    "bgColor": {
        "label": "背景色调", "icon": "🎨", "required": False,
        "options": [
            {"id":"black","label":"墨黑","color":"#0a0a0a","desc":"博物馆展陈",
             "prompt":"pure black background, dramatic studio spotlighting, museum exhibition photography"},
            {"id":"warm","label":"暖金","color":"#3a3028","desc":"宫廷华贵",
             "prompt":"warm dark golden-brown background, imperial palace atmosphere, soft directional light"},
            {"id":"celadon-gray","label":"青瓷灰","color":"#8a9088","desc":"素雅文气",
             "prompt":"misty celadon-gray gradient background, soft diffused lighting, serene scholarly atmosphere"},
            {"id":"sandalwood","label":"檀木棕","color":"#3c2a1e","desc":"古朴素净",
             "prompt":"dark sandalwood brown background, wooden collector's shelf, warm subtle ambient light"},
            {"id":"cream","label":"素白","color":"#f5f0e8","desc":"纯净无瑕",
             "prompt":"pure cream white background, bright clean studio lighting, minimalist presentation"},
        ]
    },
    "pattern": {
        "label": "纹饰图案", "icon": "🌀", "required": False, "multi": True,
        "options": [
            {"id":"dragon","label":"螭龙纹","prompt":"chi-dragon serpents coiling across the surface"},
            {"id":"cloud","label":"云气纹","prompt":"flowing cloud-scroll spirals filling the background"},
            {"id":"grain","label":"谷纹","prompt":"raised grain pattern dots in orderly rows"},
            {"id":"lotus","label":"莲花纹","prompt":"blooming lotus flower scrolls"},
            {"id":"phoenix","label":"凤鸟纹","prompt":"phoenixes with spread tail feathers"},
            {"id":"flower-bird","label":"花鸟纹","prompt":"delicate flower-and-bird natural scenes"},
            {"id":"taotie","label":"饕餮纹","prompt":"taotie beast mask with symmetrical fierce features"},
            {"id":"ruyi-pattern","label":"如意纹","prompt":"lingzhi ruyi cloud-head motifs"},
            {"id":"key-fret","label":"回纹","prompt":"continuous key-fret meander border patterns"},
            {"id":"plain","label":"素面无纹","prompt":"smooth unadorned surface, pure jade beauty alone"},
        ]
    },
    "craft": {
        "label": "雕刻工艺", "icon": "🔨", "required": False, "multi": True,
        "options": [
            {"id":"relief","label":"浮雕","prompt":"bold relief carving with figures rising from surface"},
            {"id":"openwork","label":"镂雕透雕","prompt":"intricate openwork piercing through multiple layers"},
            {"id":"round","label":"圆雕","prompt":"fully three-dimensional round sculptural carving"},
            {"id":"line","label":"阴线刻","prompt":"fine incised line engraving with hair-thin precision"},
            {"id":"thin-wall","label":"薄胎工艺","prompt":"paper-thin translucent walls that glow when backlit"},
            {"id":"gem-inlay","label":"嵌宝石","prompt":"inset rubies and turquoises catching light"},
            {"id":"gold-inlay","label":"错金丝","prompt":"gold-wire inlay tracing delicate arabesque lines"},
        ]
    },
    "visualStyle": {
        "label": "画面风格", "icon": "🖼️", "required": False,
        "options": [
            {"id":"museum","label":"博物馆写真","desc":"超写实摄影",
             "prompt":"museum artifact photography, ultra realistic 8K, dramatic lighting, sharp detail"},
            {"id":"ink-wash","label":"古风水墨","desc":"写意留白",
             "prompt":"Chinese ink-wash painting aesthetic, poetic simplicity, misty soft brush-stroke textures, elegant negative space"},
            {"id":"court","label":"宫廷画卷","desc":"富丽堂皇",
             "prompt":"Ming-Qing court painting style, rich saturated colors, ornate detailed composition, imperial grandeur"},
            {"id":"minimal","label":"极简素雅","desc":"大朴不雕",
             "prompt":"minimalist clean aesthetic, single object centered, abundant breathing space, serene meditative"},
            {"id":"archaeological","label":"文物出土","desc":"斑驳古朴",
             "prompt":"archaeological excavation photograph, half-buried in earth, genuine ancient patina, raking sunlight, raw authentic"},
        ]
    },
}

def build_design_prompt(selections: dict) -> str:
    """Build a comprehensive prompt from user's design selections."""
    parts = []
    if selections.get("visualStyle"):
        opt = next((o for o in DESIGN_OPTIONS["visualStyle"]["options"] if o["id"] == selections["visualStyle"]), None)
        if opt: parts.append(opt["prompt"])
    core = "A Chinese jade artifact: "
    obj = next((o for o in DESIGN_OPTIONS["object"]["options"] if o["id"] == selections.get("object")), None)
    if obj: core += obj["prompt"]
    mat = next((o for o in DESIGN_OPTIONS["material"]["options"] if o["id"] == selections.get("material")), None)
    if mat: core += f", carved from {mat['prompt']}"
    dyn = next((o for o in DESIGN_OPTIONS["dynasty"]["options"] if o["id"] == selections.get("dynasty")), None)
    if dyn: core += f". {dyn['prompt']}"
    parts.append(core)
    if selections.get("patterns"):
        selected = [o for o in DESIGN_OPTIONS["pattern"]["options"] if o["id"] in selections["patterns"]]
        if selected: parts.append("Surface decoration: " + ". ".join(o["prompt"] for o in selected) + ".")
    if selections.get("crafts"):
        selected = [o for o in DESIGN_OPTIONS["craft"]["options"] if o["id"] in selections["crafts"]]
        if selected: parts.append("Carving technique: " + ". ".join(o["prompt"] for o in selected) + ".")
    if selections.get("bgColor"):
        opt = next((o for o in DESIGN_OPTIONS["bgColor"]["options"] if o["id"] == selections["bgColor"]), None)
        if opt: parts.append(f"Setting: {opt['prompt']}.")
    parts.append("Professional product photography, studio lighting, square format.")
    prompt = " ".join(parts)
    print(f"[PromptBuilder] {prompt}")
    return prompt


def build_negative_prompt(selections: dict) -> str:
    """Build negative prompt based on what the user selected."""
    negatives = [
        "cartoon", "low quality", "blurry", "watermark", "text", "signature",
        "plastic", "fake", "3D render", "CGI", "multiple objects", "cluttered",
        "distorted proportions", "deformed", "disfigured",
    ]
    style_negatives = {
        "museum": "painting, sketch, cartoon, illustration, abstract",
        "ink-wash": "photorealistic, sharp focus, hard edges, glossy, shiny, 3D render",
        "court": "minimalist, empty space, monochrome, rough, primitive",
        "minimal": "cluttered, ornate, complex, busy, baroque, elaborate",
        "archaeological": "polished, perfect, shiny, clean, modern, studio lighting",
    }
    style = selections.get("visualStyle", "")
    if style in style_negatives: negatives.append(style_negatives[style])
    return ", ".join(negatives)


class DesignRequest(BaseModel):
    object: str = ""
    material: str = ""
    dynasty: str = ""
    bgColor: str = ""
    patterns: list[str] = []
    crafts: list[str] = []
    visualStyle: str = ""


# ========================================
# API - Dynasty Filter
# ========================================
@app.get("/api/dynasties")
async def list_dynasties():
    return JSONResponse(DYNASTY_LIST)

@app.get("/api/design-options")
async def get_design_options():
    result = {}
    for cat_key, cat_val in DESIGN_OPTIONS.items():
        result[cat_key] = {
            "label": cat_val["label"], "icon": cat_val.get("icon", ""),
            "required": cat_val.get("required", False), "multi": cat_val.get("multi", False),
            "options": [{"id": o["id"], "label": o["label"], "desc": o.get("desc", ""), "color": o.get("color", "")} for o in cat_val["options"]]
        }
    return JSONResponse(result)

@app.post("/api/generate-jade-design")
async def generate_jade_design(req: DesignRequest, request: Request):
    if not req.object or not req.material or not req.dynasty:
        missing = []
        if not req.object: missing.append("器物类型")
        if not req.material: missing.append("玉材选择")
        if not req.dynasty: missing.append("朝代风格")
        raise HTTPException(400, f"请选择: {', '.join(missing)}")
    creds = image_credentials(request)
    if not creds["key"]:
        raise HTTPException(400, MISSING_IMAGE_KEY_MSG)
    selections = {"object":req.object,"material":req.material,"dynasty":req.dynasty,"bgColor":req.bgColor,"patterns":req.patterns,"crafts":req.crafts,"visualStyle":req.visualStyle}
    prompt = build_design_prompt(selections)
    negative = build_negative_prompt(selections)
    print(f"[Image] Generating jade design with {creds['model']} ...")
    try:
        resp = requests.post(f"{creds['base']}/images/generations",
            headers={"Authorization": f"Bearer {creds['key']}", "Content-Type": "application/json"},
            json={"model": creds["model"], "prompt": prompt, "negative_prompt": negative, "n": 1, "size": "1024x1024"}, timeout=120)
    except requests.RequestException as e:
        print(f"[Image] Connection error: {e}")
        raise HTTPException(502, f"无法连接图片生成服务 {creds['base']}，请检查网络或 Base URL。")
    if resp.status_code in (401, 403):
        raise HTTPException(400, f"API Key 无效或无权调用该模型（HTTP {resp.status_code}），请检查设置中的 Key。")
    if resp.status_code != 200:
        err = resp.text[:300]
        print(f"[Image] HTTP {resp.status_code}: {err}")
        raise HTTPException(502, f"图片生成服务返回 {resp.status_code}: {err}")
    data = resp.json()
    img_url = data.get("data", [{}])[0].get("url", "")
    if not img_url:
        raise HTTPException(502, f"图片生成服务未返回图片地址: {resp.text[:300]}")
    print(f"[Image] Downloading result ...")
    try:
        img_resp = requests.get(img_url, timeout=60)
    except requests.RequestException as e:
        print(f"[Image] Download error: {e}")
        raise HTTPException(502, "下载生成结果失败，请重试。")
    if img_resp.status_code != 200:
        raise HTTPException(502, f"下载生成结果失败: HTTP {img_resp.status_code}")
    result_bytes = img_resp.content
    print(f"[Image] Success ({len(result_bytes)} bytes)")
    result_id = uuid.uuid4().hex[:8]; (RESULT_DIR / f"{result_id}.png").write_bytes(result_bytes)
    dyn_label = next((o["label"] for o in DESIGN_OPTIONS["dynasty"]["options"] if o["id"] == req.dynasty), req.dynasty)
    return JSONResponse({"id":result_id,"result_url":f"/api/images/{result_id}.png","dynasty":req.dynasty,"dynasty_label":dyn_label})

# ========================================
# API - Story Generator
# ========================================
class StoryRequest(BaseModel):
    keyword: str

SYSTEM_PROMPT = 'You are a Chinese jade culture expert. Return ONLY JSON: {"title":"2-6 char title","title_en":"English","explanation":"within 80 chars","source":"classical source","source_text":"original quote within 15 chars"}. Keyword: '

def generate_ai_illustration(keyword: str, title: str, creds: dict):
    """用使用者自己的 Key 生成彩色插画。返回 bytes 或 None。"""
    if not creds["key"]: return None
    try:
        prompt = f"A vividly colorful Chinese ink and color painting. Bright saturated colors: emerald green, cinnabar red, gold yellow, royal blue, pure white. Scene: the ancient Chinese story \"{title}\" ({keyword}). Elegant figures in flowing silk robes, luminous jade artifacts, ornate palace garden. Rich traditional Chinese color palette, like Tang dynasty mural or Ming court painting. Full color spectrum. NO monochrome. Square format."

        print(f"[Image] Requesting illustration for: {title}")
        resp = requests.post(f"{creds['base']}/images/generations",
            headers={"Authorization": f"Bearer {creds['key']}", "Content-Type": "application/json"},
            json={"model": creds["model"], "prompt": prompt, "n": 1, "size": "1024x1024"},
            timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            url = data.get("data", [{}])[0].get("url", "")
            if url:
                print(f"[Image] Downloading image ...")
                img_resp = requests.get(url, timeout=30)
                if img_resp.status_code == 200:
                    return img_resp.content
        else:
            print(f"[Image] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e: print(f"[Image] Exception: {e}")
    return None

def try_illustration(keyword: str, title: str, creds: dict):
    """尽力生成配图；没有 Key 时返回 (None, "none")，文字卡片照常出。"""
    if not creds["key"]: return None, "none"
    ai = generate_ai_illustration(keyword, title, creds)
    return (ai, "ai") if ai else (None, "none")

def _save_illustration(ill_bytes):
    if not ill_bytes: return None
    ill_id = uuid.uuid4().hex[:10]
    (RESULT_DIR / f"{ill_id}.png").write_bytes(ill_bytes)
    return f"/api/images/{ill_id}.png"

@app.get("/api/presets")
async def get_presets():
    return JSONResponse(PRESETS)

@app.post("/api/generate-story")
async def generate_story(req: StoryRequest, request: Request):
    kw = req.keyword.strip()
    if not kw or len(kw) > 30: raise HTTPException(400, "keyword must be 1-30 chars")

    img_creds = image_credentials(request)
    txt_creds = text_credentials(request)

    # Check presets first
    for p in PRESETS:
        if p["keyword"] == kw:
            ill_bytes, ill_src = try_illustration(kw, p["title"], img_creds)
            return JSONResponse({"id":uuid.uuid4().hex[:10],"title":p["title"],"title_en":p["title_en"],"explanation":p["explanation"],"source":p["source"],"source_text":p["source_text"],"illustration_url":_save_illustration(ill_bytes),"keyword":kw,"generated":False,"illustration_source":ill_src})

    # LLM generation
    story = None
    fallback = {"title":kw,"title_en":kw,"explanation":f"「{kw}」 is a classical allusion in Chinese jade culture.","source":"Jade Culture","source_text":"Jade is the beauty of stone, possessing five virtues."}

    if txt_creds["key"]:
        try:
            print(f"[Text] Generating story for: {kw} with {txt_creds['model']}")
            resp = requests.post(f"{txt_creds['base']}/chat/completions",
                headers={"Authorization": f"Bearer {txt_creds['key']}", "Content-Type": "application/json"},
                json={"model":txt_creds["model"],"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":kw}],"temperature":0.7,"max_tokens":300}, timeout=30)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"): content = content.split("\n",1)[1].rstrip("`")
                story = json.loads(content)
                print(f"[Text] Story: {story.get('title','')}")
            else: print(f"[Text] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e: print(f"[Text] Exception: {e}")

    if not story: story = fallback

    ill_bytes, ill_src = try_illustration(kw, story.get("title", kw), img_creds)
    return JSONResponse({"id":uuid.uuid4().hex[:10],"title":story.get("title",kw),"title_en":story.get("title_en",kw),"explanation":story.get("explanation",""),"source":story.get("source",""),"source_text":story.get("source_text",""),"illustration_url":_save_illustration(ill_bytes),"keyword":kw,"generated":True,"illustration_source":ill_src})

# ========================================
# API - Shared
# ========================================
@app.get("/api/images/{filename}")
async def get_image(filename: str):
    for d in (UPLOAD_DIR, RESULT_DIR):
        p = d / filename
        if p.exists(): return FileResponse(p, media_type="image/png")
    raise HTTPException(404, "Image not found")

@app.get("/api/health")
async def health(request: Request):
    img, txt = image_credentials(request), text_credentials(request)
    return {
        "status": "ok",
        "has_image_key": bool(img["key"]),
        "has_text_key": bool(txt["key"]),
        "image_model": img["model"],
        "text_model": txt["model"],
    }

# ========================================
# Static file serving - AFTER API routes
# ========================================
if FRONTEND_DIR.exists():
    @app.get("/", include_in_schema=False)
    async def index():
        """前端入口是 玉境.html，没有 index.html，所以给根路径补一条路由。"""
        entry = FRONTEND_DIR / "玉境.html"
        if entry.exists():
            return FileResponse(entry, media_type="text/html; charset=utf-8")
        raise HTTPException(404, "前端入口 玉境.html 不存在")

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# ========================================
# Startup
# ========================================
if __name__ == "__main__":
    import uvicorn

    def open_browser():
        webbrowser.open("http://localhost:8000")

    threading.Timer(1.5, open_browser).start()

    print("\n" + "=" * 50)
    print("  Jade Culture Hub")
    print("  http://localhost:8000")
    print("  Press Ctrl+C to stop")
    print("=" * 50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
