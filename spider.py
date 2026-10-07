import os
import re
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DoubanSpider:
    def __init__(self):
        self.base_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://movie.douban.com/",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        try:
            self.session.get("https://movie.douban.com", timeout=5)
        except:
            pass
        self.movies = []

    def get_page(self, start):
        #获取指定起始位置的页面
        url = f"{self.base_url}?start={start}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            logging.error(f"请求失败: {url}, 错误: {e}")
            return None

    def parse_page(self, html):
        #解析页面，提取电影信息
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")

        for item in items:
            try:
                # 1. 排名
                rank_tag = item.find("em")
                rank = int(rank_tag.get_text()) if rank_tag else 0
                # 2. 中文片名
                title_tag = item.find("span", class_="title")
                title = title_tag.get_text().strip() if title_tag else ""
                # 3. 评分
                rating_tag = item.find("span", class_="rating_num")
                rating = float(rating_tag.get_text().strip()) if rating_tag else 0.0
                # 4. 导演、主演、年份、国家、类型
                director = ""
                cast = ""
                year = ""
                country = ""
                genre = ""
                p_tag = item.find("div", class_="bd").find("p")
                if p_tag:
                    # 获取所有子元素的文本，按 <br/> 分割
                    contents = []
                    current_line = ""
                    for child in p_tag.contents:
                        if child.name == "br":
                            if current_line.strip():
                                contents.append(current_line.strip())
                            current_line = ""
                        else:
                            current_line += str(child)
                    if current_line.strip():
                        contents.append(current_line.strip())
                    
                    if len(contents) >= 1:
                        # 第一行：导演 / 主演
                        director_cast_line = contents[0].replace("\xa0", " ").replace("<span>", "").replace("</span>", "")
                        director_cast_line = re.sub(r"<[^>]+>", "", director_cast_line).strip()
                        if "主演:" in director_cast_line:
                            parts_line = director_cast_line.split("主演:")
                            director_part = parts_line[0].replace("导演:", "").strip()
                            cast = parts_line[1].strip() if len(parts_line) > 1 else ""
                        else:
                            director_part = director_cast_line.replace("导演:", "").strip()
                            cast = ""
                        director = director_part
                        # 豆瓣列表页的"主演"被固定长度截断，末尾会带 "/..." 占位符，
                        # 这里去掉该占位符，避免污染后续主演统计（详情页可拿完整主演，
                        # 但豆瓣详情页有反爬校验，列表页抓取时无法补全）
                        cast = re.sub(r"\s*/\s*\.{3,}\s*$", "", cast).strip()
                        cast = re.sub(r"\s*\.{3,}\s*$", "", cast).strip()
                    if len(contents) >= 2:
                        # 第二行：年份 / 国家 / 类型
                        meta_line = contents[1].replace("\xa0", " ")
                        meta_line = re.sub(r"<[^>]+>", "", meta_line).strip()
                        parts = [part.strip() for part in meta_line.split("/")]
                        
                        # 从后往前处理：最后一个是类型，倒数第二个是国家，前面的都是年份
                        if len(parts) >= 1:
                            genre = parts[-1] if len(parts) >= 1 else ""
                            country = parts[-2] if len(parts) >= 2 else ""
                            
                            # 提取年份
                            year_parts = parts[:-2] if len(parts) >= 3 else parts[:-1] if len(parts) >= 2 else parts
                            year = ""
                            for part in year_parts:
                                year_match = re.search(r"\b(\d{4})\b", part)
                                if year_match:
                                    year = year_match.group(1)
                                    break
                        else:
                            year = ""
                            country = ""
                            genre = ""

                # 6. 经典短评
                quote_tag = item.find("p", class_="quote")
                quote = quote_tag.get_text().strip() if quote_tag else ""

                self.movies.append({
                    "排名": rank,
                    "中文片名": title,
                    "评分": rating,
                    "年份": year,
                    "国家/地区": country,
                    "类型": genre,
                    "导演": director,
                    "主演": cast,
                    "经典短评": quote
                })
            except Exception as e:
                logging.error(f"解析单个电影失败: {e}")

    def crawl(self):
        
        logging.info("开始爬取豆瓣 Top250...")
        for start in range(0, 250, 25):
            page_num = start // 25 + 1
            logging.info(f"正在爬取第 {page_num} 页")
            html = self.get_page(start)
            if html:
                self.parse_page(html)
            else:
                logging.warning(f"第 {page_num} 页获取失败，跳过")
            time.sleep(5)
        logging.info(f"爬取完成，共获取 {len(self.movies)} 条数据")

    def save_csv(self):
        #保存数据到 CSV 文件
        if not self.movies:
            logging.warning("没有数据可保存")
            return
        df = pd.DataFrame(self.movies)
        # 指定列顺序
        columns = ["排名", "中文片名", "评分", "年份", "国家/地区", "类型", "导演", "主演", "经典短评"]
        df = df[columns]
        # 确保输出目录存在
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", "raw_data.csv")
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logging.info(f"数据已保存至 {filepath}，共 {len(df)} 条记录")
        print("\n前5条数据预览：")
        print(df.head())

if __name__ == "__main__":
    spider = DoubanSpider()
    spider.crawl()
    spider.save_csv()