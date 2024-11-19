from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity, Profile, Comment
from django.contrib.auth.decorators import permission_required, login_required
from .forms import UserRegistrationForm, CommentForm, PostForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views import  View
from django.urls import reverse


def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'oportunidades/opportunity_list.html', {'opportunities': opportunities})

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
