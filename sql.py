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
    {"q": "第 1 题：请听音频并观察波形图，判断轴承当前状态", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 0},
    {"q": "第 2 题：请听音频并观察波形图，判断故障类型", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 1},
    {"q": "第 3 题：请听音频并观察波形图，判断故障类型", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 2},
    {"q": "第 4 题：请听音频并观察波形图，判断故障类型", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 3},
    {"q": "第 5 题：该振动信号与声音最符合哪类故障？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 1},
    {"q": "第 6 题：该故障表现为强周期性低频冲击，它是？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 2},
    {"q": "第 7 题：声音与波形无固定周期，随机冲击，属于？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 3},
    {"q": "第 8 题：声音平稳、波形无冲击分量，轴承状态为？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 0},
    {"q": "第 9 题：船舶传动系统轴承出现该信号，最可能是？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 1},
    {"q": "第 10 题：从时域波形与声音特征判断，故障类型为？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 2},
    {"q": "第 11 题：根据故障特征判断，该轴承发生了？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 3},
    {"q": "第 12 题：该信号表明轴承处于什么状态？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 0},
    {"q": "第 13 题：在船舶强噪声环境下，该故障最易识别的特征是？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 1},
    {"q": "第 14 题：这类故障会导致机组剧烈振动，它是？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 2},
    {"q": "第 15 题：故障特征无规律、难提取，属于？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 3},
    {"q": "第 16 题：综合声音与波形判断，设备状态为？", "options": ["正常", "内圈故障", "外圈故障", "滚动体故障"],
     "ans": 0}
]

# --- 4. 侧边栏导航 ---
st.set_page_config(page_title="轴承故障诊断练习系统", layout="wide")
st.sidebar.title("🧭 导航菜单")
page = st.sidebar.radio("请选择功能", ["📖 开始测试", "📈 成绩统计"])

users = get_all_users()
user_names = [u['username'] for u in users]
user_map = {u['username']: u['id'] for u in users}
current_user = st.sidebar.selectbox("选择当前用户", user_names)

# --- 5. 页面逻辑 ---

if page == "📖 开始测试":
    st.markdown(f"## **🎯 轴承诊断在线测试 - 考生：{current_user}**")
    st.info("说明：请结合波形图和音频选择正确答案，提交后成绩将自动记录。")

    # 使用表单包裹题目
    with st.form("quiz_form"):
        user_answers = []
        for i, q in enumerate(questions):
            st.write(f"**{q['q']}**")
            # 渲染单选框
            ans = st.radio(f"选择第 {i + 1} 题答案", q['options'], key=f"q{i}", label_visibility="collapsed")
            user_answers.append(ans)
            st.divider()

        submit_button = st.form_submit_button("✅ 提交试卷")

    if submit_button:
        # 计算得分
        score = 0
        points_per_q = 100 / len(questions)
        for i, ans in enumerate(user_answers):
            if ans == questions[i]['options'][questions[i]['ans']]:
                score += points_per_q

        save_score(user_map[current_user], score)
        st.success(f"测试完成！您的得分是：{score:.1f} 分，请前往“成绩统计”查看趋势。")

elif page == "📈 成绩统计":
    st.markdown(f"## **📊 {current_user} 的学习统计**")

    # 这里的逻辑保持你之前的绘图代码
    conn = get_db_connection()
    df = pd.read_sql("SELECT test_date, score FROM scores WHERE user_id = ? ORDER BY test_date ASC", conn,
                     params=(user_map[current_user],))
    conn.close()

    if not df.empty:
        df['test_date'] = pd.to_datetime(df['test_date'])
        df = df.reset_index(drop=True)
        df['count_label'] = (df.index + 1).astype(str) + "\n(" + df['test_date'].dt.strftime('%m-%d') + ")"

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("最新成绩", f"{df['score'].iloc[-1]:.1f}")
            st.metric("平均分", f"{df['score'].mean():.1f}")
            st.dataframe(df[['count_label', 'score']], hide_index=True)

        with col2:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['count_label'], df['score'], marker='o', color='#1f77b4', linewidth=2)
            ax.set_title(f"The trend of {current_user}'s academic performance evolution", fontweight='bold')
            ax.set_xlabel("Date", fontsize=12, fontweight='bold', labelpad=10)
            ax.set_ylabel("Score", fontsize=12, fontweight='bold', labelpad=10)
            st.pyplot(fig)
    else:
        st.warning("暂无测试数据，快去参加测试吧！")
