import mysql.connector
import spacy
import re
import mysql.connector
import time
import schedule
from time import sleep
import datetime
import winsound  
from plyer import notification
import threading
import pygame.mixer
import webbrowser
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from livekit.agents import llm
import requests
from dotenv import load_dotenv
from pytube import Search
from gtts import gTTS
import pygame 



load_dotenv()
# Database connection
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="rootroot",
    database="Alarms"
)
pygame.mixer.init()
pygame.mixer.music.load("R1.mp3")


def speak(text):
            tts=gTTS(text)
            tts.save('temp.mp3')
            pygame.mixer.init()
            pygame.mixer.music.load('temp.mp3')
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove("temp.mp3")


def extract_alarm_info(text):
    """Extracts time, AM/PM, and name from an alarm request using NLP."""
    # doc = nlp(text)    
    time_match = re.search(r'\b(\d{1,2}:\d{2})\s?(AM|PM)\b', text, re.IGNORECASE)
    if time_match:
        time_db = time_match.group(1)
        am_pm = time_match.group(2).upper()
    else:
        return None, None, None
    
    task_match = re.search(r'for\s+(.*)', text, re.IGNORECASE)
    name = task_match.group(1) if task_match else ""
    
    return time_db, am_pm, name

def extract_reminder_info(text):
    """Extracts time, AM/PM, and matter from a reminder request."""
    # doc = nlp(text)
    time_match = re.search(r'\b(\d{1,2}:\d{2})\s?(AM|PM)\b', text,re.IGNORECASE)
    if time_match:
        time_db = time_match.group(1)
        am_pm = time_match.group(2).upper()
    else:
        return None, None, None
    
    matter_match = re.search(r'for\s+(.*)', text, re.IGNORECASE)
    matter = matter_match.group(1) if matter_match else ""
    
    return time_db, am_pm, matter

def get_existing_alarm(time_db, am_pm, name):
    """Checks if an alarm with the same time and similar name exists."""
    cursor = conn.cursor()
    query = "SELECT * FROM Alarm WHERE Time = %s AND AmPm = %s AND Name LIKE %s"
    cursor.execute(query, (time_db, am_pm, f"%{name}%"))
    result = cursor.fetchone()
    cursor.close()
    return result

def get_existing_reminder(time_db, am_pm, matter):
    """Checks if a reminder with the same time and matter exists."""
    cursor = conn.cursor()
    query = "SELECT * FROM Reminder WHERE Time = %s AND AmPm = %s AND Matter = %s"
    cursor.execute(query, (time_db, am_pm, matter))
    result = cursor.fetchone()
    cursor.close()
    return result

def update_alarm_status(time_db, name):
    """Updates an existing alarm's status to 'Active'."""
    cursor = conn.cursor()
    query = "UPDATE Alarm SET Status = 'Active' WHERE Time = %s AND Name = %s"
    cursor.execute(query, (time_db, name))
    conn.commit()
    cursor.close()
    print("Existing alarm updated to 'Active'.")

def update_reminder_status(time_db, matter):
    """Updates an existing reminder's status to 'Active'."""
    cursor = conn.cursor()
    query = "UPDATE Reminder SET Status = 'Active' WHERE Time = %s AND Matter = %s"
    cursor.execute(query, (time_db, matter))
    conn.commit()
    cursor.close()
    print("Existing reminder updated to 'Active'.")

def set_alarm(text):
    """Sets an alarm, checking for duplicates before inserting."""
    time_db, am_pm, name = extract_alarm_info(text)
    if not time_db or not am_pm or not name:
        print("Could not extract alarm details from input.")
        return
    
    existing_alarm = get_existing_alarm(time_db, am_pm, name)
    if existing_alarm:
        update_alarm_status(time_db, name)
    else:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO Alarm (Time, AmPm, Name, Status) VALUES (%s, %s, %s, 'Active')"
            cursor.execute(query, (time_db, am_pm, name))
            conn.commit()
            print(f"New alarm set for {time_db} and {name} successfully.")
        except mysql.connector.Error as err:
            print("Error:", err)
        finally:
            cursor.close()

    alarm_hour, alarm_minute = map(int, str(time_db).split(':'))
    if am_pm.lower() == "pm" and alarm_hour != 12:
        alarm_hour += 12
    elif am_pm.lower() == "am" and alarm_hour == 12:
        alarm_hour = 0

    alarm_time_24h = f"{alarm_hour:02d}:{alarm_minute:02d}"
    # print(f"{alarm_time_24h}")
    # Schedule the alarm in a separate thread
    thread = threading.Thread(target=schedule_alarm, args=(name, time_db, alarm_time_24h))
    thread.daemon = True  # Allows the thread to exit when the main program exits
    thread.start()
    
    # print(f"Alarm '{name}' scheduled for {alarm_time_24h} in a separate thread.")

def schedule_alarm(name, time_db, alarm_time_24h):
    schedule.every().day.at(alarm_time_24h).do(lambda: play_alarm(name, time_db))
    
    while True:
        schedule.run_pending()
        time.sleep(5)

def play_alarm(name, time_db):

    speak(f"Alarm set for '{name}' is ringing!")

    # notification.notify(
    #     title="Alarm!",
    #     message=f"{name} is ringing!",
    #     timeout=3
    # )

    for _ in range(1):
        pygame.mixer.music.play()
        time.sleep(2)
     
    # update alarm status
    cursor=conn.cursor()
    update_query = "UPDATE Alarm SET Status='Inactive' WHERE Time=%s AND Name=%s"
    cursor.execute(update_query, (time_db, name))
    conn.commit()
    
    print(f"Alarm with name : '{name}' is now Inactive.")
    cursor.close()
    conn.close()

def set_reminder(text):
    """Sets a reminder, checking for duplicates before inserting."""
    time_db, am_pm, matter = extract_reminder_info(text)
    
    if not time_db or not am_pm or not matter:
        print("Could not extract reminder details from input.")
        return
    
    existing_reminder = get_existing_reminder(time_db, am_pm, matter)
    
    if existing_reminder:
        update_reminder_status(time_db, matter)
    else:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO Reminders(Time, AmPm, Matter, Status) VALUES (%s, %s, %s, 'Active')"
            cursor.execute(query, (time_db, am_pm, matter))
            conn.commit()
            print(f"New reminder set for {time_db} with matter '{matter}' successfully.")
        except mysql.connector.Error as err:
            print("Error:", err)
        finally:
            cursor.close()

    reminder_hour, reminder_minute = map(int, str(time_db).split(':'))
    
    if am_pm.lower() == "pm" and reminder_hour != 12:
        reminder_hour += 12
    elif am_pm.lower() == "am" and reminder_hour == 12:
        reminder_hour = 0

    reminder_time_24h = f"{reminder_hour:02d}:{reminder_minute:02d}"
    print(f"Reminder set for {reminder_time_24h}")

    # Schedule the reminder in a separate thread
    thread = threading.Thread(target=schedule_reminder, args=(matter, time_db, reminder_time_24h))
    thread.daemon = True  
    thread.start()
    
    print(f"Reminder '{matter}' scheduled for {reminder_time_24h} in a separate thread.")

def schedule_reminder(matter, time_db, reminder_time_24h):
    """Schedules the reminder to run at the specified time."""
    schedule.every().day.at(reminder_time_24h).do(lambda: trigger_reminder(matter, time_db))

    while True:
        schedule.run_pending()
        time.sleep(5)

def trigger_reminder(matter, time_db):
    """Plays the reminder notification and updates status to 'Inactive'."""
    speak(f"Reminder: '{matter}' is triggered!")

    notification.notify(
        title="Reminder!",
        matter=f"Don't forget: {matter}",
        timeout=5
    )

    for _ in range(1):  # Play sound for 5 times
        pygame.mixer.music.play()
        time.sleep(2)
    
    # Update the reminder status in the database
    cursor = conn.cursor()
    update_query = "UPDATE Reminder SET Status='Inactive' WHERE Time=%s AND Message=%s"
    cursor.execute(update_query, (time_db, matter))
    conn.commit()

    print(f"Reminder with Matter: '{matter}' is now Inactive.")
    cursor.close()

def delete_all_alarms():
    """Deletes all alarms from the database."""
    cursor = conn.cursor()
    query = "DELETE FROM Alarm"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("All alarms deleted successfully.")

def delete_all_reminders():
    """Deletes all reminders from the database."""
    cursor = conn.cursor()
    query = "DELETE FROM Reminder"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("All reminders deleted successfully.")

def extract_time_info(text):
    """Extracts time and AM/PM from user input."""
    time_match = re.search(r'\b(\d{1,2}:\d{2})\s?(AM|PM)\b', text, re.IGNORECASE)
    if time_match:
        return time_match.group(1), time_match.group(2).upper()
    return None, None

def delete_alarm(text):
    """Deletes a specific alarm based on the time mentioned in the speech."""
    time_db, am_pm = extract_time_info(text)
    if not time_db or not am_pm:
        print("Could not extract time from input.")
        return
    
    cursor = conn.cursor()
    query = "DELETE FROM Alarm WHERE Time = %s AND AmPm = %s"
    cursor.execute(query, (time_db, am_pm))
    conn.commit()
    cursor.close()

    if cursor.rowcount > 0:
        print(f"Alarm at {time_db} {am_pm} deleted successfully.")
    else:
        print(f"No alarm found at {time_db} {am_pm}.")

def delete_reminder(text):
    """Deletes a specific reminder based on the time mentioned in the speech."""
    time_db, am_pm = extract_time_info(text)
    if not time_db or not am_pm:
        print("Could not extract time from input.")
        return
    
    cursor = conn.cursor()
    query = "DELETE FROM Reminder WHERE Time = %s AND AmPm = %s"
    cursor.execute(query, (time_db, am_pm))
    conn.commit()
    cursor.close()

    if cursor.rowcount > 0:
        print(f"Reminder at {time_db} {am_pm} deleted successfully.")
    else:
        print(f"No reminder found at {time_db} {am_pm}.")

def get_active_alarms():
    """Fetches and displays all active alarms from the database."""
    cursor = conn.cursor()
    query = "SELECT Time, AmPm, Name FROM Alarm WHERE Status = 'Active'"
    cursor.execute(query)
    alarms = cursor.fetchall()
    cursor.close()

    if alarms:
            # print("Some Active Alarms are found")
            return alarms
    else:
        # print("No active alarms found.")
        return []

def get_active_reminders():
    """Fetches and displays all active reminders from the database."""
    cursor = conn.cursor()
    query = "SELECT Time, AmPm, Matter FROM Reminder WHERE Status = 'Active'"
    cursor.execute(query)
    reminders = cursor.fetchall()
    cursor.close()

    if reminders:
        # print("Active Reminders:")
        return reminders
    else:
        # print("No active reminders found.")
        return []    
   
def get_driver():
    """Initializes the WebDriver if not already created and returns the instance."""
    global driver
    if driver is None:
        driver = webdriver.Chrome()  # Ensure ChromeDriver is installed
    return driver

def search_yyoutube(query):
        print(query)
        """Searches for a video on YouTube and plays the first result, handling both videos and playlists."""
        songs = re.search(r"(?i)^play\s+(.*)", query)  
        # song=songs.group(1).strip()
        search=Search(query)
        if search.results:
          first_video = search.results[0]  # Get the first result
          video_url = first_video.watch_url
        #   return  f"playing: {song}" 
          webbrowser.open(video_url)  # Open in default browser

def oopen_gmail():
    """Opens Gmail in the microsoft edge web browser."""
    gmail_url = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox"
    webbrowser.open(gmail_url)

# Function to extract the website name from the query
def extract_website(query):
    match = re.search(r"open\s+(\w+)", query, re.IGNORECASE)  # Extract word after "open"
    if match:
        return match.group(1).lower()  # Return the extracted keyword in lowercase
    return None

# Function to open website
def oopen_website(query):
        print("hello website")
        print(f"{query}")
        sites = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "stackoverflow": "https://www.stackoverflow.com",
    "github": "https://www.github.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.twitter.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "linkedin": "https://www.linkedin.com",
    "bing": "https://www.bing.com",
    "quora": "https://www.quora.com",
    "medium": "https://www.medium.com"
    }
        # keyword = extract_website(query)
        keyword=query
            # if keyword:
        if keyword in sites:
            url = sites[keyword]
        else:
            url = f"https://www.{keyword}.com"  # Guess the website URL
            
        print(f"Opening {url} ...")
        webbrowser.open(url)


def fetch_news(self):
        r=requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWSAPIKEY}") 
        if r.status_code==200:
            print("printing the raw text")
            data=r.json()
            # print(data)
            # articles=data.get('articles',[])
            # assistant.say("I am getting you the headlines sir" )
            articles=data.get('articles',[])
            return articles
            # for article in articles:
            #   return(article['title'])
        else:
            return("Error fetching news:", response.json())
