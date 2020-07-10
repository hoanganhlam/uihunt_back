from apps.ui import models
from rest_framework import serializers
from apps.media.api.serializers import UserSerializer


class UserTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserTemp
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        return super(UserTempSerializer, self).to_representation(instance)


class UISerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UI
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        return super(UISerializer, self).to_representation(instance)


class UITagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UITag
        fields = '__all__'
        extra_kwargs = {}

    def to_representation(self, instance):
        return super(UITagSerializer, self).to_representation(instance)


class CommentSerializer(serializers.ModelSerializer):
    has_child = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ['id', 'user', 'content', 'created', 'parent', 'has_child', 'ui']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_has_child(self, instance):
        return instance.children.count() > 0

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(CommentSerializer, self).to_representation(instance)
