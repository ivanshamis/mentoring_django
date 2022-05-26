from rest_framework.test import APITestCase, APIClient

from .factory import UserFactory
from ..models import User


class TestUser(object):
    def __init__(self, is_staff: bool = False):
        user = UserFactory.create(is_staff=is_staff)
        self.user_id = user.id
        self._client = APIClient()
        self._client_non_auth = APIClient()
        self._client.credentials(HTTP_AUTHORIZATION="Token " + user.token)

    def _get_client(self, auth: bool):
        return self._client if auth else self._client_non_auth

    def get_user(self):
        return User.objects.get(pk=self.user_id)

    def get(self, url, auth: bool = True):
        return self._get_client(auth).get(url)

    def post(self, url, data, auth: bool = True):
        return self._get_client(auth).post(url, data)

    def put(self, url, data, auth: bool = True):
        return self._get_client(auth).put(url, data)


class BaseAPITestCase(APITestCase):
    user = None
    admin = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = TestUser()
        cls.admin = TestUser(is_staff=True)
