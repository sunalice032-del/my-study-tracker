import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 解决显示问题
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


# --- 1. 数据库配置 ---
def get_db_connection():
    conn = sqlite3.connect('study.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, score REAL, test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("Alex",))
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("Bob",))
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("Sophia",))
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("Isabella",))
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("Caroline",))
        conn.commit()
    conn.close()


init_db()


# --- 2. 辅助函数 ---
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def save_score(user_id, score):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (user_id, score) VALUES (?, ?)", (user_id, score))
    conn.commit()
    conn.close()
# ABCD DBCA BCAD BDCA

# --- 3. 题目数据 ---
# 这里为了演示，我设置了简单的答案，你可以根据实际需求修改正确答案（0=A, 1=B, 2=C, 3=D）
questions = [
    {"q": "第 1 题：请听音频并观察波形图，判断轴承当前状态",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "波形平稳、声音无冲击，属于正常状态"},
    {"q": "第 2 题：请听音频并观察波形图，判断故障类型",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "2.png",
        "analysis": "高频周期性冲击，是内圈故障典型特征"},
    {"q": "第 3 题：请听音频并观察波形图，判断故障类型",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "3.png",
        "analysis": "低频强周期冲击，是外圈故障典型特征"},
    {"q": "第 4 题：请听音频并观察波形图，判断故障类型",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "4.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 5 题：声音与波形无固定周期，随机冲击，属于？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "4.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 6 题：该振动信号与声音最符合哪类故障？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "2.png",
        "analysis": "高频周期性冲击，是内圈故障典型特征"},
    {"q": "第 7 题：该故障表现为强周期性低频冲击，它是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "3.png",
        "analysis": "低频强周期冲击，是外圈故障典型特征"},
    {"q": "第 8 题：声音平稳、波形无冲击分量，轴承状态为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "波形平稳、声音无冲击，属于正常状态"},
    {"q": "第 9 题：船舶传动系统轴承出现该信号，最可能是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "2.png",
        "analysis": "高频周期性冲击，是内圈故障典型特征"},
    {"q": "第 10 题：从时域波形与声音特征判断，故障类型为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "3.png",
        "analysis": "低频强周期冲击，是外圈故障典型特征"},
    {"q": "第 11 题：该信号表明轴承处于什么状态？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "波形平稳、声音无冲击，属于正常状态"},
    {"q": "第 12 题：根据故障特征判断，该轴承发生了？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "4.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 13 题：在船舶强噪声环境下，该故障最易识别的特征是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "2.png",
        "analysis": "高频周期性冲击，是内圈故障典型特征"},
    {"q": "第 14 题：故障特征无规律、难提取，属于？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "4.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 15 题：这类故障会导致机组剧烈振动，它是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "3.png",
        "analysis": "低频强周期冲击，是外圈故障典型特征"},
    {"q": "第 16 题：综合声音与波形判断，设备状态为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "波形平稳、声音无冲击，属于正常状态"}
]

import streamlit as st

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="轴承故障诊断练习系统", layout="wide", initial_sidebar_state="collapsed")

# 自定义 CSS 让按钮变大并美化
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 200px;
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 15px;
        border: 2px solid #4CAF50;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #4CAF50;
        color: white;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 初始化状态 ---
if 'page' not in st.session_state:
    st.session_state.page = 'main_menu'


# 定义一个跳转函数
def navigate_to(page_name):
    st.session_state.page = page_name


# --- 3. 逻辑分发 ---

# A. 主菜单页面
if st.session_state.page == 'main_menu':
    st.title("🚢 轴承故障诊断练习系统")
    st.write("---")

    # 创建 2x2 布局
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📖\n开始测试"):
            navigate_to("开始测试")
            st.rerun()

    with col2:
        if st.button("📈\n历史成绩"):
            navigate_to("个人成绩统计")
            st.rerun()

    col3, col4 = st.columns(2)

    with col3:
        # 这里直接使用 link_button，因为它是外部跳转
        st.link_button("🛠️\n故障维修", "https://你的GitHub用户名.github.io/你的仓库名/")

    with col4:
        if st.button("📊\n轴承诊断"):
            navigate_to("轴承诊断")
            st.rerun()

# B. 功能页面内容
else:
    # 在功能页显示侧边栏，并提供一个返回主菜单的按钮
    st.sidebar.title("🧭 导航菜单")
    if st.sidebar.button("🏠 返回主页菜单"):
        navigate_to("main_menu")
        st.rerun()

    st.sidebar.markdown("---")

    # 侧边栏仍然保留切换功能
    current_page = st.sidebar.radio("快速切换",
                                    ["开始测试", "个人成绩统计", "轴承诊断"],
                                    index=["开始测试", "个人成绩统计", "轴承诊断"].index(st.session_state.page))

    # 同步侧边栏选择到状态
    if current_page != st.session_state.page:
        st.session_state.page = current_page
        st.rerun()

    # 根据状态渲染具体的页面内容
    if st.session_state.page == "开始测试":
        st.header("📖 轴承故障诊断测试")
        # 插入你的测试逻辑代码...

    elif st.session_state.page == "个人成绩统计":
        st.header("📈 个人成绩统计")
        # 插入你的成绩统计代码...

    elif st.session_state.page == "轴承诊断":
        st.header("📊 轴承诊断分析")
        st.write("这里是轴承诊断的具体功能模块内容。")
        
        
# --- 4. 侧边栏导航 ---
st.set_page_config(page_title="轴承故障诊断练习系统", layout="wide")
st.sidebar.title("🧭 导航菜单")
page = st.sidebar.radio("请选择功能", ["📖 开始测试", "📈 个人成绩统计", "📊 班级总体概况"])

users = get_all_users()
user_names = [u['username'] for u in users]
user_map = {u['username']: u['id'] for u in users}
current_user = st.sidebar.selectbox("选择当前用户", user_names)

st.sidebar.subheader("🛠️ 外部辅助工具")
st.sidebar.link_button(
    "🚀 进入故障维修系统",
    "https://zingy-raindrop-279dc3.netlify.app/",
    use_container_width=True, # 按钮宽度撑满侧边栏
    help="点击在新窗口中打开船舶轴承维修规划系统"
)


# --- 5. 页面逻辑 (开始测试部分 - 闯关模式) ---
if page == "📖 开始测试":
    st.markdown(f"## **🎯 轴承诊断在线测试 - 考生：{current_user}**")

    # 1. 初始化会话状态变量
    if 'current_q' not in st.session_state:
        st.session_state.current_q = 0  # 当前题号
    if 'temp_answers' not in st.session_state:
        st.session_state.temp_answers = [None] * len(questions)  # 暂存答案
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # --- 状态 A：答题中 ---
    if not st.session_state.submitted:
        q_idx = st.session_state.current_q
        q = questions[q_idx]

        # 显示进度条
        progress = (q_idx) / len(questions)
        st.progress(progress, text=f"进度：第 {q_idx + 1} / {len(questions)} 题")

        # 容器化显示题目内容
        with st.container(border=True):
            st.markdown(f"### **{q['q']}**")

            col_a, col_b = st.columns(2)
            with col_a:
                try:
                    st.image(q['img'], caption="时域波形图", use_container_width=True)
                except:
                    st.warning("图片加载中...")
            with col_b:
                try:
                    st.audio(q['audio'])
                except:
                    st.warning("音频加载中...")

            # 选择框 (设置默认值为之前选过的，方便上下题切换)
            ans = st.radio(
                "请选择答案：",
                q['options'],
                index=q['options'].index(st.session_state.temp_answers[q_idx]) if st.session_state.temp_answers[
                    q_idx] else None,
                key=f"q_radio_{q_idx}"
            )
            st.session_state.temp_answers[q_idx] = ans

        # 底部导航按钮
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])

        with col_nav1:
            if q_idx > 0:
                if st.button("⬅️ 上一题"):
                    st.session_state.current_q -= 1
                    st.rerun()

        with col_nav2:
            if q_idx < len(questions) - 1:
                if st.button("下一题 ➡️"):
                    if st.session_state.temp_answers[q_idx] is None:
                        st.error("请先选择一个答案")
                    else:
                        st.session_state.current_q += 1
                        st.rerun()
            else:
                # 最后一题显示提交按钮
                if st.button("✅ 完成并提交"):
                    if st.session_state.temp_answers[q_idx] is None:
                        st.error("请先选择最后一个答案")
                    else:
                        # 计算得分
                        score = 0
                        for i, user_ans in enumerate(st.session_state.temp_answers):
                            if user_ans == questions[i]['options'][questions[i]['ans']]:
                                score += (100 / len(questions))

                        # 保存成绩
                        save_score(user_map[current_user], score)
                        st.session_state.submitted = True
                        # 记录快照供解析使用
                        st.session_state.user_answers_snapshot = st.session_state.temp_answers
                        st.balloons()
                        st.rerun()

    # --- 状态 B：已完成测试 (显示结果与解析切换) ---
    else:
        # 如果已提交，显示切换开关
        view_mode = st.segmented_control(
            "请选择视图：",
            ["得分汇总", "答题解析详单"],
            default="得分汇总"
        )

        if view_mode == "得分汇总":
            # 重新计算一次分数显示
            final_score = 0
            for i, user_ans in enumerate(st.session_state.user_answers_snapshot):
                if user_ans == questions[i]['options'][questions[i]['ans']]:
                    final_score += (100 / len(questions))

            st.success(f"## 🎊 恭喜！{current_user} 同学完成测试")
            st.metric("最终得分", f"{final_score:.1f} 分")
            st.info("您可以切换到“答题解析详单”查看每道题的错误详情。")

            if st.button("🔄 重新开始测试"):
                st.session_state.submitted = False
                st.session_state.current_q = 0
                st.session_state.temp_answers = [None] * len(questions)
                st.rerun()


            # --- 视图 2：答题解析 (只读模式，对错自动折叠) ---

        else:

            st.markdown("### 📝 答题解析详单")

            # st.caption("提示：答对的题目已自动收起，答错的题目已为您自动展开解析。")

            for i, q in enumerate(questions):

                user_ans = st.session_state.user_answers_snapshot[i]

                correct_ans = q['options'][q['ans']]

                is_correct = (user_ans == correct_ans)

                # 动态设置标题标签

                status_icon = "✅" if is_correct else "❌"

                label_text = f"{status_icon} 第 {i + 1} 题：{q['q'][:20]}..."
                    # 核心逻辑：expanded=not is_correct (错题展开，对题收起)

                with st.expander(label_text, expanded=not is_correct):

                    st.markdown(f"#### **{q['q']}**")

                    # 媒体展示

                    c1, c2 = st.columns(2)

                    with c1:

                        try:
                            st.image(q['img'], caption="波形图", width=300)

                        except:
                            st.warning("图片加载失败")

                    with c2:

                        try:
                            st.audio(q['audio'])

                        except:
                            st.warning("音频加载失败")

                    # 结果对比

                    res_col1, res_col2 = st.columns(2)

                    with res_col1:

                        st.write(f"**您的选择：** :{'green' if is_correct else 'red'}[{user_ans}]")

                    with res_col2:

                        st.write(f"**正确答案：** :green[{correct_ans}]")

                    # 解析内容

                    st.info(f"**专家解析：** {q['analysis']}")

            if st.button("🔄 重新开始测试"):
                # 重置所有状态

                st.session_state.submitted = False

                st.session_state.current_q = 0

                st.session_state.temp_answers = [None] * len(questions)

                st.rerun()

elif page == "📈 个人成绩统计":
    st.markdown(f"## **📊 {current_user} 的学习统计**")

    conn = get_db_connection()
    df = pd.read_sql("SELECT test_date, score FROM scores WHERE user_id = ? ORDER BY test_date ASC", conn,
                     params=(user_map[current_user],))
    conn.close()

    if not df.empty:
        df['test_date'] = pd.to_datetime(df['test_date'])
        df = df.reset_index(drop=True)
        # 生成横轴标签
        df['count_label'] = (df.index + 1).astype(str) + "\n(" + df['test_date'].dt.strftime('%m-%d') + ")"

        # --- 核心修改：创建两个标签页 ---
        tab1, tab2 = st.tabs(["📋 查看成绩表格", "📈 历次成绩折线图"])

        with tab2:
            st.write("### 成绩演变趋势")
            fig, ax = plt.subplots(figsize=(10, 5))

            # 绘图逻辑
            ax.plot(df['count_label'], df['score'], marker='o', color='#1f77b4', linewidth=2)

            # 添加你要求的轴标签
            ax.set_xlabel("Date", fontsize=10, fontweight='bold')
            ax.set_ylabel("Score", fontsize=10, fontweight='bold')
            ax.set_title(f"The trend of {current_user}'s academic performance evolution", fontweight='bold')
            ax.set_ylim(0, 110)
            ax.grid(True, linestyle='--', alpha=0.5)

            # 在折线图点上标注具体分数
            for i, txt in enumerate(df['score']):
                ax.annotate(f"{txt:.0f}", (df['count_label'][i], df['score'][i]),
                            textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')

            st.pyplot(fig)

        with tab1:
            st.write("### 历史成绩明细表")
            # 整理一下表格显示，去掉原始 ID，让日期更好看
            display_df = df[['count_label', 'score', 'test_date']].copy()
            display_df.columns = ['测试场次', '得分', '具体时间']

            # 简单的统计信息
            c1, c2, c3 = st.columns(3)
            c1.metric("最高分", f"{df['score'].max():.1f}")
            c2.metric("平均分", f"{df['score'].mean():.1f}")
            c3.metric("测试总次数", len(df))

            st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.warning("暂无测试数据，快去参加测试吧！")

elif page == "📊 班级总体概况":
    st.markdown("## **📊 班级总体概况**")

    conn = get_db_connection()
    # 获取所有成绩记录
    all_scores_df = pd.read_sql("SELECT score FROM scores", conn)

    if not all_scores_df.empty:
        # 1. 顶部指标卡
        col_m1, col_m2, col_m3 = st.columns(3)
        avg_score = all_scores_df['score'].mean()
        max_score = all_scores_df['score'].max()
        total_tests = len(all_scores_df)

        col_m1.metric("全员平均分", f"{avg_score:.1f}")
        col_m2.metric("全员最高分", f"{max_score:.1f}")
        col_m3.metric("总测试人次", total_tests)

        st.divider()

        # 2. 模拟每题正确率统计
        # 注意：真实环境下需要建立一张“答题明细表”来存每一题的对错。
        # 这里我们根据平均分和题目难度，演示如何生成一个“题目正确率”柱状图。
        st.write("### 📝 各题正确率统计")

        # 构造演示数据（实际开发建议增加答题明细表）
        q_labels = [f"{i + 1}" for i in range(len(questions))]

        # 这里模拟一些数据，你可以根据真实业务逻辑计算
        import numpy as np

        accuracies = [85, 72, 65, 45] + [np.random.randint(60, 95) for _ in range(12)]

        acc_df = pd.DataFrame({
            "题目": q_labels,
            "正确率 (%)": accuracies
        })

        # 绘制柱状图
        fig_acc, ax_acc = plt.subplots(figsize=(12, 5))
        colors = ['#2ecc71' if x > 70 else '#e74c3c' for x in accuracies]  # 高于70%绿色，低于红色
        bars = ax_acc.bar(acc_df["题目"], acc_df["正确率 (%)"], color=colors)

        ax_acc.set_xlabel("Question", fontweight='bold')
        ax_acc.set_ylim(0, 100)
        ax_acc.set_ylabel("accuracy (%)", fontweight='bold')
        ax_acc.set_title("The distribution of the overall correct rate for each question", fontsize=14, fontweight='bold')

        # 在柱子上加数字
        for bar in bars:
            height = bar.get_height()
            ax_acc.text(bar.get_x() + bar.get_width() / 2., height + 1,
                        f'{height}%', ha='center', va='bottom', fontsize=9)

        st.pyplot(fig_acc)

        st.info("💡 **教学建议**：红色柱子代表正确率低于 70% 的题目，建议重点讲解相关故障特征。")

    else:
        st.warning("目前还没有任何测试记录。")

    conn.close()
