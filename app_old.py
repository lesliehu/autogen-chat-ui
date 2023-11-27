import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent
st.write("# AutoGen Chat Agents")

class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

selected_model = None
selected_key = None

with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo-1106', 'gpt-4'], index=1)
    selected_key = st.text_input("API Key", type="password")

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Type something...")
    if user_input:
        if not selected_key or not selected_model:
            st.warning(
                'You must provide valid OpenAI API key and choose preferred model', icon="⚠️")
            st.stop()

        llm_config = {
            "request_timeout": 600,
            "config_list": [
                {
                    "model": selected_model,
                    "api_key": selected_key
                }
            ]
        }


   # create an AssistantAgent instance named "assistant"
        assistant = TrackableAssistantAgent(
            name="assistant", llm_config=llm_config)
    # create an AssistantAgent instance named "writer"
        writer = TrackableAssistantAgent(
            name="Writer", llm_config=llm_config,
            system_message="""Writer. Help the User_Proxy analyse the articles. Synthesize the Articles"""
            )
        proof_reader = TrackableAssistantAgent(
            name="Proof_Reader", llm_config=llm_config,
            system_message="""Proof_Reader. Help the writer and the user_proxy proofread the articles."""
            )

        # create a UserProxyAgent instance named "user"
        user_proxy = TrackableUserProxyAgent(
            name="user", human_input_mode="ALWAYS", llm_config=llm_config,
            code_execution_config=True,
            system_message="""Manager. Administrate the agents on a plan. Communicate with the proofreader to proofread the output. 
            Communicate with the writer to analyse the content and ask for it to give a summary. 
                Reply CONTINUE, or the reason why the task is not solved yet."""
            )
            

        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

# Define an asynchronous function
        async def initiate_chat():
            await user_proxy.a_initiate_chat(
                assistant,
                message=user_input,
            )

        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())
