from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.users.api.resources import UserViewSet, LoginFincasApi
from apps.files.api.resources import EscanDirectory, CreateNewFolder, DeleteFolder

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='User')

urlpatterns = [
    path('login', LoginFincasApi.as_view()),
    path('scanDirectory/', EscanDirectory.as_view()),
    path('createNewFolder/', CreateNewFolder.as_view()),
    path('deleteFolder/', DeleteFolder.as_view()),
]

urlpatterns += router.urls