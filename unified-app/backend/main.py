"""
文化基因库与时空地图 — Unified Backend API
Dynasty Filter · Silk Road · Story Generator
"""

import os, re, uuid, json
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import requests

try:  # .env is optional — the app still runs on plain environment variables
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

app = FastAPI(title="Jade Culture Hub API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path("uploads"); RESULT_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True); RESULT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════
# CREDENTIALS — bring your own key
# ═══════════════════════════════════════
# 本项目不内置任何 API Key。凭据来源优先级：
#   1) 请求头（前端「设置」面板填写，浏览器 localStorage 保存）
#   2) 环境变量 / backend/.env（自部署时的默认值）
# 图片生成走 SiliconFlow（OpenAI 兼容 images/generations）；
# 文本生成走任意 OpenAI 兼容 chat/completions 服务。

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
    """Allow a client-supplied base URL, but only for public http(s) hosts.

    The base URL ends up in a server-side request, so a browser user must not be
    able to point it at loopback / RFC1918 addresses. Server operators can still
    override it freely through the environment variables.
    """
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
    """SiliconFlow (or compatible) credentials for image generation."""
    return {
        "key":   _header(request, "X-Image-Key") or ENV_IMAGE_KEY,
        "model": _header(request, "X-Image-Model") or ENV_IMAGE_MODEL,
        "base":  _client_base_url(request, "X-Image-Base", ENV_IMAGE_BASE),
    }


def text_credentials(request: Request) -> dict:
    """OpenAI-compatible credentials for story text generation."""
    return {
        "key":   _header(request, "X-Text-Key") or ENV_TEXT_KEY,
        "model": _header(request, "X-Text-Model") or ENV_TEXT_MODEL,
        "base":  _client_base_url(request, "X-Text-Base", ENV_TEXT_BASE),
    }


MISSING_IMAGE_KEY_MSG = (
    "未配置图片生成 API Key。请点击右上角 ⚙️ 设置填写 SiliconFlow Key，"
    "或在 backend/.env 中设置 SILICONFLOW_API_KEY。"
)

# ═══════════════════════════════════════
# SHARED DATA — Dynasty Prompts
# ═══════════════════════════════════════
DYNASTY_PROMPTS = {
    "han": {"label":"汉代","period":"西汉-东汉 (202 BC–220 AD)",
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
        "visual_features":["螭纹(chī dragon)","云气纹","谷纹","蚕纹","古朴厚重"],"jade_types":["青白玉","黄玉"]},
    "tang": {"label":"唐代","period":"唐代 (618–907 AD)",
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
    "song": {"label":"宋代","period":"宋代 (960–1279 AD)",
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
    "ming": {"label":"明代","period":"明代 (1368–1644 AD)",
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
    "qing": {"label":"清代","period":"清代 (1644–1912 AD)",
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

# ═══════════════════════════════════════
# SHARED DATA — Preset Stories
# ═══════════════════════════════════════
PRESETS = [ 
    {"keyword":"君子佩玉","title":"君子佩玉","title_en":"A Gentleman Wears Jade","explanation":"古代君子以玉比德，佩玉于身以时刻自省。玉之温润象征仁，纹理象征义，声音象征智，不折象征勇。","source":"《礼记·玉藻》","source_text":"君子无故，玉不去身，君子于玉比德焉。"},
    {"keyword":"弄玉吹箫","title":"弄玉吹箫","title_en":"Nong Yu Plays the Flute","explanation":"秦穆公之女弄玉善吹玉箫，引来凤凰，后与仙人萧史乘凤飞升。玉箫成为仙乐与美好姻缘的象征。","source":"《列仙传》","source_text":"萧史善吹箫，作凤鸣，秦穆公以女弄玉妻之，一旦皆随凤凰飞去。"},
    {"keyword":"完璧归赵","title":"完璧归赵","title_en":"Return the Jade Intact","explanation":"蔺相如携和氏璧出使秦国，以智勇双全迫使秦王让步，将无价之宝完好归还赵国，成为外交智慧的典范。","source":"《史记·廉颇蔺相如列传》","source_text":"城入赵而璧留秦；城不入，臣请完璧归赵。"},
    {"keyword":"化干戈为玉帛","title":"化干戈为玉帛","title_en":"Swords into Jade and Silk","explanation":"化战争为和平——干戈为兵器，玉帛为礼仪之器。古代诸侯会盟时以玉帛为礼，象征放下兵戈、结为友好。","source":"《淮南子·原道训》","source_text":"化干戈为玉帛，犹化虎狼为羔羊也。"},
    {"keyword":"金玉满堂","title":"金玉满堂","title_en":"Hall of Gold and Jade","explanation":"金玉堆满厅堂，象征极致富贵。老子提出“金玉满堂，莫之能守”，提醒世人财富无常，德行方为长久之道。","source":"《老子·九章》","source_text":"“金玉满堂，莫之能守；富贵而骄，自遗其咎。”"},
    {"keyword":"冰清玉洁","title":"冰清玉洁","title_en":"Pure as Ice, Clean as Jade","explanation":"如冰之清澈、如玉之无瑕，比喻人的品格高洁。古人认为玉有九德，纯净无瑕的玉代表了最高尚的人格追求。","source":"《魏书·广陵王传》","source_text":"“冰清玉洁，有若寒松劲竹，虽经霜雪而不改其操。”"},
]

DYNASTY_LIST = [{"id":k,"label":v["label"],"period":v["period"],"features":v["visual_features"],"jade_types":v["jade_types"]} for k,v in DYNASTY_PROMPTS.items()]

# ═══════════════════════════════════════
# DESIGN OPTIONS — Multi-level jade design selector
# ═══════════════════════════════════════
DESIGN_OPTIONS = {
    "object": {
        "label": "器物类型", "icon": "🏺", "required": True,
        "options": [
            {"id":"bi","label":"玉璧","desc":"圆盘形礼器，礼天之器","prompt":"a ceremonial bi disc, flat circular form with a central hole"},
            {"id":"cong","label":"玉琮","desc":"方柱形礼器，礼地之器","prompt":"a cong tube, square outer section with a cylindrical bore"},
            {"id":"gui","label":"玉圭","desc":"长条形礼器，权力象征","prompt":"a gui tablet, elongated flat blade shape with a pointed tip"},
            {"id":"pendant","label":"玉佩","desc":"随身配饰，君子之风","prompt":"an ornate jade pendant for wearing, elegant flowing shape"},
            {"id":"bracelet","label":"玉镯","desc":"腕间美玉，圆润天成","prompt":"a smooth jade bracelet, circular and continuous"},
            {"id":"vase","label":"玉瓶","desc":"陈设赏器，端庄典雅","prompt":"an elegant jade vase with a slender neck and full body"},
            {"id":"ruyi","label":"玉如意","desc":"吉祥如意，灵芝云头","prompt":"a ruyi scepter with a lingzhi-shaped cloud head and curved handle"},
            {"id":"seal","label":"玉印","desc":"方寸之间，权力之美","prompt":"a square jade seal with a carved knob finial on top"},
            {"id":"cup","label":"玉杯","desc":"饮器之美，玲珑剔透","prompt":"a delicate jade cup with subtle flared walls"},
            {"id":"mountain","label":"玉山子","desc":"山水意境，立体画卷","prompt":"a jade mountain carving with landscape scenes in deep relief"},
        ]
    },
    "material": {
        "label": "玉材选择", "icon": "💎", "required": True,
        "options": [
            {"id":"white","label":"白玉","color":"#f0efe8","prompt":"luminous white jade (白玉), glassy smooth surface with subtle warm undertones"},
            {"id":"celadon-white","label":"青白玉","color":"#c5d5c0","prompt":"celadon-white jade (青白玉), pale greenish-grey with natural veining"},
            {"id":"celadon","label":"青玉","color":"#a8c4a0","prompt":"celadon jade (青玉), soft misty green like distant mountains"},
            {"id":"yellow","label":"黄玉","color":"#e8d5a0","prompt":"golden-yellow jade (黄玉), rich amber warmth like honey in sunlight"},
            {"id":"spinach","label":"碧玉","color":"#5a8a60","prompt":"deep spinach-green jade (碧玉), dark and saturated like forest depths"},
            {"id":"black","label":"墨玉","color":"#3a3a3a","prompt":"black jade (墨玉), deep inky darkness with subtle undertones"},
            {"id":"brown","label":"糖玉","color":"#b8916a","prompt":"brown sugar jade (糖玉), warm caramel-brown with natural russet streaks"},
        ]
    },
    "dynasty": {
        "label": "朝代风格", "icon": "🏛️", "required": True,
        "options": [
            {"id":"han","label":"汉代","desc":"古朴厚重，礼器庄严，螭龙云气",
             "prompt":"Han dynasty (202 BC-220 AD) archaic solemn style: ritual solemnity, thick proportions, chi-dragon and cloud-scroll motifs, deep low-relief carving, rough hewn tool marks, heavy brown patina, calcification spots — like a 2000-year-old excavated treasure"},
            {"id":"tang","label":"唐代","desc":"丰满圆润，西域风情，宝相莲花",
             "prompt":"Tang dynasty (618-907 AD) cosmopolitan opulent style: full rounded generous forms, Central Asian foreigner figures, lotus and Baoxiang flower patterns, high-relief confident carving, Silk Road fusion of Chinese and Persian art, luminous polish"},
            {"id":"song","label":"宋代","desc":"清淡素雅，文人雅趣，花鸟童子",
             "prompt":"Song dynasty (960-1279 AD) literati elegant style: delicate shallow carving barely rising from surface, flower-and-bird scenes, poetic negative space, thin light proportions, soft matte finish, understated intellectual refinement — like an ink-wash painting rendered in jade"},
            {"id":"ming","label":"明代","desc":"工整大气，陆子冈风，镂雕龙凤",
             "prompt":"Ming dynasty (1368-1644 AD) Lu Zigang imperial style: dense multi-layer openwork, dragons and phoenixes with individually defined scales and feathers, meticulous precision, perfect symmetry, mirror-smooth polish, authoritative balanced composition"},
            {"id":"qing","label":"清代","desc":"繁缛精致，痕都斯坦，乾隆工",
             "prompt":"Qing dynasty (1644-1912 AD) Qianlong imperial Mughal style: paper-thin translucent walls, Hindustan Islamic-inspired floral arabesques, gold-wire inlay, inset rubies and turquoises, elaborate decoration covering every surface, breathtaking exquisite craftsmanship"},
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
            {"id":"plain","label":"素面无纹","prompt":"smooth unadorned surface, the beauty of pure jade alone"},
        ]
    },
    "craft": {
        "label": "雕刻工艺", "icon": "🔨", "required": False, "multi": True,
        "options": [
            {"id":"relief","label":"浮雕","prompt":"bold relief carving with figures rising from the surface"},
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
            {"id":"museum","label":"博物馆写真","desc":"超写实文物摄影",
             "prompt":"museum artifact photography, ultra realistic 8K, sharp detail, dramatic lighting"},
            {"id":"ink-wash","label":"古风水墨","desc":"写意留白雅致",
             "prompt":"Chinese ink-wash painting aesthetic, poetic simplicity, misty atmosphere, soft brush-stroke textures, elegant negative space"},
            {"id":"court","label":"宫廷画卷","desc":"富丽堂皇华美",
             "prompt":"Ming-Qing court painting style, rich saturated colors, ornate detailed composition, imperial grandeur, gold accents"},
            {"id":"minimal","label":"极简素雅","desc":"大朴不雕纯粹",
             "prompt":"minimalist clean aesthetic, single object centered, abundant breathing space, the jade as pure sculptural form, serene and meditative"},
            {"id":"archaeological","label":"文物出土","desc":"斑驳沧桑古朴",
             "prompt":"archaeological excavation photograph, the jade half-buried in earth, genuine ancient patina, raking sunlight revealing surface texture, raw and authentic"},
        ]
    },
}

def build_design_prompt(selections: dict) -> str:
    """Build a comprehensive prompt from user's design selections."""
    parts = []

    # Visual style (goes first as overall direction)
    if selections.get("visualStyle"):
        opt = next((o for o in DESIGN_OPTIONS["visualStyle"]["options"] if o["id"] == selections["visualStyle"]), None)
        if opt: parts.append(opt["prompt"])

    # Core description: object + material + dynasty
    core = "A Chinese jade artifact: "
    obj = next((o for o in DESIGN_OPTIONS["object"]["options"] if o["id"] == selections.get("object")), None)
    if obj: core += obj["prompt"]

    mat = next((o for o in DESIGN_OPTIONS["material"]["options"] if o["id"] == selections.get("material")), None)
    if mat: core += f", carved from {mat['prompt']}"

    dyn = next((o for o in DESIGN_OPTIONS["dynasty"]["options"] if o["id"] == selections.get("dynasty")), None)
    if dyn: core += f". {dyn['prompt']}"

    parts.append(core)

    # Patterns
    if selections.get("patterns"):
        selected = [o for o in DESIGN_OPTIONS["pattern"]["options"] if o["id"] in selections["patterns"]]
        if selected:
            parts.append("Surface decoration: " + ". ".join(o["prompt"] for o in selected) + ".")

    # Craft techniques
    if selections.get("crafts"):
        selected = [o for o in DESIGN_OPTIONS["craft"]["options"] if o["id"] in selections["crafts"]]
        if selected:
            parts.append("Carving technique: " + ". ".join(o["prompt"] for o in selected) + ".")

    # Background
    if selections.get("bgColor"):
        opt = next((o for o in DESIGN_OPTIONS["bgColor"]["options"] if o["id"] == selections["bgColor"]), None)
        if opt: parts.append(f"Setting: {opt['prompt']}.")

    # Closing
    parts.append("Professional product photography, studio lighting, square format.")

    prompt = " ".join(parts)
    print(f"[PromptBuilder] {prompt}")
    return prompt


def build_negative_prompt(selections: dict) -> str:
    """Build negative prompt based on what the user did NOT select."""
    negatives = [
        "cartoon", "low quality", "blurry", "watermark", "text", "signature",
        "plastic", "fake", "3D render", "CGI", "multiple objects", "cluttered",
        "distorted proportions", "deformed", "disfigured",
    ]

    # If user chose a visual style, exclude conflicting ones
    style_negatives = {
        "museum": "painting, sketch, cartoon, illustration, abstract",
        "ink-wash": "photorealistic, sharp focus, hard edges, glossy, shiny, 3D render",
        "court": "minimalist, empty space, monochrome, rough, primitive",
        "minimal": "cluttered, ornate, complex, busy, baroque, elaborate",
        "archaeological": "polished, perfect, shiny, clean, modern, studio lighting",
    }
    style = selections.get("visualStyle", "")
    if style in style_negatives:
        negatives.append(style_negatives[style])

    return ", ".join(negatives)


class DesignRequest(BaseModel):
    object: str = ""
    material: str = ""
    dynasty: str = ""
    bgColor: str = ""
    patterns: list[str] = []
    crafts: list[str] = []
    visualStyle: str = ""


# ═══════════════════════════════════════
# API — Dynasty Filter
# ═══════════════════════════════════════
@app.get("/api/dynasties")
async def list_dynasties():
    return JSONResponse(DYNASTY_LIST)

@app.get("/api/design-options")
async def get_design_options():
    """Return all available design options for the multi-level selector."""
    # Strip internal prompt fields before sending to frontend
    result = {}
    for cat_key, cat_val in DESIGN_OPTIONS.items():
        result[cat_key] = {
            "label": cat_val["label"],
            "icon": cat_val.get("icon", ""),
            "required": cat_val.get("required", False),
            "multi": cat_val.get("multi", False),
            "options": [{"id": o["id"], "label": o["label"], "desc": o.get("desc", ""), "color": o.get("color", "")} for o in cat_val["options"]]
        }
    return JSONResponse(result)

@app.post("/api/generate-jade-design")
async def generate_jade_design(req: DesignRequest, request: Request):
    # Validate required fields
    if not req.object or not req.material or not req.dynasty:
        missing = []
        if not req.object: missing.append("器物类型")
        if not req.material: missing.append("玉材选择")
        if not req.dynasty: missing.append("朝代风格")
        raise HTTPException(400, f"请选择: {', '.join(missing)}")

    creds = image_credentials(request)
    if not creds["key"]:
        raise HTTPException(400, MISSING_IMAGE_KEY_MSG)

    selections = {
        "object": req.object,
        "material": req.material,
        "dynasty": req.dynasty,
        "bgColor": req.bgColor,
        "patterns": req.patterns,
        "crafts": req.crafts,
        "visualStyle": req.visualStyle,
    }

    prompt = build_design_prompt(selections)
    negative = build_negative_prompt(selections)

    print(f"[Image] Generating jade design with {creds['model']} …")
    try:
        resp = requests.post(
            f"{creds['base']}/images/generations",
            headers={"Authorization": f"Bearer {creds['key']}", "Content-Type": "application/json"},
            json={
                "model": creds["model"],
                "prompt": prompt,
                "negative_prompt": negative,
                "n": 1,
                "size": "1024x1024"
            },
            timeout=120)
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

    print(f"[Image] Downloading result…")
    try:
        img_resp = requests.get(img_url, timeout=60)
    except requests.RequestException as e:
        print(f"[Image] Download error: {e}")
        raise HTTPException(502, "下载生成结果失败，请重试。")
    if img_resp.status_code != 200:
        raise HTTPException(502, f"下载生成结果失败: HTTP {img_resp.status_code}")
    result_bytes = img_resp.content
    print(f"[Image] Success ({len(result_bytes)} bytes)")

    result_id = uuid.uuid4().hex[:8]
    (RESULT_DIR / f"{result_id}.png").write_bytes(result_bytes)

    dyn_label = next((o["label"] for o in DESIGN_OPTIONS["dynasty"]["options"] if o["id"] == req.dynasty), req.dynasty)
    return JSONResponse({
        "id": result_id,
        "result_url": f"/api/images/{result_id}.png",
        "dynasty": req.dynasty,
        "dynasty_label": dyn_label,
    })

# ═══════════════════════════════════════
# API — Story Generator
# ═══════════════════════════════════════
class StoryRequest(BaseModel):
    keyword: str

SYSTEM_PROMPT = """你是精通中国玉文化和古典文献的专家。根据关键词返回JSON: {"title":"2-6字标题","title_en":"英文","explanation":"80字以内释义","source":"经典出处","source_text":"原文引用(15字以内)"}。只返回JSON。关键词："""

def generate_ai_illustration(keyword: str, title: str, creds: dict) -> bytes | None:
    """Generate a colorful illustration with the user's own key. Returns bytes or None."""
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
                print(f"[Image] Downloading illustration…")
                img_resp = requests.get(url, timeout=30)
                if img_resp.status_code == 200:
                    return img_resp.content
        else:
            print(f"[Image] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[Image] Exception: {e}")
    return None

def try_illustration(keyword: str, title: str, creds: dict) -> tuple[bytes | None, str]:
    """Best-effort illustration. Without a key the story card still renders (text only)."""
    if not creds["key"]:
        return None, "none"
    ai_bytes = generate_ai_illustration(keyword, title, creds)
    return (ai_bytes, "ai") if ai_bytes else (None, "none")

@app.get("/api/presets")
async def get_presets():
    return JSONResponse([{k:v for k,v in p.items() if k!="keyword" or True} for p in PRESETS])

def _save_illustration(ill_bytes: bytes | None) -> str | None:
    """Persist illustration bytes and return its public URL (None when absent)."""
    if not ill_bytes: return None
    ill_id = uuid.uuid4().hex[:10]
    (RESULT_DIR/f"{ill_id}.png").write_bytes(ill_bytes)
    return f"/api/images/{ill_id}.png"


@app.post("/api/generate-story")
async def generate_story(req: StoryRequest, request: Request):
    kw = req.keyword.strip()
    if not kw or len(kw)>30: raise HTTPException(400,"关键词需在1-30字之间")

    img_creds = image_credentials(request)
    txt_creds = text_credentials(request)

    # Check presets first
    for p in PRESETS:
        if p["keyword"]==kw:
            ill_bytes, ill_src = try_illustration(kw, p["title"], img_creds)
            return JSONResponse({"id":uuid.uuid4().hex[:10],"title":p["title"],"title_en":p["title_en"],"explanation":p["explanation"],"source":p["source"],"source_text":p["source_text"],"illustration_url":_save_illustration(ill_bytes),"keyword":kw,"generated":False,"illustration_source":ill_src})

    # LLM generation
    story = None
    if txt_creds["key"]:
        try:
            print(f"[Text] Generating story for: {kw} with {txt_creds['model']}")
            resp = requests.post(f"{txt_creds['base']}/chat/completions",
                headers={"Authorization":f"Bearer {txt_creds['key']}","Content-Type":"application/json"},
                json={"model":txt_creds["model"],"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":kw}],"temperature":0.7,"max_tokens":300},timeout=30)
            if resp.status_code==200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"): content = content.split("\n",1)[1].rstrip("`")
                story = json.loads(content)
                print(f"[Text] Story generated: {story.get('title','')}")
            else:
                print(f"[Text] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[Text] Exception: {e}")

    if not story:
        story = {"title":kw,"title_en":kw,"explanation":f"「{kw}」是中国玉文化中的经典典故，蕴含古人对美玉的崇敬与哲思。玉象征仁、义、智、勇、洁五德，传递了中华文明独特的玉石精神。","source":"玉文化典故","source_text":"玉者，石之美者也，有五德。"}

    ill_bytes, ill_src = try_illustration(kw, story.get("title", kw), img_creds)
    return JSONResponse({"id":uuid.uuid4().hex[:10],"title":story.get("title",kw),"title_en":story.get("title_en",kw),"explanation":story.get("explanation",""),"source":story.get("source",""),"source_text":story.get("source_text",""),"illustration_url":_save_illustration(ill_bytes),"keyword":kw,"generated":True,"illustration_source":ill_src})

# ═══════════════════════════════════════
# API — Shared
# ═══════════════════════════════════════
@app.get("/api/images/{filename}")
async def get_image(filename: str):
    for d in (UPLOAD_DIR, RESULT_DIR):
        p = d/filename
        if p.exists(): return FileResponse(p, media_type="image/png")
    raise HTTPException(404, "Image not found")

@app.get("/api/health")
async def health(request: Request):
    """Report which credentials the server currently sees (never the keys themselves)."""
    img, txt = image_credentials(request), text_credentials(request)
    return {
        "status": "ok",
        "has_image_key": bool(img["key"]),
        "has_text_key": bool(txt["key"]),
        "image_model": img["model"],
        "text_model": txt["model"],
    }

if __name__=="__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
