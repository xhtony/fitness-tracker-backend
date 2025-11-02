from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityListCreateView.as_view(), name='activity-list-create'),
    path('<int:pk>/', views.ActivityDetailView.as_view(), name='activity-detail'),
    path('stats/', views.activity_stats, name='activity-stats'),
    path('bulk-update/', views.bulk_update_status, name='bulk-update-status'),
    path('recent/', views.recent_activities, name='recent-activities'),
]


