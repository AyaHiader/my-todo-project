from django.urls import path
from test.views import RegisterAPIView,LoginAPIView,TodoListCreateAPIView,TodoUpdateDeleteAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("todos/", TodoListCreateAPIView.as_view(), name="todos"),             # GET + POST
    path("todos/<int:todo_id>/", TodoUpdateDeleteAPIView.as_view(), name="todo_detail"),  # PUT + DELETE
]