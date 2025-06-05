from django.http import HttpResponse


def homepage(request):
    return HttpResponse("Strona testowa. Docker sie wczytal. YPIEEEE")
