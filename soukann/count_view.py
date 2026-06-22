import os
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import japanize_matplotlib

def calc_metrics_and_plot(file_name, group_name, color, line_style):
    if not os.path.exists(file_name):
        print(f"❌ ファイルが見つかりません: {file_name}")
        return

    # 1. データの読み込み
    df = pd.read_csv(file_name)
    df_clean = df.dropna(subset=['view_count', 'comment_count']).copy()

    X = df_clean[['view_count']].values
    y = df_clean['comment_count'].values

    # 2. 相関係数 (r) と 決定係数 (R²) の計算
    corr = df_clean['view_count'].corr(df_clean['comment_count'])
    
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)

    print(f"📊 【{group_name}】")
    print(f"  ・相関係数 (r) : {corr:.4f}")
    print(f"  ・決定係数 (R²): {r2:.4f}")
    print("-" * 40)

    # 3. グラフの描画と保存（既存のスライド画像に数値を載せるイメージ）
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(X, y, color=color, alpha=0.5, label=f'{group_name} 実際の動画データ')
    ax.plot(X, y_pred, color=color, linestyle=line_style, linewidth=2, label='回帰直線')
    
    # グラフの隅に相関係数をプロット（これが教授ウケします）
    textstr = f'$r = {corr:.3f}$\n$R^2 = {r2:.3f}$'
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title(f"{group_name}：再生回数とコメント数の回帰・相関分析")
    ax.set_xlabel("再生回数（回）")
    ax.set_ylabel("コメント数（件）")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: "{:,}".format(int(val))))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right')

    output_img = f"{group_name.lower()}_correlation_result.png"
    plt.tight_layout()
    plt.savefig(output_img, dpi=300)
    plt.close()

def main():
    current_dir = pathlib.Path(__file__).parent.resolve()
    os.chdir(current_dir)

    print("⏳ 再生回数とコメント数の相関分析を開始します...")
    calc_metrics_and_plot('TJ_regular_language_analysis.csv', 'TravisJapan', '#ff7f0e', '-')
    calc_metrics_and_plot('ST_regular_language_analysis.csv', 'SixTONES', '#333333', '--')
    print("🎉 分析とグラフの更新が完了しました！")

if __name__ == '__main__':
    main()