import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json

@st.cache_data(ttl=3600, show_spinner="加载数据中...")
def load_data():
    #加载所有数据
    preprocessed_dir = 'data/preprocessed'
    data = {}
    
    for key in ['basic_stats', 'region_stats', 'genre_stats', 'year_stats', 
                'director_stats', 'cast_stats', 'wordcloud_stats', 'genre_top_movies']:
        with open(f'{preprocessed_dir}/{key}.json', 'r', encoding='utf-8') as f:
            data[key] = json.load(f)
    
    data['raw_df'] = pd.read_csv('data/raw_data.csv', encoding='utf-8')
    return data

def create_bar_chart(x_data, y_data, title, x_label, y_label, orientation='h', x_range=None):
    #创建横向柱状图
    fig = px.bar(x=x_data, y=y_data, title=title, labels={'x': x_label, 'y': y_label},
                 orientation=orientation, height=450)
    fig.update_layout(title_x=0.5, template='plotly_white')
    if x_range:
        fig.update_xaxes(range=x_range)
    st.plotly_chart(fig, use_container_width=True)

def create_line_chart(x_data, y_data, title, x_label, y_label, color='orange'):
    #创建折线图
    fig = px.line(x=x_data, y=y_data, title=title, labels={'x': x_label, 'y': y_label},
                  markers=True, color_discrete_sequence=[color], height=400)
    fig.update_layout(title_x=0.5, template='plotly_white', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def create_pie_chart(values, names, title):
    #创建饼图
    fig = px.pie(values=values, names=names, title=title, hole=0.3, height=450)
    fig.update_layout(title_x=0.5, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

def create_wordcloud(word_freq, title, colormap='viridis', max_words=100):
    #创建词云
    wc = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', width=1200, height=600,
                   background_color='white', max_words=max_words, colormap=colormap,
                   min_font_size=12, max_font_size=80, prefer_horizontal=0.9, margin=5)
    wc.generate_from_frequencies(word_freq)
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wc, interpolation='lanczos')
    ax.axis('off')
    ax.set_title(title, fontsize=18, pad=20)
    st.pyplot(fig)

def tab_overview(data):
    #数据概览
    st.subheader("数据概览")
    
    rating_dist = data['basic_stats']['rating_distribution']
    fig = px.bar(x=list(rating_dist.keys()), y=list(rating_dist.values()),
                  title='电影评分分布', labels={'x': '评分', 'y': '电影数量'},
                  color_discrete_sequence=['skyblue'], height=400)
    fig.update_layout(title_x=0.5, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### 数据总览")
    st.dataframe(data['raw_df'], use_container_width=True)

def tab_region(data):
    #国家/地区分析
    st.subheader("国家/地区分析")
    
    top_n = st.slider("选择显示数量", 5, 15, 10)
    region_counts = data['region_stats']['single_region_counts']
    items = list(region_counts.items())[:top_n]
    
    create_bar_chart([v for k, v in items], [k for k, v in items],
                     '各地区电影数量排名', '电影数量', '地区')
    
    min_count = st.slider("最少电影数量", 3, 10, 5)
    region_ratings = sorted([r for r in data['region_stats']['region_ratings'] if r['count'] >= min_count],
                           key=lambda x: x['mean'], reverse=True)
    
    create_bar_chart([r['mean'] for r in region_ratings], [r['地区'] for r in region_ratings],
                     f'各地区平均评分（至少{min_count}部电影）', '平均评分', '地区', x_range=[8.0, 10.0])

def tab_genre(data):
    #类型分析
    st.subheader("类型分析")
    
    genre_counts = data['genre_stats']['genre_counts']
    items = list(genre_counts.items())[:10]
    
    create_pie_chart([v for k, v in items], [k for k, v in items], '电影类型分布')
    
    genre_ratings = sorted([r for r in data['genre_stats']['genre_ratings'] if r['count'] >= 5],
                          key=lambda x: x['mean'], reverse=True)
    
    create_bar_chart([r['mean'] for r in genre_ratings], [r['类型'] for r in genre_ratings],
                     '各类型电影平均评分（至少5部电影）', '平均评分', '类型', x_range=[8.0, 10.0])

def tab_year(data):
    #年份分析
    st.subheader("年份分析")
    
    year_counts = data['year_stats']['year_counts']
    create_line_chart(list(year_counts.keys()), list(year_counts.values()),
                     '各年份电影数量趋势', '年份', '电影数量')
    
    decade_counts = data['year_stats']['decade_counts']
    fig = px.bar(x=list(decade_counts.keys()), y=list(decade_counts.values()),
                 title='各年代电影数量分布', labels={'x': '年代', 'y': '电影数量'}, height=400)
    fig.update_layout(title_x=0.5, template='plotly_white', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def tab_director(data):
    #导演分析
    st.subheader("导演分析")
    
    top_n = st.slider("选择显示数量", 5, 20, 10)
    director_counts = data['director_stats']['director_counts'][:top_n]
    
    create_bar_chart([c for n, c in director_counts], [n for n, c in director_counts],
                     f'上榜次数最多的导演（前{top_n}名）', '上榜电影数量', '导演')
    
    # 计算导演平均评分
    director_avg = sorted(data['director_stats']['director_ratings'], key=lambda x: x['mean'], reverse=True)[:10]
    
    create_bar_chart([d['mean'] for d in director_avg], [d['导演'] for d in director_avg],
                     '导演平均评分排名（至少2部电影）', '平均评分', '导演', x_range=[8.0, 10.0])
    
    st.write("### 导演详细信息")
    director_df = pd.DataFrame([{'导演': d['导演'], '平均评分': round(d['mean'], 2), '电影数量': int(d['count'])} 
                               for d in director_avg])
    st.dataframe(director_df, use_container_width=True, height=300)

def tab_recommend(data):
    #电影推荐
    st.subheader("电影推荐")
    
    recommend_type = st.selectbox("选择推荐方式", ["按类型推荐", "按国家/地区推荐", "高分电影推荐"])
    df = data['raw_df']
    
    if recommend_type == "按类型推荐":
        genres = sorted(data['genre_stats']['genre_counts'].keys())
        selected = st.selectbox("选择电影类型", genres)
        movies = data['genre_top_movies'].get(selected, [])
        
        if movies:
            movie_df = pd.DataFrame(movies)[['排名', '中文片名', '评分', '年份']]
            st.write(f"#### {selected}类型高分电影（共{len(movies)}部）")
            st.dataframe(movie_df, use_container_width=True, height=400)
    
    elif recommend_type == "按国家/地区推荐":
        regions = sorted(data['region_stats']['single_region_counts'].keys())
        selected = st.selectbox("选择国家/地区", regions)
        movies = df[df['国家/地区'].str.contains(selected, na=False)].sort_values('评分', ascending=False)
        
        if not movies.empty:
            st.write(f"#### {selected}高分电影（共{len(movies)}部）")
            st.dataframe(movies[['排名', '中文片名', '评分', '年份', '类型', '导演']], 
                        use_container_width=True, height=400)
    
    else:
        min_rating = st.slider("最低评分", 8.0, 10.0, 9.0, 0.1)
        movies = df[df['评分'] >= min_rating].sort_values('评分', ascending=False)
        
        if not movies.empty:
            st.write(f"#### 评分≥{min_rating}的电影（共{len(movies)}部）")
            st.dataframe(movies[['排名', '中文片名', '评分', '年份', '类型', '国家/地区']], 
                        use_container_width=True, height=400)

def tab_wordcloud(data):
    #词云分析
    st.subheader("词云分析")
    
    wc_type = st.selectbox("选择词云类型", ["经典短评词云", "电影类型词云", "导演词云", "主演词云"])
    
    word_freq_map = {
        "经典短评词云": dict(data['wordcloud_stats']['comment_words']),
        "电影类型词云": dict(data['wordcloud_stats']['genre_words']),
        "导演词云": dict(data['director_stats']['director_counts']),
        "主演词云": dict(data['cast_stats']['cast_counts'])
    }
    
    colormap_map = {"经典短评词云": 'viridis', "电影类型词云": 'coolwarm', 
                   "导演词云": 'plasma', "主演词云": 'magma'}
    max_words_map = {"经典短评词云": 150, "电影类型词云": 80, "导演词云": 100, "主演词云": 120}
    
    word_freq = word_freq_map[wc_type]
    create_wordcloud(word_freq, f'{wc_type}分析', colormap_map[wc_type], max_words_map[wc_type])
    
    # 显示统计信息
    if wc_type == "经典短评词云":
        st.write("#### 高频词统计")
        for i, (word, count) in enumerate(data['wordcloud_stats']['comment_words'][:20]):
            col = st.columns(2)[i % 2]
            with col:
                st.write(f"- **{word}**: {count}次")
    elif wc_type == "导演词云":
        st.write("#### 上榜次数最多的导演")
        for director, count in data['director_stats']['director_counts'][:10]:
            st.write(f"- **{director}**: {count}部")
    elif wc_type == "主演词云":
        st.write("#### 上榜次数最多的主演")
        for cast, count in data['cast_stats']['cast_counts'][:10]:
            st.write(f"- **{cast}**: {count}部")

def main():
    st.set_page_config(page_title="豆瓣 Top250 电影数据分析", page_icon="🎬", layout="wide")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    data = load_data()
    
    st.title("🎬 豆瓣 Top250 电影数据分析")
    st.markdown("---")
    
    # 侧边栏统计
    st.sidebar.header("数据概览")
    st.sidebar.write(f"📊 总电影数: {data['basic_stats']['total_movies']} 部")
    st.sidebar.write(f"⭐ 平均评分: {data['basic_stats']['avg_rating']}")
    st.sidebar.write(f"📅 年份范围: {data['basic_stats']['min_year']}-{data['basic_stats']['max_year']}年")
    
    # 标签页
    tabs = st.tabs(["📈 数据概览", "🌍 国家/地区分析", "🎭 类型分析", "📅 年份分析", 
                    "🎬 导演分析", "🎯 电影推荐", "☁️ 词云分析"])
    
    for tab, func in zip(tabs, [tab_overview, tab_region, tab_genre, tab_year, 
                                tab_director, tab_recommend, tab_wordcloud]):
        with tab:
            func(data)
    
    st.markdown("---")
    st.write("数据来源：豆瓣电影 Top250")

if __name__ == "__main__":
    main()






基于 Streamlit + Plotly 的 Web 应用，已实现：

爬虫（
spider.py
）：爬取豆瓣 Top250，解析排名/片名/评分/年份/国家/导演/主演/短评，保存为 CSV
预处理（
preprocess.py
）：生成基础统计、地区/类型/年份/导演/主演分析、词云数据、推荐数据，共8个JSON文件
可视化（
app.py
）：7个标签页 — 数据概览、国家/地区分析、类型分析、年份分析、导演分析、电影推荐、词云分析，支持柱状图/折线图/饼图/词云
