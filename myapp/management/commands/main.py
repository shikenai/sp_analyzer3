from django.core.management.base import BaseCommand
import pandas as pd
import ssl
from myapp.models import Brands
from more_itertools import chunked


def test():
    print('regi trades')


def register_brands_from_tse():
    # urlに記載されているエクセルファイルから、TOPIX Core30, Large70, Mid400　選定銘柄を選出し、モデル登録。
    # ただし、既に登録してあるものを複数回登録することはない。
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    brands = pd.read_excel(url)
    target_cols = ['TOPIX Mid400', "TOPIX Large70", "TOPIX Core30"]
    df = brands[brands['規模区分'].isin(target_cols)]
    # df.loc[:, 'コード'] = df['コード'].astype(str) + '.jp'
    df = df[['コード', '銘柄名', '規模区分']]
    df = df.reset_index(drop=True)

    _df_records = df.to_dict(orient='records')
    model_inserts = []
    _brands = Brands.objects.all()
    code_list = list(_brands.values_list('code', flat=True))

    for i in range(len(_df_records)):
        if not _df_records[i]['コード'] in code_list:
            model_inserts.append(Brands(
                code=_df_records[i]['コード'],
                name=_df_records[i]['銘柄名'],
                division=_df_records[i]['規模区分'],
            ))
    Brands.objects.bulk_create(model_inserts)


class Command(BaseCommand):
    help = 'hello test'

    def handle(self, *args, **options):
        test()
