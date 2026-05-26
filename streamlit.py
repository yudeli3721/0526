import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 基本設定
# ==========================================

st.set_page_config(layout="wide")

st.title("📌 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版")

# ==========================================
# 連接 Google Sheets
# ==========================================

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Tasks",
    ttl=0
)

# 如果試算表是空的，避免報錯
if df is None or df.empty:

    df = pd.DataFrame(
        columns=["title", "status", "owner"]
    )

# ==========================================
# 上方新增任務輸入表單
# ==========================================

st.write("### 📝 指派新任務")

with st.form("task_input_form", clear_on_submit=True):

    c_title, c_status, c_owner = st.columns([2, 1, 1])

    with c_title:

        new_title = st.text_input(
            "📌 任務名稱",
            placeholder="輸入任務名稱..."
        )

    with c_status:

        new_status = st.selectbox(
            "📂 狀態",
            ["To Do", "In Progress", "Done"]
        )

    with c_owner:

        new_owner = st.text_input(
            "👤 負責人",
            placeholder="誰來負責..."
        )

    submit_btn = st.form_submit_button(
        "確認指派並同步雲端"
    )

# ==========================================
# 新增資料
# ==========================================

if submit_btn:

    if new_title and new_owner:

        new_data = {
            "title": new_title,
            "status": new_status,
            "owner": new_owner
        }

        new_row = pd.DataFrame([new_data])

        updated_df = pd.concat(
            [df, new_row],
            ignore_index=True
        )

        conn.update(
            worksheet="Tasks",
            data=updated_df
        )

        st.success("✅ 資料已成功同步至 Google 試算表！")

        st.rerun()

    else:

        st.warning("⚠️ 請完整填寫任務名稱與負責人")

st.write("---")

# ==========================================
# Trello 三欄看板
# ==========================================

st.write("### 📊 看板動態狀態監控")

trello_col1, trello_col2, trello_col3 = st.columns(3)

status_options = [
    "To Do",
    "In Progress",
    "Done"
]

# ==========================================
# 共用卡片函式
# ==========================================

def render_cards(dataframe, current_status):

    filtered = dataframe[
        dataframe["status"] == current_status
    ]

    if not filtered.empty:

        for idx, row in filtered.iterrows():

            with st.container(border=True):

                # 任務名稱
                st.write(f"### {row['title']}")

                # 負責人
                st.caption(f"👤 負責人：{row['owner']}")

                st.write("")

                # 狀態切換
                new_status = st.selectbox(
                    "調整狀態",
                    status_options,
                    index=status_options.index(row["status"]),
                    key=f"status_{idx}"
                )

                c1, c2 = st.columns(2)

                # 更新狀態
                with c1:

                    if st.button(
                        "更新狀態",
                        key=f"update_{idx}"
                    ):

                        df.loc[idx, "status"] = new_status

                        conn.update(
                            worksheet="Tasks",
                            data=df
                        )

                        st.success("✅ 狀態已更新")

                        st.rerun()

                # 刪除任務
                with c2:

                    if st.button(
                        "🗑️ 刪除任務",
                        key=f"delete_{idx}"
                    ):

                        updated_df = df.drop(idx)

                        conn.update(
                            worksheet="Tasks",
                            data=updated_df
                        )

                        st.success("🗑️ 任務已刪除")

                        st.rerun()

    else:

        st.info("目前沒有任務")

# ==========================================
# 第一欄：To Do
# ==========================================

with trello_col1:

    st.markdown(
        """
        ### <span style='color:red'>
        📌 To Do (待辦)
        </span>
        """,
        unsafe_allow_html=True
    )

    render_cards(df, "To Do")

# ==========================================
# 第二欄：In Progress
# ==========================================

with trello_col2:

    st.markdown(
        """
        ### <span style='color:orange'>
        🚧 In Progress (執行中)
        </span>
        """,
        unsafe_allow_html=True
    )

    render_cards(df, "In Progress")

# ==========================================
# 第三欄：Done
# ==========================================

with trello_col3:

    st.markdown(
        """
        ### <span style='color:green'>
        ✅ Done (已完成)
        </span>
        """,
        unsafe_allow_html=True
    )

    render_cards(df, "Done")
```
