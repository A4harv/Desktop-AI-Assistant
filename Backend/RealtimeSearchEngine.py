from googlesearch import search
from groq import Groq 
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"{i.title}\nDescription: {i.description}\n\n"
    
    return Answer 


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month= current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data


def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load existing messages
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    # Add user's new prompt
    messages.append({"role": "user", "content": prompt.strip()})

    # Append Google Search results as system context
    search_results = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_results})

    # Optional: limit history to last 10 entries to prevent token overflow
    if len(SystemChatBot) > 10:
        SystemChatBot = SystemChatBot[-10:]

    try:
        # Call Groq API for completion
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
    #     completion = client.chat.completions.create(
    #     model="llama3-8b-8192",  # ✅ Updated model
    #     messages=SystemChatBot + messages,
    #     max_tokens=2048,
    #     temperature=0.7,
    #     top_p=1,
    #     stream=True,
    #     stop=None
    # )

    except Exception as e:
        return f"Error occurred during chat completion: {e}"

    # Collect streamed response
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    # Clean up and save updated messages
    answer = answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    # Remove last system search message to avoid growth
    SystemChatBot.pop()

    return AnswerModifier(Answer=answer)


if __name__ == "__main__":
    while True:
        prompt = input("Enter your query (or type 'exit' to quit): ")
        if prompt.strip().lower() == "exit":
            break
        elif prompt.strip() == "":
            print("Please enter a valid query.")
        else:
            print(RealtimeSearchEngine(prompt))
