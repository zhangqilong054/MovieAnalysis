# 🎬 豆瓣 Top250 电影数据分析

基于 Python 的电影数据爬取与分析系统，从豆瓣电影 Top250 采集数据，进行多维度统计分析与可视化展示。

## ✨ 功能特性

- **数据爬取**：自动爬取豆瓣 Top250 电影数据（排名、片名、评分、年份、国家/地区、类型、导演、主演、经典短评）
- **数据预处理**：对原始数据进行清洗、拆分、聚合，生成结构化统计结果
- **可视化分析**：
  - 📈 数据概览（评分分布、数据总览）
  - 🌍 国家/地区分析（电影数量排名、平均评分对比）
  - 🎭 类型分析（类型分布饼图、各类型评分排名）
  - 📅 年份分析（数量趋势、年代分布）
  - 🎬 导演分析（上榜次数、平均评分排名）
  - 🎯 电影推荐（按类型/地区/评分推荐）
  - ☁️ 词云分析（短评/类型/导演/主演词云）

## 🛠️ 技术栈

| 分类 | 技术 |
|------|------|
| 爬虫 | requests, BeautifulSoup |
| 数据处理 | pandas, jieba |
| 可视化 | Streamlit, Plotly, Matplotlib, WordCloud |

## 📁 项目结构

```
MovieAnalysis/
├── spider.py              # 豆瓣 Top250 爬虫
├── preprocess.py          # 数据预处理脚本
├── app.py                 # Streamlit 可视化应用
├── requirements.txt       # Python 依赖
├── .gitignore
├── README.md
└── data/
    ├── raw_data.csv       # 爬取的原始数据
    └── preprocessed/      # 预处理结果（JSON）
        ├── basic_stats.json
        ├── region_stats.json
        ├── genre_stats.json
        ├── year_stats.json
        ├── director_stats.json
        ├── cast_stats.json
        ├── wordcloud_stats.json
        └── genre_top_movies.json
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 爬取数据

```bash
cd MovieAnalysis
python spider.py
```

爬取结果保存至 `data/raw_data.csv`。

### 3. 数据预处理

```bash
python preprocess.py
```

预处理结果保存至 `data/preprocessed/` 目录。

### 4. 启动可视化应用

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501` 查看分析结果。

## 📊 数据说明

- **数据来源**：豆瓣电影 Top250（https://movie.douban.com/top250）
- **数据规模**：250 部电影
- **字段**：排名、中文片名、评分、年份、国家/地区、类型、导演、主演、经典短评

## ⚠️ 注意事项

- 爬虫运行时每页间隔 5 秒，请勿频繁请求，遵守网站 robots 协议
- 词云功能依赖系统中文字体（默认使用 `C:/Windows/Fonts/simhei.ttf`），Linux 环境需自行配置
- 如已有 `data/raw_data.csv`，可跳过爬虫步骤直接运行预处理