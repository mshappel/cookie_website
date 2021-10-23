from django.shortcuts import render


def index(request):
    """The home page for Cookie Booths"""
    return render(request, 'cookie_booths/index.html')
