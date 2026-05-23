from django.urls import path
from .views import FolderListCreateView, FolderDetailView, FolderValidateView


urlpatterns = [
    path('folders/', FolderListCreateView.as_view(), name='folder-list-create'),
    path('folders/<int:pk>/', FolderDetailView.as_view(), name='folder-detail'),
    path('folders/<int:pk>/validate/', FolderValidateView.as_view(), name='folder-validate'),
]