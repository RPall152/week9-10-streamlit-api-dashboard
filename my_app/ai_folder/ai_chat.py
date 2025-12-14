import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ai_chat(system_prompt: str, placeholder: str):
    page_key = f"chat_{system_prompt[:20]}"

    if page_key not in st.session_state:
        st.session_state[page_key] = [
            {"role": "system", "content": system_prompt}
        ]

    for msg in st.session_state[page_key]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    prompt = st.chat_input(placeholder)

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state[page_key].append(
            {"role": "user", "content": prompt}
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state[page_key]
        ).choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state[page_key].append(
            {"role": "assistant", "content": response}
        )

def ai_summary_button(button_label: str, system_prompt: str, data_description: str):
    if st.button(button_label):
        with st.spinner("AI is analysing the data..."):
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Here is a summary of the analytics data:\n{data_description}"
                    }
                ]
            )

            summary = completion.choices[0].message.content
            st.success("AI Summary")
            st.markdown(summary)

