from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.images import ImageFile
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from posts.forms import PostForm

ADD_INDEX = 'posts:index'
ADD_POST_CREATE = 'posts:post_create'
ADD_GROUP_LIST = 'posts:group_posts'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username='Nik')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.ADD_PROFILE = 'posts:profile'
        cls.ADD_POST_DETAIL = 'posts:post_detail'
        cls.ADD_POST_EDIT = 'posts:post_edit'
        cls.ADD_FOLLOW_INDEX = 'posts:follow_index'
        cls.ADD_PROFILE_FOLLOW = 'posts:profile_follow'
        cls.ADD_PROFILE_UNFOLLOW = 'posts:profile_unfollow'
        cls.another_group = Group.objects.create(
            title='a-test-title',
            slug='a-test-slug',
            description='a-test-description'
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.a_user = User.objects.create_user(username='Somebody')

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse(ADD_INDEX): 'posts/index.html',
            reverse(
                PostPagesTests.ADD_PROFILE, kwargs={'username': f'{self.user}'}
            ): 'posts/profile.html',
            reverse(
                PostPagesTests.ADD_POST_DETAIL,
                kwargs={'post_id': f'{self.post.pk}'}
            ): 'posts/post_detail.html',
            reverse(
                ADD_GROUP_LIST, kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(ADD_POST_CREATE): 'posts/create_post.html',
            reverse(
                PostPagesTests.ADD_POST_EDIT,
                kwargs={'post_id': f'{self.post.pk}'}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.guest_client.get(reverse(ADD_INDEX))
        test_object = response.context['page_obj'][0]
        self.assertEqual(test_object.text, 'test-text')

    def test_profile_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse(
                PostPagesTests.ADD_PROFILE,
                kwargs={'username': f'{self.a_user}'}
            )
        )
        test_post_author = response.context['author'] == self.a_user
        self.assertEqual(test_post_author, True)

    def test_post_detail_show_correct_context(self):
        response = self.guest_client.get(
            reverse(
                PostPagesTests.ADD_POST_DETAIL,
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        test_post_id = response.context['post_detail']
        test_image = response.context['post_detail'].image
        self.assertEqual(test_post_id.pk, self.post.pk)
        self.assertIsInstance(test_image, ImageFile)

    def test_group_posts_show_correct_context(self):
        response = self.guest_client.get(
            reverse(ADD_GROUP_LIST, kwargs={'slug': 'test-slug'})
        )
        test_post_group = response.context['group']
        self.assertEqual(test_post_group.title, f'{self.group}')

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse(ADD_POST_CREATE))
        test_form = response.context['form']
        self.assertIsInstance(test_form, PostForm)
        self.assertIsNone(response.context.get('is_edit', None))

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                PostPagesTests.ADD_POST_EDIT,
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])
        self.assertIsInstance(response.context['is_edit'], bool)

    def test_post_exists_on_pages_and_not_dublicated(self):
        value = 'test-slug'
        dict_names = {
            reverse(ADD_INDEX): value,
            reverse(ADD_GROUP_LIST, kwargs={'slug': 'test-slug'}): value,
            reverse(
                PostPagesTests.ADD_PROFILE, kwargs={'username': f'{self.user}'}
            ): value,
        }
        for address, expected_value in dict_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                test_obj = response.context['page_obj'][0]
                self.assertEqual(test_obj.group.slug, expected_value)

        self.assertFalse(Post.objects.filter(
            pk=self.post.id,
            text='test-text',
            group=self.another_group.pk
        ).exists()
        )

    def test_post_has_img_in_context(self):
        template_names = (
            reverse(ADD_INDEX),
            reverse(
                PostPagesTests.ADD_PROFILE,
                kwargs={'username': f'{self.user}'}),
            reverse(
                ADD_GROUP_LIST, kwargs={'slug': 'test-slug'}),
        )
        for address in template_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                image = response.context['page_obj'][0].image
                self.assertIsInstance(image, ImageFile)

    def test_index_page_cashe(self):
        response = self.authorized_client.get(reverse(ADD_INDEX))
        cache_before = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        self.assertEqual(response.content, cache_before)
        cache.clear()
        response_after = self.guest_client.get(reverse(ADD_INDEX))
        cache_after = response_after.content
        self.assertNotEqual(cache_after, cache_before)

    def test_auth_user_follow_and_track_feed(self):
        self.a_user_client = Client()
        self.a_user_client.force_login(self.a_user)
        post = Post.objects.create(
            text='text_test',
            author=self.user,
        )
        self.a_user_client.get(
            reverse(
                PostPagesTests.ADD_PROFILE_FOLLOW,
                kwargs={'username': f'{self.post.author}'}
            )
        )
        self.assertTrue(Follow.objects.filter(
            user=self.a_user,
            author=self.post.author,
        ).exists())
        response = self.a_user_client.get(
            reverse(PostPagesTests.ADD_FOLLOW_INDEX))
        self.assertIn(
            post,
            response.context['page_obj'])

    def test_auth_user_unfollow(self):
        self.a_user_client = Client()
        self.a_user_client.force_login(self.a_user)
        self.a_user_client.get(
            reverse(
                PostPagesTests.ADD_PROFILE_UNFOLLOW,
                kwargs={'username': f'{self.post.author}'}
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=self.a_user,
            author=self.post.author,
        ).exists())

    def test_post_appearance_in_feed(self):
        post = Post.objects.create(
            text='text_test',
            author=self.user,
        )
        self.a_user_client = Client()
        self.a_user_client.force_login(self.a_user)
        response = self.a_user_client.get(
            reverse(PostPagesTests.ADD_FOLLOW_INDEX))
        self.assertNotIn(post, response.context['page_obj'])


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username='Nik')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.bulk_create([
            Post(author=cls.user, text=f'test-text {i}', group=cls.group)
            for i in range(13)
        ])
        cls.posts = Post.objects.bulk_create(cls.posts_obj)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_first_page_contains_ten_obj(self):
        qty = settings.POSTS_PER_PAGE
        pages = {
            reverse(ADD_INDEX): qty,
            reverse(ADD_GROUP_LIST, kwargs={'slug': 'test-slug'}): qty,
            reverse(
                PostPagesTests.ADD_PROFILE, kwargs={'username': f'{self.user}'}
            ): qty,
        }
        for name_address, qty in pages.items():
            with self.subTest(name_address=name_address):
                response = self.guest_client.get(name_address)
                self.assertEqual(len(response.context['page_obj']), qty)

    def test_second_page_contains_four_obj(self):
        qty = 3
        pages = {
            reverse(ADD_INDEX) + '?page=2': qty,
            reverse(ADD_GROUP_LIST, kwargs={'slug': 'test-slug'})
            + '?page=2': qty,
            reverse(
                PostPagesTests.ADD_PROFILE,
                kwargs={'username': f'{self.user}'}
            ) + '?page=2': qty,
        }
        for name_address, qty in pages.items():
            with self.subTest(name_address=name_address):
                response = self.guest_client.get(name_address)
                self.assertEqual(len(response.context['page_obj']), qty)
