import os
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

def main():
    # 0. パスの自動調整（VS Code対策）
    current_dir = pathlib.Path(__file__).parent.resolve()
    os.chdir(current_dir)
    print(f"現在の実行フォルダ: {os.getcwd()}")

    # 1. データの読み込み
    tj_file = 'TJ_regular_language_analysis.csv'
    st_file = 'ST_regular_language_analysis.csv' 

    try:
        df_tj = pd.read_csv(tj_file)
        df_st = pd.read_csv(st_file)
    except FileNotFoundError as e:
        print(f"❌ CSVファイルが見つかりません。スクリプトと同じフォルダに配置してください。\nエラー: {e}")
        return

    # 2. データの割り当て（動画の長さ[秒] と 再生回数）
    x_column = 'duration_sec'   # X軸：動画の長さ
    y_column = 'view_count'     # Y軸：再生回数

    # 欠損値（空欄）のデータを除外
    df_tj_clean = df_tj.dropna(subset=[x_column, y_column]).copy()
    df_st_clean = df_st.dropna(subset=[x_column, y_column]).copy()

    # 💡 【確認完了】秒単位を「分単位」に正しく変換します
    df_tj_clean['duration_min'] = df_tj_clean[x_column] / 60.0
    df_st_clean['duration_min'] = df_st_clean[x_column] / 60.0

    # 3. グループごとに回帰分析（最小二乗法）を実行（y = w*x + b）
    X_tj = df_tj_clean['duration_min'].values
    Y_tj = df_tj_clean[y_column].values
    w_tj, b_tj = np.polyfit(X_tj, Y_tj, 1)

    X_st = df_st_clean['duration_min'].values
    Y_st = df_st_clean[y_column].values
    w_st, b_st = np.polyfit(X_st, Y_st, 1)

    # ターミナルへの結果出力
    print("\n" + "="*80)
    print(" 🎉 【グループ別 回帰分析結果】動画の長さ（分）と 再生回数 の関係性")
    print("="*80)
    print(f"🧡 Travis Japan : 再生回数 = {w_tj:.2f} * 動画時間 + {b_tj:.2f}")
    print(f"   ➔ 動画が1分長くなるごとに、再生回数が平均 【 {w_tj:.0f} 回 】 変化する傾向")
    print("-"*80)
    print(f"🖤 SixTONES     : 再生回数 = {w_st:.2f} * 動画時間 + {b_st:.2f}")
    print(f"   ➔ 動画が1分長くなるごとに、再生回数が平均 【 {w_st:.0f} 回 】 変化する傾向")
    print("="*80)

    # ==============================================================================
    # 4. 【図①】Travis Japan 単体のグラフ描画
    # ==============================================================================
    plt.figure(figsize=(10, 5))
    plt.scatter(X_tj, Y_tj, alpha=0.5, color='#ffa500', label='Travis Japan 実際の動画データ')
    
    x_line_tj = np.linspace(X_tj.min(), X_tj.max(), 100)
    y_line_tj = w_tj * x_line_tj + b_tj
    plt.plot(x_line_tj, y_line_tj, color='#d48800', linewidth=3, 
             label=f'回帰直線 (1分あたり: {w_tj:.0f}回)')

    plt.title('Travis Japan：動画時間と再生回数の回帰分析', fontsize=13, fontweight='bold')
    plt.xlabel('動画の長さ（分）', fontsize=11)
    plt.ylabel('再生回数（回）', fontsize=11)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, loc: "{:,}".format(int(y))))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10, loc='upper right')
    
    output_tj_img = 'tj_duration_views_result.png'
    plt.tight_layout()
    plt.savefig(output_tj_img, dpi=300)
    plt.close()
    print(f"📷 1/3: トラジャ個別の図を 『 {output_tj_img} 』 として保存しました。")

    # ==============================================================================
    # 5. 【図②】SixTONES 単体のグラフ描画
    # ==============================================================================
    plt.figure(figsize=(10, 5))
    plt.scatter(X_st, Y_st, alpha=0.5, color='#555555', label='SixTONES 実際の動画データ')
    
    x_line_st = np.linspace(X_st.min(), X_st.max(), 100)
    y_line_st = w_st * x_line_st + b_st
    plt.plot(x_line_st, y_line_st, color='#111111', linewidth=3, linestyle='--',
             label=f'回帰直線 (1分あたり: {w_st:.0f}回)')

    plt.title('SixTONES：動画時間と再生回数の回帰分析', fontsize=13, fontweight='bold')
    plt.xlabel('動画の長さ（分）', fontsize=11)
    plt.ylabel('再生回数（回）', fontsize=11)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, loc: "{:,}".format(int(y))))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10, loc='upper right')
    
    output_st_img = 'st_duration_views_result.png'
    plt.tight_layout()
    plt.savefig(output_st_img, dpi=300)
    plt.close()
    print(f"📷 2/3: ストーンズ個別の図を 『 {output_st_img} 』 として保存しました。")

    # ==============================================================================
    # 6. 【図③】🌟合体グラフの描画（2群の比較用）
    # ==============================================================================
    plt.figure(figsize=(11, 6))
    
    # トラジャ側のプロット
    plt.scatter(X_tj, Y_tj, alpha=0.3, color='#ffa500', label='Travis Japan (データ点)')
    plt.plot(x_line_tj, y_line_tj, color='#d48800', linewidth=3, 
             label=f'トラジャ回帰直線 (傾き: {w_tj:.0f})')
    
    # ストーンズ側のプロット
    plt.scatter(X_st, Y_st, alpha=0.3, color='#555555', label='SixTONES (データ点)')
    plt.plot(x_line_st, y_line_st, color='#111111', linewidth=3, linestyle='--',
             label=f'ストーンズ回帰直線 (傾き: {w_st:.0f})')

    plt.title('グループ別比較：動画時間と再生回数の回帰直線', fontsize=14, fontweight='bold')
    plt.xlabel('動画の長さ（分）', fontsize=12)
    plt.ylabel('再生回数（回）', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, loc: "{:,}".format(int(y))))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10, loc='upper right')
    
    output_combined_img = 'combined_duration_views_result.png'
    plt.tight_layout()
    plt.savefig(output_combined_img, dpi=300)
    plt.close()
    print(f"📷 3/3: 🌟群比較用の合体図を 『 {output_combined_img} 』 として保存しました！")

if __name__ == '__main__':
    main()