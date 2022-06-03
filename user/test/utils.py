import random
import string

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from .factory import UserFactory
from ..models import User


class TestUser(object):
    def __init__(self, is_staff: bool = False):
        self.user_password = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )
        user = UserFactory.create(
            is_staff=is_staff, password=make_password(self.user_password)
        )
        self.user_id = user.id
        self._client_auth = APIClient()
        self._client_non_auth = APIClient()
        self._client_auth.credentials(HTTP_AUTHORIZATION="Token " + user.token)

    def get_user(self):
        return User.objects.get(pk=self.user_id)

    def get(self, url):
        return self._client_auth.get(url)

    def get_non_auth(self, url):
        return self._client_non_auth.get(url)

    def post(self, url, data):
        return self._client_auth.post(url, data)

    def post_non_auth(self, url, data):
        return self._client_non_auth.post(url, data)

    def put(self, url, data):
        return self._client_auth.put(url, data)

    def put_non_auth(self, url, data):
        return self._client_non_auth.put(url, data)

    def delete(self, url, data):
        return self._client_auth.delete(url, data)

    def delete_non_auth(self, url, data):
        return self._client_non_auth.delete(url, data)


class BaseAPITestCase(APITestCase):
    url: str
    api_detail: str
    default_pk: int or str
    user: TestUser
    admin: TestUser
    request_user: TestUser
    tested_user: TestUser

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = TestUser()
        cls.admin = TestUser(is_staff=True)

    def get_detail_url(self, pk=None):
        return reverse(self.api_detail, kwargs={"pk": pk if pk else self.default_pk})
