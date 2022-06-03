from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status

from .factory import UserFactory
from .utils import BaseAPITestCase
from ..constants import ErrorMessages
from ..models import User

API_AUTH = "api:auth"


class UserSignupTestCase(BaseAPITestCase):
    url = reverse(API_AUTH + "-signup")

    def test_signup(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={
                "email": new_user.email,
                "username": new_user.username,
                "password": new_user.password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data, {"email": new_user.email, "username": new_user.username}
        )
        self.assertTrue(
            User.objects.filter(
                email=new_user.email, username=new_user.username
            ).exists()
        )

    def test_signup_exists(self):
        existing_user = self.user.get_user()
        response = self.user.post_non_auth(
            self.url,
            data={
                "email": existing_user.email,
                "username": existing_user.username,
                "password": existing_user.password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ["email", "username"]:
            self.assertEqual(
                response.data.get("errors").get(field)[0],
                ErrorMessages.get_user_exists_message(field),
            )

    def test_signup_no_email(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={"username": new_user.username, "password": new_user.password},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("email")[0], ErrorMessages.FIELD_IS_REQUIRED
        )

    def test_signup_wrong_email(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={
                "email": new_user.username,
                "username": new_user.username,
                "password": new_user.password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("email")[0], ErrorMessages.NOT_VALID_EMAIL
        )

    def test_signup_no_password(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={"email": new_user.email, "username": new_user.username},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("password")[0],
            ErrorMessages.FIELD_IS_REQUIRED,
        )

    def test_signup_no_username(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={"email": new_user.email, "password": new_user.password},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("username")[0],
            ErrorMessages.FIELD_IS_REQUIRED,
        )

    def test_signup_weak_password(self):
        new_user = UserFactory.build()
        response = self.user.post_non_auth(
            self.url,
            data={
                "email": new_user.email,
                "username": new_user.username,
                "password": "1" * (ErrorMessages.MIN_PASSWORD_LENGTH - 1),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("errors").get("password")[0],
            ErrorMessages.get_week_password_message(),
        )


class UserLoginTestCase(BaseAPITestCase):
    url = reverse(API_AUTH + "-login")

    def test_login(self):
        existing_user = self.user.get_user()
        existing_password = self.user.user_password
        response = self.user.post_non_auth(
            self.url,
            data={"username": existing_user.email, "password": existing_password},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("token" in response.data)

    def test_inactive(self):
        existing_password = self.user.user_password
        user = UserFactory.create(
            is_active=False, password=make_password(existing_password)
        )
        response = self.user.post_non_auth(
            self.url,
            data={"username": user.email, "password": existing_password},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data.get("errors"), list)
        self.assertEqual(
            response.data.get("errors")[0], ErrorMessages.USER_IS_DEACTIVATED
        )

    def test_wrong_password(self):
        user = self.user.get_user()
        user_password = self.user.user_password
        response = self.user.post_non_auth(
            self.url,
            data={"username": user.email, "password": user_password + "_wrong"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data.get("errors"), list)
        self.assertEqual(
            response.data.get("errors")[0], ErrorMessages.USER_WRONG_CREDENTIALS
        )
