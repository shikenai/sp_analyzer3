from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from myapp.management.commands import main


def register_brands(request):
    main.register_brands_from_tse()
    return JsonResponse({'user': 'taro'})


def register_trades(request):
    main.test()
    return JsonResponse({'kind': 'trade'})


def home(request):
    return redirect("http://localhost:5173/")
