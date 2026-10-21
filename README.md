<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:065F46,100:C9A227&height=200&section=header&text=Jade%20Realm&fontSize=66&fontColor=ffffff&fontAlignY=34&desc=%E7%8E%89%E5%A2%83%20%C2%B7%20An%20Interactive%20Chinese%20Jade%20Experience&descSize=15&descAlignY=58" width="100%" alt="Jade Realm"/>

<h1>玉境 · Jade Realm</h1>

<p>
<b>选器物、配玉材、挑朝代，让 AI 把一堆选择题琢成一件玉器</b><br/>
再把和田、玛雅、毛利三条玉料路线铺在地图上，最后把一句成语写成一张可以分享的典故卡片
</p>

<p>
  <img src="https://img.shields.io/badge/状态-可用-22C55E?style=for-the-badge" alt="status"/>
  <img src="https://img.shields.io/badge/API_Key-自带_BYOK-F59E0B?style=for-the-badge" alt="BYOK"/>
  <img src="https://img.shields.io/badge/许可-MIT-0EA5E9?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/形态-前后端分离-065F46?style=for-the-badge" alt="arch"/>
</p>

<p>
  <a href="#-功能">功能</a> ·
  <a href="#-技术栈">技术栈</a> ·
  <a href="#-目录结构">目录结构</a> ·
  <a href="#-快速开始">快速开始</a> ·
  <a href="#-配置-key">配置 Key</a> ·
  <a href="#-常见问题">常见问题</a>
</p>

</div>

> ⚠️ **关于 API Key**：本仓库**不附带、也不会附带**任何模型 Key。
> 生图与文本生成需要你自行申请 [SiliconFlow](https://cloud.siliconflow.cn/account/ak)（图像）与任意 OpenAI 兼容服务（文本）的 Key，
> 在页面右上角 **⚙️ 设置** 里填一次即可，Key 只保存在你自己的浏览器里。
>
> 没有 Key 时，典故文字、丝路地图、朝代知识库**照常可用**，只有「AI 生图」会被挡住并给出明确提示。

---

## ✨ 功能

| 模块 | 能力 |
|:--|:--|
| 🏺 **玉器设计** | 器物 · 玉材 · 朝代 · 纹饰 · 工艺 · 画面风格 · 背景色调 七级选择，逐层拼装成生图提示词 |
| 📷 **朝代滤镜** | 汉 · 唐 · 宋 · 明 · 清 五朝玉作风格，正负提示词成套预置（螭纹谷纹、痕都斯坦、陆子冈…） |
| 🗺️ **丝路玉路** | 和田 / 玛雅 / 毛利 三条玉料路线，Leaflet 地图 + 公元前 2000 到 1800 年的 14 个时间节点 |
| 📜 **典故生成** | 6 条内置玉文化典故 + 任意关键词，AI 生成释义、典籍出处与原文，一键出卡片 |
| 🖼️ **配图与分享** | 典故 AI 配图、卡片导出 PNG、二维码分享、文字复制 |
| 🔑 **自带 Key** | 浏览器内填写并本地保存，随请求头下发；无 Key 时自动降级，不报错不白屏 |

---

## 🛠️ 技术栈

<h3 align="center">前端</h3>

<p align="center">
  <img src="https://img.shields.io/badge/React-18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind"/>
  <img src="https://img.shields.io/badge/Leaflet-1.9-199900?style=for-the-badge&logo=leaflet&logoColor=white" alt="Leaflet"/>
</p>

<h3 align="center">后端与模型</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/SiliconFlow-图像生成-F59E0B?style=for-the-badge&logo=openai&logoColor=white" alt="SiliconFlow"/>
  <img src="https://img.shields.io/badge/OpenAI_兼容-文本生成-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
</p>

| 层 | 选型 |
|:--|:--|
| 前端 | React 18 · Vite 5 · Tailwind CSS 3 · Leaflet 1.9 · html-to-image · qrcode |
| 后端 | Python 3.10+ · FastAPI · Uvicorn · Requests · python-dotenv |
| 图像 | SiliconFlow `images/generations`（默认 `Tongyi-MAI/Z-Image-Turbo`） |
| 文本 | 任意 OpenAI 兼容 `chat/completions`（默认 `gpt-4o-mini`） |

---

## 📂 目录结构

```
Jade_realm/
├── unified-app/                  # 主应用（推荐从这里开始）
│   ├── backend/
│   │   ├── main.py               # FastAPI：设计选项 / 生图 / 典故 / 静态图片
│   │   ├── requirements.txt
│   │   └── .env.example          # 服务端 Key 模板（复制为 .env）
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── api.js            # 请求封装 + Key 读写（localStorage）
│   │   │   ├── App.jsx           # 三 Tab 外壳 + 设置入口
│   │   │   └── components/
│   │   │       ├── SettingsModal.jsx        # 模型 Key 设置面板
│   │   │       ├── tab1-dynasty/            # 玉器设计 + 朝代滤镜
│   │   │       ├── tab2-silkroad/           # 丝路玉路地图与时间轴
│   │   │       └── tab3-story/              # 典故生成与分享卡片
│   │   ├── package.json
│   │   └── vite.config.js        # /api 代理到 localhost:8000
│   └── standalone.html           # 早期单文件原型（存档，接口未与后端对齐）
└── submission/                   # 单文件交付版
    ├── backend/
    │   ├── main.py               # FastAPI + 静态托管前端
    │   ├── requirements.txt
    │   └── .env.example
    ├── frontend/玉境.html         # 单文件前端，右上角 ⚙️ 填 Key
    └── start.bat                 # Windows 一键装依赖并启动
```

> `unified-app` 与 `submission` 是同一套功能的两代实现：
> 前者已拆成 React 组件、便于继续开发；后者是单文件 HTML + 自带静态托管的后端，**拷贝即跑**，适合交作业或做 demo。

---

## 🚀 快速开始

### 方式一：React 版（`unified-app`）

**1）启动后端**

```bash
cd unified-app/backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 可选：想给整站配默认 Key 时再填
python -m uvicorn main:app --reload --port 8000
```

**2）启动前端**

```bash
cd unified-app/frontend
npm install
npm run dev                   # 打开 http://localhost:3000
```

Vite 已把 `/api` 代理到 `http://localhost:8000`，前后端分开跑即可。

### 方式二：单文件版（`submission`）

```bash
cd submission/backend
pip install -r requirements.txt
python main.py                # 自动打开 http://localhost:8000
```

Windows 用户也可以直接双击 `submission/start.bat`。

启动后点右上角 **⚙️**，把 Key 填进去，就能开始生成。

---

## 🔑 配置 Key

项目不提供 Key，三种填法任选，**优先级：页面设置 > `.env` > 进程环境变量**。

| 方式 | 生效范围 | 适用场景 |
|:--|:--|:--|
| 页面右上角 **⚙️ 设置** | 当前浏览器 | 最快体验；存 `localStorage`，换浏览器需重填 |
| `backend/.env` | 该后端的所有使用者 | 自己长期跑一份服务 |
| 进程环境变量 | 当前进程 | Docker / 云主机部署 |

`.env` 里可用的键（复制 `.env.example` 后填）：

```dotenv
SILICONFLOW_API_KEY=            # 图片生成，必填才有 AI 玉器/配图
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_IMAGE_MODEL=Tongyi-MAI/Z-Image-Turbo

OPENAI_API_KEY=                 # 文本生成，留空则用内置典故模板
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TEXT_MODEL=gpt-4o-mini
```

前端通过以下请求头把用户自填的 Key 传给后端（后端优先读请求头）：

| 请求头 | 含义 |
|:--|:--|
| `X-Image-Key` | 图片生成 Key |
| `X-Image-Model` | 图片模型名 |
| `X-Image-Base` | 图片接口 Base URL（仅接受公网 `http(s)`，内网 / 回环地址会被忽略） |
| `X-Text-Key` | 文本生成 Key |
| `X-Text-Model` | 文本模型名 |
| `X-Text-Base` | 文本接口 Base URL（同上，防 SSRF） |

### 没有 Key 会怎样

| 功能 | 无 Key 表现 |
|:--|:--|
| AI 生图 / 配图 | 返回 400 并提示去 ⚙️ 填写，不会白屏、不会 500 |
| 典故卡片 | 正常生成（内置模板或预设），只是没有 AI 配图 |
| 丝路地图 / 朝代知识 | 完全可用，纯前端数据 |

---

## 🧩 接口

| 方法 | 路径 | 说明 |
|:--:|:--|:--|
| `GET` | `/api/health` | 探测后端与「当前请求可见的 Key」状态（不返回 Key 本身） |
| `GET` | `/api/dynasties` | 五朝玉作风格与视觉特征 |
| `GET` | `/api/design-options` | 七类设计选项（器物 / 玉材 / 朝代 / 背景 / 纹饰 / 工艺 / 风格） |
| `POST` | `/api/generate-jade-design` | 按选项拼提示词并生图，返回 `result_url` |
| `GET` | `/api/presets` | 内置典故列表 |
| `POST` | `/api/generate-story` | 关键词 → 典故（文本 + 可选配图） |
| `GET` | `/api/images/{filename}` | 读取生成结果图片 |

---

## ❓ 常见问题

**Q：为什么 Key 存在浏览器里，不存后端？**
因为项目不附带 Key，也不做账号体系。存浏览器意味着谁用谁填，后端只做转发，不替你保管别人的 Key。

**Q：能直接部署到公网给别人用吗？**
不建议。`X-*-Base` 允许用户覆盖上游地址（已做内网地址过滤，但仍属信任边界外）。要给公众用，请改成服务端统一持有 Key + 登录鉴权。

**Q：生图报 401 / 403？**
Key 无效、过期，或该 Key 没有对应模型的权限。到 ⚙️ 里换一个再试；模型名写错也会报错，默认用 `Tongyi-MAI/Z-Image-Turbo`。

**Q：`unified-app/standalone.html` 能跑吗？**
不能。它是更早的单文件原型，调用的 `/api/generate-jade` 上传式接口在当前后端里已经不存在，仅作存档保留。

---

## 📄 License

[MIT](LICENSE) © Keith-hq

<div align="center">

<sub>玉不琢，不成器；提示词不调，不出图。</sub>

</div>
