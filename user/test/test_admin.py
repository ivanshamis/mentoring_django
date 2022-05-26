from rest_framework import status

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
