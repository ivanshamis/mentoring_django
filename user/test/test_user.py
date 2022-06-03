from rest_framework import status

from ..constants import ErrorMessages
from .utils import BaseAPITestCase

API_DETAIL = "api:user-detail"


class UserGetTestCase(BaseAPITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request_user = cls.user
        cls.tested_user = cls.admin
        cls.api_detail = API_DETAIL
        cls.default_pk = cls.tested_user.user_id

    def test_get(self):
        response = self.request_user.get(self.get_detail_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["id", "email", "username", "first_name", "last_name"]:
            self.assertEqual(
                response.data.get(field),
                str(getattr(self.tested_user.get_user(), field)),
            )

    def test_get_non_auth(self):
        response = self.request_user.get_non_auth(self.get_detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"), ErrorMessages.NOT_AUTHENTICATED)

    def test_get_not_exists(self):
        response = self.request_user.get(self.get_detail_url(1000000))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), ErrorMessages.NOT_FOUND)

    def test_get_bad_pk(self):
        response = self.request_user.get(self.get_detail_url("some_string"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), ErrorMessages.NOT_FOUND)


class UserUpdateTestCase(BaseAPITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_detail = API_DETAIL
        cls.default_pk = cls.admin.user_id

    def test_update_not_allowed(self):
        response = self.user.put(
            self.get_detail_url(), data={"username": "new_username"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), ErrorMessages.NOT_ALLOWED)


class UserGetCurrentTestCase(BaseAPITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_detail = API_DETAIL
        cls.default_pk = "me"

    def test_get_me(self):
        response = self.user.get(self.get_detail_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_me_non_auth(self):
        response = self.user.get_non_auth(self.get_detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"), ErrorMessages.NOT_AUTHENTICATED)


class UserUpdateCurrentTestCase(BaseAPITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_detail = API_DETAIL
        cls.default_pk = "me"

    def test_update_me(self):
        new_username = "new_username"
        response = self.user.put(self.get_detail_url(), data={"username": new_username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().username, new_username)

    def test_update_me_non_auth(self):
        response = self.user.put_non_auth(
            self.get_detail_url(), data={"username": "username"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"), ErrorMessages.NOT_AUTHENTICATED)

    def test_update_me_no_username(self):
        response = self.user.put(
            self.get_detail_url(), data={"first_name": "first_name"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("username")[0],
            ErrorMessages.FIELD_IS_REQUIRED,
        )

    def test_update_me_readonly_email(self):
        old_email = self.user.get_user().email
        response = self.user.put(
            self.get_detail_url(),
            data={"username": "new_username", "email": "new@emai.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().email, old_email)

    def test_update_me_readonly_is_active(self):
        old_is_active = self.user.get_user().is_active
        response = self.user.put(
            self.get_detail_url(),
            data={"username": "new_username", "is_active": not old_is_active},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().is_active, old_is_active)

    def test_update_me_readonly_is_staff(self):
        old_is_staff = self.user.get_user().is_staff
        response = self.user.put(
            self.get_detail_url(),
            data={"username": "new_username", "is_staff": not old_is_staff},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.get_user().is_staff, old_is_staff)
