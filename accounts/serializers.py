from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Incorrect email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User is disabled.")

        return {"user": user}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "password",
        )
        extra_kwargs = {
            "uuid": {"required": False, "read_only": True},
            "password": {"required": True, "write_only": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(
            validated_data.pop("email"),
            validated_data.pop("password"),
            **validated_data
        )
