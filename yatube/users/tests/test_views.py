from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

ADD_SIGNUP = 'users:signup'
ADD_LOGOUT = 'users:logout'
ADD_LOGIN = 'users:login'
ADD_PASS_CHANGE = 'users:password_change_form'
ADD_PASS_DONE = 'users:password_change_done'
ADD_PASS_RESET = 'users:password_reset'


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_name_uses_correct_template(self):
        names_dict = {
            ADD_SIGNUP: 'users/signup.html',
            ADD_LOGIN: 'users/login.html',
            ADD_PASS_CHANGE: 'users/password_change_form.html',
            ADD_PASS_DONE: 'users/password_change_done.html',
            ADD_PASS_RESET: 'users/login.html',
            ADD_LOGOUT: 'users/logged_out.html',
        }
        for name, template in names_dict.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
