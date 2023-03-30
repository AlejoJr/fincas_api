import sys

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
            return self.get_serializer().Meta.model.objects.all()
        return self.get_serializer().Meta.model.objects.filter(id=pk).first()
    
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.create_user(username=request.data['username'],
                                            first_name=request.data['first_name'],
                                            email=request.data['email'],
                                            password=request.data['password'],
                                            is_superuser=request.data['is_superuser'],
                                            cod_finca=request.data['cod_finca'],
                                            nombre_finca=request.data['nombre_finca'])
            return Response('Created-OK', status=status.HTTP_201_CREATED)
        except Exception:
            e = sys.exc_info()[1]
            if e.args[0] == 1062:
                return Response(e.args[0], status=status.HTTP_226_IM_USED)
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
        user = self.get_queryset().filter(id=pk).first()
        if user:
            user.delete()
            return Response({'message': 'Usuario eliminado correctamente!'}, status=status.HTTP_200_OK)
        return Response({'error': 'No existe el usuario para eliminarlo'}, status=status.HTTP_400_BAD_REQUEST)
    

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

