from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Activity, ActivityLog
from .serializers import ActivitySerializer, ActivityCreateSerializer, ActivityUpdateSerializer


class ActivityListCreateView(generics.ListCreateAPIView):
    """List all activities for the authenticated user or create a new activity"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'planned_date', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ActivityCreateSerializer
        return ActivitySerializer
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an activity"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ActivityUpdateSerializer
        return ActivitySerializer
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_stats(request):
    """Get activity statistics for the authenticated user"""
    user = request.user
    
    # Get current month activities
    from datetime import datetime, timedelta
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_activities = Activity.objects.filter(
        user=user,
        created_at__gte=start_of_month
    )
    
    # Calculate statistics
    total_activities = monthly_activities.count()
    completed_activities = monthly_activities.filter(status='completed').count()
    planned_activities = monthly_activities.filter(status='planned').count()
    in_progress_activities = monthly_activities.filter(status='in_progress').count()
    
    # Calculate totals
    total_calories_burned = monthly_activities.aggregate(
        total=Sum('calories_burned')
    )['total'] or 0
    
    total_calories_consumed = monthly_activities.aggregate(
        total=Sum('calories_consumed')
    )['total'] or 0
    
    total_steps = monthly_activities.aggregate(
        total=Sum('steps_count')
    )['total'] or 0
    
    total_duration = monthly_activities.aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0
    
    # Activities by type
    activities_by_type = {}
    for activity_type, _ in Activity.ACTIVITY_TYPES:
        count = monthly_activities.filter(activity_type=activity_type).count()
        if count > 0:
            activities_by_type[activity_type] = count
    
    return Response({
        'monthly_stats': {
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'planned_activities': planned_activities,
            'in_progress_activities': in_progress_activities,
            'completion_rate': round((completed_activities / total_activities * 100) if total_activities > 0 else 0, 2)
        },
        'totals': {
            'calories_burned': total_calories_burned,
            'calories_consumed': total_calories_consumed,
            'steps': total_steps,
            'duration_minutes': total_duration
        },
        'activities_by_type': activities_by_type
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_status(request):
    """Bulk update status for multiple activities"""
    activity_ids = request.data.get('activity_ids', [])
    new_status = request.data.get('status')
    
    if not activity_ids or not new_status:
        return Response(
            {'error': 'activity_ids and status are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_status not in [choice[0] for choice in Activity.STATUS_CHOICES]:
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update activities
    activities = Activity.objects.filter(
        id__in=activity_ids, 
        user=request.user
    )
    
    updated_count = 0
    for activity in activities:
        old_status = activity.status
        if old_status != new_status:
            ActivityLog.objects.create(
                activity=activity,
                old_status=old_status,
                new_status=new_status,
                notes=f"Bulk status update from {old_status} to {new_status}"
            )
            activity.status = new_status
            activity.save()
            updated_count += 1
    
    return Response({
        'message': f'Updated {updated_count} activities',
        'updated_count': updated_count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities(request):
    """Get recent activities for the authenticated user"""
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    activities = Activity.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:limit]
    
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)