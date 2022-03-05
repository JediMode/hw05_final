from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descr',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
        )

    def test_post_models_has_correct_object_names(self):
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))
        post = PostModelTest.post
        expected_post_name = post.text
        self.assertEqual(expected_post_name, str(post))

    def test_post_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите текст...',
            'group': 'Выберите группу...'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nik')
        cls.comment = Post.objects.create(
            author=cls.user,
            text='test-comment',
            )
        
    def test_post_comment_has_correct_object_names(self):
        comment = CommentModelTest.comment
        expected_field = comment.text
        self.assertEqual(expected_field, str(comment))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='Auth')
        cls.user = User.objects.create_user(username='User')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.auth,
        )

    def test_post_follow_verbose_name(self):
        test_object = FollowModelTest.follow
        verboses_field = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, value in verboses_field.items():
            with self.subTest(field=field):
                self.assertEqual(
                    test_object._meta.get_field(field).verbose_name, value)
