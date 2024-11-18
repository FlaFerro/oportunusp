from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity
from django.contrib.auth.decorators import permission_required
from .forms import UserRegistrationForm, PostForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views import  View
from django.http import HttpResponseRedirect
from django.urls import reverse

def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'oportunidades/opportunity_list.html', {'opportunities': opportunities})

def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    return render(request, 'oportunidades/opportunity_detail.html', {'opportunity': opportunity})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redireciona para a página de login
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    return render(request, 'oportunidades/home.html')

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