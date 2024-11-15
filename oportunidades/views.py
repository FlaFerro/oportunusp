from django.shortcuts import render, get_object_or_404, redirect
from .models import Opportunity
from django.contrib.auth.decorators import permission_required

def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, 'oportunidades/opportunity_list.html', {'opportunities': opportunities})

def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    return render(request, 'oportunidades/opportunity_detail.html', {'opportunity': opportunity})

