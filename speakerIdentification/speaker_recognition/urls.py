from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('enroll/',csrf_exempt(views.enroll_view), name='enrolling'),
    path('identify/',csrf_exempt(views.identify_view), name='indentifying'),
    path('unroll/',csrf_exempt(views.unroll_view), name='unrolling'),
    path('createProfile/',csrf_exempt(views.createProfileView), name='creatingprofile')
]