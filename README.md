# 🧬 Cell Lineage Manager (細胞継代管理アプリ)

## 概要 (Overview)
細胞培養の研究現場における「継代記録」と「細胞系統の追跡」を効率化するために開発されたWebアプリケーションです。
手書きノートやExcel管理で発生しがちな「計算ミス」や「親子関係の記録漏れ」を防ぎ、視覚的な系統樹（Tree View）で細胞の履歴を一元管理できます。

## 解決した課題 (Problem Solved)
* **記録の煩雑さ:** 継代ごとのPDL（個体群倍加レベル）や倍加時間の計算を自動化しました。
* **履歴のブラックボックス化:** 「この細胞の親はどれだっけ？」という問題を、自動描画される系統樹で解決しました。
* **操作ミス:** 誤って親細胞を削除してデータ整合性が壊れないよう、Safe Delete機能を実装しました。

## 主な機能 (Features)
* **細胞登録:** 継代数、播種数などの基本情報を入力しデータベース化。
* **自動計算:** 継代時にPDLと倍加時間を自動算出し、細胞の増殖能を数値化。
* **系統樹可視化:** Graphvizを用いて、細胞の親子関係をツリー形式で自動描画。
* **フィルタリング:** 膨大なデータの中から、特定の系統のみを抽出して表示。
* **データ保護:** 子孫を持つ細胞の削除をブロックする整合性チェック機能。

## 技術スタック (Tech Stack)
* **Frontend:** Streamlit
* **Backend logic:** Python
* **Data Handling:** Pandas
* **Visualization:** Graphviz

## ローカルでの実行方法 (Installation)
```bash
# リポジトリのクローン
git clone [https://github.com/](https://github.com/)kazukiimai1118-ship-it/cell-lineage-manager.git

# ディレクトリへ移動
cd cell-lineage-manager

# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリの起動
streamlit run cell_app.py
