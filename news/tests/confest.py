# news/tests/conftest.py
import pytest
from django.test.client import Client

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
