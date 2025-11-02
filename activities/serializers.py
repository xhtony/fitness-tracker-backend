from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Activity, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'old_status', 'new_status', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class ActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    logs = ActivityLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'user', 'title', 'description', 'activity_type', 'status',
            'planned_date', 'completed_date', 'duration_minutes', 'calories_burned',
            'calories_consumed', 'steps_count', 'notes', 'created_at', 'updated_at', 'logs'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Log status changes
        if 'status' in validated_data and instance.status != validated_data['status']:
            ActivityLog.objects.create(
                activity=instance,
                old_status=instance.status,
                new_status=validated_data['status'],
                notes=f"Status changed from {instance.status} to {validated_data['status']}"
            )
        return super().update(instance, validated_data)


class ActivityCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating activities"""
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'activity_type', 'status',
            'planned_date', 'duration_minutes', 'calories_burned',
            'calories_consumed', 'steps_count', 'notes'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ActivityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating activity status and other fields"""
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'status', 'duration_minutes',
            'calories_burned', 'calories_consumed', 'steps_count', 'notes'
        ]
    
    def update(self, instance, validated_data):
        # Log status changes
        if 'status' in validated_data and instance.status != validated_data['status']:
            ActivityLog.objects.create(
                activity=instance,
                old_status=instance.status,
                new_status=validated_data['status'],
                notes=f"Status changed from {instance.status} to {validated_data['status']}"
            )
        return super().update(instance, validated_data)


