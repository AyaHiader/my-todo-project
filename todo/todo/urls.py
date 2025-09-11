from django.contrib import admin
from django.urls import path
from test.views import (
    RegisterAPIView,
    LoginAPIView,
    TodoListCreateAPIView,   
    TodoUpdateDeleteAPIView 
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/login/', LoginAPIView.as_view(), name='login'),

    path('api/todos/', TodoListCreateAPIView.as_view(), name='todos'),             
    path('api/todos/<int:todo_id>/', TodoUpdateDeleteAPIView.as_view(), name='todo_detail'), 
]
