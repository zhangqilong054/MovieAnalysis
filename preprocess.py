import pandas as pd
import json
import os
from collections import Counter
import jieba

df = pd.read_csv('data/raw_data.csv', encoding='utf-8-sig')

# 创建预处理结果目录
os.makedirs('data/preprocessed', exist_ok=True)

print("开始数据预处理...")

# 1. 基础统计
basic_stats = {
    "total_movies": len(df),
    "avg_rating": round(df['评分'].mean(), 2),
    "min_year": int(df['年份'].min()),
    "max_year": int(df['年份'].max()),
    "rating_distribution": df['评分'].value_counts().sort_index().to_dict()
}
with open('data/preprocessed/basic_stats.json', 'w', encoding='utf-8') as f:
    json.dump(basic_stats, f, ensure_ascii=False, indent=2)
print("[OK] 基础统计完成")

# 2. 国家/地区分析
region_list = []
for idx, row in df.iterrows():
    regions = str(row['国家/地区']).split()
    for region in regions:
        region_list.append({'地区': region, '评分': row['评分'], '类型': row['类型']})
region_df = pd.DataFrame(region_list)

region_stats = {
    "country_counts": df['国家/地区'].value_counts().head(15).to_dict(),
    "single_region_counts": region_df['地区'].value_counts().head(15).to_dict(),
    "region_ratings": region_df.groupby('地区')['评分'].agg(['mean', 'count']).reset_index().to_dict('records')
}
with open('data/preprocessed/region_stats.json', 'w', encoding='utf-8') as f:
    json.dump(region_stats, f, ensure_ascii=False, indent=2)
print("[OK] 国家/地区分析完成")

# 3. 类型分析
genre_list = []
for idx, row in df.iterrows():
    genres = str(row['类型']).split()
    for genre in genres:
        genre_list.append({'类型': genre, '评分': row['评分'], '年份': row['年份']})
genre_df = pd.DataFrame(genre_list)

genre_stats = {
    "genre_counts": genre_df['类型'].value_counts().to_dict(),
    "genre_ratings": genre_df.groupby('类型')['评分'].agg(['mean', 'count']).reset_index().to_dict('records')
}
with open('data/preprocessed/genre_stats.json', 'w', encoding='utf-8') as f:
    json.dump(genre_stats, f, ensure_ascii=False, indent=2)
print("[OK] 类型分析完成")

# 4. 年份分析
df['年代'] = df['年份'].apply(lambda x: f"{str(x)[:3]}0年代")
year_stats = {
    "year_counts": df['年份'].value_counts().sort_index().to_dict(),
    "decade_counts": df['年代'].value_counts().sort_index().to_dict()
}
with open('data/preprocessed/year_stats.json', 'w', encoding='utf-8') as f:
    json.dump(year_stats, f, ensure_ascii=False, indent=2)
print("[OK] 年份分析完成")

# 5. 导演分析
director_list = []
director_data = []
for idx, row in df.iterrows():
    directors = str(row['导演']).split('/')
    for d in directors:
        d = d.strip()
        if d:
            director_list.append(d)
            director_data.append({'导演': d, '评分': row['评分']})

director_stats = {
    "director_counts": Counter(director_list).most_common(20),
    "director_ratings": pd.DataFrame(director_data).groupby('导演')['评分'].agg(['mean', 'count']).reset_index().to_dict('records')
}
with open('data/preprocessed/director_stats.json', 'w', encoding='utf-8') as f:
    json.dump(director_stats, f, ensure_ascii=False, indent=2)
print("[OK] 导演分析完成")

# 6. 主演分析
cast_list = []
for c in df['主演']:
    cast_list.extend(str(c).split('/'))
cast_list = [c.strip() for c in cast_list if c.strip()]
cast_stats = {
    "cast_counts": Counter(cast_list).most_common(20)
}
with open('data/preprocessed/cast_stats.json', 'w', encoding='utf-8') as f:
    json.dump(cast_stats, f, ensure_ascii=False, indent=2)
print("[OK] 主演分析完成")

# 7. 词云数据预处理
# 经典短评词频
comments = " ".join(df['经典短评'].dropna().astype(str))

word_list = list(jieba.cut(comments))
stopwords = ['的', '了', '是', '我', '你', '他', '她', '它', '们', '这', '那', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '用', '里', '看', '在', '电影', '影片']
filtered_words = [w for w in word_list if len(w) > 1 and w not in stopwords]
wordcloud_stats = {
    "comment_words": Counter(filtered_words).most_common(100),
    "genre_words": Counter(genre_df['类型'].tolist()).most_common(50)
}
with open('data/preprocessed/wordcloud_stats.json', 'w', encoding='utf-8') as f:
    json.dump(wordcloud_stats, f, ensure_ascii=False, indent=2)
print("[OK] 词云数据预处理完成")

# 8. 电影推荐数据
# 按类型分组的高分电影
genre_top_movies = {}
for idx, row in df.iterrows():
    genres = str(row['类型']).split()
    for genre in genres:
        if genre not in genre_top_movies:
            genre_top_movies[genre] = []
        genre_top_movies[genre].append({
            "排名": int(row['排名']),
            "中文片名": row['中文片名'],
            "评分": float(row['评分']),
            "年份": int(row['年份']) if pd.notna(row['年份']) else 0
        })
# 每个类型按评分排序
for genre in genre_top_movies:
    genre_top_movies[genre] = sorted(genre_top_movies[genre], key=lambda x: x['评分'], reverse=True)

with open('data/preprocessed/genre_top_movies.json', 'w', encoding='utf-8') as f:
    json.dump(genre_top_movies, f, ensure_ascii=False, indent=2)
print("[OK] 电影推荐数据预处理完成")

print("\n预处理完成！所有结果已保存到 data/preprocessed/ 目录")
