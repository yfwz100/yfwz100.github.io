#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'yfwz100'
SITENAME = "Zhi 的博客"
META_DESCRIPTION = '游戏|机器学习|数据挖掘|可视化'
# PROFILE_IMAGE = '/theme/img/0315.jpg'
PROFILE_IMAGE = ''
SITEURL = '/'
EMAIL_ADDRESS = 'yfwz100@163.com'
GITHUB_ADDRESS = 'https://github.com/yfwz100'
SITE_SUBTEXT = '技术改变世界，数据改变生活'
DISQUS_SITENAME = 'zhi'

SHOW_ARTICLE_AUTHOR = True

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = 'zh_CN'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Menu
CATEGORIES_ON_MENU = True
TAGS_ON_MENU = True
ARCHIVES_ON_MENU = True
PAGES_ON_MENU = True
MENU_ITEMS = (
  ('首页', '/'),
)

# Blogroll
LINKS = (
  ('52nlp', 'http://www.52nlp.cn'),
)

# Social widget
SOCIAL = (
  ('@yfwz100', 'http://weibo.com/yfwz100'),
  ('简书', 'http://www.jianshu.com/users/6edeb5b9e00b/latest_articles'),
  ('豆瓣', 'http://www.douban.com/people/yfwz100')
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = './theme/'
