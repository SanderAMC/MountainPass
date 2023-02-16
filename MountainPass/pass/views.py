from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from rest_framework import viewsets
from rest_framework.response import Response
from .models import PerevalAdded
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Create your views here.
def reverse_to_submit(request):
    return redirect('submitData')

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


    def create_dependence(self, serializer):
        if serializer.is_valid():
            return serializer.save()
        else:
            return self.serializer_error_response(serializer.errors)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('user_email', openapi.IN_QUERY, description="user e-mail", type=openapi.TYPE_STRING)])
    def get_records_by_user(self, request, **kwargs):
        try:
            user = Users.objects.get(email=request.GET['user_email'])
            passages = PerevalAdded.objects.filter(user=user)
            data = PassAddedSerializer(passages, many=True).data
            return Response(data, status=200)
        except:
            # passages = {}
            return Response({'message': 'No records found'}, status=200)


    def post(self, request):
        try:
            data = request.data
            if not data:
                return Response({'message': 'Empty request', 'id': None}, status=400)
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

            serializer = PassAddedSerializer(data=data)
            if serializer.is_valid():
                try:
                    data.pop('user')
                    pereval_new = PerevalAdded.objects.create(
                        user=self.create_dependence(user_serializer),
                        coords=self.create_dependence(CoordsSerializer(data=data.pop('coords'))),
                        levels=self.create_dependence(LevelSerializer(data=data.pop('level'))),
                        **data)
                except Exception as e:
                    return Response({'message': str(e), 'id': None}, status=400)
            else:
                return self.serializer_error_response(serializer.errors)

            for image in images:
                image['pereval'] = pereval_new.id
                self.create_dependence(ImagesSerializer(data=image))

            return Response({'message': 'Success', 'id': pereval_new.id}, status=200)

        except Exception as e:
            return Response({'message': str(e), 'id': None}, status=500)

