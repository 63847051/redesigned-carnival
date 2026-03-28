#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎专栏文章爬虫（Selenium 版本）
使用 Selenium 模拟浏览器访问
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import sys


def fetch_zhihu_article_selenium(url):
    """
    使用 Selenium 获取知乎专栏文章

    Args:
        url: 知乎专栏文章 URL

    Returns:
        文章内容（markdown 格式）
    """

    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')

    driver = None

    try:
        # 启动浏览器
        driver = webdriver.Chrome(options=chrome_options)

        # 访问页面
        print("🔍 正在访问知乎...")
        driver.get(url)

        # 等待页面加载
        print("⏳ 等待页面加载...")
        time.sleep(5)

        # 检查是否需要登录
        if '登录' in driver.title or '登录' in driver.page_source:
            print("❌ 知乎需要登录，无法继续")
            return None

        # 尝试提取文章内容
        content = None

        # 方法 1: Post-RichText
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'Post-RichText'))
            )
            content = element.text
            print("✅ 使用方法 1 提取成功（Post-RichText）")
        except TimeoutException:
            pass

        # 方法 2: RichText
        if not content:
            try:
                element = driver.find_element(By.CLASS_NAME, 'RichText')
                content = element.text
                print("✅ 使用方法 2 提取成功（RichText）")
            except:
                pass

        # 方法 3: article
        if not content:
            try:
                element = driver.find_element(By.TAG_NAME, 'article')
                content = element.text
                print("✅ 使用方法 3 提取成功（article）")
            except:
                pass

        if not content:
            print("❌ 无法提取文章内容")
            return None

        # 提取标题
        try:
            title_element = driver.find_element(By.CLASS_NAME, 'Post-Title')
            title = title_element.text
        except:
            title = "未知标题"

        return f"# {title}\n\n{content}"

    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        return None
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python zhihu-fetcher-selenium.py <知乎文章URL>")
        sys.exit(1)

    url = sys.argv[1]
    article = fetch_zhihu_article_selenium(url)

    if article:
        print(article)
    else:
        print("❌ 获取文章失败")
        sys.exit(1)
