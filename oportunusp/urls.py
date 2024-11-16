from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oportunidades/', include('oportunidades.urls')),
    path('', include('oportunidades.urls')),
]
