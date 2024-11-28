from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_opportunities')  # Quem publicou
    category = models.CharField(max_length=100)  # Área da pesquisa
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Se a oportunidade está ativa
    subscribers = models.ManyToManyField(User, related_name='subscribed_opportunities', blank=True)  # Usuários inscritos

    def __str__(self):
        return self.title

    @property
    def dono(self):
        # Propriedade para acessar o perfil do dono da oportunidade
        return self.posted_by.profile  # Assuming the user has a profile

    @property
    def subscriber_emails(self):
        # Retorna uma lista de e-mails dos inscritos
        return [user.email for user in self.subscribers.all()]


class Profile(models.Model):
    USER_TYPES = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('laboratorio', 'Laboratório'),
        ('grupo_extensao', 'Grupo de Extensão'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    user_type = models.CharField(max_length=50, choices=USER_TYPES, default='aluno')  # Campo para escolher o tipo de usuário
    full_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Quem fez o comentário
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='comments')  # A oportunidade ao qual o comentário pertence
    content = models.TextField()  # Texto do comentário
    date_posted = models.DateTimeField(default=timezone.now)  # Data de criação
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # Respostas ao comentário (comentário pai)

    def __str__(self):
        return f"Comentário de {self.user.username} em {self.opportunity.title}"
    
    class Meta:
        ordering = ['date_posted']
