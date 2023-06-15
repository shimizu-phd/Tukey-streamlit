import numpy as np
import streamlit as st
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib
import japanize_matplotlib



st.title('Tukey HSD 多重比較検定')
df = None

way = st.selectbox('方法を選択してください.', ('直接入力', 'CSVから読み取り'))
st.write('\n')
st.write('\n')

if way == '直接入力':
    st.markdown('''
            - 下記のように条件名 :(半角コロン)　数値（カンマ区切り）で入力してください.  
            - 条件ごとに改行してください.  
            - データ数が違う場合はデータ数が同じになるようにNanで埋めてください.  
            - 条件と数値の個数に制限はありません.
            '''
            )
    st.markdown('---')
    st.markdown('''
                アンピシリン処理: 1.25, 1.37, 1.56, Nan, Nan  
                ゲンタマイシン処理: 1.93, 1.82, 1.75, 1.77, 1.81  
                バンコマイシン処理: 1.53, 1.34, 1.19, 1.25, Nan  
                .....  
                .....
                ''')
    st.markdown('---')
    text = st.text_area('データを入力')

    if text:
        # 改行で分けてリストにする
        text_split = text.split('\n')
        # 改行などが入っていて中身のないデータになっているものを除く
        text_split = [s for s in text_split if s.strip() != '']
        # リストの値の個数が条件の個数になる
        n_category = len(text_split)
        st.write(f'カテゴリー数：{len(text_split)}')
        dict = {}
        for i in range(n_category):
            # :で分けてリストにする、その1番目が数値なので、それをさらに,で分割する
            value_split = text_split[i].split(':')[1].split(',')
            # stripeで余分なスペースを削除する
            value_split_nospace = [i.strip() for i in value_split]
            # 'Nan'をnp.nanに置換。'Nan'がいくつあるかわからないのでwhileですべて置換する。
            while 'Nan' in value_split_nospace:
                index = value_split_nospace.index('Nan')
                value_split_nospace[index] = np.nan
            # 条件名が重複した場合は連番はつける
            # 連番を付加するための数字を初期化
            number = 1
            key_ori = text_split[i].split(':')[0]
            key = key_ori
            # 重複がなくなるまで連番を付加し続ける
            while key in dict.keys():
                number += 1
                key = f"{key_ori}{number}"
            # 連番を付加した文字列をリストに追加
            dict[key] = None
            # np.isnanがTrueでなければintegerに変換し、それ以外はそのまま
            dict[key] = [float(x) if not np.isnan(float(x)) else x for x in value_split_nospace]

        df = pd.DataFrame(dict)

if way == 'CSVから読み取り':
    st.markdown('''
            - CSVファイルは一行目に条件名を記載し、その下に数値を入れてください.  
            - 条件と数値の数に制限はありません.  
            - 各条件に含まれるデータ数が違っていても問題ありません.
            '''
            )
    st.markdown('---')
    st.markdown('''
                |アンピシリン処理|ゲンタマイシン処理|バンコマイシン処理|
                | ---- | ---- | ---- |
                |1.25|1.93|1.53|
                |1.37|1.82|1.34|
                |1.56|1.75|1.19|
                ||1.77|1.25|
                ||1.81||
                ''')
    st.markdown('---')
    with open('./sample.csv') as f:
        st.download_button('サンプルCSVのダウンロード', f, 'sample.csv', "text/csv")
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください.", type="csv")
    if uploaded_file is not None:
        # DataFrameへの読み込み
        df = pd.read_csv(uploaded_file)

if df is not None:
    # .meltでそれぞれの値に条件を対応させる
    df_melt = df.melt(var_name='category', value_name='value')
    df_melt = df_melt.dropna()
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df)
    with col2:
        st.dataframe(df_melt)
    st.write('この数値で良ければ解析ボタンを押してください.')
    button = st.button('解析')
    if button:
        result = pairwise_tukeyhsd(df_melt["value"], df_melt["category"])
        summary = result.summary()

        summary_df = pd.DataFrame(summary)
        summary_df.columns = summary_df.iloc[0]
        summary_df = summary_df[1:]
        st.write('\n')
        st.write('結果')
        st.dataframe(summary_df)
        #エクセルで文字化けしないようにutf-8ではなくutf-8-sigでエンコード
        csv = summary_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button('結果CSVのダウンロード', csv, 'result.csv', "text/csv")


        fig = result.plot_simultaneous()
        st.write('\n')
        st.write('平均と95％信頼区間')
        st.pyplot(fig)
