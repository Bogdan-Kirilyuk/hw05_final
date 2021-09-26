from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Т' * 22,
        )

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post_text = PostModelTest.post
        expected_object_text = post_text.text[:15]
        self.assertEqual(expected_object_text, str(post_text))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group_title = GroupModelTest.group
        expected_object_title = group_title.title
        self.assertEqual(expected_object_title, str(group_title))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для комментария',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Вежливый комментарий',
            post=cls.post,
        )

    def test_models_have_correct_object_names_comments(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment_text = CommentModelTest.comment
        expected_object_text = comment_text.text[:15]
        self.assertEqual(expected_object_text, str(comment_text))
