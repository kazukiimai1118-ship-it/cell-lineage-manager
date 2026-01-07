import json
import os
import uuid # 重複しないIDを作るためのライブラリ
from datetime import datetime
import calc
import graphviz

# データを保存するファイル名
DATA_FILE = "cells.json"

class CellManager:
    def __init__(self):
        """
        クラスの初期化メソッド
        アプリ起動時に自動的にデータを読み込みます
        """
        self.cells = [] # 全細胞データを格納するリスト
        self.load_data()

    def add_cell(self, cell_type, label, passage, seeded_count, parent_id=None):
        """
        新しい細胞を登録するメソッド
        """
        # ユニークなIDを生成 (例: "c001..."のような文字列)
        new_id = str(uuid.uuid4())[:8]

        # 今日の日付
        today = datetime.now().strftime("%Y-%m-%d")

        # 辞書データを作成 (Day 22の設計に基づく)
        new_cell = {
            "cell_type": cell_type,
            "id": new_id,
            "parent_id": parent_id,
            "label": label,
            "date": today,
            "passage": int(passage),
            "seeded_count": int(seeded_count),
            "harvested_count": None,    # まだ回収していない
            "pdl": 0.0,
            "doubling_time": None,
            "status": "active"
        }

        self.cells.append(new_cell)
        self.save_data()                # 追加したらすぐに保存
        print(f"✅ 細胞を追加しました: {cell_type} (ID: {new_id})")
        return new_cell
    
    # ↓↓↓ [追加] この新しい目そっとをクラス内に追加足てください ↓↓↓
    def register_passage(self, parent_id, harvested_count, seeded_count, label, hours=48):
        """
        継代処理を行う目そっと
        １．親細胞のデータを更新 (回収数、倍加時間など)
        ２．子細胞 (次世代)を新規作成
        """

        # 1. 親細胞を殺す
        parent_cell = None
        for cell in self.cells:
            if cell["id"] == parent_id:
                parent_cell = cell
                break
        if parent_cell is None:
            print("エラー: 親細胞が見つかりません")
            return None
        
        # 2. 計算モジュールを使ってPDLなどを算出
        # 前回のPDLを取得 (なければ0)
        prev_pdl = parent_cell.get("pdl", 0.0)

        # PDL増加分と、新しい積層PDLを計算
        delta_pdl, new_pdl = calc.calculate_pdl(
            parent_cell["seeded_count"],
            harvested_count,
            prev_pdl
        )

        # 倍加時間 (Doubuling Time)を計算
        dt = calc.calculate_doubling_time(hours, delta_pdl)

        # 3. 親細胞のデータを更新 (回収情報などを記録)
        parent_cell["harvested_count"] = harvested_count
        parent_cell["doubling_time"] = dt
        # 親細胞はもう役割を終えたのでステータスを変更しても良いが、今回はそのまま

        # 4. 子細胞 (次世代)の登録
        # 親の情報を引き継ぐ
        new_passage = parent_cell["passage"] + 1
        cell_type = parent_cell["cell_type"]

        # add_cellを再利用して登録 (PDLは計算済みの新しい値をセットする必要があるため、少し工夫が必要)
        # ここでは直接辞書を作って追加する
        new_id = str(uuid.uuid4())[:8]
        today = datetime.now().strftime("%Y-%m-%d")

        new_cell = {
            "cell_type": cell_type,
            "id": new_id,
            "parent_id": parent_id,     # 親のIDを記録！これがツリーの元になる
            "label": label,
            "date": today,
            "passage": new_passage,
            "seeded_count": int(seeded_count),
            "harvested_count": None,    # まだ回収していない
            "pdl": new_pdl,             # 積算PDLを引き継ぐ
            "doubling_time": None,
            "status": "active"
        }

        self.cells.append(new_cell)
        self.save_data() # 保存

        return new_cell
    
    def get_all_cells(self):
        """
        全データを返す
        """
        return self.cells
    
    def save_data(self):
        """
        現在のself.cellsの内容をJSONファイルに保存する
        """
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cells, f, indent=4, ensure_ascii=False)
            # print("データ保存完了") # デバッグ用
        except Exception as e:
            print(f"✖ 保存エラー: {e}")
    
    def load_data(self):
        """
        JSONファイルがあれば読み込んでself.cellにセットする
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.cells = json.load(f)
                print(f"{len(self.cells)}件のデータを読み込みました。")
            except Exception as e:
                print(f"✖ 読み込みエラー: {e}")
                self.cells = []
        else:
            print("🆕 新規データファイルを作成します。")
            self.cells = []

    def render_lineage_graph(self, cell_list):
        """
        細胞リストを受け取り、Graphvizのグラフオブジェクトを返す関数
        """
        # Graphvizのグラフ定義
        graph = graphviz.Digraph()
        graph.attr(rankdir='LR')    # 左から右へ流れるように配置 (縦が良い場合は削除)

        # ノードとエッジの作製
        for cell in cell_list:
            # ノードの追加 (ラベルには細胞名を表示)
            # shape='box'で見やすく、style='filled'などで色付けも可能
            graph.node(cell['id'], label=cell['label'], shape='box', style='rounded')

            # 親がいる場合はエッジ(線をつなぐ)
            if cell.get('parent_id'):
                graph.edge(cell['parent_id'], cell["id"])
        return graph
    
    # 細胞の削除メソッド
    def delete_cell(self, cell_id):
        """
        指定されたIDの細胞を削除するメソッド (リスト管理版)
        """
        # 1. 子細胞がいるかチェック
        # self.cellsリストの中から、parent_id が 削除対象(cell_id) と一致するものを探す
        children = [c for c in self.cells if c.get("parent_id") == cell_id]

        if len(children) > 0:
            # 子がいるので削除拒否
            child_names = [c.get("cell_type", "不明") for c in children]
            return False, f"エラー: この細胞は子細胞 ({', '.join(child_names)}など)をもっているため削除できません。"
        
        # 2. 削除実行
        # 「削除対象のIDではないもの」だけを集めて、新しいリストにする (=削除対象だけ除外される)
        original_count = len(self.cells)
        self.cells = [c for c in self.cells if c["id"] != cell_id]

        # 念のため、本当に減ったかチェック
        if len(self.cells) == original_count:
            return False, "エラー: 指定されたIDの細胞が見つかりませんでした。"
        
        # 3. 保存
        self.save_data()

        return True, "削除に成功しました。"
    
    # 子孫を探す機能
    def get_lineage(self, root_id):
        """
        指定されたID (root_id) と、そのすべての子孫細胞のリストを返すメソッド
        """
        # 1. 根本となる親細胞を探す
        root_cell = next((c for c in self.cells if c["id"] == root_id), None)
        if not root_cell:
            return []
        
        # 2. 結果リスト (まずは親だけ入れる)
        lineage_cells = [root_cell]

        # 3. 再帰的に子を探す内部関数
        def find_children_recursive(current_parent_id):
            # parent_id が current_parent_id と一致する細胞 (=直下の子) を探す
            children = [c for c in self.cells if c.get("parent_id") == current_parent_id]

            for child in children:
                lineage_cells.append(child) # 結果に追加
                find_children_recursive(child["id"]) # ★ここが再帰！その子の子供も探しに行く

        # 4. 探索開始
        find_children_recursive(root_id)

        return lineage_cells
    
# --- 動作確認用 ---
"""
if __name__ == "__main__":
    manager = CellManager()

    #テスト: 細胞２つを追加してみる
    manager.add_cell("HeLa", "Control", 5, 500000)
    manager.add_cell("iPS-201B7", "Lot.A", 10, 10000)

    # 現在のリストを表示
    print("\n--- 現在の細胞リスト ---")
    for cell in manager.get_all_cells():
        print(cell)
"""