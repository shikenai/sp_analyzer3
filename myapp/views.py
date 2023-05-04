from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from myapp.management.commands import main
import datetime as dt


def analyze(request):
    main.analyze()
    return JsonResponse({'ana': 'lyze'})

def get_new_trades(request):
    main.get_new_trades()
    return JsonResponse({'new': 'trades'})


def register_brands(request):
    main.register_brands_from_tse()
    return JsonResponse({'user': 'taro'})


def register_trades(request):
    t = dt.datetime.now()
    main.register_trades()
    elapsed_time = dt.datetime.now() - t
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    print(f"{minutes:.0f}分{seconds:.0f}秒")
    return JsonResponse({'kind': 'trade'})


def home(request):
    return redirect("http://localhost:5173/")
