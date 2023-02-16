from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import PerevalAdded
from .serializers import *


# Create your views here.

class PassageAPIView(viewsets.ViewSet):

    @staticmethod
    def serializer_error_response(errors, param='id'):
        message = ''
        for k, v in errors.items():
            message += f'{k}: {str(*v)}'
        if param == 'state':
            return Response({'message': message, 'state': 0}, status=400)
        else:
            return Response({'message': message, 'id': None}, status=400)


    def post(self, request):
        try:
            data = request.data
            def create_dependence(serializer):
                if serializer.is_valid():
                    return serializer.save()
                else:
                    return self.serializer_error_response(serializer.errors)

            try:
                user = Users.objects.get(email=data['user']['email'])
                user_serializer = UsersSerializer(user, data=data['user'])
            except:
                user_serializer = UsersSerializer(data=data['user'])

            try:
                images = data['images']
                data.pop('images')
            except:
                images = []


            serializer = PerevalAddedSerializer(data=data)
            if serializer.is_valid():
                try:
                    data.pop('user')
                    pereval_new = PerevalAdded.objects.create(
                        user=create_dependence(user_serializer),
                        coords=create_dependence(CoordsSerializer(data=data.pop('coords'))),
                        levels=create_dependence(LevelSerializer(data=data.pop('level'))),
                        **data)
                except Exception as e:
                    return Response({'message': str(e), 'id': None}, status=400)
            else:
                return self.serializer_error_response(serializer.errors)

            for image in images:
                image['pereval'] = pereval_new.id
                create_dependence(ImagesSerializer(data=image))

            return Response({'message': 'Success', 'id': pereval_new.id}, status=200)

        except Exception as e:
            return Response({'message': str(e), 'id': None}, status=500)

