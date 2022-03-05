from http import HTTPStatus

from django.test import Client, TestCase
from django.core.cache import cache

from posts.models import Group, Post, User

URL_INDEX = '/'
URL_POST_CREATE = '/create/'
URL_GROUP_LIST = '/group/test-slug/'
URL_ANON_CREATE_REDIRECT = '/auth/login/?next=/create/'
URL_UNEXISTING = '/unexisting_page/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.user,
        )
        cls.URL_PROFILE = f'/profile/{cls.post.author}/'
        cls.URL_POST_DETAIL = f'/posts/{cls.post.id}/'
        cls.URL_POST_EDIT = f'/posts/{cls.post.id}/edit/'
        cls.URL_ANON_EDIT_REDIRECT = (
            f'/auth/login/?next=/posts/{cls.post.id}/edit/')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_post_not_found_url(self):
        response = self.guest_client.get(URL_UNEXISTING)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_post_guest_client_url_work(self):
        status_code = HTTPStatus.OK.value
        urls_dict = {
            URL_INDEX: status_code,
            URL_GROUP_LIST: status_code,
            PostURLTests.URL_PROFILE: status_code,
            PostURLTests.URL_POST_DETAIL: status_code,
        }
        for address, status in urls_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_post_authorised_client_url_work(self):
        status_code = HTTPStatus.OK.value
        urls_dict = {
            URL_POST_CREATE: status_code,
            PostURLTests.URL_POST_EDIT: status_code,
        }
        for address, status in urls_dict.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_post_urls_redirects_anonymous(self):
        response_value = self.guest_client
        dict_redirect = {
            response_value.get(
                URL_POST_CREATE, follow=True
            ): URL_ANON_CREATE_REDIRECT,
            response_value.get(
                PostURLTests.URL_POST_EDIT, follow=True
            ): PostURLTests.URL_ANON_EDIT_REDIRECT,
        }
        for request, reply in dict_redirect.items():
            with self.subTest(request=request):
                response = request
                self.assertRedirects(response, reply)

    def test_post_urls_uses_correct_template(self):
        template_url_names = {
            URL_INDEX: 'posts/index.html',
            URL_GROUP_LIST: 'posts/group_list.html',
            URL_POST_CREATE: 'posts/create_post.html',
            PostURLTests.URL_PROFILE: 'posts/profile.html',
            PostURLTests.URL_POST_DETAIL: 'posts/post_detail.html',
            PostURLTests.URL_POST_EDIT: 'posts/create_post.html'
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
