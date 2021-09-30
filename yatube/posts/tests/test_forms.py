import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Группа',
            description='Тестовый текст',
            slug='test-slug',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.image = 'posts/small.gif'

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data_create = {
            'text': 'Текст теста создания поста',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args={self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data_create['text'])
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.image, self.image)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_edit = Post.objects.create(
            author=self.user,
            text='Текст теста редактирования поста',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new_text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={post_edit.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args={post_edit.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            id=post_edit.id,
            text=form_data['text'],
        ).exists()
        )

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comment_count = Comment.objects.count()
        post_comment = Post.objects.create(
            author=self.user,
            text='Текст поста',
        )
        form_data_comment = {
            'text': 'Текст теста создания коммента',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args={post_comment.id}),
            data=form_data_comment,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args={post_comment.id})
        )
        self.assertEqual(Post.objects.count(), comment_count + 1)
        last_comment = Comment.objects.latest('id')
        self.assertEqual(last_comment.text, form_data_comment['text'])
        self.assertEqual(last_comment.author, self.user)
        self.assertEqual(last_comment.post, post_comment)
