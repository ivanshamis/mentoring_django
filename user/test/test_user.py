from rest_framework import status

from .utils import BaseAPITestCase
from ..models import User

USER_URL = "/api/user/"


class UserGetCurrentTestCase(BaseAPITestCase):
    url = USER_URL + "me/"

    def test_get_me(self):
        response = self.user.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_me_non_auth(self):
        response = self.user.get(self.url, auth=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserUpdateCurrentTestCase(BaseAPITestCase):
    url = USER_URL + "me/"

    def test_update_me(self):
        new_username = "new_username"
        response = self.user.put(self.url, data={"username": new_username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().username, new_username)
