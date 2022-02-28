import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from posts.forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
ADD_INDEX = 'posts:index'
ADD_POST_CREATE = 'posts:post_create'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='text-comment'
        )
        cls.ADD_PROFILE = 'posts:profile'
        cls.ADD_POST_DETAIL = 'posts:post_detail'
        cls.ADD_POST_EDIT = 'posts:post_edit'
        cls.ADD_COMMENT = 'posts:add_comment'
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_post_create(self):
        post_count = Post.objects.count()
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_img,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Тестовый текст',
            'author': 'Nik',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(ADD_POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                PostFormTest.ADD_PROFILE, kwargs={'username': f'{self.user}'})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=self.user,
                group=self.group.pk,
                image='posts/small.gif',
            ).exists()
        )

    def test_form_post_edit(self):
        orig_post = self.post.text
        form_data = {
            'text': 'Отредактированный текст',
            'author': 'Nik',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                PostFormTest.ADD_POST_EDIT,
                kwargs={'post_id': f'{self.post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertRedirects(
            response, reverse(
                PostFormTest.ADD_POST_DETAIL,
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        self.assertNotEqual(orig_post, edited_post)

    def test_auth_client_can_leave_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'text-comment',
        }
        response = self.authorized_client.post(
            reverse(
                PostFormTest.ADD_COMMENT,
                kwargs={'post_id': f'{self.post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(
            response, reverse(
                PostFormTest.ADD_POST_DETAIL,
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.user)

    def test_comments_exists_on_post_detail_page(self):
        response = self.guest_client.get(
            reverse(
                PostFormTest.ADD_POST_DETAIL,
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        self.assertTrue(PostFormTest.comment, response.context['comments'])
