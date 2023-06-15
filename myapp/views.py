import pandas as pd
from django.http import JsonResponse
from django.shortcuts import redirect
from myapp.management.commands import main
import datetime as dt
from django.views.decorators.csrf import csrf_exempt
import json
from myapp.models import Brands, Judge, Trades


def show(request):
    df_zero, df_p1, df_p2, df_m1, df_m2, df_holding, df_watching = main.show()
    zero = df_zero.to_json(orient='records')
    p1 = df_p1.to_json(orient='records')
    p2 = df_p2.to_json(orient='records')
    m1 = df_m1.to_json(orient='records')
    m2 = df_m2.to_json(orient='records')
    holding = df_holding.to_json(orient='records')
    watching = df_watching.to_json(orient='records')
    return JsonResponse({'zero': zero,
                         'p1': p1,
                         'p2': p2,
                         'm1': m1,
                         'm2': m2,
                         'holding': holding,
                         'watching': watching})


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
        _judges = Judge.objects.filter(brand=_brand)
        if _judges:
            _judge = _judges.order_by('-created_at').first()
            params = {
                "is_holding": _brand.is_holding,
                "is_watching": _brand.is_watching,
                "judge_date": _judge.date,
                "judge_trend": _judge.trend,
                "judge_text": _judge.judge,
            }
        else:
            params = {
                "is_holding": _brand.is_holding,
                "is_watching": _brand.is_watching,
            }
        print(params)
        return JsonResponse(params)


@csrf_exempt
def reg_judge(request):
    print('now post')
    if request.method == 'POST':
        datas = json.loads(request.body)
        _brand_code = datas['brand_code']
        _is_watching = datas['is_watching']
        _is_holding = datas['is_holding']
        _brand = Brands.objects.filter(code=_brand_code).first()
        _brand.is_holding = _is_holding
        _brand.is_watching = _is_watching
        _brand.save()

        _date = datas['judge_date']
        _text = datas['judge_text']
        _trend = datas['judge_trend']

        judge = Judge()
        judge.brand = _brand
        date = dt.datetime.strptime(_date, '%Y-%m-%d').date()
        judge.date = date
        judge.judge = _text
        judge.trend = _trend
        judge.save()
        print('done')
        return JsonResponse({'states': 'done'})
    else:
        print('else')
        return JsonResponse({'kind': 'trade'})


def survey(request):
    print('survey')
    main.survey()
    return JsonResponse({'kind': 'trade'})


def check(request):
    print('check')
    _trades = Trades.objects.all()
    _brands = Brands.objects.filter(code='7752.jp')
    __df = pd.DataFrame.from_records(_brands.values())
    id = __df['id'][0]

    _df = pd.DataFrame.from_records(_trades.values())
    df = _df[_df['brand_id']==id]
    print(df)
    return JsonResponse({'kind': 'trade'})

def home(request):
    return redirect("http://localhost:5173/")
