import math

def calculate_pdl(seeded, harvested, previous_pdl):
    """
    播種数、回収数、前回のPDLを受け取り、
    今回のPDL増加分と、新しい関さんPDLを返す関数
    """
    # ゼロ除算を防ぐための安全策 (もし播種数が0なら計算できない)
    if seeded <= 0 or harvested <= 0:
        return 0.0, previous_pdl

    # ここに計算式を書く
    new_pdl = 3.322 * math.log10(harvested / seeded) + previous_pdl
    delta_pdl = new_pdl - previous_pdl
    # return delta_pdl, new_pdl (2つの値を返すと便利です)
    return delta_pdl, new_pdl

def calculate_doubling_time(hours, delta_pdl):
    """
    培養時間(時間単位)とPDL増加分を受け取り、
    倍加時間を返す関数
    """
    #PDLが増えていない (0以下)場合は計算できないのでNoneを返すなどの処理
    if delta_pdl <= 0:
        return None

    # ここに計算式を書く
    doubling_time = hours / delta_pdl
    return doubling_time

# --- 動作確認用 ---
if __name__ == "__main__":
    #ここで適当な数字を入れてテストしてみてください
    # 例: 50万個撒いて、48時間後に200万個になった場合
    s = 500000
    h = 2000000
    prev_pdl = 10.0
    hours = 48

    # 関数を呼び出してprintを結果を表示するコード
    delta, current_pdl = calculate_pdl(s, h, prev_pdl)
    dt = calculate_doubling_time(hours, delta)

    # 結果の表示 (f-stringを使うと綺麗に見えます)
    print(f"--- 計算結果 ---")
    print(f"播種数: {s}, 回収数: {h}")
    print(f"増加PDL: {delta:.2f}")      # 小数点第二位まで表示
    print(f"現在PDL: {current_pdl:.2f}")
    print(f"倍加時間: {dt:.2f} 時間")
