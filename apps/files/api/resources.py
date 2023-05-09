import os
import shutil
import json
from django.conf import settings
from django.views.static import serve
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from rest_framework import generics
from django.http import HttpResponse
from wsgiref.util import FileWrapper

import smtplib
from email.message import EmailMessage

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
            obj = {"text": str(finca), "id": str(
                finca), "children": True, "state": {"selected": True}}
            list_dir.append(obj)
            print('Nodo: ', list_dir)
            # Creo la ruta Raiz
            return Response(list_dir, status=status.HTTP_200_OK)
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
            saveObj = True
            obj = {}
            obj['id'] = str(element.name) + '_' + str(element.inode())
            obj['text'] = str(element.name)
            if element.is_dir():
                obj['children'] = True
                obj['type'] = "folder"
            else:
                obj['children'] = False
                obj['type'] = "file"
                if element.name.startswith('.'):
                    if request.user.is_superuser == True:
                        obj['a_attr'] = {"href": settings.RUTA_DOWNLOAD + '/' + parent + '/' + str(element.name)}
                    else:
                        saveObj = False
                else:
                    obj['a_attr'] = {"href": settings.RUTA_DOWNLOAD + '/' + parent + '/' + str(element.name)}

            if saveObj:
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
                os.mkdir(path)  # <- Creamos la carpeta

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except FileExistsError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'El directorio ya existe', 'error': str(
                error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(
                error).split(':')[0]}]
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
                
                shutil.rmtree(path)# <- Eliminamos toda la carpeta incluyendo archivos

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(
                error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)


class UploadFile(APIView):
    """API Encargada de subir un archivo al servidor"""

    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        try:
            file_obj = request.FILES['document']
            node = json.loads(request.data['node'])
            finca = request.data['finca']
            base_dir = settings.MI_DIRECTORIO
            relativePath = ''
            
            nodeText = node.get("text")
            parents = node.get("parents")
            parents.remove('#')
            parents.reverse()

            for parent in parents:
                relativePath += parent.split('_')[0] + '/'

            relativePath += nodeText+'/'
            path = os.path.join(base_dir, relativePath)

            if request.user.is_superuser == False:
                destination = open(path + '.'+file_obj.name, 'wb+') #<- Si No es administrador, se guarda como archivo oculto
                email = SMTP()
                email.conecta_servidor_smtp()
                email.manda_mensaje('alejandrokaicedo960@gmail.com', 
                                    'Revisar Documento',
                                    'animxjr@gmail.com',
                                    'Existe un nuevo documento en el tablon de anuncios pendiente por revisar \
                                    <br> <b>Finca: </b>' + str(finca) + '<br> <b>Archivo: </b>' + str(file_obj.name))
                email.desconecta_servidor_smtp()
            else:
                destination = open(path + file_obj.name, 'wb+')

            for chunk in file_obj.chunks():
                destination.write(chunk)
            destination.close()

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except IOError as error:
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción IOError', 'error': str(
                error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)


class DeleteFile(APIView):
    """Class para eliminar un archivo"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Elimina un archivo de la carpeta
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

                relativePath += nodeText
                path = os.path.join(base_dir, relativePath)
                os.remove(path) #<- Eliminamos el archivo
                
            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(
                error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)
    

class ApproveFile(APIView):
    """Class para aprobar un archivo"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Aprobar un archivo
        :param request: (path)
        """
        node = request.data['node']
        try:
            if node:
                relativePath = ''
                base_dir = settings.MI_DIRECTORIO
                nodeText = node.get("text")
                newNameFile = nodeText[1:]
                parents = node.get("parents")
                parents.remove('#')
                parents.reverse()
                for parent in parents:
                    relativePath += parent.split('_')[0] + '/'

                newRelativePath = relativePath + newNameFile
                relativePath += nodeText

                path = os.path.join(base_dir, relativePath)
                newPath = os.path.join(base_dir, newRelativePath)

                os.rename(path, newPath) #<- Renombramos el archivo

            respJson = [{'status': 'OK', 'message': 'Created'}]
            return Response(respJson, status=status.HTTP_200_OK)
        except OSError as error:
            print(type(error))
            respJson = [{'status': 'ERROR', 'message': 'Ocurrió una excepción OSError', 'error': str(
                error).split(':')[0]}]
            return Response(respJson, status=status.HTTP_403_FORBIDDEN)

class FileDownloadListAPIView(generics.ListAPIView):
    """Class para descargar un archivo"""

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, path, nameFile, format=None):
        base_dir = settings.MI_DIRECTORIO
        pathFile = base_dir + path
        print('Archivo a descargar: ', pathFile)
        document = open(pathFile, 'rb')
        response = HttpResponse(FileWrapper(document), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nameFile
        return response
    

class SMTP:
     db = None
     cursor = None

     def __init__(self):
         pass

     def conecta_servidor_smtp(self):
         self.smtp = smtplib.SMTP(host='smtp.upv.es', local_hostname='gestion.dsic.upv.es')

     def desconecta_servidor_smtp(self):
         self.smtp.quit()

     def manda_mensaje(self, de, asunto, a, texto ):
         mensaje = EmailMessage()
         mensaje['Subject'] = asunto
         mensaje['From'] = de
         mandar_a = [a]
         mensaje['To'] = ','.join(mandar_a)
         mensaje.set_content(texto, subtype="html")
         self.smtp.send_message(mensaje)