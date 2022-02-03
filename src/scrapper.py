# ========================================================================
# Copyright 2021 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================

__author__ = 'Jinho D. Choi'

import glob
import json
import os
import re
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

URL_REVIEWS = 'https://www.techradar.com/{}/archive/{}/{:02d}'  # .format(reviews|news, YYYY, MM)
RE_CAL = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)[ ]+(\d{1,2})')


def cleanspace(text: str) -> str:
    return ' '.join(text.split())


def get_html(url: str):
    html = requests.get(url).content
    return BeautifulSoup(html.decode('utf-8'), 'html.parser')


def get_article(source: str) -> Optional[Dict]:
    def get_items(pcdiv):
        if not pcdiv: return []
        l = []

        for li in pcdiv.find_all('li'):
            text = li.find(text=True, recursive=False)
            if text: l.append(cleanspace(text))
        return l

    top = get_html(source)
    article = top.find('article')
    header = article.find('div', {'class': 'header-container'})  # review
    if header is None: header = article.find('header')  # news

    # header
    if header is None:
        print('- Container not found')
        return None

    # header: category
    lis = header.find('ol').find_all('li')
    category = os.path.basename(lis[-1].find('a').get('href').strip())

    # header: title
    title = cleanspace(header.find('h1').get_text())

    # header: author
    span = header.find('span', {'class': 'by-author'})
    author = os.path.basename(span.find('a').get('href').strip()) if span else None

    # time
    time = header.find('time')
    updated = cleanspace(time.get('datetime').strip()) if time else ''

    # header: summary
    h2 = header.find('h2')
    if h2 is None: h2 = header.find('p', {'class': 'strapline'})
    summary = cleanspace(h2.get_text()) if h2 else ''

    # verdict (review only)
    div = article.find('div', {'class': 'pretty-verdict'})
    if div:
        p = div.find('p', {'class': 'pretty-verdict__verdict'})
        verdict = cleanspace(p.get_text()) if p else ''
        pros = get_items(div.find('div', {'class': 'pretty-verdict__pros'}))
        cons = get_items(div.find('div', {'class': 'pretty-verdict__cons'}))
    else:
        verdict, pros, cons = None, None, None

    # body
    div = article.find('div', {'id': 'article-body'})
    article = []
    headers = {}
    links = {}

    for com in div.find_all(['p', 'h2'], recursive=False):
        text = cleanspace(com.get_text())
        if not text: continue

        if com.name == 'h2':
            headers[len(article)] = text
        else:
            article.append(text)
            for a in com.find_all('a'):
                links[cleanspace(a.get_text())] = a.get('href').strip()

    d = {
        'source': source,
        'title': title,
        'category': category,
        'updated': updated,
        'author': author,
        'summary': summary,
        'verdict': verdict,
        'pros': pros,
        'cons': cons,
        'article': article,
        'headers': headers,
        'links': links
    }

    if verdict is None:
        del d['verdict']
        del d['pros']
        del d['cons']

    return d


def get_archive(rootdir: str, year: int, month: int):
    outdir = os.path.join(rootdir, '{}'.format(year))
    if not os.path.exists(outdir): os.makedirs(outdir)
    top = get_html(URL_REVIEWS.format(rootdir, year, month))
    div = top.find('div', {'class': 'archive-list'})
    date = None

    for li in div.find_all('li'):
        cls = li.get('class')
        if cls is None: continue

        if 'date-heading' in cls:
            m = RE_CAL.match(li.get_text().strip())
            if not m: print(li)
            date = int(m.group(2))
        elif 'day-article' in cls:
            source = li.find('a').get('href').strip()
            filename = '{}-{:02d}-{:02d}-{}.json'.format(year, month, date, os.path.basename(source))
            outfile = os.path.join(outdir, filename)
            if os.path.exists(outfile): continue
            print(filename)
            d = get_article(source)
            if d: json.dump(d, open(outfile, 'w'), indent=2)


def compare():
    news = {os.path.basename(filename) for filename in glob.glob('news/2021/*.json')}
    reviews = {os.path.basename(filename) for filename in glob.glob('reviews/2021/*.json')}
    print(len(news), len(reviews))
    print(news - reviews)
    print(reviews - news)


if __name__ == '__main__':
    year = 2021
    for month in range(11, 13):
        get_archive('news', year, month)
