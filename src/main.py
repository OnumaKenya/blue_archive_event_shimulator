import pandas as pd
import streamlit as st
from ortools.linear_solver import pywraplp

st.header("ブルアカイベント周回数最適化")

st.subheader("アイテム種類・必要数設定")
row_items = pd.DataFrame(None, index=range(4), columns=["アイテム名", "必要数"])
row_items["必要数"] = 15000
row_items["アイテム名"] = ["アイテム" + str(i) for i in range(1, 5)]
items = st.experimental_data_editor(row_items, num_rows="dynamic")
items = items.set_index("アイテム名")

st.subheader("消費AP、入手数設定")
idx = pd.Index(["Quest9", "Quest10", "Quest11", "Quest12"], name="クエスト名")
cols = pd.Index(list(items.index) + ["消費AP"])
row_df = pd.DataFrame(0.0, index=idx, columns=cols)
# 初期値設定
row_df["消費AP"] = 15

df = st.experimental_data_editor(row_df, num_rows="dynamic")

if st.button("周回数最適化実行"):
    # モデル構築
    solver = pywraplp.Solver("MIP", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    infinity = solver.infinity()

    # 変数定義
    quests = df.index
    x = pd.Series([solver.IntVar(0.0, infinity, f"x[{q}]") for q in quests], index=quests, name="周回数")

    # 制約追加
    for i in items.index:
        solver.Add(x.dot(df[i]) >= items.loc[i, "必要数"])
    solver.Minimize(x.dot(df["消費AP"]))
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        st.write("最適周回数")
        st.write(x.map(lambda v: v.solution_value()))
        st.info(f"総消費AP:{solver.Objective().Value()}")
    else:
        st.warning("最適化に失敗しました。パラメータを見直してください。")