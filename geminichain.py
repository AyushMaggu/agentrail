from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from tokenomics import count_tokens


class geminichain:
    def __init__(self, mem='n', system_message=None,temperature=0.3):
        if mem not in ('y', 'n'):
            raise ValueError("mem must be 'y' or 'n'")
        
        self.system_message = system_message
        self.memory = ConversationBufferMemory() if mem == 'y' else None
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=temperature)
        
    def add_user_message(self, msg):
        if self.memory:
            self.memory.chat_memory.add_user_message(msg)

    def add_ai_message(self, msg):
        if self.memory:
            self.memory.chat_memory.add_ai_message(msg)
    
    def get_response(self, query):
        self.query = query
        if self.memory:
            #print(f"This is the system message that provides general instructions regarding you(AI) and the nature of the conversation : {self.system_message}.\n"
            #    f"You possess the ongoing chat history between you(AI) and Human. This is the current chat history: {self.get_chat_history()}.\n"  
            #    f"Respond to this new user question: {self.query}")
            answer = self.llm.invoke(
                f"This is the system message that provides general instructional context regarding you(AI) and the nature of the conversation : {self.system_message}.\n"
                f"You possess the ongoing chat history between you(AI) and Human user. This is the current chat history: {self.get_chat_history()}.\n"  
                f"Respond to this new user question/query given the ongoing chat context: {self.query}"
            )
            self.add_user_message(self.query)
            self.add_ai_message(answer.content)
            #print(answer.content)
        else:
            answer = self.llm.invoke(
                f"This is the system message that provides general instructions regarding you(AI) and the nature of the conversation : {self.system_message}."  
                f"Respond to this new user input: {self.query}"
            )
            
        #print(answer.content)
        return answer.content
        

    def get_chat_history(self):
        return str(self.memory.chat_memory) if self.memory else "No memories available. Input mem='y' in the Geminichain object to save memories"

    
    def set_system_message(self, system_message):
        self.system_message = system_message
        #return f"{system_message}"

    
    def get_last_ai_msg(self):
        given_string =  self.get_chat_history()
        # Find the start and end index of the AIMessage content
        aimessage_start = given_string.find('AIMessage(content=')
        aimessage_end = given_string.find(')]', aimessage_start)

        if aimessage_start != -1 and aimessage_end != -1:
            aimessage_content = given_string[aimessage_start + len('AIMessage(content=') + 1: aimessage_end - 1]
            #print(aimessage_content)
        else:
            aimessage_content=None
            print("No AIMessage content found.")
        return aimessage_content
    

    def get_token_count(self,query):
        self.final_prompt = str(self.system_message)+"\n"+str(self.memory.chat_memory)+"\n"+query
        return count_tokens(self.final_prompt)

    


