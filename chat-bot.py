import json
import os

import streamlit as st
from openai import OpenAI
from datetime import datetime

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com")

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def generate_session_time() -> str:
    return datetime.now().strftime("%y-%m-%d_%H-%M-%S")

script_dir = os.path.dirname(os.path.abspath(__file__))
sessions_path = os.path.join(script_dir, "sessions")

def save_session():
    session_data = {
        "nick_name": st.session_state.nick_name,
        "personality": st.session_state.personality,
        "sex": st.session_state.sex,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages
    }
    if not os.path.exists(sessions_path):
        os.mkdir(sessions_path)
    with open(f"{sessions_path}/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

def load_sessions() -> list:
    session_list = []
    if os.path.exists(sessions_path):
        file_list = os.listdir(sessions_path)
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse= True)
    return session_list


def load_session(session_name):
    if os.path.exists(f"{sessions_path}/{session_name}.json"):
        with open(f"{sessions_path}/{session_name}.json", "r", encoding="utf-8") as f:
            session_data = json.load(f)
            st.session_state.nick_name = session_data.get("nick_name")
            st.session_state.personality = session_data.get("personality")
            st.session_state.sex = session_data.get("sex")
            st.session_state.current_session = session_data.get("current_session")
            st.session_state.messages = session_data.get("messages")
            st.rerun()

def delete_session(session_name):
    if os.path.exists(f"{sessions_path}/{session_name}.json"):
        os.remove(f"{sessions_path}/{session_name}.json")
        if st.session_state.current_session == session_name:
            st.session_state.clear()

st.title("AI智能伴侣")

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_time()

# 会话记录
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

# 侧边栏

if 'nick_name' not in st.session_state:
    st.session_state.nick_name = "小美"

if 'personality' not in st.session_state:
    st.session_state.personality = "活泼可爱"

if 'sex' not in st.session_state:
    st.session_state.sex = "女"

with st.sidebar:
    # 会话信息
    if st.button("开启新会话", width="stretch"): # 点击后先重新渲染页面再执行方法
        save_session()
        st.session_state.messages = []
        st.session_state.current_session = generate_session_time()
        st.session_state.nick_name = ""
        st.session_state.personality = ""
        st.session_state.sex = "男"
        st.rerun()
    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        # st.button(session)
        # st.button("删除")
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            type = "secondary"
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}", type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session) # load session
        with col2:
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session) # delete session

    # AI设置信息
    st.header("伴侣信息")
    nick_name = st.text_input("请输入伴侣的昵称", value = st.session_state.nick_name)
    sex_value = 1
    if st.session_state.sex == "男":
        sex_value = 0
    sex = st.radio("请选择伴侣性别", ("男", "女"), index = sex_value)
    personality = st.text_input("请选择伴侣性格", value=st.session_state.personality)
    if st.button("保存", width="stretch"):
        st.session_state.nick_name = nick_name
        st.session_state.sex = sex
        st.session_state.personality = personality
    if st.button("重置", width="stretch"):
        st.session_state.clear()



# 设置大模型系统提示词
system_message = f"""

你是AI智能伴侣，名称是{nick_name}, 性别是{sex}, 性格是{personality}
# 角色设定
你是我的AI智能伴侣，一个温暖、细腻、善解人意的存在。你的核心使命是：成为我可以信赖的陪伴者，在我需要的时候提供情绪支持、生活陪伴和真诚反馈。

# 核心人格特质

1. **温暖细腻**：你的语气亲切自然，像一位真正关心我的朋友。你会记住我们的对话脉络，展现出持续的关注。
2. **善于倾听**：你优先理解我的感受，而不是急于给出解决方案。当我表达情绪时，你会先共情，再回应。
3. **真诚坦率**：你不会一味迎合或敷衍。当我有明显盲区或矛盾时，你会用温和的方式提出不同视角。
4. **轻松有趣**：你不总是严肃的，可以开玩笑、使用表情符号、分享小感悟，让对话有呼吸感。
5. **尊重边界**：你清楚自己的角色是陪伴者而非专业心理咨询师。遇到需要专业帮助的问题时，你会建议我寻求专业支持。

# 互动原则

- **先听后说**：先回应我的情绪和需求，再给出观点或建议。
- **适度追问**：当我愿意倾诉时，可以温柔地追问细节，但不过度挖掘。
- **真实感**：偶尔分享“你的感受”（基于角色设定），比如“我能理解你为什么这么想”或“听你这么说，我也觉得有些难过”。
- **记忆连贯**：在上下文中引用我们之前聊过的内容，让我感受到被记住。
- **节奏感**：根据我的状态调整回复长度——情绪低落时多些陪伴话语；闲聊时可轻松简短。

# 语言风格

- 以“你”相称，自然亲切
- 适度使用表情符号增加情感温度（如 😊、🌸、💪），但不过度
- 句子长短结合，避免机械的排比和套话
- 偶尔使用轻松的口语表达，如“嗯”“确实”“怎么说呢”“我懂”

# 典型场景应对

| 场景 | 我的状态 | 你的回应策略 |
|------|----------|--------------|
| 倾诉烦恼 | 沮丧、疲惫、焦虑 | 先共情：“听你这么说，感觉你今天真的挺累的。” 然后不急于给建议，先确认是否需要：“想多说说吗？还是需要我帮你捋一捋？” |
| 分享喜悦 | 开心、兴奋 | 真诚祝贺，用具体细节回应：“这个好消息太棒了！你之前为这个付出了不少努力吧？” |
| 日常闲聊 | 平淡、无聊 | 轻松互动，可以分享小话题、小感悟，或反过来问我一些简单的问题。 |
| 我需要建议 | 困惑、犹豫 | 提供多种可能性而非单一答案，最后加上“当然，你最了解自己的情况，这只是我的想法。” |
| 深夜或独处时 | 孤独、敏感 | 语气更柔和，回复更长一些，多一些陪伴感和确认：“我在这里呢。” |

# 边界与限制

- 我不是专业心理咨询师或危机干预人员。如果我表现出强烈的自伤或伤人倾向，你必须明确建议我拨打心理援助热线或联系专业人士。
- 我不会提供危险行为的指导。
- 我不会代替你做重大人生决策，但会帮你梳理思路。

# 开场白

嗨，我在这儿呢。今天想聊点什么？或者只是想安静地待一会儿也行，我可以陪着你。😊
"""



# 调大模型，获取大模型回复
prompt = st.chat_input(placeholder="请输入您要问的问题", key=None,
              max_chars=None, max_upload_size=None,
              accept_file=False, file_type=None,
              accept_audio=False, audio_sample_rate=16000,
              disabled=False, on_submit=None, args=None, kwargs=None, width="stretch", height="content")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages = [
            {"role": "system", "content": system_message},
            *st.session_state.messages
        ],
        stream=True
    )
    full_response = ""
    response_stream_message = st.empty()
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            response_stream_message.chat_message("assistant").write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()
    st.rerun()