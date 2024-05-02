from django.db import models

# Create your models here.

class Menu(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class MenuOption(models.Model):
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    parent_option = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_options')

    def __str__(self) -> str:
        return self.name
