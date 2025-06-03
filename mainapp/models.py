from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    salt = models.BinaryField()
    password_hash = models.CharField(max_length=64)
    previous_password_hash1 = models.CharField(max_length=64, blank=True, null=True)
    previous_password_hash2 = models.CharField(max_length=64, blank=True, null=True)
    previous_password_hash3 = models.CharField(max_length=64, blank=True, null=True)


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, unique=True)
    created_by = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
