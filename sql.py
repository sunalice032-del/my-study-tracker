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
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 6 题：该振动信号与声音最符合哪类故障？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 7 题：该故障表现为强周期性低频冲击，它是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 8 题：声音平稳、波形无冲击分量，轴承状态为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 9 题：船舶传动系统轴承出现该信号，最可能是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 10 题：从时域波形与声音特征判断，故障类型为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 11 题：该信号表明轴承处于什么状态？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 12 题：根据故障特征判断，该轴承发生了？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 13 题：在船舶强噪声环境下，该故障最易识别的特征是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 1,
        "audio": "2.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 14 题：故障特征无规律、难提取，属于？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 3,
        "audio": "4.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 15 题：这类故障会导致机组剧烈振动，它是？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 2,
        "audio": "3.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"},
    {"q": "第 16 题：综合声音与波形判断，设备状态为？",
        "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
        "ans": 0,
        "audio": "1.wav",
        "img": "1.png",
        "analysis": "无规则随机冲击，是滚动体故障典型特征"}
]

# --- 4. 侧边栏导航 ---
st.set_page_config(page_title="轴承故障诊断练习系统", layout="wide")
st.sidebar.title("🧭 导航菜单")
page = st.sidebar.radio("请选择功能", ["📖 开始测试", "📈 个人成绩统计", "📊 班级总体概况"])

users = get_all_users()
user_names = [u['username'] for u in users]
user_map = {u['username']: u['id'] for u in users}
current_user = st.sidebar.selectbox("选择当前用户", user_names)

# --- 5. 页面逻辑 (开始测试部分) ---
if page == "📖 开始测试":
    st.markdown(f"## **🎯 轴承诊断在线测试 - 考生：{current_user}**")

    # 使用 Session State 记录是否已提交，以便提交后显示切换按钮
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'user_answers_snapshot' not in st.session_state:
        st.session_state.user_answers_snapshot = []

    # 如果已提交，显示切换开关
    view_mode = "原始题目"
    if st.session_state.submitted:
        view_mode = st.segmented_control(
            "选择视图模式",
            ["原始题目", "答题解析"],
            default="答题解析"
        )

    # --- 视图 1：原始题目 (表单模式) ---
    if view_mode == "原始题目":
        with st.form("quiz_form"):
            temp_answers = []
            for i, q in enumerate(questions):
                st.markdown(f"#### **{q['q']}**")

                col_a, col_b = st.columns(2)
                with col_a:
                    try:
                        st.image(q['img'], caption="时域波形图", use_container_width=True)
                    except:
                        st.warning(f"等待上传图片: {q['img']}")
                with col_b:
                    try:
                        st.audio(q['audio'])
                    except:
                        st.warning(f"等待上传音频: {q['audio']}")

                ans = st.radio(f"选择答案", q['options'], key=f"q_raw_{i}", label_visibility="collapsed")
                temp_answers.append(ans)
                st.divider()

            submit_button = st.form_submit_button("✅ 提交试卷")

        if submit_button:
            # 计算得分
            score = 0
            for i, ans in enumerate(temp_answers):
                if ans == questions[i]['options'][questions[i]['ans']]:
                    score += (100 / len(questions))

            # 保存数据
            save_score(user_map[current_user], score)
            st.session_state.submitted = True
            st.session_state.user_answers_snapshot = temp_answers  # 记录答案用于解析显示
            st.balloons()
            st.success(f"提交成功！得分：{score:.1f}。现在您可以切换到“答题解析”查看详情。")
            st.rerun()  # 刷新以显示切换按钮

    # --- 视图 2：答题解析 (只读模式，带题目内容) ---
    else:
        st.markdown("### 📝 答题解析详单")
        for i, q in enumerate(questions):
            user_ans = st.session_state.user_answers_snapshot[i]
            correct_ans = q['options'][q['ans']]
            is_correct = user_ans == correct_ans

            # 使用带有颜色的容器
            with st.container(border=True):
                st.markdown(f"**{q['q']}** {'✅' if is_correct else '❌'}")

                # 解析页面也要显示图片和音频
                c1, c2 = st.columns(2)
                with c1: st.image(q['img'], width=300)
                with c2: st.audio(q['audio'])

                # 显示对比
                col_res1, col_res2 = st.columns(2)
                col_res1.write(f"**您的选择：** :{'green' if is_correct else 'red'}[{user_ans}]")
                col_res2.write(f"**正确答案：** :green[{correct_ans}]")

                st.info(f"**解析：** {q['analysis']}")

        if st.button("🔄 重新开始测试"):
            st.session_state.submitted = False
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
