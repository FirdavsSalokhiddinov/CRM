from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Customer


class AccountSignalTests(TestCase):
    def test_default_groups_are_created(self):
        self.assertTrue(Group.objects.filter(name="admin").exists())
        self.assertTrue(Group.objects.filter(name="customer").exists())

    def test_regular_user_gets_customer_group_and_profile(self):
        user = User.objects.create_user(
            username="newcustomer",
            email="customer@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(user.groups.filter(name="customer").exists())
        self.assertFalse(user.groups.filter(name="admin").exists())

        customer = Customer.objects.get(user=user)
        self.assertEqual(customer.name, "newcustomer")

    def test_superuser_gets_admin_group_without_customer_profile(self):
        admin_user = User.objects.create_superuser(
            username="boss",
            email="boss@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(admin_user.groups.filter(name="admin").exists())
        self.assertFalse(admin_user.groups.filter(name="customer").exists())
        self.assertFalse(Customer.objects.filter(user=admin_user).exists())


class AccountViewTests(TestCase):
    def test_register_page_creates_user_and_customer_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "janedoe",
                "email": "jane@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="janedoe")
        self.assertTrue(user.groups.filter(name="customer").exists())
        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_customer_is_redirected_from_home_to_user_page(self):
        user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="StrongPass123!",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("user-page"))

    def test_admin_can_open_dashboard(self):
        admin_user = User.objects.create_superuser(
            username="admin1",
            email="admin1@example.com",
            password="StrongPass123!",
        )

        self.client.force_login(admin_user)
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
