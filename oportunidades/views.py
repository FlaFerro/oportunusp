from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity, Profile, Comment
from django.contrib.auth.decorators import permission_required, login_required
from .forms import UserRegistrationForm, CommentForm, PostForm, ProfileEditForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views import  View
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.db.models import Q

@login_required
def subscribe_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.subscribers.add(request.user)  # Adiciona o usuário à lista de inscritos
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
            Q(title__icontains=query) | Q(description__icontains=query)  # Busca no título e descrição
        )
    else:
        opportunities = Opportunity.objects.all()
    
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

    return render(request, 'oportunidades/opportunity_detail.html', {
        'opportunity': opportunity,
        'comments': comments,
        'comment_form': comment_form
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])  # Define a senha
                user.save()
                # Cria o perfil do usuário
                Profile.objects.create(
                    user=user,
                    description=form.cleaned_data.get('description'),
                    profile_pic=form.cleaned_data.get('profile_pic')
                )
            return redirect('login')  # Redireciona para a página de login
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    return render(request, 'oportunidades/home.html')

@login_required
def user_profile(request):
    profile = Profile.objects.get(user=request.user)
    opportunities = Opportunity.objects.filter(posted_by=request.user)
    return render(request, 'oportunidades/user_profile.html', {
        'profile': profile,
        'opportunities': opportunities,
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
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.posted_by = request.user  # Atribui o usuário logado como criador
            opportunity.save()
            return redirect('opportunity_list')  # Redireciona para a lista de oportunidades
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

