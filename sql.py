import streamlit as st
import sqlite3  # 改用内置的 sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# --- 1. 数据库连接配置 (改为 SQLite) ---
def get_db_connection():
    # 在当前目录创建一个名为 study.db 的文件
    conn = sqlite3.connect('study.db', check_same_thread=False)
    # 让查询结果可以通过字段名访问（类似字典）
    conn.row_factory = sqlite3.Row
    return conn


# --- 新增：初始化数据库表 ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        )
    ''')
    # 创建成绩表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score REAL,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 如果没用户，默认加一个
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username) VALUES (?)", ("测试学生",))
    conn.commit()
    conn.close()


# 运行初始化
init_db()


# --- 2. 获取所有用户列表 ---
def get_all_users():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        return cursor.fetchall()
    finally:
        conn.close()


# --- 3. 获取指定用户的历史成绩 ---
def get_user_scores(user_id):
    conn = get_db_connection()
    try:
        query = "SELECT test_date, score FROM scores WHERE user_id = ? ORDER BY test_date ASC"
        df = pd.read_sql(query, conn, params=(user_id,))
        if not df.empty:
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            df['test_date'] = pd.to_datetime(df['test_date'])
        return df
    except Exception as e:
        st.error(f"读取异常: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


# --- 4. Streamlit 网页界面 ---
st.set_page_config(page_title="学习成绩统计系统", layout="wide")
st.markdown("## **📈 个人学习统计与成绩趋势**")

users = get_all_users()
user_names = [u['username'] for u in users]
user_map = {u['username']: u['id'] for u in users}

st.sidebar.header("用户登录")
selected_user = st.sidebar.selectbox("请选择您的账号", user_names)

if selected_user:
    u_id = user_map[selected_user]
    st.subheader(f"欢迎回来，{selected_user}！")
    df = get_user_scores(u_id)

    if not df.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("### 历史成绩明细")
            st.dataframe(df, use_container_width=True)
            st.metric("平均分", round(df['score'].mean(), 2))

        with col2:
            st.write("### 成绩波动折线图")
            # 处理横坐标：第N次 (日期)
            df = df.reset_index(drop=True)
            df['count_label'] = (df.index + 1).astype(str) + "次\n(" + df['test_date'].dt.strftime('%m-%d') + ")"

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['count_label'], df['score'], marker='o', color='#1f77b4', linewidth=2)
            ax.set_title(f"{selected_user} 的成绩演变趋势", fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)
    else:
        st.info("该用户目前还没有测试记录。")

# --- 5. 添加新成绩 ---
st.divider()
st.markdown("### **📝 录入新测试成绩**")
new_score = st.number_input("本次测试分数", min_value=0.0, max_value=100.0, step=0.5)
if st.button("提交成绩"):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # SQLite 占位符是 ?
        cursor.execute("INSERT INTO scores (user_id, score) VALUES (?, ?)", (user_map[selected_user], new_score))
        conn.commit()
        st.success("成绩已保存！请手动刷新页面查看。")
    finally:
        conn.close()
# # streamlit run sql.py
# import streamlit as st
# import sqlite3  # 替换 pymysql
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # 数据库连接改为 SQLite
# def get_db_connection():
#     # 这会在当前目录下创建一个 study.db 文件
#     conn = sqlite3.connect('study.db', check_same_thread=False)
#     conn.row_factory = sqlite3.Row # 使其支持字典格式读取
#     return conn
#
# # 初始化数据库（如果表不存在则创建，方便云端直接运行）
# def init_db():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)''')
#     cursor.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, user_id INTEGER, score REAL, test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     # 预设一个测试用户
#     cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (1, '测试学生')")
#     conn.commit()
#     conn.close()
#
# init_db()
#
# # ... 后续的 get_user_scores 等函数中，
# # 把 SQL 语句里的 %s 统一替换为 ? (这是 SQLite 的占位符)
# # 例如：cursor.execute("SELECT ... WHERE user_id = ?", (user_id,))
# # 解决中文显示问题
# plt.rcParams['font.sans-serif'] = ['SimHei'] # Windows 常用黑体
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#
# #
# # # --- 1. 数据库连接配置 ---
# # def get_db_connection():
# #     return pymysql.connect(
# #         host='127.0.0.1',
# #         user='root',
# #         password='1111',  # 替换为你的数据库密码
# #         database='study_tracker',
# #         charset='utf8mb4',
# #         cursorclass=pymysql.cursors.DictCursor
# #     )
#
#
# # --- 2. 获取所有用户列表 ---
# def get_all_users():
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT id, username FROM users")
#             return cursor.fetchall()
#     finally:
#         conn.close()
#
#
# # --- 3. 获取指定用户的历史成绩 ---
# # def get_user_scores(user_id):
# #     conn = get_db_connection()
# #     try:
# #         # 查询该用户的所有成绩，按时间升序排列
# #         query = "SELECT test_date, score FROM scores WHERE user_id = %s ORDER BY test_date ASC"
# #         df = pd.read_sql(query, conn)
# #         return df
# #     finally:
# #         conn.close()
# # def get_user_scores(user_id):
# #     conn = get_db_connection()
# #     try:
# #         query = "SELECT test_date, score FROM scores WHERE user_id = %s ORDER BY test_date ASC"
# #         # 重要：通过 params 传递参数，确保 SQL 正确转义
# #         df = pd.read_sql(query, conn, params=(user_id,))
# #
# #         # --- 新增下面这一行：强制转换 score 列为数字 ---
# #         if not df.empty:
# #             df['score'] = pd.to_numeric(df['score'], errors='coerce')
# #
# #         return df
# #     finally:
# #         conn.close()
#
# import pandas as pd
# import pymysql
# from decimal import Decimal
#
#
# def get_user_scores(user_id):
#     conn = get_db_connection()
#     try:
#         # 1. 使用原生游标执行查询
#         with conn.cursor() as cursor:
#             query = "SELECT test_date, score FROM scores WHERE user_id = ? ORDER BY test_date ASC"
#             cursor.execute(query, (user_id,))
#             result = cursor.fetchall()  # 获取到的是字典列表: [{'test_date': ..., 'score': ...}, ...]
#
#         # 2. 将结果转换为 DataFrame
#         df = pd.DataFrame(result)
#
#         if not df.empty:
#             # --- 关键修正：强制转换类型 ---
#
#             # 将 DECIMAL (Decimal对象) 转换为 float (数字)
#             df['score'] = pd.to_numeric(df['score'], errors='coerce')
#
#             # 将 TIMESTAMP 转换为 Pandas 的 Datetime 格式
#             df['test_date'] = pd.to_datetime(df['test_date'])
#
#             # 检查转换后是否有空值并剔除
#             df = df.dropna(subset=['score'])
#
#         return df
#     except Exception as e:
#         st.error(f"数据库读取异常: {e}")
#         return pd.DataFrame()
#     finally:
#         conn.close()
#
# # --- 4. Streamlit 网页界面 ---
# st.set_page_config(page_title="学习成绩统计系统", layout="wide")
#
# st.title("📈 个人学习统计与成绩趋势")
#
# # 侧边栏：免密登录选择
# users = get_all_users()
# user_names = [u['username'] for u in users]
# user_map = {u['username']: u['id'] for u in users}
#
# st.sidebar.header("用户登录")
# selected_user = st.sidebar.selectbox("请选择您的账号", user_names)
#
# if selected_user:
#     u_id = user_map[selected_user]
#     st.subheader(f"欢迎回来，{selected_user}！")
#
#     # 获取数据
#     df = get_user_scores(u_id)
#
#     if not df.empty:
#         # 数据展示布局
#         col1, col2 = st.columns([1, 2])
#
#         with col1:
#             st.write("### 历史成绩明细")
#             st.dataframe(df, use_container_width=True)
#
#             # 简单的统计指标
#             st.metric("平均分", round(df['score'].mean(), 2))
#             st.metric("最高分", df['score'].max())
#
#         with col2:
#             st.write("### 成绩波动折线图")
#
#             # --- 新增逻辑：生成“第N次(日期)”的标签 ---
#             # 1. 重置索引以获取从 0 开始的数字，加 1 得到次数
#             df = df.reset_index(drop=True)
#             df['count_label'] = (df.index + 1).astype(str) + "次\n(" + df['test_date'].dt.strftime('%m-%d') + ")"
#
#             # 使用 Matplotlib 绘图
#             fig, ax = plt.subplots(figsize=(10, 5))
#
#             # 注意：这里横坐标换成了新生成的 'count_label'
#             ax.plot(df['count_label'], df['score'], marker='o', linestyle='-', color='#1f77b4', linewidth=2)
#
#             # 美化图表
#             ax.set_xlabel("测试次数 (日期)")
#             ax.set_ylabel("分数")
#             ax.set_title(f"{selected_user} 的成绩演变趋势", fontweight='bold')
#             ax.grid(True, linestyle='--', alpha=0.3)
#
#             # 如果数据点很多，可以适当旋转坐标轴文字
#             plt.xticks(rotation=0)
#
#             st.pyplot(fig)
#     else:
#         st.info("该用户目前还没有测试记录。")
#
# # --- 5. 添加新成绩的功能 ---
# st.divider()
# st.subheader("📝 录入新测试成绩")
# new_score = st.number_input("本次测试分数", min_value=0.0, max_value=100.0, step=0.5)
# if st.button("提交成绩"):
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = "INSERT INTO scores (user_id, score) VALUES (%s, %s)"
#             cursor.execute(sql, (user_map[selected_user], new_score))
#         conn.commit()
#         st.success("成绩已保存！刷新页面即可查看更新后的折线图。")
#     except Exception as e:
#         st.error(f"保存失败: {e}")
#     finally:
#         conn.close()
