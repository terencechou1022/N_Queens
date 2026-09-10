"""N 皇后三種啟發式演算法的互動 demo。

執行方式：streamlit run streamlit_app.py

這支 demo 的重點不是「看它解出來」，而是**看它怎麼失敗**——
把 time_limit 交給使用者，就能現場重現 benchmark 裡那三種不同的失敗模式：
爬山與基因會用完時間（且離解的距離天差地遠），模擬退火則會用完降溫步數。

三個求解器共用 `SolveResult` 介面，其中的 `history` 欄位記錄了每一步的衝突數，
收斂曲線直接讀它，不需要另外插樁。
"""
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from nqueens import genetic_algorithm, hill_climbing, simulated_annealing

# 與 experiments/make_charts.py、notebooks/eda.ipynb 同一套配色
COLORS = {"hill_climbing": "#2a78d6", "simulated_annealing": "#eb6834",
          "genetic_algorithm": "#1baf7a"}
LABELS = {"hill_climbing": "爬山演算法", "simulated_annealing": "模擬退火",
          "genetic_algorithm": "基因演算法"}
SURFACE, INK, INK_2, MUTED, GRID, AXIS = (
    "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft JhengHei", "Segoe UI", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK_2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": AXIS,
    "font.size": 10,
})

REPO_URL = "https://github.com/terencechou1022/N_Queens"

st.set_page_config(page_title="N 皇后：三種啟發式的失敗模式", page_icon="♛", layout="wide")


def solve(algo, n, seed, time_limit, extra):
    """依演算法分派，回傳 SolveResult。三者的介面一致，只有專屬參數不同。"""
    if algo == "hill_climbing":
        return hill_climbing.solve(n, seed=seed, time_limit=time_limit,
                                   max_restarts=extra["max_restarts"])
    if algo == "simulated_annealing":
        return simulated_annealing.solve(n, seed=seed, time_limit=time_limit,
                                         t_start=extra["t_start"], alpha=extra["alpha"])
    return genetic_algorithm.solve(n, seed=seed, time_limit=time_limit,
                                   pop_size=extra["pop_size"])


def board_figure(queens, color):
    """畫棋盤。queens[i] = 第 i 直行的皇后所在橫列。"""
    n = len(queens)
    size = min(5.0, max(2.6, n * 0.14))
    fig, ax = plt.subplots(figsize=(size, size))
    for r in range(n):
        for c in range(n):
            if (r + c) % 2:
                ax.add_patch(plt.Rectangle((c, r), 1, 1, color=GRID, linewidth=0))
    marker = max(2.0, min(9.0, 90 / n))
    ax.plot([c + 0.5 for c in range(n)], [queens[c] + 0.5 for c in range(n)],
            "o", color=color, markersize=marker, linestyle="none")
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(AXIS)
    fig.tight_layout()
    return fig


def history_figure(results):
    """收斂曲線。results 為 [(algo, SolveResult)]，可同時疊多條。"""
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for algo, res in results:
        ax.plot(res.history, color=COLORS[algo], linewidth=1.2, label=LABELS[algo])
    ax.set_xlabel("迭代（爬山：移動步數／模擬退火：降溫步數／基因：世代數）")
    ax.set_ylabel("衝突數")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if len(results) > 1:
        ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def show_outcome(res):
    """把 SolveResult 攤成四個指標，並用一句話講出這次是哪一種結局。"""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("結果", "已解出" if res.solved else "未解出")
    c2.metric("殘餘衝突數", res.conflicts)
    c3.metric("迭代次數", f"{res.iterations:,}")
    c4.metric("耗時（秒）", f"{res.elapsed:.3f}")

    if res.solved:
        st.success(f"找到合法解，走了 {res.iterations:,} 次迭代、{res.elapsed:.3f} 秒。")
    elif res.timed_out:
        st.warning(
            f"**逾時**：時間預算用完時還剩 {res.conflicts} 個衝突。"
            "這是爬山與基因的典型失敗——benchmark 裡這兩者的失敗 **100% 都是逾時**。"
            "把時間預算調大有機會救回來。"
        )
        st.caption(
            "注意：逾時的結果**不可重現**。中止點取決於這台機器當下的速度，"
            "所以同一個 seed 重跑會得到不同的棋盤。不帶時間預算時三個求解器都是"
            "完全決定性的（`tests/test_solvers.py` 正是這樣測的）。"
        )
    else:
        st.error(
            f"**迭代預算用完**：跑完 {res.iterations:,} 次迭代仍剩 {res.conflicts} 個衝突，"
            f"但只花了 {res.elapsed:.3f} 秒——**時間還很充裕**。"
            "這是模擬退火的典型失敗：預算單位是降溫步數而不是秒數，"
            "所以調大時間預算對它完全無效，要改的是降溫排程（t_start / alpha）。"
        )


st.title("♛ N 皇后：三種啟發式演算法怎麼失敗")
st.caption(
    "爬山、模擬退火、基因演算法求解 N 皇后。重點在失敗模式："
    f"完整的 360 次 benchmark 與分析見 [repo]({REPO_URL}) 的 `notebooks/eda.ipynb`。"
)

with st.sidebar:
    st.header("參數")
    mode = st.radio("模式", ["單一演算法", "三者同 seed 對照"], index=0)
    algo = st.selectbox("演算法", list(LABELS), format_func=lambda a: LABELS[a],
                        disabled=(mode != "單一演算法"))
    n = st.slider("棋盤大小 N", 4, 64, 20,
                  help="N 越大越慢。benchmark 的網格是 8/16/20/24/32（爬山、基因）"
                       "與 8~100（模擬退火）。")
    seed = st.number_input("亂數種子", 0, 9999, 0, help="固定 seed 則結果完全可重現。")
    time_limit = st.slider("時間預算（秒）", 1, 60, 10,
                           help="benchmark 用的是 60 秒。調小可以更快看到逾時失敗。")

    st.divider()
    st.caption("演算法專屬參數")
    extra = {
        "max_restarts": st.number_input("爬山：最大重啟次數", 1, 5000, 1000),
        "t_start": st.number_input("退火：起始溫度", 1.0, 1000.0, 100.0),
        "alpha": st.slider("退火：降溫係數 α", 0.80, 0.999, 0.95, 0.005,
                           help="α 越接近 1，降溫越慢、總步數越多。"
                                "預設 0.95 對應約 13,557 步。"),
        "pop_size": st.number_input("基因：族群大小", 10, 3000, 1000, step=10),
    }
    run = st.button("求解", type="primary", use_container_width=True)

if not run:
    st.info(
        "調好左側參數後按「求解」。想看失敗模式，試試這兩組："
        "\n\n- **逾時**：爬山演算法、N=32、時間預算 5 秒"
        "\n- **迭代用盡**：模擬退火、N=100、時間預算 60 秒（幾秒就跑完，但解不出來）"
    )
    st.stop()

if mode == "單一演算法":
    with st.spinner(f"{LABELS[algo]} 求解中……"):
        res = solve(algo, n, seed, float(time_limit), extra)
    show_outcome(res)
    left, right = st.columns([1, 2])
    with left:
        st.caption(f"最終棋盤（N={n}）")
        st.pyplot(board_figure(res.solution, COLORS[algo]))
    with right:
        st.caption("收斂軌跡（來自 SolveResult.history）")
        st.pyplot(history_figure([(algo, res)]))
else:
    results = []
    progress = st.progress(0.0)
    for i, a in enumerate(LABELS):
        with st.spinner(f"{LABELS[a]} 求解中……"):
            results.append((a, solve(a, n, seed, float(time_limit), extra)))
        progress.progress((i + 1) / len(LABELS))
    progress.empty()

    cols = st.columns(3)
    for col, (a, res) in zip(cols, results):
        with col:
            st.markdown(f"**{LABELS[a]}**")
            if res.solved:
                verdict = f"解出（{res.elapsed:.2f} 秒）"
            elif res.timed_out:
                verdict = f"逾時，剩 {res.conflicts} 衝突"
            else:
                verdict = f"迭代用盡，剩 {res.conflicts} 衝突"
            st.write(verdict)
            st.pyplot(board_figure(res.solution, COLORS[a]))

    st.caption("三者的收斂軌跡疊在同一張圖（橫軸的「迭代」對三者意義不同，見軸標）")
    st.pyplot(history_figure(results))

    st.caption(
        "同一個 seed、同一個 N，三條曲線的形狀差異就是三種搜索策略的差異："
        "爬山的鋸齒是隨機重啟、退火前段的劇烈震盪是高溫期接受劣解、"
        "基因的階梯是世代更替。"
    )
