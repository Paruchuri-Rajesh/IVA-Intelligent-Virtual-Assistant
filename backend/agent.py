from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    tokenize,
    tts
)
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from livekit import rtc,agents
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
import os
import asyncio
import time
from db_driver import get_active_alarms,get_active_reminders
import datetime
import sys
import asyncio
from typing import Annotated
import asyncio
from typing import Annotated
import deepgram
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero
from livekit.agents import llm,JobContext, WorkerOptions, cli, tokenize, tts
from livekit import agents
import enum
from typing import Annotated
import logging
from db_driver import set_alarm, set_reminder, extract_alarm_info, extract_reminder_info,delete_alarm
from db_driver import delete_all_alarms,delete_all_reminders,delete_reminder,extract_time_info,get_active_alarms
from db_driver import search_yyoutube,oopen_gmail,oopen_website,fetch_news,get_active_reminders
from selenium import webdriver
import os 
import pyautogui
from livekit.agents import pipeline
from gtts import gTTS
import pygame 


logger = logging.getLogger("Alarm-Reminder")
logger.setLevel(logging.INFO)

class AlarmDetails(enum.Enum):
    TIME = "time_db"
    AM_PM = "am_pm"
    NAME = "name"

# def speak(text):
#             tts=gTTS(text)
#             tts.save('temp.mp3')
#             pygame.mixer.init()
#             pygame.mixer.music.load('temp.mp3')
#             pygame.mixer.music.play()

#             while pygame.mixer.music.get_busy():
#                 pygame.time.Clock().tick(10)

#             pygame.mixer.music.unload()
#             os.remove("temp.mp3")

class ReminderDetails(enum.Enum):
    TIME = "time_db"
    AM_PM = "am_pm"
    MATTER = "matter"

class AssistantFnc(agents.llm.FunctionContext):
    def __init__(self,answer_fn):
        load_dotenv()
        super().__init__()
        self.recent_alarm = {}
        self.recent_reminder = {}
        self._answer = answer_fn
    
       

    @agents.llm.ai_callable(description="Set an alarm at 07:30 AM for my morning run")
    def setup_alarm(self, text: Annotated[str, "User's request for setting up an alarm"]):
        """
        Sets an alarm based on the input text.
        Example: "Set an alarm at 07:30 AM for my morning run"
        """
        logger.info("Setting up an alarm: %s", text)
        time_db, am_pm, name = extract_alarm_info(text)

        if not time_db or not am_pm or not name:
            return "Could not extract alarm details. Please specify a time and a task."

        self.recent_alarm = {"time_db": time_db, "am_pm": am_pm, "name": name}

        set_alarm(text)
        return f"Alarm has been set for {time_db} {am_pm} - {name}."

    @agents.llm.ai_callable(description="Set up a reminder at 07:30 AM for my morning run")
    def setup_reminder(self, text: Annotated[str, "User's request for setting a reminder"]):
        """
        Sets a reminder based on the input text.
        Example: "Remind me to call John at 15:00"
        """
        logger.info("Setting up a reminder: %s", text)
        time_db, am_pm, matter = extract_reminder_info(text)

        if not time_db or not am_pm or not matter:
            return "Could not extract reminder details. Please specify a time_db and a task."

        self.recent_reminder = {"time_db": time_db, "am_pm": am_pm, "matter": matter}
        set_reminder(text)
        return f"Reminder has been set for {time_db} {am_pm} - {matter}."

    @agents.llm.ai_callable(description="Get details of the most recent alarm set.")
    def get_recent_alarm(self):
        """
        Returns the details of the most recently set alarm.
        Example: "What is my latest alarm?"
        """
        if self.recent_alarm:
            return f"Your last alarm is set for {self.recent_alarm['time_db']} {self.recent_alarm['am_pm']} - {self.recent_alarm['name']}."
        else:
            return "No alarm has been set recently."

    @agents.llm.ai_callable(description="Get details of the most recent reminder set.")
    def get_recent_reminder(self):
        """
        Returns the details of the most recently set reminder.
        Example: "What is my latest reminder?"
        """
        if self.recent_reminder:
            return f"Your last reminder is set for {self.recent_reminder['time_db']} {self.recent_reminder['am_pm']} - {self.recent_reminder['matter']}."
        else:
            return "No reminder has been set recently."

    @agents.llm.ai_callable(description="Delete all alarms from the database.")
    def delete_aall_alarms(self):
        """Requests the agent to delete all alarms."""
        delete_all_alarms()
        return "All the Alarms have been deleted Successfully."

    @agents.llm.ai_callable(description="Delete all reminders from the database.")
    def delete_aall_reminders(self):
        """Requests the agent to delete all reminders."""
        delete_all_reminders()
        return "All the Reminders have been deleted Successfully."

    @agents.llm.ai_callable(description="Delete an alarm set at a specific time_db. Example: 'Delete alarm at 07:30 AM'.")
    def delete_aalarm(self,text: Annotated[str, "User's request for deleting an Alarm"]):
        """Requests the agent to delete a specific alarm with the given time_db."""
        delete_alarm(text)
        time_db,am_pm=extract_time_info(text)
        return f"Request to delete alarm at {time_db} {am_pm} is successfull."

    @agents.llm.ai_callable(description="Delete a reminder set at a specific time. Example: 'Delete reminder at 03:00 PM'.")
    def delete_rreminder(self,text: Annotated[str, "User's request for deleting a Reminder"]):
        """Requests the agent to delete a specific reminder with the given time."""
        delete_reminder(text)
        time_db,am_pm=extract_time_info(text)
        return f"Request to delete reminder at {time_db} {am_pm} is successfull."

    @agents.llm.ai_callable(description="Fetch all active alarms from my database.")
    def get_aactive_alarms(self):
        """Requests the agent to retrieve all active alarms."""
        alarms=get_active_alarms()
            

        if alarms:
            alarm_messages = [f"Alarm set for {time} {am_pm} for {name}" for time, am_pm, name in alarms]
            response = "You have the following active alarms:\n" + "\n".join(alarm_messages)
        else:
             response = "No active alarms found."

        return response


    @agents.llm.ai_callable(description="Fetch all active reminders from my database.")
    def get_aactive_reminders(self):
        """Requests the agent to retrieve all active reminders."""
        reminders=get_active_reminders()


        if reminders:
            reminder_messages = [f"reminder set for {time} {am_pm} for {matter}" for time, am_pm, matter in reminders]
            response = "You have the following active reminders:\n" + "\n".join(reminder_messages)
        else:
             response = "No active reminders found."

        return response
    
    @agents.llm.ai_callable(description="Search YouTube for a given query using the function in db_driver.")
    def search_youtube(
        self,
        query: Annotated[str, agents.llm.TypeInfo(description="The search query for YouTube")] ):  

        search_yyoutube(query)  
        
        return "Searching YouTube for '{query}'"
    
    @agents.llm.ai_callable(description="Opens my  Gmail  inbox in the default web browser.")
    def open_gmail(self):
        oopen_gmail()
        return "Opening Gmail..."
    
    @agents.llm.ai_callable(description ="If the user asks to open any specific website")
    def open_website( self,query: Annotated[str, agents.llm.TypeInfo(description="The search query for website")]):
        
        oopen_website(query)
        return "opening the website that You asked me to open"
    

    @agents.llm.ai_callable(description="user asks you to fetch the news")
    def open_news(self):
        articles=fetch_news(self)
        titles = [article['title'] for article in articles]  # Extract titles
        all_titles = ". ".join(titles)  # Join with a period for natural speech
        return all_titles

    @agents.llm.ai_callable(description="User asks to shutdown")
    def commit_suicide(self,text: Annotated[str, "User's request for shutting down the program"]):
        """Handles user speech but only responds when called by name (IVA).
        Allows shutdown with a voice command 'IVA, shutdown'."""
            pyautogui.click(1043,889)


    @agents.llm.ai_callable(description="User asks to cut the voice of the agent")
    def mute(self,text: Annotated[str, "User's request for cutting  down the mic or voice"]):
        """Handles user speech but only responds when called by name (IVA).
        Allows shutdown with a voice command 'IVA, shutdown'."""
        
            pyautogui.click(837,889)
    
        
    @agents.llm.ai_callable(description=("Called when asked  something that would require vision capabilities,""for example, an image, video, or the webcam feed."))
    async def image(self,user_msg: Annotated[str,agents.llm.TypeInfo(description="The user message that triggered this function"),],):
        print(f"Message triggering vision capabilities: {user_msg}")
        # use_visuals(self,user_msg)
        await self._answer(user_msg,use_image=True)
        # return "Processing Image request"
    
    @agents.llm.ai_callable(description=("called when the user asked for any information from web that would not require any vision capabilities"))
    async def info(self,user_msg: Annotated[str,agents.llm.TypeInfo(description="The user message that triggered this function"),],):
        await self._answer(user_msg,use_image=False)

async def get_video_track(room: rtc.Room):
    """Get the first video track from the room. We'll use this track to process images."""
    print("In get_video_track function")

    video_track = asyncio.Future[rtc.RemoteVideoTrack]()
    print(video_track)
    for _, participant in room.remote_participants.items():
        for _, track_publication in participant.track_publications.items():
            if track_publication.track is not None and isinstance(
                track_publication.track, rtc.RemoteVideoTrack
             ):
                video_track.set_result(track_publication.track)
                print(f"Using video track {track_publication.track.sid}")
                break


    return await video_track

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    

    chat_context = ChatContext(
        messages=[
            ChatMessage(
                role="system",
                content=(
                    "Your name is IVA.The abrreviation of IVA is Intelligent Virtual assistant. You are a funny, witty bot. Your interface with users will be voice and vision."
                    "Respond with short and concise answers. Avoid using unpronouncable punctuation or emojis."
                ),
            )
        ]
    )

    gpt = openai.LLM(model="gpt-4o")

    # Since OpenAI does not support streaming TTS, we'll use it with a StreamAdapter
    # to make it compatible with the VoiceAssistant
    openai_tts = tts.StreamAdapter(
        tts=openai.TTS(voice="alloy"),
        sentence_tokenizer=tokenize.basic.SentenceTokenizer(),)

    chat = rtc.ChatManager(ctx.room)
    latest_image: rtc.VideoFrame | None = None
    shared_state = {"latest_image": None} 

    async def _answer(text: str, use_image: bool = False):
            """
            Answer the user's message with the given text and optionally the latest
            image captured from the video track.
            """

            print("In _answer function call ")
            if not text:
                text="No content provided"
                print(text)

            print(f"latest_image is : {shared_state["latest_image"]}")

            content: list[str | ChatImage] = [text]
            if use_image and shared_state["latest_image"]:
                content.append(ChatImage(image=shared_state["latest_image"]))
            if ctx.room.connection_state != rtc.ConnectionState.CONN_CONNECTED:
                print("⚠️ Connection lost to LiveKit server!")
            # logger.info("Chat Context Messages: %s", chat_context.messages)
            print(f"content present is :  {content}")
            chat_context.messages.append(ChatMessage(role="user", content=content))
            # print(f"The chat context which willbe passed to chatgpt is : {chat_context} ")
            print(f"Sending chat context: {chat_context.messages}")
            stream =gpt.chat(chat_ctx=chat_context)
            print(f"Received stream response: {stream}")
            if not stream:
                    print("⚠️ GPT-4o did not return a response.")
            else:
                    print(f"Assistant will say: {stream}")
            await assistant.say(stream, allow_interruptions=True)



    assistant_fnc = AssistantFnc(_answer)
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),  # We'll use Silero's Voice Activity Detector (VAD)
        stt=deepgram.STT(),  # We'll use Deepgram's Speech To Text (STT)
        llm=gpt,
        tts=openai_tts,  # We'll use OpenAI's Text To Speech (TTS)
        fnc_ctx=assistant_fnc,
        chat_ctx=chat_context,
        max_nested_fnc_calls= 100,
    )

    chat = rtc.ChatManager(ctx.room)
 
    async def check_alarms():
        """Continuously checks for alarms and makes the assistant speak when they go off."""
        # print("✅ check_alarms() started!")  # Debugging log

        while True:
            alarms = get_active_alarms()  # Fetch alarms

            if not alarms:  
                print("⚠️ No active alarms found. Waiting for new alarms...")  
            else:
                print(f"⏰ Active Alarms are there")  # Debugging log
                current_time =datetime.datetime.now().strftime("%I:%M %p").strip()  # Get current time in 12-hour format
                
                for time_db, am_pm, name in alarms:
                    alarm_time =datetime.datetime.strptime(f"{time_db} {am_pm}", "%I:%M:%S %p").strftime("%I:%M %p").strip()
                    # print(f"alarm_time is : {alarm_time}")
                    # print(f"🔎 Checking alarm: {repr(alarm_time)} (Current time: {repr(current_time)})")  # Debug with repr()

                    if alarm_time == current_time:
                        print(f"🚨 Alarm triggered: {alarm_time} - {name}")
                        
            await asyncio.sleep(15)  # ✅ Keep checking every  15 seconds


    # ✅ Start the alarm-checking loop inside entrypoint()
    asyncio.create_task(check_alarms())

    async def check_reminders():
        """Continuously checks for reminders and makes the assistant speak when they go off."""
        # print("✅ check_reminders() started!")  # Debugging log

        while True:
            reminders = get_active_reminders()  # Fetch reminders

            if not reminders:  
                print("⚠️ No active reminders found. Waiting for new reminders...")  
            else:
                current_time = datetime.datetime.now().strftime("%I:%M %p").strip()  # Get current time in 12-hour format

                for time_db, am_pm, matter in reminders:
                    reminder_time = datetime.datetime.strptime(f"{time_db} {am_pm}", "%I:%M:%S %p").strftime("%I:%M %p").strip()

                    if reminder_time == current_time:
                        print(f"🚨 Reminder triggered: {reminder_time} - {matter}")

                        # Make the agent speak the reminder
                        session.conversation.item.create(
                            llm.ChatMessage(
                                role="assistant",
                                content=f"Reminder alert! Time: {reminder_time}. {matter}."
                            )
                        )
                        session.response.create()  # ✅ Assistant speaks the reminder
                        
            await asyncio.sleep(15)  # ✅ Keep checking every 15 seconds

    # ✅ Start the reminder-checking loop inside entrypoint()
    asyncio.create_task(check_reminders())

    assistant.start(ctx.room)

    await asyncio.sleep(1)
    await assistant.say("Hi there! How can I help?", allow_interruptions=False)

    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        print("got the video_track function")
        video_track = await get_video_track(ctx.room)
        

        async for event in rtc.VideoStream(video_track):

            shared_state["latest_image"] = event.frame


if __name__ == "__main__":

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
