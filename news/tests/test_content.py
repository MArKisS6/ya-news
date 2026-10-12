from django.conf import settings
from django.test import TestCase

from news.models import News


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create(
            News(title=f'Новость {index}', text='Просто текст.')
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )
