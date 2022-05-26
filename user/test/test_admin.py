from rest_framework import status

from .test_user import UserGetTestCase
from .utils import BaseAPITestCase
from ..models import User

ADMIN_URL = "/api/admin/"


class AdminListingTestCase(BaseAPITestCase):
    url = ADMIN_URL

    def test_listing(self):
        response = self.admin.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), User.objects.count())
        for field in ["id", "email", "username"]:
            self.assertEqual(
                response.data[0].get(field), getattr(User.objects.first(), field)
            )
            self.assertEqual(
                response.data[-1].get(field), getattr(User.objects.last(), field)
            )

    def test_listing_non_auth(self):
        response = self.admin.get(self.url, auth=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listing_non_admin(self):
        response = self.user.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminGetTestCase(UserGetTestCase):
    url = ADMIN_URL + "{pk}/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request_user = cls.admin
        cls.tested_user = cls.user

    def test_get(self):
        super().test_get()

    def test_get_non_auth(self):
        super().test_get_non_auth()

    def test_get_not_exists(self):
        super().test_get_not_exists()

    def test_get_bad_pk(self):
        super().test_get_bad_pk()


class AdminUpdateTestCase(BaseAPITestCase):
    url = ADMIN_URL + "{pk}/"

    def test_update(self):
        new_username = "new_username_from_admin"
        response = self.admin.put(
            self.url.format(pk=self.user.user_id), data={"username": new_username}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().username, new_username)

    def test_update_non_auth(self):
        response = self.admin.put(self.url, data={"username": "username"}, auth=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_non_admin(self):
        response = self.user.put(self.url, data={"username": "username"}, auth=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
