from ninja import NinjaAPI, Router
from .models import User, Todo
from .serializers import RegisterSchema, LoginSchema, TodoSchema, TodoUpdateSchema
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from django.shortcuts import get_object_or_404
from typing import List, Dict
from django.contrib.auth import get_user_model

api = NinjaAPI()
router = Router()
User = get_user_model()

# ---------------- Helper Functions ----------------
def get_user_from_token(token: str):
    try:
        untoken = UntypedToken(token)  # يتحقق من صلاحية الـ JWT
        user_id = untoken["user_id"]
        return User.objects.get(id=user_id)
    except Exception as e:
        print("JWT error:", e)
        return None

def auth_required(request):
    """
    🔹 يتحقق من Authorization header أولًا
    🔹 إذا غير موجود، يتحقق من access_token cookie
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
        token = request.COOKIES.get("access_token")

    if not token:
        return None

    return get_user_from_token(token)

# ---------------- Register ----------------
@router.post("/register", response={201: Dict, 400: Dict})
def register(request, payload: RegisterSchema):
    if User.objects.filter(email=payload.email).exists():
        return 400, {"error": "User already exists"}
    User.objects.create_user(email=payload.email, password=payload.password)
    return 201, {"message": "User created"}

# ---------------- Login ----------------
@router.post("/login", response={200: Dict, 400: Dict})
def login(request, payload: LoginSchema):
    try:
        user = User.objects.get(email=payload.email)
        if not user.check_password(payload.password):
            return 400, {"error": "Invalid credentials"}
    except User.DoesNotExist:
        return 400, {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response = api.create_response(
        request,
        {"message": "Login successful"},
        status=200
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,   # لا يمكن قراءتها من JS
        secure=False,    # ضع True إذا تستخدم HTTPS
        samesite="Lax",
        path="/",
        max_age=60*60
    )
    return response

# ---------------- Todos ----------------
@router.get("/todos", response={200: List[TodoSchema], 401: Dict})
def list_todos(request):
    user = auth_required(request)
    if not user:
        return 401, {"error": "Authentication required"}
    return 200, Todo.objects.filter(user=user)

@router.post("/todos", response={201: TodoSchema, 401: Dict})
def create_todo(request, payload: TodoSchema):
    user = auth_required(request)
    if not user:
        return 401, {"error": "Authentication required"}
    todo = Todo.objects.create(user=user, **payload.dict())
    return 201, todo

@router.put("/todos/{todo_id}", response={200: TodoSchema, 401: Dict})
def update_todo(request, todo_id: int, payload: TodoUpdateSchema):
    user = auth_required(request)
    if not user:
        return 401, {"error": "Authentication required"}
    todo = get_object_or_404(Todo, id=todo_id, user=user)
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(todo, k, v)
    todo.save()
    return 200, todo

@router.delete("/todos/{todo_id}", response={200: Dict, 401: Dict})
def delete_todo(request, todo_id: int):
    user = auth_required(request)
    if not user:
        return 401, {"error": "Authentication required"}
    todo = get_object_or_404(Todo, id=todo_id, user=user)
    todo.delete()
    return 200, {"message": "Todo deleted"}

@router.delete("/todos/reset", response={200: Dict, 401: Dict, 403: Dict})
def reset_todos(request):
    user = auth_required(request)
    if not user:
        return 401, {"error": "Authentication required"}
    if user.role != "admin":
        return 403, {"error": "Admin access required"}
    Todo.objects.all().delete()
    return 200, {"message": "All TODOs deleted"}

# ---------------- Register Router ----------------
api.add_router("/api/", router)
