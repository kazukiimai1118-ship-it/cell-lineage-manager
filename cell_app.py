import streamlit as st
import pandas as pd
from cell_manager import CellManager
import graphviz

# ページ設定 (ブラウザのタブ名などを設定)
st.set_page_config(page_title="Cell Lineage Manager", layout="wide")

# マネージャーの初期化
manager = CellManager()

# タイトル
st.title("Cell Lineage Manager")

# --- サイドバーをタブ分けする ---
tab1, tab2, tab3 = st.sidebar.tabs(["新規登録", "継代 (Passage)", "細胞の削除"])


# === タブ１: 新規登録 ===
with tab1:
    with st.sidebar.form("register_form"):
        # 入力項目
        cell_type = st.text_input("細胞種名 (Cell Type)", placeholder="例: HeLa, HEK293T")
        label = st.text_input("ラベル (任意)", placeholder="例: Lot.3, GFP(+)")
        passage = st.number_input("継代数 (Passage)", min_value=0, value=0)
        seeded_count = st.number_input("播種細胞数 (Seeded)", min_value=1000, value=500000, step=10000)

        # 登録ボタン
        submitted = st.form_submit_button("登録する")

        if submitted:
            if cell_type:
                # マネージャーを使って保存
                manager.add_cell(cell_type, label, passage, seeded_count)
                st.sidebar.success(f"{cell_type}を登録しました！")
            else:
                st.sidebar.error("細胞種名は必須です。")

# === タブ２: 継代操作 ===
with tab2:
    st.write("培養中の細胞を継代する場合")

    # 選択肢用のリストを作成 (IDと細胞名を表示)
    # 辞書IDをキー、表示名を値にする
    all_cells = manager.get_all_cells()

    # まだ回収されていない(activeな)細胞だけ選べるとベストだが、一旦全リスト
    cell_options = {c["id"]: f"{c['cell_type']} (ID:{c['id']}) P{c['passage']}" for c in all_cells}

    selected_parent_id = st.selectbox(
        "親細胞を選択", # <--- この１行 (文字列)が必要です！
        options=list(cell_options.keys()),
        format_func=lambda x: cell_options[x] # IDから表示名に変換
    )

    with st. form("passage_form"):
        # 親細胞の回収データ
        harvested = st.number_input("回収細胞数 (Harvested)", min_value=1, value=1000000, step=10000)
        hours = st.number_input("培養時間 (Hours)", value=48)

        st.markdown("---") # 区切り線

        # 次世代の播種データ
        new_label = st.text_input("次世代のラベル", value="")
        next_seeded = st.number_input("次世代の播種数 (Seeded)", value=500000, step=10000)

        if st.form_submit_button("継代を実行"):
            if selected_parent_id:
                # マネージャーの継代処理を呼び出す
                child = manager.register_passage(
                    selected_parent_id, harvested, next_seeded, new_label, hours
                )

                if child:
                    st.success(f"継代完了! 次はP{child['passage']}です。")
                    st.rerun() # 画面更新して表に反映
            else:
                st.error("親細胞を選んでください")

# === タブ３: 細胞の削除 ===
with tab3:
    st.write("登録している細胞を削除する場合")

    st.subheader("細胞データの削除")

    # リストから選択肢を作成
    # manager.cells は辞書のリストなので、forループで回す
    if manager.cells:
        # IDをキー、表示名を値にする辞書
        cell_options = {
            c["id"]: f"{c.get('cell_type')} (ID: {c['id'][:6]}...)"
            for c in manager.cells
        }

        # セレクトボックス
        target_id_to_delete = st.selectbox(
            "削除する細胞を選択",
            options=list(cell_options.keys()),
            format_func=lambda x: cell_options[x]
        )

        # 削除ボタン
        if st.button("削除実行"):
            # Managerに削除を依頼
            success, msg = manager.delete_cell(target_id_to_delete)

            if success:
                st.success(msg)
                import time
                time.sleep(1)   # メッセージを読ませるために一瞬待つ
                st.rerun()      # 画面更新
            else:
                st.error(msg)
        else:
            st.info("登録されている細胞はありません。")

# --- メイン画面をタブ分けする ---
tab4, tab5 = st.tabs(["細胞管理リスト", "系統樹ビュー"])

# --- メイン画面: データ一覧表示 ---

# === タブ1: 管理画面 ===
with tab4:
    st.header("培養中の細胞一覧")

    # データを取得
    cells = manager.get_all_cells()

    if cells:
        # 見やすいようにPandasデータフレームに変換
        df = pd.DataFrame(cells)

        # 表示したい列だけ選んで、列名を日本語にする (オプション)
        display_columns = {
            "id": "ID",
            "cell_type": "細胞種",
            "label": "ラベル",
            "passage": "継代数",
            "seeded_count": "播種数",
            "date": "開始数",
            "status": "状態"
        }

        # データフレームを表示 (use_container_width=Trueで横幅いっぱいに)
        st.dataframe(
            df[display_columns.keys()].rename(columns=display_columns),
            use_container_width=True
        )
    else:
        st.info("まだ登録された細胞はありません。サイドバーから登録してください。")

# === タブ2: 系統樹 ===
with tab5:
    st.header("🧬 細胞系統樹")
    st.markdown("細胞の継代履歴をツリー形式で表示します。")

    # --- 1. フィルターUIの追加 ---
    filter_mode = st.radio(
        "表示モード",
        ["すべて表示", "特定の系統のみ表示"],
        horizontal=True
    )

    target_cells = [] # 最終的に表示する細胞リスト

    if filter_mode == "すべて表示":
        # 全データを取得
        target_cells = manager.get_all_cells()

    else: # "特定の系統のみ表示" の場合
        if manager.cells:
            # 選択肢の作製
            options = {c["id"]: f"{c['cell_type']} (ID: {c['id'][:6]}...)" for c in manager.cells}

            # 起点となる細胞を選択
            selected_root_id = st.selectbox(
                "起点となる細胞を選択 (その子孫を表示します)",
                options=list(options.keys()),
                format_func=lambda x: options[x]
            )

            # ★ここでさっき作ったメソッドを使う
            target_cells = manager.get_lineage(selected_root_id)

            st.info(f"選択された系統の細胞数: {len(target_cells)}")
        else:
            st.warning("データがありません。")

    # --- 2. 描画 ---
    if not target_cells:
        st.info("表示するデータがありません。")
    else:
        # フィルタリングされたリスト(target_cells)を渡してグラフ化
        lineage_graph = manager.render_lineage_graph(target_cells)
        st.graphviz_chart(lineage_graph, use_container_width=True)

# デバッグ用: JSONの中身をそのまま表示 (開発中のみ便利)
# st.write(cells)