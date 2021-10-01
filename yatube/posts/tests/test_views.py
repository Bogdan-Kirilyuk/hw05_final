from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestTemplate')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовый заголовок',
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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=uploaded,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', args={self.user}):
            'posts/profile.html',
            reverse('posts:post_detail', args={self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', args={self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_cache(self):
        """Кеширование index.html работает."""
        content = self.authorized_client.get(
            reverse('posts:index')).content
        self.post.delete()
        content_cached = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content, content_cached)
        cache.clear()
        content_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content, content_clear)

    def check_post_page(self, test_post):
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.image, self.post.image)

    def test_context_index(self):
        """Тестирование context страницы index."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_page(response.context['page_obj'][0])

    def test_context_group_list(self):
        """Тестирование context страницы group_list."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.check_post_page(response.context['page_obj'][0])
        context_group = response.context['group']
        self.assertEqual(context_group, self.group)

    def test_context_profile(self):
        """Тестирование context страницы profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', args={self.user}))
        self.check_post_page(response.context['page_obj'][0])
        context_author = response.context['author']
        self.assertEqual(context_author, self.post.author)

    def test_context_page_post_detail(self):
        """Словарь context одного поста соответствует ожиданиям."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.id}))
        self.check_post_page(response.context['post'])

    def test_context_page_post_edit(self):
        """Словарь context редактирования поста соответствует ожиданиям."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.id}))
        self.check_post_page(response.context['post'])
        context_is_edit = response.context['is_edit']
        self.assertTrue(context_is_edit)

    def test_form_on_page(self):
        """Форма создания и редактирования соответствует ожиданиям."""
        templates_pages_names = [
            reverse('posts:post_edit', args={self.post.id}),
            reverse('posts:post_create'),
        ]
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                for reverse_name in templates_pages_names:
                    response = self.authorized_client.get(reverse_name)
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='TestPoginator')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='TestPoginator-заголовок',
            description='TestPoginator-описание',
            slug='TestPoginator-slug',
        )
        number_of_users = 13
        for i in range(number_of_users):
            Post.objects.create(
                text='Текст поста',
                author=self.user,
                group=self.group,
            )

    def test_paginator(self):
        """Пагинация работает как надо."""
        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', args={self.user}),
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):

    def setUp(self):
        self.follower = User.objects.create_user(username='Follower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)
        self.author = User.objects.create_user(username='author')
        self.post_author = Post.objects.create(
            text='текст автора',
            author=self.author,
        )

    def test_follow_author(self):
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        last_follow = Follow.objects.latest('id')
        self.assertEqual(last_follow.author, self.author)
        self.assertEqual(last_follow.user, self.follower)
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.author}))

    def test_unfollow_author(self):
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args={self.author}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.author}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_new_post_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        post_follow = response.context['page_obj'][0]
        self.assertEqual(post_follow, self.post_author)

    def test_new_post_unfollow(self):
        new_author = User.objects.create_user(username='new_author')
        self.authorized_client.force_login(new_author)
        Post.objects.create(
            text='новый текст автора',
            author=new_author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
