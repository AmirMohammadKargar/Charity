from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'phone', 'address',
         'gender', 'age', 'description', 'first_name', 'last_name', 'email'
        )
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            address=validated_data['address'],
            gender=validated_data['gender'],
            age=validated_data['age'],
            description=validated_data['description'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    