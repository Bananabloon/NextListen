from django.http import HttpResponse


def homepage(request):
    return HttpResponse("Strona testowa. Docker sie wczytal. YPIEEEE")


def about(request):
    return HttpResponse("Strona about. Nie wiem jeszcze po co, przykladowa :D")
