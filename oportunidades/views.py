from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity
from django.contrib.auth.decorators import permission_required
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView

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