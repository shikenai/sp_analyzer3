from django.core.management.base import BaseCommand
import pandas as pd
import ssl
from myapp.models import Brands, Trades
from more_itertools import chunked
import os


def register_trades():
    file_list = get_topix_files()
    print('register trades')
    for f in file_list:
        print(f)
        read_trades_csv(f)
    print('DONE')


def read_trades_csv(df_path):
    df = pd.read_csv(df_path)
    df_date = df['Attributes']
    new_columns = df.iloc[0].tolist()
    df.columns = new_columns
    for i in range(1, ((len(new_columns) - 1) // 5) + 1):
        extracted_df = pd.concat([df_date, df[new_columns[i]]], axis=1)
        extracted_df = extracted_df.drop([0, 1])
        extracted_df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
        extracted_df = extracted_df.astype(
            {'Close': float, 'High': float, 'Open': float, 'Low': float, 'Volume': float})
        extracted_df['Date'] = pd.to_datetime(extracted_df['Date']).dt.date
        _brand = Brands.objects.filter(code=new_columns[i]).first()
        extracted_df['brand'] = _brand
        extracted_df_records = extracted_df.to_dict(orient='records')
        models_insert = []
        # print(extracted_df_records)
        for j in range(len(extracted_df_records)):
            t_date = extracted_df_records[j]['Date']
            t_brand = extracted_df_records[j]['brand']
            print(t_brand)
            _trades = Trades.objects.filter(Date=t_date, brand=t_brand)
            if not _trades.exists():
                models_insert.append(Trades(
                    brand=extracted_df_records[j]['brand'],
                    Date=extracted_df_records[j]['Date'],
                    Close=extracted_df_records[j]['Close'],
                    High=extracted_df_records[j]['High'],
                    Low=extracted_df_records[j]['Low'],
                    Open=extracted_df_records[j]['Open'],
                    Volume=extracted_df_records[j]['Volume'],
                ))
            else:
                print('pass')
                pass
        Trades.objects.bulk_create(models_insert)


def get_topix_files():
    # ベースデータからcsvを取得する。２つに別れている想定のため、まずは２つのファイル名を取得
    folder_path = os.path.join(os.getcwd(), 'data', 'base')
    file_list = []
    for file_name in os.listdir(folder_path):
        if 'topix' in file_name:
            file_list.append(os.path.join(folder_path, file_name))
    return file_list


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
        # 既に登録されていない場合は登録する
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
