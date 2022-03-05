from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()

URL_SIGNUP = '/auth/signup/'
URL_LOGOUT = '/auth/logout/'
URL_LOGIN = '/auth/login/'
URL_PASS_CHANGE = '/auth/password_change/'
URL_CHANGE_DONE = '/auth/password_change/done/'
URL_PASS_RESET = '/auth/password_reset/'
URL_ANON_PASS_CHANGE_REDIRECTS = (
    '/auth/login/?next=/auth/password_change/')
URL_ANON_CHANGE_DONE_REDIRECTS = (
    '/auth/login/?next=/auth/password_change/done/')


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_users_guest_urls_works(self):
        status_code = HTTPStatus.OK.value
        urls_names = {
            URL_SIGNUP: status_code,
            URL_LOGIN: status_code,
        }
        for url, status in urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_users_auth_urls_works(self):
        status_code = HTTPStatus.OK.value
        urls_names = {
            URL_PASS_CHANGE: status_code,
            URL_CHANGE_DONE: status_code,
            URL_PASS_RESET: status_code,
            URL_LOGOUT: status_code,
        }
        for url, status in urls_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_users_urls_uses_correct_templates(self):
        template_urls_names = {
            URL_SIGNUP: 'users/signup.html',
            URL_LOGIN: 'users/login.html',
            URL_PASS_RESET: 'users/login.html',
            URL_LOGOUT: 'users/logged_out.html',
        }
        for url, template in template_urls_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_users_urls_redirects_anonymous(self):
        response = self.guest_client
        url_redirect = {
            response.get(
                URL_PASS_CHANGE, follow=True): URL_ANON_PASS_CHANGE_REDIRECTS,
            response.get(
                URL_CHANGE_DONE, follow=True): URL_ANON_CHANGE_DONE_REDIRECTS,
        }
        for request, reply in url_redirect.items():
            with self.subTest(request=request):
                response_second = request
                self.assertRedirects(response_second, reply)
