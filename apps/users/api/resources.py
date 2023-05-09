import sys
import os
import shutil
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout

from apps.users.api.serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """Clase que contiene los metodos genericos para la vista de los User (Finca)
    ['get', 'post', 'put', 'delete']"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_queryset(self, pk=None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.all().order_by('nombre_finca')
        return self.get_serializer().Meta.model.objects.filter(id=pk).first()
    
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.create_user(nombre_finca=request.data['nameFinca'],
                                            cod_finca=request.data['codeFinca'],
                                            username=request.data['usernameFinca'],
                                            password=request.data['passwordFinca'])

            cod_finca = request.data['codeFinca']
            base_dir = settings.MI_DIRECTORIO
            path = os.path.join(base_dir, cod_finca + '/tablon de anuncios')
            os.makedirs(path, exist_ok=True)  # <- Creamos la carpeta

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_201_CREATED)
        except Exception:
            e = sys.exc_info()[1]
            if e.args[0] == 1062:
                fieldError = e.args[1].split('\'')
                respJson = [{'status': 'ERROR', 'message': 'El campo: <b>' + fieldError[1]+'</b> ya existe en el sistema!', 'error':''}]
                return Response(respJson, status=status.HTTP_226_IM_USED)
            else:
                return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)
            
    def update(self, request, pk=None, *args, **kwargs):
        if self.get_queryset(pk):
            user_serializer = self.serializer_class(self.get_queryset(pk), data=request.data)
            if user_serializer.is_valid():
                updateUser = User(
                    id=user_serializer.initial_data['id'],
                    username=user_serializer.initial_data['username'],
                    first_name=user_serializer.initial_data['first_name'],
                    email=user_serializer.initial_data['email'],
                    password=make_password(user_serializer.initial_data['password']),
                    is_superuser=user_serializer.initial_data['is_superuser'],
                    cod_finca=user_serializer.initial_data['cod_finca'],
                    nombre_finca=user_serializer.initial_data['nombre_finca'])
                updateUser.save()
                return Response("Updated-OK", status=status.HTTP_200_OK)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, pk=None, *args, **kwargs):
        user = self.get_queryset().filter(cod_finca=pk).first()
        if user:
            user.delete()
            base_dir = settings.MI_DIRECTORIO
            path = os.path.join(base_dir, pk)
            shutil.rmtree(path)# <- Eliminamos toda la FINCA incluyendo archivos
            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        
        respJson = [{'status': 'ERROR', 'message': 'No existe la finca para eliminarla', 'error':'No se pudo eliminar la finca'}]
        return Response(respJson, status=status.HTTP_400_BAD_REQUEST)
    

class LoginFincasApi(APIView):
    """ Class para autenticar un usuario via local y crear un login session """

    authentication_classes = ()

    def post(self, request):
        """Loguearse en la API y retornar un Token de Sesion
        :param request: (username, password)
        :return: Token sessión
        """
        user_obj = authenticate(username=request.data['username'],
                                password=request.data['password'])
        if user_obj:
            auth_login(request, user_obj)
            token, _ = Token.objects.get_or_create(user=user_obj)

            data = {
                'id': user_obj.id,
                'username': user_obj.username,
                'cod_finca': user_obj.cod_finca,
                'nombre_finca': user_obj.nombre_finca,
                'is_superuser': user_obj.is_superuser,
                'token': token.key
            }

            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'No Authenticate': 'El usuario no existe'}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)


class UpdatePassword(APIView):
    """ Class para actualizar la contraseña de una finca """

    authentication_classes = ()

    def post(self, request):
        """Actualizar contraseña de finca
        :param request: (finca, password)
        :return: OK
        """

        try:
            user = request.data['codeFinca']
            passwd = request.data['password']
            option = request.data['option']

            if option == '-1':
                u= User.objects.get(cod_finca=option)
            else:
                u= User.objects.get(cod_finca=user)
                
            u.set_password(passwd)
            u.save()
            
            respJson = [{'status': 'OK', 'message': 'Contraseña Actualizada'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except:
            respJson = [{'status': 'ERROR', 'message': 'Error actualizando contraseña'}]
            return Response(respJson, status=status.HTTP_400_BAD_REQUEST)


            