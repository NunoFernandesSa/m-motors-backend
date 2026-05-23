from django.urls import path
from .views import FolderListCreateView, FolderDetailView, FolderValidateView


urlpatterns = [
    path('', FolderListCreateView.as_view(), name='folder-list-create'),
    path('<int:pk>/', FolderDetailView.as_view(), name='folder-detail'),
    path('<int:pk>/validate/', FolderValidateView.as_view(), name='folder-validate'),
]