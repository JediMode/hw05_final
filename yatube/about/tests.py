from http import HTTPStatus

from django.test import Client, TestCase

URL_AUTHOR = '/about/author/'
URL_TECH = '/about/tech/'


class AboutURLTests(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_uses_correct_html(self):
        url_names_templates = {
            URL_AUTHOR: 'about/author.html',
            URL_TECH: 'about/tech.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_urls_works(self):
        status_code = HTTPStatus.OK.value
        url_names = {
            URL_AUTHOR: status_code,
            URL_TECH: status_code,
        }
        for url, status in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)
