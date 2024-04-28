import os
from dotenv import load_dotenv

# File rulebase
from Rulebased import RuleBasedChatbot

# On web framework
from flask import Flask, request, abort

# ingestion multiple file
import glob
from PyPDF2 import PdfReader

# File PDF Extract and vectorstor
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# AI Conversation
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

# LINE API SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()
app = Flask(__name__)

# Replace these values with your LINE Channel Access Token, Channel Secret, and OpenAI API Key\Channel access token
# Channel access token
line_bot_api = LineBotApi('Channel access token in LINE Developer')
# Channel Secret
handler = WebhookHandler('Channel Secret in LINE Developer') 

    
# Manage File PDF
def extract_text_from_pdf(pdf_files):
    text = ""
    for pdf in pdf_files:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text_raw):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len
    )
    chunk = text_splitter.split_text(text_raw)
    return chunk

def get_vectorstore(text_chunks):
    # version openai==0.27.6
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

#On LINE Application vectorstore
def handle_userinput(event, user_question, vectorstore):
    if '$' in user_question:
        chatbot = RuleBasedChatbot() # Call from Rulebased.py
        response = chatbot.respond(user_question)
        # If the user input contains a dollar sign, reply with the same message
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    else:
        # Initialize chat_history with an empty list
        chat_history = []

        # Call the conversation chain function
        response = get_conversation_chain(vectorstore)({
            'question': user_question,
            'chat_history': chat_history
        })

        # Update chat_history with the new messages
        chat_history.extend(response['chat_history'])

        # Respond to the user on LINE
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response['answer'])
        )

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
        
    return 'OK',200

def is_image(file_path):
    # Check if the file exists and has a valid image extension
    return os.path.isfile(file_path) and any(ext in file_path.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif'])

pdf_files = glob.glob('**/*.pdf', recursive=True)

text_raw = extract_text_from_pdf(pdf_files)
    
text_chunks = get_text_chunks(text_raw)
    
vectorstore = get_vectorstore(text_chunks)

#function get input of user for LINE Application
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_question = event.message.text
    handle_userinput(event, user_question, vectorstore)

if __name__ == '__main__':
    app.run()