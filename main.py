import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import difflib
import os
from dotenv import load_dotenv
import requests
from openai import OpenAI
from plyer import notification
import pyautogui

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
       
recogniser = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 220)

# Function for Speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to find closest match of the song requested in command
def findClosestSong(requested_song, library):
    matches = difflib.get_close_matches(requested_song, library.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

# Function to get command.
def getWakeWord():
    wake_word = " "
    while wake_word == " ":
        r = sr.Recognizer()
        print("recognising...")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = r.listen(source, timeout=2, phrase_time_limit=2)
                # print(audio)
            wake_word = r.recognize_google(audio, language="en-in")
            print(wake_word)
        except Exception as e:
            print("Error; {0}".format(e))
    return wake_word

# Function to handle open command
def handleOpenCommand(c):
    query = c.replace("open", "")
    try:
        if "open google" in c.lower():
            webbrowser.open("https://google.com")
        elif "open instagram" in c.lower():
            webbrowser.open("https://instagram.com")
        elif "open spotify" in c.lower():
            webbrowser.open("https://spotify.com")
        elif "open youtube" in c.lower():
            webbrowser.open("https://youtube.com")
        elif "open linkedin" in c.lower():
            webbrowser.open("https://linkedin.com")
        else :
            pyautogui.press("super")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")

    except Exception as e:
        print("Error; {0}".format(e)) 

# Function to get list name
def getListName(command):
    words = command.split()
    index = words.index("list")
    return words[index-1]

# Function to add task inside the list
def addTask(listName):
    speak(f"{listName} list has been created, what items would you like to add in this list.")
    while True:
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                item = r.recognize_google(audio, language="en-in")
                # print(command)
                if("exit" in item.lower()):
                    speak(f"{listName} list has been saved successfully, exiting.")
                    break
                else:
                    item = item.strip()
                    with open (f"{listName}.txt", "a") as file:
                        file.write(f"{item}\n")
                        speak(f"{item} has been added to the {listName} list.")
        except Exception as e:
            print("Error; {0}".format(e))

# Function to handle different operations related to list
def handleListOperations(c):
    try:
        if "create" in c.lower() and "list" in c.lower():
                listName = getListName(c)
                with open (f"{listName}.txt", "w") as file:
                    file.write(f"{listName} list\n")
                addTask(listName)

        elif "add" in c.lower() and "list" in c.lower():
            listName = getListName(c)
            addTask(listName)

        elif "read" in c.lower() and "list" in c.lower():
            listName = getListName(c)
            with open (f"{listName}.txt") as file:
                speak(file.read())

        elif "show" in c.lower() and "list" in c.lower():
            listName = getListName(c)
            with open (f"{listName}.txt", "r") as file:
                tasks = file.read()
            notification.notify(
                title=f"{listName} List",
                message=tasks
            )

        elif "clear" in c.lower() and "list" in c.lower():
            listName = getListName(c)
            with open (f"{listName}.txt", "w") as file:
                file.write("")
            speak(f"{listName} list has been cleared succesfully")

        elif "delete" in c.lower() and "list" in c.lower():
            listName = getListName(c)
            fileName = f"{listName}.txt"
            try:
                os.remove(fileName)
                speak(f"{listName} list has been deleted succesfully")
            except:
                speak(f"{listName} list does not exists.")    
    except Exception as e:
        print("Error; {0}".format(e))      


# Function to handle general commands with the help of openai
def handleAiProcess(request):
    global chat
    chat.append({"role": "user", "content": request})
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
    api_key= OPENAI_API_KEY
    )
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    store=True,
    max_tokens=80,            # Limit the response length
    temperature=0.2,          # For StraightForward replies
    messages=chat
    )

    response = (completion.choices[0].message.content)
    chat.append({"role": "assistant", "content": response})
    return response

# Function to process the input command.
def processCommand(c):
    # print(c)
    try:
        if "open" in c.lower():
            handleOpenCommand(c)

        elif "play" in c.lower():
            song = " ".join(c.lower().split(" ")[1:])
            closest_match = findClosestSong(song, musicLibrary.music)
            if closest_match:
                link = musicLibrary.music[closest_match]
                webbrowser.open(link)
                speak(f"Playing {closest_match}")
            else:
                speak(f"Sorry, I couldn't find {song} in yout library.")
                print(f"Error: {song} not found in the music library.")

        elif "news" in c.lower():
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()

                #Extract all articles
                articles = data.get('articles', [])

                #Speak the healines
                for article in articles[:10]:
                    speak(article['title'])

        elif "list" in c.lower():
            handleListOperations(c)  

        elif "search" in c.lower():
            query = c.replace("search", "")
            webbrowser.open(f"https://google.com/search?q={query}")

        elif "clear chat" in c.lower():
            global chat
            chat = []
            speak("Chat cleared successfully.")

        else:
            # Pass the command to openAi
            response = handleAiProcess(c)
            # print(response)
            speak(response)
            
    except Exception as e:
        print("Error; {0}".format(e))    

# The program begins from here
if __name__ == "__main__":
    speak("Initializing")
    chat = []
    # print(sr.Microphone.list_microphone_names())
    while True:
        wake_word = getWakeWord()
        if("jarvis" in wake_word.lower()):
            speak("activated...")
            #listen for command
            while True:
                r = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)
                        audio = r.listen(source)
                        command = r.recognize_google(audio, language="en-in")
                        # print(command)
                        if("exit" in command.lower()):
                            break
                        else:
                            processCommand(command)
                except Exception as e:
                    print("Error; {0}".format(e))
     