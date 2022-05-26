from rest_framework import status

from .utils import BaseAPITestCase
from .factory import UserFactory
from ..models import User

AUTH_URL = "/api/auth/"


class UserSignupTestCase(BaseAPITestCase):
    url = AUTH_URL + "signup/"

    def test_signup(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={
                "email": new_user.email,
                "username": new_user.username,
                "password": new_user.password,
            },
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data, {"email": new_user.email, "username": new_user.username}
        )
        self.assertTrue(User.objects.filter(email=new_user.email).exists())

    def test_signup_exists(self):
        existing_user = self.user.get_user()
        response = self.user.post(
            self.url,
            data={
                "email": existing_user.email,
                "username": existing_user.username,
                "password": existing_user.password,
            },
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_signup_no_email(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={"username": new_user.username, "password": new_user.password},
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_signup_wrong_email(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={
                "email": new_user.username,
                "username": new_user.username,
                "password": new_user.password,
            },
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_signup_no_password(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={"email": new_user.email, "username": new_user.username},
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_signup_no_username(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={"email": new_user.email, "password": new_user.password},
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)

    def test_signup_weak_password(self):
        new_user = UserFactory.build()
        response = self.user.post(
            self.url,
            data={
                "email": new_user.email,
                "username": new_user.username,
                "password": "1" * 7,
            },
            auth=False,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("errors" in response.data)


class UserLoginTestCase(BaseAPITestCase):
    url = f"{AUTH_URL}login/"

    def test_login(self):
        existing_user = self.user.get_user()
        response = self.user.post(
            self.url,
            data={"username": existing_user.email, "password": existing_user.password},
            auth=False,
        )
        # TODO "A user with this email and password was not found."
        # print(response.data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
