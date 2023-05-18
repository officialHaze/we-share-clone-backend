from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from files.models import ShortURL
import os


def get_long_url(id):
    #check the db if instance exists with the given id
    qs = ShortURL.objects.filter(id=id)
    if qs:
        instance = qs[0] #get the instance
        instance.visited += 1 #increment visitors by 1
        instance.save()
        long_url = instance.long_url
        return long_url
    else:
        raise Exception("instance does not exist")


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def redirect_to_long_url(req, *args, **kwargs):
    id = kwargs.get('id')
    try:
        long_url = get_long_url(id)
        return redirect(long_url)
    except:
        redirect_url = os.environ.get('BASE_URL')
        return redirect(f'{redirect_url}/404')


@api_view(["GET"])
def connection_stream(req, *args, **kwargs):
    return redirect('https://seol-share.vercel.app')
