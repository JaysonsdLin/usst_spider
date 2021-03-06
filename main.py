"""
USST NEWS Crawler
"""
import re
import json
import codecs
from time import sleep

import requests
from lxml import html


URL_TMPL = 'http://www.usst.edu.cn/s/1/t/517/p/2/i/{page}/list.htm'
NEWS_LINK_PATTERN = re.compile("<a href=\\'(\/s\/\d+\/t\/\d+\/\d+\/\w+\/info\d+\.htm)\\' target=\\'\\' style=\\'\\'><font color=\\'\\'>(.*)<\/font><\/a>")
NEWS_LINK_PREFIX = 'http://www.usst.edu.cn'
NEWS_CONTENT_XPATH = '//td[@class="mc_content"]'
FLOOR_PAGE_INDEX = 1
CEIL_PAGE_INDEX = 381


def construct_url(tmpl=URL_TMPL, _floor=FLOOR_PAGE_INDEX, _ceil=CEIL_PAGE_INDEX):
    """
    A url generator accord to url template
    """
    for i in xrange(_floor, _ceil):
        yield tmpl.format(page=i)

def construct_url_spec():
    """
    construct url method spec
    """
    index = 1
    for url in construct_url():
        assert URL_TMPL.format(page=index) == url
        index += 1

def crawl_page():
    """
    page crawler
    """
    pages, page_index = [], 1
    session = requests.Session()
    for url in construct_url():
        print 'crawling page: {index}'.format(index=page_index)
        page_content = session.get(url).content
        pages.append({'content': page_content, 'index': page_index})
        print 'crawled page: {index} done'.format(index=page_index)
        page_index += 1
        sleep(2)
    return pages

def extract_news_link(page_info):
    """
    news link extractor accord to page content
    """
    search_res = NEWS_LINK_PATTERN.findall(page_info['content'])
    result = []
    for res in search_res:
        result.append({
            'title': res[1],
            'link': res[0],
            'page_index': page_info['index']
        })
    return result

def crawl_news_content(news_link_infos):
    """
    news page content crawler
    """
    session = requests.Session()
    result = []
    for news_link_info in news_link_infos:
        content = session.get(NEWS_LINK_PREFIX + news_link_info['link']).content
        result.append({
            'raw_content': content,
            'title': news_link_info['title'],
            'link': news_link_info['link'],
            'page_index': news_link_info['page_index']
        })
    return result

def extract_news_content(news_content):
    """
    news content extractor
    """
    page_dom = html.fromstring(news_content['raw_content'])
    mc_content = page_dom.xpath(NEWS_CONTENT_XPATH)[0]
    return {
        'content': mc_content.text_content(),
        'page_index': news_content['page_index'],
        'title': news_content['title'],
        'link': news_content['link']
    }

def main():
    """
    main
    """
    print 'prepare anything for you'
    page_infos = crawl_page()
    news_link_infos = []
    result = []
    for page_info in page_infos:
        news_link_infos.extend(extract_news_link(page_info))
    news_contents = crawl_news_content(news_link_infos)
    for news_content in news_contents:
        news_detail = extract_news_content(news_content)
        result.append(news_detail)
        # or save here
    with codecs.open('result.json', 'wb', 'utf-8') as w_file:
        json.dump(result, w_file)
    print 'you are all set'

if __name__ == '__main__':
    main()
