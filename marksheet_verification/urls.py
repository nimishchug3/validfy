from django.urls import path
from .views import upload_marksheet

urlpatterns = [
    path('upload/', upload_marksheet, name='upload_marksheet'),
]
