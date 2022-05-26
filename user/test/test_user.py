from rest_framework import status

from .utils import BaseAPITestCase

USER_URL = "/api/user/"


class UserGetTestCase(BaseAPITestCase):
    url = USER_URL + "{pk}/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request_user = cls.user
        cls.tested_user = cls.admin

    def test_get(self):
        response = self.request_user.get(self.url.format(pk=self.tested_user.user_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["id", "email", "username", "first_name", "last_name"]:
            self.assertEqual(
                response.data.get(field), getattr(self.tested_user.get_user(), field)
            )

    def test_get_non_auth(self):
        response = self.request_user.get(
            self.url.format(pk=self.tested_user.user_id), auth=False
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_not_exists(self):
        response = self.request_user.get(self.url.format(pk=1000))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_bad_pk(self):
        response = self.request_user.get(self.url.format(pk="some_string"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserUpdateTestCase(BaseAPITestCase):
    url = USER_URL + "{pk}/"

    def test_update(self):
        response = self.user.put(
            self.url.format(pk=self.admin.user_id), data={"username": "new_username"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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

    def test_update_me_non_auth(self):
        response = self.user.put(self.url, data={"username": "username"}, auth=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_me_no_username(self):
        response = self.user.put(self.url, data={"first_name": "first_name"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_update_me_readonly_email(self):
        old_email = self.user.get_user().email
        response = self.user.put(
            self.url, data={"username": "new_username", "email": "new@emai.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().email, old_email)

    def test_update_me_readonly_is_active(self):
        old_is_active = self.user.get_user().is_active
        response = self.user.put(
            self.url, data={"username": "new_username", "is_active": not old_is_active}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().is_active, old_is_active)

    def test_update_me_readonly_is_staff(self):
        old_is_staff = self.user.get_user().is_staff
        response = self.user.put(
            self.url, data={"username": "new_username", "is_staff": not old_is_staff}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().is_staff, old_is_staff)
