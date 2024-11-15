from django.db import models
from django.contrib.auth.models import User

class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Quem publicou
    category = models.CharField(max_length=100)  # Área da pesquisa
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Se a oportunidade está ativa

    def __str__(self):
        return self.title
