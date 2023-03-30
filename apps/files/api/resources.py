import os
import shutil
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class EscanDirectory(APIView):
    """Class para escanear un directorio completo"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # serializer_class = SaiSerializer

    def post(self, request):
        """Escanear un directorio
        :param request: (path)
        :return: Dirs y Files
        """
        actual_dir = request.data["actual_dir"]
        finca = request.data['finca']
        parent = ''

        list_dir = []
        if len(actual_dir.get("parents")) == 0:
            obj = { "text" : str(finca), "id" : str(finca), "children" : True, "state": {"selected": True} }
            list_dir.append(obj)
            print('Nodo: ', list_dir)
            return Response(list_dir, status=status.HTTP_200_OK) # Creo la ruta Raiz
        else:
            parents = actual_dir.get("parents")
            parents.remove('#')
            parents.reverse()
            for folder in parents:
                parentSplit = folder.split('_')
                parent += parentSplit[0] + '/'
                print('RELATIVA PARENT: ', parent)
            parent += str(actual_dir.get('text'))

        base_dir = settings.MI_DIRECTORIO + '/' + parent
        
        path = os.scandir(base_dir)
        for element in path:
            obj = {}
            obj['id'] = str(element.name) + '_' + str(element.inode())
            obj['text'] = str(element.name)
            if element.is_dir():
                obj['children'] = True
                obj['type'] = "folder"
            else:
                obj['children'] = False
                obj['type'] = "file"
                obj['a_attr'] = {"href": settings.RUTA_DOWNLOAD + '/' + parent + '/' + str(element.name)}

            list_dir.append(obj)
        
        print('Nodos: ', list_dir)
        return Response(list_dir, status=status.HTTP_200_OK)


class CreateNewFolder(APIView):
    """Class para crear una nueva carpeta"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # serializer_class = SaiSerializer

    def post(self, request):
        """Crea una nueva carpeta
        :param request: (path)
        :return: name Folder
        """
        nameNewFolder = request.data["nameNewFolder"]
        node = request.data['node']
        try:
            if nameNewFolder and node:
                relativePath = ''
                base_dir = settings.MI_DIRECTORIO
                idNode = node.get("id")
                parents = node.get("parents")
                parents.remove('#')
                parents.reverse()
                for parent in parents:
                    relativePath += parent.split('_')[0] + '/'
                
                relativePath += idNode.split('_')[0]+'/'
                path = os.path.join(base_dir, relativePath+nameNewFolder)
                os.mkdir(path) #<- Creamos la carpeta

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except FileExistsError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'El directorio ya existe', 'error': str(error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)
        

class DeleteFolder(APIView):
    """Class para eliminar una carpeta"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # serializer_class = SaiSerializer

    def post(self, request):
        """Crea una nueva carpeta
        :param request: (path)
        :return: name Folder
        """
        node = request.data['node']
        try:
            if node:
                relativePath = ''
                base_dir = settings.MI_DIRECTORIO
                nodeText = node.get("text")
                parents = node.get("parents")
                parents.remove('#')
                parents.reverse()
                for parent in parents:
                    relativePath += parent.split('_')[0] + '/'
                
                relativePath += nodeText+'/'
                path = os.path.join(base_dir, relativePath)
                shutil.rmtree(path) #<- Eliminamos toda la carpeta incluyendo archivos
            
            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)