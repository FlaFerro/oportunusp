from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Criação dos grupos após a migração
    Group.objects.get_or_create(name='Aluno')
    Group.objects.get_or_create(name='Professor')
    Group.objects.get_or_create(name='Laboratório')
    Group.objects.get_or_create(name='Grupo de Extensão')
