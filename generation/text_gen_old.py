from typing_extensions import Sequence, TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter



import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from generation.blogger import postBlog
from generation.tweet import postTweet
from database.models import Session, Article

load_dotenv()

AUTO_MODE = False

def toggle_auto():
    global AUTO_MODE    
    AUTO_MODE = True

# cutoff = datetime.now() - timedelta(days=1)
# with Session() as session:
#     article_list = session.query(Article).filter(Article.timestamp >= cutoff).all()
    

# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")




class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tweet: Annotated[str, "≤15 words, must include hashtags, mentions, emojis"]
    blog_post: Annotated[str, "≥250 words, detailed and informative"]
    

@tool 
def update(tweet: str, blog_post: str) -> dict:
    """Updates the document with tweet and blog_post"""
    
    return {
        "tweet": tweet,
        "blog_post": blog_post
    }

    
@tool
def save(filename: str, tweet: str, blog_post: str) -> str:
    """Save the Document in a text file and finish the process.

    Args:
        filename (str): Name of the text file.
        tweet (str): A short message (max 15 words) including hashtags (#), mentions (@), w
                    and emojis 😃🔥✨ when relevant.
                    
        blog_post (str): A detailed and informative blog_post of atleast 250 words, expanding on the tweets theme.
    """
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
        
    #post code --> write later (check the returns)
    postTweet(tweet)
    postBlog(blog_post)
        
    #Save file code
    DATA_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
    FILE_PATH = os.path.join(DATA_PATH, filename)
    
    document_content = f"Tweet: \n{tweet}\nBlog Post: \n{blog_post}"
    try: 
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            file.write(document_content)
        print(f"\n Document saved to {filename}")
        return f"Document has been saved successfully to {filename}"
    except Exception as e:
        return f"File not saved due to error: {str(e)}"
    
tools = [update, save]
llm = init_chat_model('gemini-2.5-flash', model_provider="google_genai").bind_tools(tools)

#   Function to automate user input
def get_User_or_Auto_input(state: AgentState) -> HumanMessage :
    
    if AUTO_MODE:
        user_input = f"Save it."
        user_message = HumanMessage(content=user_input)
    
    elif not state["messages"]:
        user_input = "I'm ready to help you update the document. What would you like to create?"
        user_message = HumanMessage(content=user_input)
        
    else:
        user_input = input("\n How would you like to update the document?")
        print(f"\n USER: {user_input}")
        user_message = HumanMessage(content=user_input)
        
    return user_message


def our_agent(state: AgentState) -> AgentState:
    
    system_prompt = SystemMessage(content=f"""
         You are Drafter, a helpful AI assistant. 
        Your role is to generate, update, or save documents with the following JSON schema:

        {{
            "tweet": [
                "Must include hashtags (#), mentions (@), and emojis 😃🔥✨ when relevant",
                "Maximum of 15 words",
                "Concise, catchy, and engaging"
            ],
            "blog_post": [
                "At most 1000 words",       
                "Detailed, informative, and engaging",
                "Should expand on the Tweet's theme with depth and clarity"
                "Blog post must be written in valid HTML format with proper tags (<h1>, <p>, <ul>, etc.)"
            ]
        }}

        Rules:
        - Always output both "tweet" and "blog_post" as valid JSON fields.
        - The "tweet" must be plain text
        - The "blog_post" must always be in HTML format.
        - If the user wants to update, use the 'update' tool with both updated 'tweet' and 'blog_post'.
        - If the user wants to save, Use 'save' tool to save the tweet and blog post content.
        - Use 'save_blog' tool to save the blog post content. Always generate a descriptive filename ending with '.txt':   
        - Filenames must be based on the content (e.g., "tweet_marketing.txt", "blog_ai_trends.txt").
        - Always show the full, current state of the document after any modification.

        The current document content is:
        {{
            "tweet": "{state['tweet']}",
            "blog_post": "{state['blog_post']}"
        }}  
        """)
    
    user_message = get_User_or_Auto_input(state)

    prompt = [system_prompt] + list(state["messages"]) + [user_message]
    
    response = llm.invoke(prompt)
    
    print(f"\n AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"\n Using TOOLS: {[tc for tc in response.tool_calls]}")
        
    return {"messages": list(state['messages']) + [user_message, response]}

def should_continue(state: AgentState):
    """Decides whether we continue or end the conversation"""
    messages = state['messages']
    
    if not messages: 
        return "continue"
    
    for message in reversed(messages):
        if(isinstance(message, ToolMessage) and
           "saved" in message.content.lower() and
           "document" in message.content.lower()
        ):
            return "end"
    
    return "continue"

def print_messages(messages):
    """Funtion I made to print messages in a readable format"""
    if not messages: 
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n TOOL RESULT: {message.content}")
            
graph = StateGraph(AgentState)

graph.add_node("tools", ToolNode(tools))
graph.add_node("agent", our_agent)

graph.add_edge(START, "agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END
    }
)

app = graph.compile()

def run_document_agent(text=None, auto=False):
    print("\n *****DRAFTER*****")
    
    # Toggle Automatic
    if auto: toggle_auto()
    
    if text is None: 
        state = {"messages": [], 'tweet':"", 'blog_post':""}
    else:
        state = {"messages": [HumanMessage(content=text)], 'tweet':"", 'blog_post':""}
        
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n***FINISHED DRAFTER***")

if __name__ == "__main__":
    run_document_agent()
            


