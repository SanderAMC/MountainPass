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


    @swagger_auto_schema(metods=['post'], request_body=PassAddedSerializer)
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


    @swagger_auto_schema(metods=['get'], manual_parameters=[
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


    @swagger_auto_schema(metods=['get'], request_body=PassAddedSerializer)
    def get_one(self, request, **kwargs):
        try:
            passage = PerevalAdded.objects.get(pk=kwargs['pk'])
            data = PassAddedSerializer(passage).data
            return Response(data, status=200)
        except:
            return Response({'message': "There's no such record", 'id': None}, status=400)

    @swagger_auto_schema(metods=['patch'], request_body=PassAddedSerializer)
    def edit_one(self, reguest, **kwargs):
        try:
            passage = PerevalAdded.objects.get(pk=kwargs['pk'])
            if passage.status == 'new':
                data = reguest.data
                data.pop('user')
                Images.objects.filter(pereval_id=passage.id).delete()
                images = data.pop('images')
                serializers = []
                serializers.append(CoordsSerializer(Coords.objects.get(id=passage.coords_id), data=data.pop('coords')))
                serializers.append(LevelSerializer(Level.objects.get(id=passage.level_id), data=data.pop('levels')))
                serializers.append((PassAddedSerializer(passage, data=data)))
                for image in images:
                    image['pereval'] = passage.id
                    serializers.append(ImagesSerializer(data=image))
                for serializer in serializers:
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return self.serializer_error_response(serializer.errors, 'state')
                return Response({'message': None, 'state': 1}, status=200)
            else:
                return Response({'message': "It's not a NEW status of the record.", 'state': 0}, status=400)
        except:
            return Response({'message': "There's no such record", 'state': 0}, status=400)

