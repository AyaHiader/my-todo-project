# test/serializers.py
from rest_framework import serializers
from .models import Todo

# -------------------
# Todo Serializer
# -------------------
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'status']

# -------------------
# Register Request Serializer (for Swagger input)
# -------------------
class RegisterRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# -------------------
# Register Response Serializer (for Swagger output)
# -------------------
class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    refresh = serializers.CharField()
    access = serializers.CharField()



