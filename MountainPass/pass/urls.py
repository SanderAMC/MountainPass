from django.contrib import admin
from django.urls import path, include
from .views import PassageAPIView, reverse_to_submit


urlpatterns = [
    path('', reverse_to_submit),
    path('submitData/', PassageAPIView.as_view({'post': 'post', }), name='submitData'),
]

