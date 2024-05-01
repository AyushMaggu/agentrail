import tiktoken

def count_tokens(text):    
    encoding=tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count=len(encoding.encode(text))
    return token_count


#import nltk
#nltk.download('punkt')
    
#nltk_tokens = nltk.word_tokenize("""This is not a long piece of text, 
#but I am deliberately trying to make it long for my sample testing""")
#print(nltk_tokens)
#print("\n")
#print("Number of tokens uinsg NLTK: " ,len(nltk_tokens))

