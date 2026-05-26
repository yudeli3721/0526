import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")

st.title("📌 階段四終極完成版：Trello 看板")
st.caption("Google Sheets 雲端同步版本")

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet="Tasks", ttl=0)

if df is None or df.empty:
    df = pd.DataFrame(columns=["title", "status", "owner"])

st.write("### 📝 新增任務")

with st.form("task_form", clear_on_submit=True):

    title = st.text_input("任務名稱")
    status = st.selectbox("狀態", ["To Do", "In Progress", "Done"])
    owner = st.text_input("負責人")

    submit = st.form_submit_button("新增")

if submit and title and owner:

    new_row = pd.DataFrame([{
        "title": title,
        "status": status,
        "owner": owner
    }])

    df = pd.concat([df, new_row], ignore_index=True)

    conn.update(worksheet="Tasks", data=df)

    st.rerun()

st.write("---")
st.write("### 看板")

cols = st.columns(3)

statuses = ["To Do", "In Progress", "Done"]

def render(status_name):
    filtered = df[df["status"] == status_name]

    for i, row in filtered.iterrows():
        with st.container(border=True):
            st.write(row["title"])
            st.caption(row["owner"])

            new_status = st.selectbox(
                "改狀態",
                statuses,
                index=statuses.index(row["status"]),
                key=f"{i}-{status_name}"
            )

            if st.button("更新", key=f"btn-{i}-{status_name}"):

                df.loc[i, "status"] = new_status
                conn.update(worksheet="Tasks", data=df)
                st.rerun()

with cols[0]:
    st.subheader("To Do")
    render("To Do")

with cols[1]:
    st.subheader("In Progress")
    render("In Progress")

with cols[2]:
    st.subheader("Done")
    render("Done")
