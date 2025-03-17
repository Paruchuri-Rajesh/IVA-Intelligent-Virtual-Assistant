AI Agent for Alarms and Reminders
This project consists of both the frontend and backend. The frontend is a simple two-page website for hosting the agent,
while the backend is the main component. Our AI-powered agent assists with tasks related to alarms and reminders, such as setting alarms and reminders, deleting them, and 
fetching active alarms and reminders. The core functionalities are implemented in the da_driver.py file. Ensure you have a database created with the same TABLES as specified in the IVA.sql file.

Pre-Requisites:
Before running the project, install Visual Studio Code, MySQL Workbench, and ensure you have the required API keys: 
LIVEKIT_URL,
LIVEKIT_API_KEY,
LIVEKIT_API_SECRET,
OPENAI_API_KEY (Paid API),
DEEPGRAM_API_KEY,
NEWS_API_KEY.

Installation and Setup:
Install dependencies using pip install -r requirements.txt.
Add your API keys in a .env file.
Create separate virtual environments for the backend and frontend.
Modify the local host port number in vite.config.js if necessary.
Run three key files in separate PowerShell terminals:
(i) Run the agent backend using python **agent.py dev**, 
(ii) Run the server backend using **python server.py dev** (this fetches a token from LiveKit when a user logs in), and 
(iii) Run the frontend using **npm run dev**(this starts the frontend server and provides a URL to access the agent).
Run all three commands simultaneously in separate PowerShell terminals after activating the virtual environment using . env\Scripts\activate.
References:
For additional guidance, refer to the following YouTube tutorials:
**"https://youtu.be/Ew7fOQpkKBw?feature=shared"**, 
**"https://youtu.be/nvmV0a2geaQ?feature=shared"**.
