/?O  m                             hypernews/hypernews/urls.py)"""hypernews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from news.views import construct


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', construct)
]
    hypernews/news/views.py ¤from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def construct(request):
    return HttpResponse("Coming soon")
    base.py:# -*- coding: utf-8 -*-
import copy
import http.cookiejar
import json
import os
import re
import urllib
from datetime import datetime

from hstest.django_test import DjangoTest
from hstest.check_result import CheckResult


class HyperNewsTest(DjangoTest):
    COMMON_LINK_PATTERN = '''<a[^>]+href=['"]([a-zA-Z\d/_]+)['"][^>]*>'''
    CSRF_PATTERN = b'<input[^>]+name="csrfmiddlewaretoken" ' \
                   b'value="(?P<csrf>\w+)"[^>]*>'
    GROUPS_FIRST_PATTERN = '<h4>.*?</h4>.*?<ul>.+?</ul>'
    GROUPS_SECOND_PATTERN = (
        '''<a[^>]+href=['"]([a-zA-Z\d/_]+)['"][^>]*>(.+?)</a>'''
    )
    H2_PATTERN = '<h2>(.+?)</h2>'
    H4_PATTERN = '<h4>(.+?)</h4>'
    PARAGRAPH_PATTERN = '<p>(.+?)</p>'
    TEXT_LINK_PATTERN = '''<a[^>]+href=['"][a-zA-Z\d/_]+['"][^>]*>(.+?)</a>'''
    cookie_jar = http.cookiejar.CookieJar()

    def __init__(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.news_file_name = 'news.json'
        os.environ['NEWS_JSON_PATH'] = os.path.join(current_dir,
                                                    self.news_file_name)
        super().__init__(*args, **kwargs)

    def __stripped_list(self, list):
        return [item.strip() for item in list]

    def __setup(self):
        self.news_data = [{
            'created': '2020-02-09 14:15:10',
            'text': 'Text of the news 1',
            'title': 'News 1',
            'link': 1
        }, {
            'created': '2020-02-10 14:15:10',
            'text': 'Text of the news 2',
            'title': 'News 2',
            'link': 2
        }, {
            'created': '2020-02-09 16:15:10',
            'text': 'Text of the news 3',
            'title': 'News 3',
            'link': 3
        }]
        with open(self.news_file_name, 'w') as f:
            json.dump(self.news_data, f)

    def check_coming_soon_page(self) -> CheckResult:
        self.__setup()
        try:
            page = self.read_page(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        coming_soon_text = 'Coming soon'

        # response.url for the backward compatibility
        if (coming_soon_text not in page
                and response.url != f'http://localhost:{self.port}/news/'):
            return CheckResult.false(
                '"Coming soon" page should contain "Coming soon" text'
            )

        return CheckResult.true()

    def check_coming_soon_page_redirect(self) -> CheckResult:
        self.__setup()

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        if response.url != f'http://localhost:{self.port}/news/':
            return CheckResult.false(
                f'"Coming soon" page should redirects '
                f'to the http://localhost:{self.port}/news/'
            )

        return CheckResult.true()

    def check_main_header(self) -> CheckResult:
        self.__setup()
        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        h2_headers = re.findall(self.H2_PATTERN, page, re.S)
        h2_headers = self.__stripped_list(h2_headers)
        main_header = 'Hyper news'

        if main_header not in h2_headers:
            return CheckResult.false(
                'Main page should contain <h2> element with text "Hyper news"'
            )

        return CheckResult.true()

    def check_news_page(self) -> CheckResult:
        self.__setup()
        testing_news = self.news_data[0]
        link = testing_news['link']
        created = testing_news['created']

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/{link}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the news page.'
            )

        page_headers = re.findall(self.H2_PATTERN, page, re.S)
        page_headers = self.__stripped_list(page_headers)
        page_paragraphs = re.findall(self.PARAGRAPH_PATTERN, page, re.S)
        page_paragraphs = self.__stripped_list(page_paragraphs)
        if testing_news['title'] not in page_headers:
            return CheckResult.false(
                'News page should contain <h2> element with the data '
                'of the title field from json file.'
            )

        if testing_news['text'] not in page_paragraphs:
            return CheckResult.false(
                'News page should contain <p> element with the data '
                'of the text field from json file.'
            )

        if created not in page_paragraphs:
            return CheckResult.false(
                'News page should contain <p> element with the data '
                'of the created field from json file '
                'in the format: "%Y-%m-%d %H:%M:%S".'
            )

        return CheckResult.true()

    def check_main_page_create_link(self):
        self.__setup()
        create_link = '/news/create/'

        try:
            page = self.read_page(f'http://localhost:{self.port}/news')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if create_link not in links_from_page:
            return CheckResult.false(
                f'Main page should contain <a> element with href {create_link}'
            )

        return CheckResult.true()

    def check_main_page(self) -> CheckResult:
        self.__setup()
        created_set = set()
        news_data = copy.deepcopy(self.news_data)
        for news in news_data:
            created_dt = datetime.strptime(news['created'],
                                           '%Y-%m-%d %H:%M:%S') \
                                 .date()
            created_set.add(created_dt)

        created_list = [x for x in created_set]
        created_list.sort(reverse=True)
        created_list_str = [x.strftime('%Y-%m-%d') for x in created_list]
        for element in created_list_str:
            print(element)

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        h4_headers = re.findall(self.H4_PATTERN, page, re.S)
        h4_headers = self.__stripped_list(h4_headers)
        filtered_h4 = list(filter(lambda x: x in created_list_str, h4_headers))

        if filtered_h4 != created_list_str:
            return CheckResult.false(
                'Main page should contain <h4> elements grouped by '
                'date created and first should be fresh news.'
            )

        for news in news_data:
            created_date = datetime.strptime(news['created'],
                                             '%Y-%m-%d %H:%M:%S') \
                .date()
            news['created_date'] = created_date
            news['created_date_str'] = created_date.strftime('%Y-%m-%d')
            news['link'] = '/news/{}/'.format(news['link'])

        file_data = sorted(news_data, key=lambda x: x['title'])
        file_data = sorted(
            file_data, key=lambda x: x['created_date'], reverse=True)

        for news in file_data:
            news.pop('created_date')
            news.pop('created')
            news.pop('text')

        groups = re.findall(self.GROUPS_FIRST_PATTERN, page, re.S)
        news_list = [
            sorted(re.findall(self.GROUPS_SECOND_PATTERN, group, re.S),
                   key=lambda news: news[1])
            for group in groups
        ]
        response_data = []
        for news_l, h4 in zip(news_list, filtered_h4):
            for news in news_l:
                response_data.append({
                    'created_date_str': h4,
                    'link': news[0],
                    'title': news[1].strip()
                })

        if response_data != file_data:
            return CheckResult.false(
                'Main page should contain <a> elements with href to news pages.'
            )


        return CheckResult.true()

    def check_creating_news(self):
        self.__setup()
        old_news_titles = [news['title'] for news in self.news_data]

        new_news = {
            'title': 'News 4',
            'text': 'Text of the news 4',
        }

        titles = (*old_news_titles, new_news['title'])

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            create_page_response = opener.open(
                f'http://localhost:{self.port}/news/create/')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the create page.')

        create_page = create_page_response.read()

        csrf_options = re.findall(self.CSRF_PATTERN, create_page)
        if not csrf_options:
            return CheckResult.false(
                'Missing csrf_token in the create page form')

        try:
            create_response = opener.open(
                f'http://localhost:{self.port}/news/create/',
                data=urllib.parse.urlencode({
                        'title': new_news['title'],
                    'text': new_news['text'],
                    'csrfmiddlewaretoken': csrf_options[0],
                }).encode()
            )
        except urllib.error.URLError as err:
            if 'Forbidden' not in err.reason:
                return CheckResult.false(
                    f'Wrong response for forbidden requests: {err.reason}')

        if create_response.url != f'http://localhost:{self.port}/news/':
            return CheckResult.false(
                'After creating news handler should redirects to the /news/ '
                'page')

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        links_from_page = re.findall(self.TEXT_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        for title in titles:
            if title not in links_from_page:
                return CheckResult.false(
                    f'After creating news main page can\'t find {title}')

        return CheckResult.true()

    def check_create_page_main_link(self):
        self.__setup()
        main_link = '/news/'

        try:
            page = self.read_page(
                f'http://localhost:{self.port}/news/create/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the create page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if main_link not in links_from_page:
            return CheckResult.false(
                f'Create page should contain <a> element with href {main_link}'
            )

        return CheckResult.true()

    def check_news_page_main_link(self):
        self.__setup()
        main_link = '/news/'

        testing_news = self.news_data[0]
        link = testing_news['link']

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/{link}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the news page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if main_link not in links_from_page:
            return CheckResult.false(
                f'News page should contain <a> element with href {main_link}'
            )

        return CheckResult.true()

    def check_main_page_search(self):
        self.__setup()
        q = '2'
        news_data = copy.deepcopy(self.news_data)

        for news in news_data:
            created_date = datetime.strptime(news['created'],
                                             '%Y-%m-%d %H:%M:%S') \
                .date()
            news['created_date_str'] = created_date.strftime('%Y-%m-%d')

        all_headers = set((x['created_date_str'] for x in news_data))
        visible_headers = set((x['created_date_str'] for x in news_data
                               if q in x['title']))
        invisible_headers = all_headers - visible_headers
        visible_titles = [x['title'] for x in news_data
                          if q in x['title']]
        invisible_titles = [x['title'] for x in news_data
                            if q not in x['title']]

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/?q={q}')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the search page.'
            )

        h4_headers = re.findall(self.H4_PATTERN, page, re.S)
        h4_headers = self.__stripped_list(h4_headers)

        for header in visible_headers:
            if header not in h4_headers:
                return CheckResult.false(
                    f'Search page should contain headers with found news'
                )

        for header in invisible_headers:
            if header in h4_headers:
                return CheckResult.false(
                    f'Search page should not contain headers with unfound news'
                )

        titles = re.findall(self.TEXT_LINK_PATTERN, page, re.S)
        titles = self.__stripped_list(titles)

        for title in visible_titles:
            if title not in titles:
                return CheckResult.false(
                    f'Search page should contain unfound news'
                )

        for title in invisible_titles:
            if title in titles:
                return CheckResult.false(
                    f'Search page should contain found news'
                )

        return CheckResult.true()
    hypernews/hypernews/settings.pyГ"""
Django settings for hypernews project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEWS_JSON_PATH = 'news.json'  # You can choose any path you want
NEWS_JSON_PATH = os.environ.get('NEWS_JSON_PATH') or NEWS_JSON_PATH  # DO NOT MODIFY THIS LINE

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(-q5783z2mh-cd217skey@(+_np2&j0=sl6suvo)ah2uwz@9ij'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hypernews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hypernews.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
    	news.json [{"created": "2020-02-09 14:15:10", "text": "Text of the news 1", "title": "News 1", "link": 1}, {"created": "2020-02-10 14:15:10", "text": "Text of the news 2", "title": "News 2", "link": 2}, {"created": "2020-02-09 16:15:10", "text": "Text of the news 3", "title": "News 3", "link": 3}]    hypernews/hypernews/urls.pyп"""hypernews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
    hypernews/news/views.py ?from django.shortcuts import render

# Create your views here.
    hypernews/hypernews/settings.pyё"""
Django settings for hypernews project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEWS_JSON_PATH = 'news.json'  # You can choose any path you want
NEWS_JSON_PATH = os.environ.get('NEWS_JSON_PATH') or NEWS_JSON_PATH  # DO NOT MODIFY THIS LINE

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(-q5783z2mh-cd217skey@(+_np2&j0=sl6suvo)ah2uwz@9ij'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hypernews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hypernews.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
    hypernews/db.sqlite3      'hypernews/news/templates/news/news.html <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>
        {% if  title  %}
            {{ title }}
        {% else %}
             news is not ready now
        {% endif %}
    </title>
</head>
<body>
    <h2>{{ title }}</h2>
    <h2>{{ text }}</h2>
    <p>{{ text }}</p>
    <p>{{ created }}</p>
    <p>{{ link }}</p>
    <a target="_blank" href="/news/"> Main Page </a>
</body>
</html>    (hypernews/news/templates/news/index.html\<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>

</head>
<body>
    <h2>{{ blog_name }}</h2>
    <div>{{ post.text }}</div>
    {% for comment in post.comments %}
        <div>Comment #{{ forloop.counter }}: {{ comment }}</div>
    {% endfor %}


    <h2>Redesign Blog Post</h2>
    <div>{{ post.text }}</div>
    <div>There are {{post.text.split | length}} words in post</div>
    <div>Created at: {{post.created_at | date:"Y.m.d"}}</div>
    <div>Likes: {{post.likes | default:0 | add:1}}</div>
    <div>{{post.comments |join:"<br />"}}</div>
</body>
</html>    'hypernews/news/templates/news/soon.html “<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h2>Coming soon</h2>
</body>
</html>    ,hypernews/news/templates/news/main_page.htmlё<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Main page</title>
</head>
<body>
    <h2>Hyper news</h2>
    <ul>
        {% for news in context %}
            <li> news.link </li>
        {% endfor %}
        <h4>2020-02-02</h4>
    </ul>
    <ul>
        <li><a href="/news/9234732/">The birth of the star</a></li>
        <li><a href="/news/2389742/">The raise of Jupyter</a></li>
    </ul>

</body>
</html>    hypernews/news/urls.py ·from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("", MainView.as_view()),
    path('<int:link_id>/', NewsView.as_view()),
]    hypernews/hypernews/urls.pyD"""hypernews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('news.urls')),
    path("news/", include('news.urls'))
]
    hypernews/news/views.py‡from django.views import View
from django.shortcuts import render
import json


class MainView(View):
    def get(self, request):
        with open('C:\\Python\\django\\HyperNews Portal\\HyperNews Portal\\task\\hypernews\\news\\news.json',
                  'r') as json_file:
            list_from_json = json.load(json_file)
            date_list = [ list_from_json['created'] for i in list_from_json]

        return render(request, 'news/main_page.html', context=context)


class NewsView(View):
    def get(self, request, link_id):
        with open('C:\\Python\\django\\HyperNews Portal\\HyperNews Portal\\task\\hypernews\\news\\news.json',
                  'r') as json_file:
            dict_from_json = json.load(json_file)
        for news in dict_from_json:
            if news["link"] == link_id:
                context = {
                    "created": news['created'],
                    "text": news['text'],
                    "title": news['title'],
                    "link": news['link']
                }
            else:
                context = dict_from_json[0]
        return render(request, 'news/news.html', context=context)
    base.py:# -*- coding: utf-8 -*-
import copy
import http.cookiejar
import json
import os
import re
import urllib
from datetime import datetime

from hstest.django_test import DjangoTest
from hstest.check_result import CheckResult


class HyperNewsTest(DjangoTest):
    COMMON_LINK_PATTERN = '''<a[^>]+href=['"]([a-zA-Z\d/_]+)['"][^>]*>'''
    CSRF_PATTERN = b'<input[^>]+name="csrfmiddlewaretoken" ' \
                   b'value="(?P<csrf>\w+)"[^>]*>'
    GROUPS_FIRST_PATTERN = '<h4>.*?</h4>.*?<ul>.+?</ul>'
    GROUPS_SECOND_PATTERN = (
        '''<a[^>]+href=['"]([a-zA-Z\d/_]+)['"][^>]*>(.+?)</a>'''
    )
    H2_PATTERN = '<h2>(.+?)</h2>'
    H4_PATTERN = '<h4>(.+?)</h4>'
    PARAGRAPH_PATTERN = '<p>(.+?)</p>'
    TEXT_LINK_PATTERN = '''<a[^>]+href=['"][a-zA-Z\d/_]+['"][^>]*>(.+?)</a>'''
    cookie_jar = http.cookiejar.CookieJar()

    def __init__(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.news_file_name = 'hypernews/news/news.json'
        os.environ['NEWS_JSON_PATH'] = os.path.join(current_dir,
                                                    self.news_file_name)
        super().__init__(*args, **kwargs)

    def __stripped_list(self, list):
        return [item.strip() for item in list]

    def __setup(self):
        self.news_data = [{
            'created': '2020-02-09 14:15:10',
            'text': 'Text of the news 1',
            'title': 'News 1',
            'link': 1
        }, {
            'created': '2020-02-10 14:15:10',
            'text': 'Text of the news 2',
            'title': 'News 2',
            'link': 2
        }, {
            'created': '2020-02-09 16:15:10',
            'text': 'Text of the news 3',
            'title': 'News 3',
            'link': 3
        }]
        with open(self.news_file_name, 'w') as f:
            json.dump(self.news_data, f)

    def check_coming_soon_page(self) -> CheckResult:
        self.__setup()
        try:
            page = self.read_page(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        coming_soon_text = 'Coming soon'

        # response.url for the backward compatibility
        if (coming_soon_text not in page
                and response.url != f'http://localhost:{self.port}/news/'):
            return CheckResult.false(
                '"Coming soon" page should contain "Coming soon" text'
            )

        return CheckResult.true()

    def check_coming_soon_page_redirect(self) -> CheckResult:
        self.__setup()

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the "Coming soon" page.')

        if response.url != f'http://localhost:{self.port}/news/':
            return CheckResult.false(
                f'"Coming soon" page should redirects '
                f'to the http://localhost:{self.port}/news/'
            )

        return CheckResult.true()

    def check_main_header(self) -> CheckResult:
        self.__setup()
        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        h2_headers = re.findall(self.H2_PATTERN, page, re.S)
        h2_headers = self.__stripped_list(h2_headers)
        main_header = 'Hyper news'

        if main_header not in h2_headers:
            return CheckResult.false(
                'Main page should contain <h2> element with text "Hyper news"'
            )

        return CheckResult.true()

    def check_news_page(self) -> CheckResult:
        self.__setup()
        testing_news = self.news_data[0]
        link = testing_news['link']
        created = testing_news['created']

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/{link}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the news page.'
            )

        page_headers = re.findall(self.H2_PATTERN, page, re.S)
        page_headers = self.__stripped_list(page_headers)
        page_paragraphs = re.findall(self.PARAGRAPH_PATTERN, page, re.S)
        page_paragraphs = self.__stripped_list(page_paragraphs)
        if testing_news['title'] not in page_headers:
            return CheckResult.false(
                'News page should contain <h2> element with the data '
                'of the title field from json file.'
            )

        if testing_news['text'] not in page_paragraphs:
            return CheckResult.false(
                'News page should contain <p> element with the data '
                'of the text field from json file.'
            )

        if created not in page_paragraphs:
            return CheckResult.false(
                'News page should contain <p> element with the data '
                'of the created field from json file '
                'in the format: "%Y-%m-%d %H:%M:%S".'
            )

        return CheckResult.true()

    def check_main_page_create_link(self):
        self.__setup()
        create_link = '/news/create/'

        try:
            page = self.read_page(f'http://localhost:{self.port}/news')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if create_link not in links_from_page:
            return CheckResult.false(
                f'Main page should contain <a> element with href {create_link}'
            )

        return CheckResult.true()

    def check_main_page(self) -> CheckResult:
        self.__setup()
        created_set = set()
        news_data = copy.deepcopy(self.news_data)
        for news in news_data:
            created_dt = datetime.strptime(news['created'],
                                           '%Y-%m-%d %H:%M:%S') \
                                 .date()
            created_set.add(created_dt)

        created_list = [x for x in created_set]
        created_list.sort(reverse=True)
        created_list_str = [x.strftime('%Y-%m-%d') for x in created_list]

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        h4_headers = re.findall(self.H4_PATTERN, page, re.S)
        h4_headers = self.__stripped_list(h4_headers)
        filtered_h4 = list(filter(lambda x: x in created_list_str, h4_headers))

        if filtered_h4 != created_list_str:
            return CheckResult.false(
                'Main page should contain <h4> elements grouped by '
                'date created and first should be fresh news.'
            )

        for news in news_data:
            created_date = datetime.strptime(news['created'],
                                             '%Y-%m-%d %H:%M:%S') \
                .date()
            news['created_date'] = created_date
            news['created_date_str'] = created_date.strftime('%Y-%m-%d')
            news['link'] = '/news/{}/'.format(news['link'])

        file_data = sorted(news_data, key=lambda x: x['title'])
        file_data = sorted(
            file_data, key=lambda x: x['created_date'], reverse=True)

        for news in file_data:
            news.pop('created_date')
            news.pop('created')
            news.pop('text')

        groups = re.findall(self.GROUPS_FIRST_PATTERN, page, re.S)
        news_list = [
            sorted(re.findall(self.GROUPS_SECOND_PATTERN, group, re.S),
                   key=lambda news: news[1])
            for group in groups
        ]
        response_data = []
        for news_l, h4 in zip(news_list, filtered_h4):
            for news in news_l:
                response_data.append({
                    'created_date_str': h4,
                    'link': news[0],
                    'title': news[1].strip()
                })

        if response_data != file_data:
            return CheckResult.false(
                'Main page should contain <a> elements with href to news pages.'
            )


        return CheckResult.true()

    def check_creating_news(self):
        self.__setup()
        old_news_titles = [news['title'] for news in self.news_data]

        new_news = {
            'title': 'News 4',
            'text': 'Text of the news 4',
        }

        titles = (*old_news_titles, new_news['title'])

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            create_page_response = opener.open(
                f'http://localhost:{self.port}/news/create/')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the create page.')

        create_page = create_page_response.read()

        csrf_options = re.findall(self.CSRF_PATTERN, create_page)
        if not csrf_options:
            return CheckResult.false(
                'Missing csrf_token in the create page form')

        try:
            create_response = opener.open(
                f'http://localhost:{self.port}/news/create/',
                data=urllib.parse.urlencode({
                        'title': new_news['title'],
                    'text': new_news['text'],
                    'csrfmiddlewaretoken': csrf_options[0],
                }).encode()
            )
        except urllib.error.URLError as err:
            if 'Forbidden' not in err.reason:
                return CheckResult.false(
                    f'Wrong response for forbidden requests: {err.reason}')

        if create_response.url != f'http://localhost:{self.port}/news/':
            return CheckResult.false(
                'After creating news handler should redirects to the /news/ '
                'page')

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the main page.'
            )

        links_from_page = re.findall(self.TEXT_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        for title in titles:
            if title not in links_from_page:
                return CheckResult.false(
                    f'After creating news main page can\'t find {title}')

        return CheckResult.true()

    def check_create_page_main_link(self):
        self.__setup()
        main_link = '/news/'

        try:
            page = self.read_page(
                f'http://localhost:{self.port}/news/create/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the create page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if main_link not in links_from_page:
            return CheckResult.false(
                f'Create page should contain <a> element with href {main_link}'
            )

        return CheckResult.true()

    def check_news_page_main_link(self):
        self.__setup()
        main_link = '/news/'

        testing_news = self.news_data[0]
        link = testing_news['link']

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/{link}/')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the news page.'
            )

        links_from_page = re.findall(self.COMMON_LINK_PATTERN, page, re.S)
        links_from_page = self.__stripped_list(links_from_page)

        if main_link not in links_from_page:
            return CheckResult.false(
                f'News page should contain <a> element with href {main_link}'
            )

        return CheckResult.true()

    def check_main_page_search(self):
        self.__setup()
        q = '2'
        news_data = copy.deepcopy(self.news_data)

        for news in news_data:
            created_date = datetime.strptime(news['created'],
                                             '%Y-%m-%d %H:%M:%S') \
                .date()
            news['created_date_str'] = created_date.strftime('%Y-%m-%d')

        all_headers = set((x['created_date_str'] for x in news_data))
        visible_headers = set((x['created_date_str'] for x in news_data
                               if q in x['title']))
        invisible_headers = all_headers - visible_headers
        visible_titles = [x['title'] for x in news_data
                          if q in x['title']]
        invisible_titles = [x['title'] for x in news_data
                            if q not in x['title']]

        try:
            page = self.read_page(f'http://localhost:{self.port}/news/?q={q}')
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the search page.'
            )

        h4_headers = re.findall(self.H4_PATTERN, page, re.S)
        h4_headers = self.__stripped_list(h4_headers)

        for header in visible_headers:
            if header not in h4_headers:
                return CheckResult.false(
                    f'Search page should contain headers with found news'
                )

        for header in invisible_headers:
            if header in h4_headers:
                return CheckResult.false(
                    f'Search page should not contain headers with unfound news'
                )

        titles = re.findall(self.TEXT_LINK_PATTERN, page, re.S)
        titles = self.__stripped_list(titles)

        for title in visible_titles:
            if title not in titles:
                return CheckResult.false(
                    f'Search page should contain found news'
                )

        for title in invisible_titles:
            if title in titles:
                return CheckResult.false(
                    f'Search page should not contain unfound news'
                )

        return CheckResult.true()
    hypernews/hypernews/settings.py
T"""
Django settings for hypernews project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#NEWS_JSON_PATH = 'C:\\Python\\django\\HyperNews Portal\\HyperNews Portal\\task\\hypernews\\news\\news.json'  # You can choose any path you want
NEWS_JSON_PATH = 'news.json'  # You can choose any path you want
NEWS_JSON_PATH = os.environ.get('NEWS_JSON_PATH') or NEWS_JSON_PATH  # DO NOT MODIFY THIS LINE

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(-q5783z2mh-cd217skey@(+_np2&j0=sl6suvo)ah2uwz@9ij'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hypernews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hypernews.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
    hypernews/news/json_reform.pyimport json

with open('C:\\Python\\django\\HyperNews Portal\\HyperNews Portal\\task\\hypernews\\news\\news.json',
          'r') as json_file:
    list_from_json = json.load(json_file)
    date_list = [list_from_json['created'] for i in list_from_json()]
print(', '.join(date_list))    hypernews/news/news.jsonV[{
  "created": "2020-02-09 14:15:10",
  "text": "Text of the news 1",
  "title": "News 1",
  "link": 1
},
  {
    "created": "2020-02-10 14:15:10",
    "text": "Text of the news 2",
    "title": "News 2",
    "link": 2
  },
  {
    "created": "2020-02-09 16:15:10",
    "text": "Text of the news 3",
    "title": "News 3",
    "link": 3
  }]    hypernews/db.sqlite3