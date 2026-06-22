import os
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import japanize_matplotlib

def calc_duration_metrics(file_name, group_name, color, line_style):
    if not os.path.exists(file_name):
        print(f"❌ ファイルが見つかりません: {file_name}")
        return

    # 1. データの読み込み
    df = pd.read_csv(file_name)
    df_clean = df.dropna(subset=['duration_sec', 'view_count']).copy()

    # 秒を「分」に変換（スライドの条件に合わせる）
    df_clean['duration_min'] = df_clean['duration_sec'] / 60.0

    X = df_clean[['duration_min']].values
    y = df_clean['view_count'].values

    # 2. 相関係数 (r) と 決定係数 (R²) の計算
    corr = df_clean['duration_min'].corr(df_clean['view_count'])
    
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)

    print(f"📊 【{group_name}】")
    print(f"  ・動画時間と再生回数の相関係数 (r) : {corr:.4f}")
    print(f"  ・決定係数 (R²): {r2:.4f}")
    print("-" * 40)

    # 3. グラフの描画と保存
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(X, y, color=color, alpha=0.5, label=f'{group_name} 実際の動画データ')
    ax.plot(X, y_pred, color=color, linestyle=line_style, linewidth=2, label='回帰直線')
    
    # グラフの隅に相関係数をプロット
    textstr = f'$r = {corr:.3f}$\n$R^2 = {r2:.3f}$'
    ax.text(0.75, 0.95, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title(f"{group_name}：動画時間と再生回数の回帰・相関分析")
    ax.set_xlabel("動画の長さ（分）")
    ax.set_ylabel("再生回数（回）")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')

    output_img = f"{group_name.lower()}_duration_correlation.png"
    plt.tight_layout()
    plt.savefig(output_img, dpi=300)
    plt.close()

def main():
    # パスの自動調整
    current_dir = pathlib.Path(__file__).parent.resolve()
    os.chdir(current_dir)

    print("⏳ 動画時間と再生回数の相関分析を開始します...")
    calc_duration_metrics('TJ_regular_language_analysis.csv', 'TravisJapan', '#ff7f0e', '-')
    calc_duration_metrics('ST_regular_language_analysis.csv', 'SixTONES', '#333333', '--')
    print("🎉 分析完了！新しいグラフ画像を保存しました。")

if __name__ == '__main__':
    main()