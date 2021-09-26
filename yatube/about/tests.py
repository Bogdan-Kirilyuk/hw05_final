from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        super().setUpClass()
        self.guest_client = Client()

    def test_author(self):
        """Страница author доступна."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        """Cтраница tech доступна."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)
