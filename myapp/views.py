from django.http import JsonResponse
from django.shortcuts import redirect
from myapp.management.commands import main
import datetime as dt
from django.views.decorators.csrf import csrf_exempt
import json
from myapp.models import Brands


def show(request):
    df_zero, df_p1, df_p2, df_m1, df_m2 = main.show()
    zero = df_zero.to_json(orient='records')
    p1 = df_p1.to_json(orient='records')
    p2 = df_p2.to_json(orient='records')
    m1 = df_m1.to_json(orient='records')
    m2 = df_m2.to_json(orient='records')
    return JsonResponse({'zero': zero,
                         'p1': p1,
                         'p2': p2,
                         'm1': m1,
                         'm2': m2})


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


@csrf_exempt
def get_states(request):
    if request.method == 'POST':
        datas = json.loads(request.body)
        brand_code = datas['brand_code']
        _brand = Brands.objects.filter(code=brand_code).first()
        print(_brand)
        params = {
            "is_holding": _brand.is_holding,
            "is_watching": _brand.is_watching
        }
        print(params)
        return JsonResponse(params)

@csrf_exempt
def post(request):
    print('now post')
    if request.method == 'POST':
        datas = json.loads(request.body)
        print(datas['brand_code'])
        print(datas['is_holding'])
    else:
        print('else')
    return JsonResponse({'kind': 'trade'})


def home(request):
    return redirect("http://localhost:5173/")
