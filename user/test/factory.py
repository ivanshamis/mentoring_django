from factory import django, Faker

from ..models import User


class UserFactory(django.DjangoModelFactory):
    username = Faker("user_name")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    password = Faker("password")

    class Meta:
        model = User
