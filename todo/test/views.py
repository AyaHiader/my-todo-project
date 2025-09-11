# test/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Todo
from .serializers import TodoSerializer, RegisterRequestSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.openapi import AutoSchema

# -------------------
# Custom Authentication to read JWT from cookie
# -------------------
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

# -------------------
# Register Endpoint
# -------------------
@extend_schema(
    request=RegisterRequestSerializer,
    responses={201: OpenApiResponse(description="User created successfully")}
)
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    schema = AutoSchema()

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if User.objects.filter(username=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=email, email=email, password=password)
        return Response({"message": "User created"}, status=status.HTTP_201_CREATED)


@extend_schema(
    request=RegisterRequestSerializer,
    responses={200: OpenApiResponse(description="Login successful with JWT tokens")}
)
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    schema = AutoSchema()

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({"message": "Login successful"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite='Lax',  # يمكن تغييره حسب حاجتك
            max_age=3600      # صلاحية التوكن بالثواني
        )
        return response

# -------------------
# Todos List + Create
# -------------------
@extend_schema(
    request=TodoSerializer,
    responses={200: OpenApiResponse(TodoSerializer)},
    description="List and Create todos"
)
class TodoListCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    schema = AutoSchema()

    def get(self, request):
        todos = Todo.objects.filter(user=request.user)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            todo = Todo.objects.create(user=request.user, **serializer.validated_data)
            return Response(TodoSerializer(todo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# -------------------
# Todo Update + Delete
# -------------------
@extend_schema(
    request=TodoSerializer,
    responses={200: OpenApiResponse(TodoSerializer)},
    description="Update or Delete a todo"
)
class TodoUpdateDeleteAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    schema = AutoSchema()

    def put(self, request, todo_id):
        try:
            todo = Todo.objects.get(id=todo_id, user=request.user)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, todo_id):
        try:
            todo = Todo.objects.get(id=todo_id, user=request.user)
            todo.delete()
            return Response({"message": "Todo deleted"})
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)