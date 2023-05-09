from django.urls import path, re_path

from rest_framework.routers import SimpleRouter

from apps.users.api.resources import UserViewSet, LoginFincasApi, UpdatePassword
from apps.files.api.resources import EscanDirectory, CreateNewFolder, DeleteFolder, \
                                     UploadFile, DeleteFile, FileDownloadListAPIView, ApproveFile
                                        

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='User')

urlpatterns = [
    path('login', LoginFincasApi.as_view()),
    path('scanDirectory/', EscanDirectory.as_view()),
    path('createNewFolder/', CreateNewFolder.as_view()),
    path('deleteFolder/', DeleteFolder.as_view()),
    path('uploadFile/', UploadFile.as_view()),
    path('deleteFile/', DeleteFile.as_view()),
    path('approveFile/', ApproveFile.as_view()),
    path('updatePassword/', UpdatePassword.as_view()),
    path('download/<path:path>/<str:nameFile>/',FileDownloadListAPIView.as_view())
]

urlpatterns += router.urls