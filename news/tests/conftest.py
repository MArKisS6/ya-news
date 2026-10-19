# news/tests/conftest.py
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news():
    """Фикстура создаёт новость."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model):
    """Фикстура создаёт автора комментария."""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    """Фикстура создаёт читателя."""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    """Клиент, залогиненный под автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент, залогиненный под читателем."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(news, author):
    """Фикстура создаёт комментарий от имени автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_id_for_args(news):
    """Возвращает кортеж с id новости для args в reverse."""
    return (news.id,)


@pytest.fixture
def news_bulk():
    """Фикстура создаёт пакет новостей с разными датами."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(news, author):
    """Фикстура создаёт 10 комментариев с разным временем."""
    now = timezone.now()
    comments_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


@pytest.fixture
def form_data():
    """Данные для POST-запроса при создании/редактировании комментария."""
    return {'text': 'Текст комментария'}
