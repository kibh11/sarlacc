from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def data_input(request):
    return HttpResponse('<p>there will be pepsin digestion data here someday<p>')