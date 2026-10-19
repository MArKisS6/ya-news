# news/tests/test_logic.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Аноним не может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    """Комментарий с запрещённым словом не создаётся."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
    }
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    assertFormError(form, 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment, form_data):
    """Автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(reader_client, comment, form_data):
    """Чужой не может редактировать комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(reader_client, comment):
    """Чужой не может удалить комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1