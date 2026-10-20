export const ROUTE_COLORS = {
  hotan:  { line:'#4ade80', marker:'#22c55e', fill:'rgba(74,222,128,.12)', name:'和田玉路线', en:'Hotan Jade Route' },
  maya:   { line:'#fbbf24', marker:'#f59e0b', fill:'rgba(251,191,36,.12)', name:'玛雅翡翠路线', en:'Maya Jadeite Route' },
  maori:  { line:'#60a5fa', marker:'#3b82f6', fill:'rgba(96,165,250,.12)', name:'毛利碧玉路线', en:'Maori Pounamu Route' },
};

export const ROUTES = {
  hotan: { id:'hotan', color:ROUTE_COLORS.hotan,
    path:[[37.1147,79.9225],[39.4736,75.9896],[40.1421,94.6620],[38.9317,100.4553],[34.2630,108.9420]] },
  maya: { id:'maya', color:ROUTE_COLORS.maya,
    path:[[15.0,-89.5],[14.8333,-89.15],[17.4833,-92.05],[20.6833,-88.5667]] },
  maori: { id:'maori', color:ROUTE_COLORS.maori,
    path:[[-42.6667,171.0333],[-43.3833,172.65],[-38.1333,176.25],[-35.7333,174.3167]] },
};

export const MARKERS = {
  hotan: { id:'hotan',routeId:'hotan',name:'和田 (于阗)',nameEn:'Hotan (Khotan)',latlng:[37.1147,79.9225],
    period:'公元前2000年至今',desc:'昆仑山脉北麓，世界最著名软玉产地。和田玉自新石器时代被开采，经于阗国输入中原。',
    artifact:'战国 和田玉龙形佩',material:'和田青白玉',
    audio:'https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3c/Erhu_sample.ogg/Erhu_sample.ogg.mp3' },
  kashgar: { id:'kashgar',routeId:'hotan',name:'喀什 (疏勒)',nameEn:'Kashgar',latlng:[39.4736,75.9896],
    period:'公元前2世纪至今',desc:'丝绸之路南北道交汇枢纽。和田玉经此西传中亚、波斯，东运中原。',
    artifact:'唐 胡人献玉俑',material:'白玉',audio:'' },
  dunhuang: { id:'dunhuang',routeId:'hotan',name:'敦煌 (沙州)',nameEn:'Dunhuang',latlng:[40.1421,94.6620],
    period:'公元前1世纪至今',desc:'丝绸之路"咽喉"，莫高窟所在地。大量壁画记录了西域玉石贸易盛况。',
    artifact:'唐 莫高窟玉观音像',material:'青玉',audio:'' },
  changan: { id:'changan',routeId:'hotan',name:'长安 (西安)',nameEn:"Chang'an (Xi'an)",latlng:[34.263,108.942],
    period:'公元前1000年至今',desc:'丝绸之路东方终点，十三朝古都。历代皇室玉器作坊汇聚于此。',
    artifact:'汉 皇后之玺',material:'和田白玉',audio:'' },
  motagua: { id:'motagua',routeId:'maya',name:'莫塔瓜河谷',nameEn:'Motagua Valley',latlng:[15.0,-89.5],
    period:'公元前1500年至今',desc:'中美洲唯一翡翠产地。翠绿色硬玉是奥尔梅克、玛雅文明最珍贵材料。',
    artifact:'奥尔梅克 翡翠面具',material:'翡翠 Jadeite',audio:'' },
  palenque: { id:'palenque',routeId:'maya',name:'帕伦克',nameEn:'Palenque',latlng:[17.4833,-92.05],
    period:'公元300-800年',desc:'玛雅西部重要城邦，王室墓葬出土了最为精美的翡翠随葬品。',
    artifact:'巴加尔二世翡翠面具',material:'翡翠 Jadeite',audio:'' },
  chichen: { id:'chichen',routeId:'maya',name:'奇琴伊察',nameEn:'Chichén Itzá',latlng:[20.6833,-88.5667],
    period:'公元600-1200年',desc:'玛雅后古典期最大中心城市，翡翠投入圣井祭祀，路线北方终点。',
    artifact:'圣井出土 翡翠盘',material:'翡翠 Jadeite',audio:'' },
  arahura: { id:'arahura',routeId:'maori',name:'阿拉胡拉河',nameEn:'Arahura River',latlng:[-42.6667,171.0333],
    period:'公元1300年至今',desc:'南岛西海岸最主要的碧玉产地，出产inanga、kahurangi和kawakawa品种。',
    artifact:'Hei-tiki 人形玉坠',material:'Pounamu 软玉',audio:'' },
  rotorua: { id:'rotorua',routeId:'maori',name:'罗托鲁瓦',nameEn:'Rotorua',latlng:[-38.1333,176.25],
    period:'公元1500年至今',desc:'北岛Te Arawa部落中心，来自南岛的碧玉在此被加工成hei-tiki和mere。',
    artifact:'Pounamu耳坠',material:'Pounamu 软玉',audio:'' },
  whangarei: { id:'whangarei',routeId:'maori',name:'旺阿雷',nameEn:'Whangarei',latlng:[-35.7333,174.3167],
    period:'公元1500年至今',desc:'碧玉贸易网络最北端，证明毛利人发达的远距离贸易体系。',
    artifact:'Pounamu仪式短棍',material:'Pounamu 软玉',audio:'' },
};

export const MARKER_ORDER = { hotan:['hotan','kashgar','dunhuang','changan'], maya:['motagua','palenque','chichen'], maori:['arahura','rotorua','whangarei'] };

export const TIMELINE_EVENTS = [
  { year:-2000,label:'约公元前2000年',title:'良渚文化 — 玉器文明开端',routeId:'hotan',latlng:[30.416,119.977],summary:'长江下游良渚文化出土大量玉琮、玉璧，标志东亚最早的玉器礼制体系。部分玉料来自和田，证明新石器时代已存在超长距离玉石贸易。',icon:'🏺'},
  { year:-1500,label:'约公元前1500年',title:'奥尔梅克文明 — 翡翠文化起源',routeId:'maya',latlng:[17.8,-94.5],summary:'墨西哥湾沿岸奥尔梅克人开始从危地马拉莫塔瓜河谷获取翡翠，制作仪式面具。翡翠被视为生命、丰收和权力的象征。',icon:'🎭'},
  { year:-1300,label:'约公元前1300年',title:'殷墟妇好墓 — 商代和田玉巅峰',routeId:'hotan',latlng:[36.125,114.3167],summary:'安阳殷墟妇好墓出土755件玉器，经矿物鉴定大部分为和田玉。证明商代已建立从昆仑山到中原的稳定玉料供应线。',icon:'👑'},
  { year:-600,label:'约公元前600年',title:'玉门关 — "玉之路"正式命名',routeId:'hotan',latlng:[40.35,93.85],summary:'敦煌西北的玉门关因西域输入玉石而得名。"玉石之路"成为丝绸之路的前身和重要组成部分。',icon:'🏯'},
  { year:-138,label:'公元前138年',title:'张骞出使西域 — 丝绸之路开通',routeId:'hotan',latlng:[34.263,108.942],summary:'汉武帝遣张骞出使西域，带回大量和田玉料。汉朝设西域都护府，将和田纳入版图，玉石贸易进入官方管控时代。',icon:'🐫'},
  { year:250,label:'约公元250年',title:'玛雅古典期 — 翡翠贸易黄金时代',routeId:'maya',latlng:[17.4833,-92.05],summary:'玛雅文明进入古典期高峰，翡翠成为王室专属奢侈品。从莫塔瓜河谷到尤卡坦半岛的贸易路线达到最活跃状态。',icon:'🏛️'},
  { year:630,label:'约公元630年',title:'唐代 — 丝绸之路全盛',routeId:'hotan',latlng:[34.263,108.942],summary:'唐太宗被尊为"天可汗"，西域诸国纷纷进贡和田美玉。长安成为世界最大玉石加工贸易中心，玉器样式吸收波斯、粟特风格。',icon:'🌏'},
  { year:900,label:'约公元900年',title:'玛雅文明衰落 — 翡翠路线南移',routeId:'maya',latlng:[20.6833,-88.5667],summary:'古典玛雅城邦相继衰落，但翡翠贸易并未完全中断。阿兹特克文明在墨西哥谷地兴起，继续从危地马拉获取翡翠。',icon:'📉'},
  { year:1300,label:'约公元1300年',title:'毛利人抵达新西兰 — 发现Pounamu',routeId:'maori',latlng:[-42.6667,171.0333],summary:'波利尼西亚航海者抵达南岛西海岸，发现阿拉胡拉河流域的碧玉。Ngāi Tahu部落传说中Poutini神将绿玉带到西海岸。',icon:'⛵'},
  { year:1420,label:'约公元1420年',title:'明代 — 玉器走向民间',routeId:'hotan',latlng:[32.05,118.7667],summary:'明朝解除玉器皇室垄断，苏州、扬州成为民间玉雕中心。"陆子冈"款玉牌名扬天下。郑和下西洋将中国玉器传播至东南亚。',icon:'💎'},
  { year:1521,label:'公元1521年',title:'西班牙征服 — 玛雅翡翠贸易终结',routeId:'maya',latlng:[20.6833,-88.5667],summary:'西班牙征服者占领阿兹特克帝国和中美洲。翡翠矿区逐渐荒废，传统贸易路线断裂。欧洲殖民者更关注黄金和白银。',icon:'⚔️'},
  { year:1600,label:'约公元1600年',title:'毛利碧玉贸易网络成熟',routeId:'maori',latlng:[-38.1333,176.25],summary:'南岛西海岸到北岛各地的碧玉贸易网络完全建立。Pounamu被制成hei-tiki、mere和耳坠，成为毛利部落权力和身份的终极象征。',icon:'🪨'},
  { year:1760,label:'约公元1760年',title:'清代 — 痕都斯坦玉器传入',routeId:'hotan',latlng:[39.9167,116.3833],summary:'乾隆帝平定准噶尔后，和田正式纳入版图。痕都斯坦（莫卧儿印度）风格的薄胎玉器传入，与中原玉雕技艺融合，形成清代玉器巅峰——"乾隆工"。',icon:'👑'},
  { year:1800,label:'约公元1800年',title:'欧洲接触 — 毛利碧玉文化转折',routeId:'maori',latlng:[-35.7333,174.3167],summary:'欧洲殖民者和捕鲸者大量抵达新西兰。金属工具改变了碧玉加工方式，部分毛利碧玉制品被作为外交礼物送给欧洲王室。',icon:'🤝'},
];

export const DEFAULT_CENTER = [25, 30];
export const DEFAULT_ZOOM = 2.2;
