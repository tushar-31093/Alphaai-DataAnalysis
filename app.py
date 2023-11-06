import streamlit as st
import openai
from io import StringIO
import pandas as pd

if "data_file" not in st.session_state:
    st.session_state.data_file = None

# Title
st.markdown(
    """
    <h1 style="color: blue; text-align: right; 
        font-size: 48px; 
        text-shadow: 2px 2px 2px LightBlue;">Data to text</h1> 
        <p style="color: blue; text-align: right">Load your data and ask anything</p>
    <hr/>
    """,
    unsafe_allow_html=True,
)

with st.expander("See instructions for use"):
    st.markdown(
        """
        <h4>Instructions</h4>
        <p>
    The app allows you to upload a CSV files an ask ChatGPT questions about it. But first you must 
    enter a valid OpenAI API key. Then you should choose a file using the upload widget in the sidebar.
    </P>
    <p>
    You could for example ask ChatGPT to give you a summary of the data in the CSV or make a calculation 
    from the data in the rows and columns, e.g. what is the total/average/etc. of a column.
    You can even ask it to write a report or article based on the data.
    </p>
    <p>
    If the subject of the data is not clear from the table itself, you can tell ChatGPT
    what is is about in a prompt, e.g. "The data concerns the voting intentions of UK citizens 
    in various age groups if there were to be another referendum on membership of the EU"
    </p>
    <p>
    The app remembers the previous questions that you have asked and so if you do not get the answer
    that you wanted you can refine the question in a subsequent prompt.

    """,
        unsafe_allow_html=True,
    )

st.markdown(
    """<p style="color:red;font-size: 18px;font-weight:bold">You must enter a valid OpenAI API key in order to use this app and any usage 
will be billed to your OpenAI account. This token will be stored only for the duration of this session.</p>""",
    unsafe_allow_html=True,
)
openai.api_key = st.text_input("API key")

# initialise the system prompt
prompt_template = ""

with st.sidebar:
  st.sidebar.image("aai_white.png", use_column_width=True)
  chosen_file = st.file_uploader("Choose a file")
  if st.session_state.data_file != chosen_file:
      st.session_state.data_file = chosen_file
      # Convert to a string based IO:
      stringio = StringIO(st.session_state.data_file.getvalue().decode("utf-8"))
      # To read file as string:
      csv_data = stringio.read()

      st.header("Data")
      st.markdown(
          f"""<div style="color: blue; text-align: right;">Reading: {st.session_state.data_file.name}</div>""",
          unsafe_allow_html=True,
      )

      # Set the instructions
      prompt_template = f"""
      The following text enclosed in angle brackets, <>, is a CSV file. The first line contains the column headings and the rest is the actual data.

      <{csv_data}>
      """
      # Initialize chat history
      st.session_state.messages = [{"role": "system", "content": prompt_template}]
  if st.session_state.data_file != None:
      st.dataframe(pd.read_csv(chosen_file))

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": prompt_template}]
else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

if query := st.chat_input("Enter your query:"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=st.session_state.messages, temperature=0
    )
    with st.chat_message("assistant"):
        # print(response.choices[0].message.content)
        st.markdown(response.choices[0].message.content)
        st.session_state.messages.append(response.choices[0].message)

    # Download latest response
    st.download_button(
        label="Download result",
        data=response.choices[0].message.content,
        file_name="result.txt",
        mime="text",
    )
