from django.contrib import admin
from django.urls import path, include
from .views import PassageAPIView


urlpatterns = [
    path('submitData/', PassageAPIView.as_view({'post': 'post'})),
]

