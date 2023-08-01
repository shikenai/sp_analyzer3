from django.core.management.base import BaseCommand
import pandas as pd
import ssl
from myapp.models import Brands, Trades
from more_itertools import chunked
import os
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import datetime as dt
import japanize_matplotlib


def show():
    folder_path = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'img')
    col_list = ['sign', 'rsi', 'brand', 'filename']
    df_zero = pd.DataFrame(columns=col_list)
    df_p1 = pd.DataFrame(columns=col_list)
    df_p2 = pd.DataFrame(columns=col_list)
    df_m1 = pd.DataFrame(columns=col_list)
    df_m2 = pd.DataFrame(columns=col_list)
    df_watching = pd.DataFrame(columns=col_list)
    df_holding = pd.DataFrame(columns=col_list)

    link_path = '/src/assets/img/'

    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            if not filename[0] == '.':
                i1 = filename.index('【')
                i2 = filename.index('】')
                i3 = filename.index('(')
                i4 = filename.index(';')
                i5 = filename.index(')')
                brand = filename[i1 + 1:i2]
                sign = filename[i3 + 1:i4]
                rsi = filename[i4 + 1:i5]
                new_row = [[sign, rsi, brand, link_path + filename]]
                temp_df = pd.DataFrame(new_row, columns=col_list)

                if sign == '0':
                    df_zero = pd.concat([df_zero, temp_df])
                elif sign == '1':
                    df_p1 = pd.concat([df_p1, temp_df])
                elif sign == '2':
                    df_p2 = pd.concat([df_p2, temp_df])
                elif sign == '-1':
                    df_m1 = pd.concat([df_m1, temp_df])
                elif sign == '-2':
                    df_m2 = pd.concat([df_m2, temp_df])
                _brand = Brands.objects.filter(code=brand[:7]).first()
                if _brand.is_watching:
                    df_watching = pd.concat([df_watching, temp_df])
                if _brand.is_holding:
                    df_holding = pd.concat([df_holding, temp_df])

    df_zero = df_zero.sort_values('rsi')
    df_p2 = df_p2.sort_values('rsi')
    df_p1 = df_p1.sort_values('rsi')
    df_m2 = df_m2.sort_values('rsi', ascending=False)
    df_m1 = df_m1.sort_values('rsi', ascending=False)
    df_watching = df_watching.sort_values('rsi')
    df_holding = df_holding.sort_values('rsi')
    return df_zero, df_p1, df_p2, df_m1, df_m2, df_holding, df_watching


def survey():
    t = dt.datetime.now()
    erazer('img2')
    erazer('buy')
    erazer('sell')
    erazer('next_sell')
    erazer('next_buy')
    trades = Trades.objects.all()
    brands = Brands.objects.all()

    list_brands_id = brands.values_list('id', flat=True)
    df = pd.DataFrame.from_records(trades.values())
    # list_brands_id = list_brands_id[:1]
    for i in list_brands_id:
        extracted_df = df[df['brand_id'] == i]
        extracted_df = extracted_df.sort_values('Date', ascending=True)
        # extracted_df = add_high_low_mean(extracted_df)
        extracted_df = add_ma2(extracted_df, 'Close', (5, 10, 25, 60))
        extracted_df = compare_columns(extracted_df, 'Close_5ma', 'Close_10ma', 'gx_is')
        extracted_df = compare_columns(extracted_df, 'Close_5ma', 'Close_25ma', 'gx_im')

        extracted_df = add_ma2(extracted_df, 'High', (3, 10))
        extracted_df = add_ma2(extracted_df, 'Low', (3, 10))
        extracted_df = add_macd(extracted_df, positive=True)
        extracted_df = get_continual_states(extracted_df, 'High_3ma')
        extracted_df = get_continual_states(extracted_df, 'Low_3ma')
        extracted_df = get_continual_states(extracted_df, 'Close_5ma')
        extracted_df = get_continual_states(extracted_df, 'Close_10ma')
        extracted_df = get_continual_states(extracted_df, 'Close_25ma')
        extracted_df = get_continual_states(extracted_df, 'Close_60ma')

        # pd.set_option('display.max_rows', extracted_df.shape[0])
        # pd.set_option('display.max_columns', extracted_df.shape[1])
        extracted_df.index = pd.to_datetime(extracted_df['Date'], format='mixed')
        extracted_df = extracted_df.dropna()

        plot_img3(extracted_df.tail(260))

    elapsed_time = dt.datetime.now() - t
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    print(f"{minutes:.0f}分{seconds:.0f}秒")


def analyze():
    t = dt.datetime.now()
    erazer()
    trades = Trades.objects.all()
    brands = Brands.objects.all()

    list_brands_id = brands.values_list('id', flat=True)
    df = pd.DataFrame.from_records(trades.values())
    # list_brands_id = list_brands_id[:1]
    for i in list_brands_id:
        extracted_df = df[df['brand_id'] == i]
        extracted_df = extracted_df.sort_values('Date', ascending=True)
        extracted_df = add_bb(extracted_df)
        extracted_df = add_ma(extracted_df, 'Close')
        extracted_df = add_macd(extracted_df)
        extracted_df = add_rsi(extracted_df)
        extracted_df = add_stochastic(extracted_df)
        extracted_df = add_ichimoku(extracted_df)
        pd.set_option('display.max_rows', extracted_df.shape[0])
        pd.set_option('display.max_columns', extracted_df.shape[1])
        extracted_df.index = pd.to_datetime(extracted_df['Date'], format='mixed')
        extracted_df = extracted_df.dropna()
        plot_img(extracted_df)
    elapsed_time = dt.datetime.now() - t
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    print(f"{minutes:.0f}分{seconds:.0f}秒")


def plot_img(df):
    # 銘柄情報を取得
    filepath = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'img')
    brand = Brands.objects.get(id=df['brand_id'][0])
    filename_head = f'{df["sign"][-1]}【{brand.code}  {brand.name}】'
    filename_tail = f'({df["sign"][-1]};{int(df["rsi"][-1])}).png'
    full_filename = os.path.join(filepath, filename_head + filename_tail)
    title = str(df["sign"][-1]) + '  ' + brand.code + '  ' + brand.name + '  ' + brand.division
    print(full_filename)
    # print(df.columns)
    # 直近の最高値、最安値
    df["h_line"] = df["High"].rolling(20, min_periods=1).max()
    df["l_line"] = df["Low"].rolling(20, min_periods=1).min()
    adp = [mpf.make_addplot(df[['h_line', 'l_line']], type='step', alpha=0.2, panel=0)]

    # 移動平均とBBの設定（パネル０に描画するもの）
    column_list = df.columns
    ma_bb_columns = [c for c in column_list if 'ma' in c or 'band' in c]
    for c in ma_bb_columns:
        if 'ma' in c and 'macd' not in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle='--', alpha=0.7))
        elif 'band' in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle=':', alpha=0.5))

    # macdの描画
    adp.append(mpf.make_addplot(df['macd'], type='line', panel=1, color='green'))
    adp.append(mpf.make_addplot(df['macd_signal'], type='line', panel=1, color='blue'))
    adp.append(mpf.make_addplot(df['hist'], type='bar', panel=1, color='red'))
    adp.append(mpf.make_addplot(df['hist_diff_3mean'], type='line', panel=1, color='yellow', alpha=0.6))
    adp.append(mpf.make_addplot(df['sign'], type='line', panel=1, color='gray'))

    # RSI
    adp.append(mpf.make_addplot(df[['rsi', 'UL', 'DL']], ylim=[0, 100], panel=2))

    # stocha
    adp.append(mpf.make_addplot(df[['%D', '%SD', 'UL', 'DL']], ylim=[0, 100], panel=3))

    # 全体のスタイル
    mc = mpf.make_marketcolors(up='#049DBF', down='#D93D4A',
                               edge='#F2CED1', wick={'up': '#049DBF', 'down': '#D93D4A'})
    cs = mpf.make_mpf_style(marketcolors=mc, gridcolor="lightgray", rc={"font.family": plt.rcParams["font.family"][0]})
    mpf.plot(df, type='candle', addplot=adp,
             fill_between=dict(y1=df['span1'].values, y2=df['span2'].values, alpha=0.2, color='gray'), figsize=(19, 12),
             style=cs, savefig=full_filename, panel_ratios=(3, 1, 1, 1), title=title, tight_layout=True)
    plt.clf()
    plt.close()


def plot_img2(df):
    # 銘柄情報を取得
    print('plot2')
    filepath = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'img2')
    brand = Brands.objects.get(id=df['brand_id'][0])
    # Close_?ma_positive:1ならば上昇、0ならば下降
    filename_head = f'({str(df["Close_5ma_positive"][-1])}{str(df["Close_25ma_positive"][-1])}{str(df["Close_5ma_positive"][-1])}){round(df["momentum"][-1], 1)}({df["sign"][-1]} {df["sign2"][-1]})【{brand.code}  {brand.name}】'
    # sign:macd転換したか継続したか
    # sign2:macdの状態がどの程度継続しているか
    filename_tail = f'({df["sign"][-1]}{df["sign2"][-1]};{int(df["rsi"][-1])}).png'
    full_filename = os.path.join(filepath, filename_head + filename_tail)
    title = str(df["sign2"][-1]) + '  ' + brand.code + '  ' + brand.name + '  ' + brand.division
    print(full_filename)
    print(df)
    # print(df.columns)
    # 直近の最高値、最安値
    df["h_line"] = df["High"].rolling(20, min_periods=1).max()
    df["l_line"] = df["Low"].rolling(20, min_periods=1).min()
    adp = [mpf.make_addplot(df[['h_line', 'l_line']], type='step', alpha=0.2, panel=0)]
    adp = [mpf.make_addplot(df['high_low_mean'], type='line', alpha=0.5, panel=0)]

    # 移動平均とBBの設定（パネル０に描画するもの）
    column_list = df.columns
    ma_bb_columns = [c for c in column_list if 'ma' in c or 'band' in c]
    for c in ma_bb_columns:
        if 'ma' in c and 'macd' not in c and 'positive' not in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle='--', alpha=0.7))
        elif 'band' in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle=':', alpha=0.5))

    # macdの描画
    adp.append(mpf.make_addplot(df['macd'], type='line', panel=1, color='green'))
    adp.append(mpf.make_addplot(df['macd_signal'], type='line', panel=1, color='blue'))
    adp.append(mpf.make_addplot(df['hist'], type='bar', panel=1, color='red'))
    adp.append(mpf.make_addplot(df['hist_diff_3mean'], type='line', panel=1, color='yellow', alpha=0.6))
    adp.append(mpf.make_addplot(df['sign2'], type='line', panel=1, color='gray'))

    # RSI
    adp.append(mpf.make_addplot(df[['rsi', 'UL', 'DL']], ylim=[0, 100], panel=2))

    # stocha
    adp.append(mpf.make_addplot(df[['%D', '%SD', 'UL', 'DL']], ylim=[0, 100], panel=3))

    # 全体のスタイル
    mc = mpf.make_marketcolors(up='#049DBF', down='#D93D4A',
                               edge='#F2CED1', wick={'up': '#049DBF', 'down': '#D93D4A'})
    cs = mpf.make_mpf_style(marketcolors=mc, gridcolor="lightgray", rc={"font.family": plt.rcParams["font.family"][0]})
    mpf.plot(df, type='candle', addplot=adp,
             fill_between=dict(y1=df['span1'].values, y2=df['span2'].values, alpha=0.2, color='gray'), figsize=(19, 12),
             style=cs, savefig=full_filename, panel_ratios=(3, 1, 1, 1), title=title, tight_layout=True)
    plt.clf()
    plt.close()


def plot_img3(df):
    filepath = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'img2')
    filepath_buy = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'buy')
    filepath_sell = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'sell')
    filepath_next_buy = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'next_buy')
    filepath_next_sell = os.path.join(os.getcwd(), 'front', 'src', 'assets', 'next_sell')

    brand = Brands.objects.get(id=df['brand_id'][0])
    # Close_?ma_positive:1ならば上昇、0ならば下降
    #
    macd_sign4 = round(df["hist_diff_3mean"][-4], 2)
    macd_sign3 = round(df["hist_diff_3mean"][-3], 2)
    macd_sign2 = round(df["hist_diff_3mean"][-2], 2)
    macd_sign1 = round(df["hist_diff_3mean"][-1], 2)
    head_head = str(round(df["hist"][-1], 1)).replace("-", "▲")
    filename_head = f'({str(df["Close_5ma_positive"][-1])}{str(df["Close_25ma_positive"][-1])}{str(df["Close_60ma_positive"][-1])}){head_head},勢い：5ma_diff（{round(df["Close_5ma_diff_rate"][-1], 1)}） macd：{str(macd_sign4).replace("-", "▲")}→{str(macd_sign3).replace("-", "▲")}→{str(macd_sign2).replace("-", "▲")}→{str(macd_sign1).replace("-", "▲")}、gxis経過{df["gx_is"][-1]}日、gxim経過{df["gx_im"][-1]}日【{brand.code}  {brand.name}】'
    # filename_head = f'【{brand.code}  {brand.name}】'
    # sign:macd転換したか継続したか
    # sign2:macdの状態がどの程度継続しているか
    # filename_tail = f'({df["sign"][-1]}{df["sign2"][-1]};{int(df["rsi"][-1])}).png'
    filename_tail = f'.png'
    full_filename = os.path.join(filepath, filename_head + filename_tail)
    title = brand.code + '  ' + brand.name + '  ' + brand.division
    print(filename_head)
    # print(df.columns)
    # 直近の最高値、最安値
    # df["h_line"] = df["High"].rolling(20, min_periods=1).max()
    # df["l_line"] = df["Low"].rolling(20, min_periods=1).min()
    # adp = [mpf.make_addplot(df[['h_line', 'l_line']], type='step', alpha=0.2, panel=0)]
    # adp = [mpf.make_addplot(df['hl_mean'], type='line', alpha=0.5, panel=0)]

    # macdの描画
    adp = [mpf.make_addplot(df['macd'], type='line', panel=2, color='green')]
    adp.append(mpf.make_addplot(df['macd_signal'], type='line', panel=2, color='blue'))
    adp.append(mpf.make_addplot(df['hist'], type='bar', panel=2, color='red'))
    adp.append(mpf.make_addplot(df['hist_diff_3mean'], type='line', panel=2, color='black'))
    # adp.append(mpf.make_addplot(df['sign'], type='line', panel=2, color='gray'))

    # 移動平均とBBの設定（パネル０に描画するもの）
    column_list = df.columns
    ma_columns = [c for c in column_list if 'ma' in c]
    for c in ma_columns:
        if 'ma' in c and 'hl' not in c and 'diff' not in c and 'continual' not in c and 'positive' not in c and 'High' not in c and 'Low' not in c and 'macd' not in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle='--', alpha=0.7))
        elif 'hl' in c and 'diff' not in c and 'continual' not in c:
            adp.append(mpf.make_addplot(df[c], type='line', panel=0, linestyle=':', alpha=0.5))

    # 全体のスタイル
    mc = mpf.make_marketcolors(up='#D93D4A', down='#5AFF19',
                               edge='#F2CED1', wick={'up': '#049DBF', 'down': '#D93D4A'})
    cs = mpf.make_mpf_style(marketcolors=mc, gridcolor="lightgray", rc={"font.family": plt.rcParams["font.family"][0]})
    mpf.plot(df, type='candle', addplot=adp, figsize=(19, 12), volume=True,
             style=cs, savefig=full_filename, title=title, tight_layout=True)
    if macd_sign4 < macd_sign3 < macd_sign2 < macd_sign1:
        diff = calculate_average(macd_sign1, macd_sign2, macd_sign3, macd_sign4)
        filename_head = f'({str(df["Close_5ma_positive"][-1])}{str(df["Close_25ma_positive"][-1])}{str(df["Close_60ma_positive"][-1])}){head_head},勢い：5ma_diff（{round(df["Close_5ma_diff_rate"][-1], 1)}） macd：{str(macd_sign4).replace("-", "▲")}→{str(macd_sign3).replace("-", "▲")}→{str(macd_sign2).replace("-", "▲")}→{str(macd_sign1).replace("-", "▲")}→【{str(round((macd_sign1 + diff), 2)).replace("-", "▲")}】、gxis経過{df["gx_is"][-1]}日、gxim経過{df["gx_im"][-1]}日【{brand.code}  {brand.name}】'
        if (macd_sign2 < 0 and 0 < macd_sign1 < 1) or (macd_sign1 < 0 and 0 < (macd_sign1 + diff)):
            full_filename_buy = os.path.join(filepath_buy, filename_head + filename_tail)
            mpf.plot(df, type='candle', addplot=adp, figsize=(19, 12), volume=True,
                     style=cs, savefig=full_filename_buy, title=title, tight_layout=True)
        elif (macd_sign3 < 0 and 0 < macd_sign2):
            full_filename_buy = os.path.join(filepath_next_buy, filename_head + filename_tail)
            mpf.plot(df, type='candle', addplot=adp, figsize=(19, 12), volume=True,
                     style=cs, savefig=full_filename_buy, title=title, tight_layout=True)

    elif macd_sign4 > macd_sign3 > macd_sign2 > macd_sign1:
        diff = calculate_average(macd_sign1, macd_sign2, macd_sign3, macd_sign4)
        filename_head = f'({str(df["Close_5ma_positive"][-1])}{str(df["Close_25ma_positive"][-1])}{str(df["Close_60ma_positive"][-1])}){head_head},勢い：5ma_diff（{round(df["Close_5ma_diff_rate"][-1], 1)}） macd：{str(macd_sign4).replace("-", "▲")}→{str(macd_sign3).replace("-", "▲")}→{str(macd_sign2).replace("-", "▲")}→{str(macd_sign1).replace("-", "▲")}→【{str(round((macd_sign1 + diff), 2)).replace("-", "▲")}】、gxis経過{df["gx_is"][-1]}日、gxim経過{df["gx_im"][-1]}日【{brand.code}  {brand.name}】'
        if (macd_sign2 > 0 and 0 < macd_sign1 < 1) or (macd_sign1 > 0 and 0 > (macd_sign1 + diff)):
            full_filename_sell = os.path.join(filepath_sell, filename_head + filename_tail)
            mpf.plot(df, type='candle', addplot=adp, figsize=(19, 12), volume=True,
                     style=cs, savefig=full_filename_sell, title=title, tight_layout=True)
        elif (0 < macd_sign3 and macd_sign2 < 0):
            full_filename_sell = os.path.join(filepath_next_sell, filename_head + filename_tail)
            mpf.plot(df, type='candle', addplot=adp, figsize=(19, 12), volume=True,
                     style=cs, savefig=full_filename_sell, title=title, tight_layout=True)
    plt.clf()
    plt.close()


# ============【ココカラ】dfに移動平均等を追加する===============
def add_stochastic(df, term=14):
    stochastic = pd.DataFrame()
    stochastic['%K'] = ((df['Close'] - df['Low'].rolling(term).min())
                        / (df['High'].rolling(term).max() - df['Low'].rolling(term).min())) * 100
    stochastic['%D'] = stochastic['%K'].rolling(3).mean()
    stochastic['%SD'] = stochastic['%D'].rolling(3).mean()
    # stochastic['UL'] = 80
    # stochastic['DL'] = 20
    df = pd.concat([df, stochastic], axis=1)
    return df


def calculate_average(A, B, C, D):
    diff1 = A - B
    diff2 = B - C
    diff3 = C - D
    average = round((diff1 + diff2 + diff3) / 3, 2)
    return average


def compare_columns(df, column_a, column_b, new_col_name):
    diff_values = []
    prev_diff = 0

    for index, row in df.iterrows():
        a = row[column_a]
        b = row[column_b]

        if a > b:
            if prev_diff < 0:
                diff = 1
                prev_diff = 1
            else:
                prev_diff += 1
                diff = prev_diff
        elif a < b:
            if prev_diff > 0:
                diff = -1
                prev_diff = -1
            else:
                prev_diff -= 1
                diff = prev_diff
        else:
            diff = 0
            prev_diff = 0
        diff_values.append(diff)

    df[new_col_name] = diff_values
    return df


def add_bb(df, bb_period=20, bb_dev=2):
    # ボリンジャーバンドの計算
    rolling_mean = df['Close'].rolling(bb_period).mean()
    rolling_std = df['Close'].rolling(bb_period).std()
    upper_band = rolling_mean + (bb_dev * rolling_std)
    lower_band = rolling_mean - (bb_dev * rolling_std)
    df['upper_band'] = upper_band
    df['lower_band'] = lower_band
    return df


def add_ma(df, col, _list=(5, 25, 60), positive=False):
    for i in _list:
        df[f'{col}_{str(i)}ma'] = df[col].rolling(i).mean()
        if positive:
            df[f'{col}_{str(i)}ma_diff'] = df[f'{col}_{str(i)}ma'].diff()
            df[f'{col}_{str(i)}ma_positive'] = df[f'{col}_{str(i)}ma_diff'].apply(lambda x: 1 if x > 0 else -1)
            # df = df.drop(f'{col}_{str(i)}ma_diff', axis=1)
    print(_list[0])
    print(df.columns)
    print(f'{col}_{_list[0]}ma_diff')
    df['momentum'] = df[f'{col}_{_list[0]}ma_diff'] - df[f'{col}_{_list[1]}ma_diff']
    return df


def add_ma2(df, col, _list):
    for i in _list:
        df[f'{col}_{str(i)}ma'] = df[col].rolling(i).mean()
        df[f'{col}_{str(i)}ma_diff'] = df[f'{col}_{str(i)}ma'].diff()
        df[f'{col}_{str(i)}ma_diff_rate'] = round(df[f'{col}_{str(i)}ma_diff'] / df[col] * 100, 3)
        df[f'{col}_{str(i)}ma_positive'] = df[f'{col}_{str(i)}ma_diff'].apply(lambda x: 1 if x > 0 else -1)
        df = df.drop(f'{col}_{str(i)}ma_diff', axis=1)

    return df


def get_continual_states(df, col):
    diff_signs = np.sign(df[col].diff())

    result = []
    val = 0
    for sign in diff_signs:
        if sign == 1:
            if val < 0:
                val = 1
            else:
                val += 1
        elif sign == -1:
            if val > 0:
                val = -1
            else:
                val -= 1

        result.append(val)
    df[f'{col}_continual'] = result

    return df


def add_high_low_mean(df):
    df['hl_mean'] = df[['High', 'Low']].mean(axis=1)
    return df


def add_macd(df, positive=False):
    # 普通のmacd
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    macd_df = pd.DataFrame({'macd': macd, 'macd_signal': signal, 'hist': hist})
    macd_df['hist_diff'] = macd_df['hist'].diff()
    macd_df['hist_diff_3mean'] = macd_df['hist'].diff().rolling(3).mean()
    macd_df['t'] = macd_df['hist_diff_3mean'].apply(sign_func)
    macd_df['t_shift'] = macd_df['hist_diff_3mean'].shift(1).apply(sign_func)
    macd_df['hist_posi'] = macd_df['hist'].apply(sign_func)
    macd_df['sign'] = 0
    if positive:
        diff_signs = np.sign(macd_df['hist_diff_3mean'].diff()).fillna(0)
        result = []
        val = 0
        for sign in diff_signs:
            if sign == 1:
                if val < 0:
                    val = 1
                else:
                    val += 1
            elif sign == -1:
                if val > 0:
                    val = -1
                else:
                    val -= 1

            result.append(val)
        macd_df['sign2'] = result
        pd.set_option('display.max_rows', macd_df.shape[0])
        pd.set_option('display.max_columns', macd_df.shape[1])

    macd_df.loc[(macd_df['hist_posi'] == -1) & (macd_df['t_shift'] == -1) & (macd_df['t'] == 1), 'sign'] = 2
    macd_df.loc[(macd_df['hist_posi'] == -1) & (macd_df['t_shift'] == 1) & (macd_df['t'] == 1), 'sign'] = 1
    macd_df.loc[(macd_df['hist_posi'] == 1) & (macd_df['t_shift'] == 1) & (macd_df['t'] == -1), 'sign'] = -2
    macd_df.loc[(macd_df['hist_posi'] == 1) & (macd_df['t_shift'] == -1) & (macd_df['t'] == -1), 'sign'] = -1

    macd_df = macd_df.drop(['t', 't_shift', 'hist_diff', 'hist_posi'], axis=1)
    df = pd.concat([df, macd_df], axis=1)
    return df


def sign_func(x):
    if x > 0:
        return 1
    else:
        return -1


def add_rsi(df, term=14):
    rsi = pd.DataFrame()
    rsi['diff'] = df['Close'].diff()
    f_plus = lambda x: x if x > 0 else 0
    f_minus = lambda x: x if x < 0 else 0
    rsi['diff+'] = rsi['diff'].map(f_plus)
    rsi['diff-'] = rsi['diff'].map(f_minus)
    rsi['rs'] = rsi['diff+'].rolling(window=term, center=False).mean() \
                / rsi['diff-'].abs().rolling(window=term, center=False).mean()
    rsi['rsi'] = 100.0 - (100.0 / (1.0 + rsi['rs']))
    rsi = rsi.drop(['diff', 'diff+', 'diff-', 'rs'], axis=1)
    rsi['UL'] = 80
    rsi['DL'] = 20
    df = pd.concat([df, rsi], axis=1)
    return df


def add_ichimoku(df):
    high = df.High
    low = df.Low
    # 基準線
    max26 = high.rolling(window=26).max()
    min26 = low.rolling(window=26).min()
    df['basic_line'] = (max26 + min26) / 2
    # 転換線
    max9 = high.rolling(window=9).max()
    min9 = low.rolling(window=9).min()
    df['turn_line'] = (max9 + min9) / 2
    # 先行スパン１
    df['span1'] = (df['basic_line'] + df['turn_line']) / 2
    # 先行スパン２
    high52 = high.rolling(window=52).max()
    low52 = low.rolling(window=52).min()
    df['span2'] = (high52 + low52) / 2
    # # 遅行線
    # df['slow_line'] = df['Close'].shift(-25)
    df = df.drop(['basic_line', 'turn_line'], axis=1)
    return df


# ============【ココマデ】dfに移動平均等を追加する===============
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
        _brand = Brands.objects.filter(code=str(b) + '.jp').first()
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
    df.to_csv(os.path.join(os.getcwd(), 'data', 'new_trades', f'{df["Date"][0].strftime("%Y%m%d")}_new_trades.csv'))
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
    cnt = 0
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
            # print(t_brand)
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
        # print(models_insert[0].Close)
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
    df.loc[:, 'コード'] = df['コード'].astype(str) + '.jp'
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
    print('DONE')


def erazer(folder_name):
    folder_path = os.path.join(os.getcwd(), 'front', 'src', 'assets', folder_name)  # フォルダのパスを設定

    for file_name in os.listdir(folder_path):  # フォルダ内のファイル名を取得
        file_path = os.path.join(folder_path, file_name)  # ファイルのパスを設定
        if os.path.isfile(file_path):  # ファイルであれば
            os.remove(file_path)  # ファイルを削除
        elif os.path.isdir(file_path):  # フォルダであれば
            os.rmdir(file_path)  # フォルダを削除


def test():
    print('test')


class Command(BaseCommand):
    help = 'hello test'

    def handle(self, *args, **options):
        test()
