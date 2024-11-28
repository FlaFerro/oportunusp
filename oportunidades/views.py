from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity, Profile, Comment
from django.contrib.auth.decorators import permission_required, login_required
from .forms import UserRegistrationForm, CommentForm, PostForm, ProfileEditForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views import  View
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings



@login_required
def subscribe_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Verifica se o usuário é do tipo 'aluno'
    if request.user.profile.user_type != 'aluno':
        messages.error(request, "Você precisa ser um aluno para se inscrever nesta oportunidade.")
        return redirect('opportunity_detail', pk=opportunity.pk)  # Redireciona para a página de detalhes da oportunidade
    
    # Adiciona o usuário à lista de inscritos
    opportunity.subscribers.add(request.user)

    # Obtém os dados do aluno e do dono da oportunidade
    aluno = request.user.profile
    dono = opportunity.dono  # 'dono' agora é um objeto Profile

    # Enviar e-mail para o dono da oportunidade
    send_mail(
        subject=f"Nova inscrição na oportunidade: {opportunity.title}",
        message=f"Você recebeu uma nova inscrição!\n\nAluno: {aluno.full_name}\nE-mail: {aluno.user.email}\nDescrição: {aluno.description}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[dono.user.email],  # E-mail do dono da oportunidade
    )

    # Enviar e-mail para o aluno confirmando a inscrição
    send_mail(
        subject=f"Inscrição realizada com sucesso: {opportunity.title}",
        message=f"Parabéns, {aluno.full_name}!\nVocê se inscreveu com sucesso na oportunidade {opportunity.title}.\n\nDetalhes da oportunidade:\nTítulo: {opportunity.title}\nDescrição: {opportunity.description}\nDono da Oportunidade: {dono.full_name}\nE-mail do Dono: {dono.user.email}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[aluno.user.email],  # E-mail do aluno
    )

    # Mensagem de sucesso para o aluno
    messages.success(request, "Inscrição realizada com sucesso! Você recebeu um e-mail de confirmação.")

    return redirect('opportunity_detail', pk=pk)

    
@login_required
def unsubscribe_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.subscribers.remove(request.user)  # Remove o usuário da lista de inscritos
    return redirect('opportunity_detail', pk=pk)

def opportunity_list(request):
    query = request.GET.get('q')  # Obtém o termo de busca da URL
    if query:
        opportunities = Opportunity.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        opportunities = Opportunity.objects.all()

    # Filtra oportunidades visíveis para outros usuários
    if request.user.is_authenticated:
        opportunities = opportunities.filter(
            Q(is_active=True) | Q(posted_by=request.user)
        )
    else:
        opportunities = opportunities.filter(is_active=True)

    return render(request, 'oportunidades/opportunity_list.html', {'opportunities': opportunities, 'query': query})

# def opportunity_detail(request, pk):
#     opportunity = get_object_or_404(Opportunity, pk=pk)
#     return render(request, 'oportunidades/opportunity_detail.html', {'opportunity': opportunity})

@login_required
def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Criar um novo comentário
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user  # Atribuir o usuário atual como autor do comentário
            new_comment.opportunity = opportunity  # Associar o comentário à oportunidade
            parent_comment_id = request.POST.get('parent_comment')
            if parent_comment_id:
                parent_comment = get_object_or_404(Comment, id=parent_comment_id)
                new_comment.parent_comment = parent_comment  # Associar o comentário pai se houver
            new_comment.save()
            return redirect('opportunity_detail', pk=opportunity.pk)
    else:
        comment_form = CommentForm()

    # Buscar os comentários da oportunidade
    comments = opportunity.comments.filter(parent_comment__isnull=True)  # Comentários principais (não respostas)

    # Somente o criador da oportunidade pode ver os inscritos
    inscritos = opportunity.subscribers.all() if opportunity.posted_by == request.user else None

    return render(request, 'oportunidades/opportunity_detail.html', {
        'opportunity': opportunity,
        'comments': comments,
        'comment_form': comment_form,
        'inscritos': inscritos,  # Adiciona inscritos ao contexto
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Cria o usuário com senha criptografada
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Cria o perfil do usuário
            profile = Profile.objects.create(
                user=user,
                full_name = form.cleaned_data.get('full_name'),
                description=form.cleaned_data.get('description'),
                profile_pic=form.cleaned_data.get('profile_pic'),
                user_type=form.cleaned_data['user_type']
            )

            # Adiciona o usuário ao grupo com base no tipo selecionado
            user_type = form.cleaned_data['user_type']
            if user_type == 'aluno':
                group = Group.objects.get(name='Aluno')
            elif user_type == 'professor':
                group = Group.objects.get(name='Professor')
            elif user_type == 'laboratorio':
                group = Group.objects.get(name='Laboratório')
            elif user_type == 'grupo_extensao':
                group = Group.objects.get(name='Grupo de Extensão')

            # Adiciona o usuário ao grupo correspondente
            user.groups.add(group)

            # Realiza login após o registro
            login(request, user)

            # Redireciona para a página inicial ou outra página de sua escolha
            return redirect('home')  # Substitua 'home' pelo nome da sua URL inicial
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    return render(request, 'oportunidades/home.html')

@login_required
def user_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Oportunidades criadas pelo usuário
    created_opportunities = Opportunity.objects.filter(posted_by=request.user)
    
    # Oportunidades nas quais o usuário está inscrito
    subscribed_opportunities = request.user.subscribed_opportunities.all()

    return render(request, 'oportunidades/user_profile.html', {
        'profile': profile,
        'opportunities': created_opportunities,
        'subscribed_opportunities': subscribed_opportunities,
    })

# Aqui você pode customizar a LoginView, se necessário.
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'


@method_decorator(login_required, name='dispatch')
class opportunity_edit_updateView(View):

    def get(self, request, pk):
        opportunity = get_object_or_404(Opportunity, pk=pk)
        form = PostForm(
            initial={
                'title': opportunity.title,
                'description' : opportunity.description,
                'category': opportunity.category,
                'is_active': opportunity.is_active
            })
        context = {'opportunity': opportunity, 'form':form}
        return render(request, 'oportunidades/opportunity_edit.html', context)
    def post(self,request,pk):
        opportunity = get_object_or_404(Opportunity, pk=pk)
        form = PostForm(request.POST)
        if form.is_valid():
            opportunity.title = form.cleaned_data['title']
            opportunity.description = form.cleaned_data['description']
            opportunity.category = form.cleaned_data['category']
            opportunity.is_active = form.cleaned_data['is_active']
            opportunity.save()
            return HttpResponseRedirect(reverse('opportunity_detail', args = (pk, )))


@login_required
def create_opportunity(request):
    # Verificar se o usuário tem permissão para criar oportunidades
    if request.user.profile.user_type not in ['laboratorio', 'grupo_extensao', 'professor']:
        messages.error(request, "Você não tem permissão para criar oportunidades.")
        return redirect('home')  # Redireciona para a página inicial ou outra página desejada

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.posted_by = request.user
            opportunity.save()
            messages.success(request, "Oportunidade criada com sucesso!")
            return redirect('opportunity_list')  # Redireciona para a lista de oportunidades ou outra página
    else:
        form = PostForm()

    return render(request, 'oportunidades/create_opportunity.html', {'form': form})


def edit_user_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        opportunities = Opportunity.objects.filter(posted_by=request.user)
        form = ProfileEditForm(request.POST,request.FILES)
        if form.is_valid():
            profile.description = form.cleaned_data['description']
            profile.profile_pic = form.cleaned_data['profile_pic']
            profile.save()
            return render(request, 'oportunidades/user_profile.html', {
        'profile': profile,
        'opportunities': opportunities,
    })
    else:
        form = ProfileEditForm(
            initial = {
                'description' : profile.description,
                'profile_pic' : profile.profile_pic
            })
    return render(request, 'oportunidades/user_profile_edit.html', {'form': form, 'profile': profile})

def profile_list(request):
    query = request.GET.get('q', '')  # Obtém o termo de busca da query string
    profiles = Profile.objects.filter(
        Q(user__username__icontains=query) | Q(user__email__icontains=query)
    ) if query else Profile.objects.all()
    return render(request, 'oportunidades/profile_list.html', {'profiles': profiles})

def profile_detail(request, pk):
    profile = get_object_or_404(Profile, user__id=pk)
    created_opportunities = Opportunity.objects.filter(posted_by=profile.user)
    subscribed_opportunities = Opportunity.objects.filter(subscribers=profile.user)
    
    return render(request, 'oportunidades/profile_detail.html', {
        'profile': profile,
        'created_opportunities': created_opportunities,
        'subscribed_opportunities': subscribed_opportunities,
    })
