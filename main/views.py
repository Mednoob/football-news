from django.shortcuts import render

def show_main(request):
    context = {
        "npm": "2406399081",
        "name": "Ahmad Yaqdhan",
        "class": "PBP A"
    }

    return render(request, "main.html", context)
