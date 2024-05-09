from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class Expense(models.Model):
    # name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payee = models.CharField(max_length=50)
    payer = models.CharField(max_length=50)  # Add a payer field

    def save(self, *args, **kwargs):
        if not self.payee or not self.payer:
            raise ValueError("Both username and payer must be set for Expense object.")
        super().save(*args, **kwargs)