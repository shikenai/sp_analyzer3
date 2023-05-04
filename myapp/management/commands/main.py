from django.core.management.base import BaseCommand
import pandas as pd
import ssl
from myapp.models import Brands, Trades
from more_itertools import chunked
import os
import requests
from bs4 import BeautifulSoup
import time



# ---------------【ココカラ】ネットから当日の取引データを登録-------------------
def get_new_trades():
    _df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'base', 'test.csv'))
    brands_list = list(_df['コード'].astype('str'))
    # brands_list = brands_list[:3]
    df = pd.DataFrame(columns=["Date", "Close", "High", "Low", "Open", "Volume", "brand"])
    for b in brands_list:
        url = "https://kabutan.jp/stock/?code=" + b
        res = requests.get(url)
        doc = BeautifulSoup(res.text, 'html.parser')
        el = doc.select("#kobetsu_left tr")
        time_elapsed = res.elapsed.total_seconds()
        print(b)
        print('time_elapsed:', time_elapsed)
        _brand = Brands.objects.filter(code=str(b)+'.jp').first()
        time_tags = doc.find_all('time')
        datetimes = [tag['datetime'] for tag in time_tags]
        if 'T' in datetimes[7]:
            _date = datetimes[7].split('T')[0]
        else:
            _date = datetimes[7]
        if el is not None:
            open = float(el[0].select('td')[0].getText().replace(',', ''))
            high = float(el[1].select('td')[0].getText().replace(',', ''))
            low = float(el[2].select('td')[0].getText().replace(',', ''))
            close = float(el[3].select('td')[0].getText().replace(',', ''))
            volume = int(el[4].select('td')[0].getText().replace(',', '')[: -2])

        new_list = [_date, close, high, low, open, volume, _brand]

        df.loc[len(df)] = pd.Series(new_list, index=df.columns)

        time.sleep(5)
    df = df.astype({'Close': float, 'High': float, 'Open': float, 'Low': float, 'Volume': float})
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df.to_csv(os.path.join(os.getcwd(),'data','new_trades', f'{df["Date"][0].strftime("%Y%m%d")}_new_trades.csv'))
    df_records = df.to_dict(orient='records')
    model_inserts = []
    print(df_records)
    for i in range(len(df_records)):
        t_date = df_records[i]['Date']
        t_brand = df_records[i]['brand']
        _trades = Trades.objects.filter(Date=t_date, brand=t_brand)
        if not _trades.exists():
            model_inserts.append(Trades(
                Date=df_records[i]['Date'],
                Close=df_records[i]['Close'],
                High=df_records[i]['High'],
                Low=df_records[i]['Low'],
                Open=df_records[i]['Open'],
                Volume=df_records[i]['Volume'],
                brand=df_records[i]['brand'],
            ))
    print(model_inserts)
    Trades.objects.bulk_create(model_inserts)
# ---------------【ココマデ】ネットから当日の取引データを登録-------------------
# ---------------【ココカラ】CSVから取引データを登録-------------------

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


# ---------------【ココマデ】CSVから取引データを登録-------------------

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
