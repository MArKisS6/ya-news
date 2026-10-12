# news/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from news.models import Comment, News

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    
Unittest в Django: тестирование маршрутов
Приступим к тестированию маршрутов проекта YaNews; часть работы уже выполнена в прошлом уроке — тем лучше для нас!
В плане тестирования несколько пунктов относятся к маршрутам, посмотрим на них ещё раз:
Главная страница доступна анонимному пользователю. [Done!]
Страница отдельной новости доступна анонимному пользователю.
Страницы удаления и редактирования комментария доступны автору комментария.
При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
Авторизованный пользователь не может зайти на страницу редактирования или удаления чужих комментариев (возвращается ошибка 404).
Страницы регистрации пользователей и входа в учётную запись доступны анонимным пользователям.
В вашем файле news/tests/test_routes.py сейчас должен быть код теста, проверяющего доступность главной страницы проекта:
Скопировать код
PYTHON

# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):

    def test_home_page(self):
        url = reverse('news:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) 
Если по какой-то причине этого кода нет — добавьте его, запустите тесты и убедитесь, что они возвращают OK.
Если всё действительно OK — значит, доступность главной страницы протестирована и первый пункт плана выполнен.
Что там дальше?
Доступность отдельной страницы новости
Чтобы протестировать доступность страницы отдельной новости, для начала надо создать новость — ведь БД, на которой проводится тестирование, перед запуском тестов не содержит никаких объектов.
Создаём объект для теста
Добавляем фикстуру с созданием первой новости:
Скопировать код
PYTHON

# news/tests/test_routes.py
...  

# Импортируем класс модели новостей.
from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    ... 
Сейчас неважно, какой именно заголовок и текст будут у новости. При тестировании маршрутов содержимое свойств объекта проверяться не будет; значения этих строк не нужно сохранять в константы: в коде тестов эти строки больше нигде не пригодятся.
Получаем адрес страницы для запроса
Строки кода, описывающие URL к странице новости, выглядят так:
Скопировать код
PYTHON

# news/urls.py
...

app_name = 'news'

urlpatterns = [
    ...,
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
    ...,
] 
Адресом страницы с новостью, созданной в фикстуре, будет /news/1/: нам точно известно, что это первый объект, который создан в пустой таблице БД. 
Единица в адресе — это id новости и, одновременно, её первичный ключ (Primary Key, pk). Если в описании модели явно не указано, какое поле служит первичным ключом (а в модели News это не указано), то Django автоматически добавляет в модель поле с первичным ключом. 
Настройки этого поля для конкретного приложения задаются через AppConfig.default_auto_field, а глобально, для всего проекта — в settings.py через DEFAULT_AUTO_FIELD. Тип этого поля по умолчанию — BigAutoField (целое число от 1 до 9223372036854775807).
Несмотря на то, что адрес страницы известен — не стоит «хардкодить», писать этот адрес в явном виде, строкой '/news/1/'. Если структура адресов поменяется — придётся менять и эту строку с адресом везде, где она используется. 
Есть и другая причина: может быть написана ещё одна фикстура, которая, например, создаст объект класса News для всего тестирующего модуля. И тогда адрес страницы для объекта, созданного в фикстуре класса, будет другой.
Правильным решением будет обратиться к адресу страницы через функцию reverse(). В неё надо передать 
namespace и name страницы — увидеть их можно в файле urls.py приложения; в нашем случае это 'news:detail'
pk (Primary Key) записи; в нашем случае pk совпадает с id.
Передать необходимые значения в функцию reverse() можно через позиционные или именованные аргументы:
Скопировать код
PYTHON

url = reverse('news:detail', args=(self.news.pk,))
# Или      
url = reverse('news:detail', kwargs={'pk': self.news.pk}) 
В каждом из приведённых вариантов происходит одно и то же — переменной url присваивается строка '/news/1/'. То же самое можно сделать, указывая id объекта, а не pk. При этом нужно помнить, что вообще-то первичный ключ не всегда равен id, и в каких-то проектах он может быть другим.
Скопировать код
PYTHON

url = reverse('news:detail', args=(self.news.id,))
# Или
url = reverse('news:detail', kwargs={'pk': self.news.id}) 
Далее в тестах мы будем использовать вариант reverse('news:detail', args=(self.news.id,)), но вы можете использовать любой предложенный, кроме явного «хардкода» — строки /news/1/. 
Полный код теста будет выглядеть так:
Скопировать код
PYTHON

# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_home_page(self):
        url = reverse('news:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) 
Обязательно переносите каждый пример кода в свой проект и запускайте тесты; анализируйте и сам код, и результаты тестирования!
Тесты test_home_page() и test_detail_page() работают нормально, но их можно улучшить. В этих тестах повторяется один и тот же код: одинаково вызывается функция reverse(), одинаково отправляется GET-запрос к проверяемой странице, одинаково проверяется статус ответа. Разница между этими тестами — только в адресах страниц. 
Вспомним о принципе DRY и объединим эти два теста в один: соберём в кортеж аргументы для функции reverse() и применим метод subTest():
Скопировать код
PYTHON

# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_pages_availability(self):
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов, 
            # поэтому вторым параметром ставим None.
            ('news:home', None),
            # Путь для страницы новости 
            # принимает в качестве позиционного аргумента
            # id записи; передаём его в кортеже.
            ('news:detail', (self.news.id,))
        )
        # Итерируемся по внешнему кортежу 
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 
Выглядит как излишнее усложнение: ведь нужно проверить всего две страницы. Но в плане тестирования есть пункт 6: «Страницы регистрации пользователей и входа в учётную запись доступны анонимным пользователям». 
Страницы логина и регистрации пользователей можно проверить в том же тесте test_pages_availability(), нужно только дополнить кортеж с параметрами.
Имена, по которым доступны нужные страницы, берём в головном файле yanews/urls.py.
Скопировать код
PYTHON

# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_pages_availability(self):
        urls = (
            ('news:home', None),
            ('news:detail', (self.news.id,)),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
