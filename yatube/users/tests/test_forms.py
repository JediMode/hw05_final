from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm, User


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_create_user(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'user1',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), users_count+1)
        self.assertTrue(
            User.objects.filter(username='user1').exists()
        )
