from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import tag

DEFAULT_USER = "testuser"
DEFAULT_EMAIL = "test@user.local"
DEFAULT_PASS = "1test2password3"


def setup_login(self):
    self.client = Client()
    self.user = User.objects.create_user(
        DEFAULT_USER, DEFAULT_EMAIL, DEFAULT_PASS)


def do_login(self):
    self.client.login(username=DEFAULT_USER, password=DEFAULT_PASS)


@tag('view')
class LoginViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to Prihud")

    def test_login_get_redirect_when_logged(self):
        do_login(self)
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)

    def test_login_post(self):
        response = self.client.post(reverse('login'), data={
            'username': DEFAULT_USER,
            'password': DEFAULT_PASS
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.context, None)

    def test_login_post_failed(self):
        response = self.client.post(reverse('login'), data={
            'username': 'invalid',
            'password': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['login_failed'], True)

    def test_login_other_method(self):
        response = self.client.put(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to Prihud")


@tag('view')
class LogoutTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_logout(self):
        do_login(self)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to Prihud")


@tag('view')
class IndexViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_index(self):
        do_login(self)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Welcome back, {DEFAULT_USER}")
