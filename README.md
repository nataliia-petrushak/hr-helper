# HR Helper Bot

## Description:
HR Helper Bot is a Telegram bot designed to assist HR professionals and recruiters in finding and filtering candidates for job positions. The bot interacts with users via Telegram messages, guiding them through the process of specifying job criteria and preferences, filtering candidate profiles accordingly, and providing a list of suitable candidates.

### Key Features:

#### User Interaction: 
HR Helper Bot engages users in conversational interactions, prompting them to input job criteria such as job position, location, skills, experience level, and salary expectations.
#### Filtering Candidates: 
Based on the user's input, the bot filters candidate profiles from a specified source (e.g., work.ua).
#### Candidate Evaluation: 
HR Helper Bot evaluates candidate profiles based on predefined criteria such as education, additional skills, language proficiency, and experience level.
#### Exporting Candidate Lists: 
Once the candidate filtering process is complete, the bot generates a list of suitable candidates and exports it to a CSV file for further review and processing.
#### Error Handling: 
The bot includes error handling mechanisms to handle user input errors gracefully and provide informative error messages when necessary.

### Technologies Used:

#### Python: 
The bot is developed using Python programming language, leveraging libraries such as telebot, aiohttp, BeautifulSoup, and python-dotenv.
#### Telegram API: 
HR Helper Bot interacts with users via the Telegram API, allowing users to communicate with the bot through Telegram messages.
#### Web Scraping: 
The bot utilizes web scraping techniques to extract candidate profiles from job listing websites (e.g., work.ua).
#### CSV Export: 
Candidate lists are exported to CSV format using Python's built-in csv module for easy sharing and analysis.

### Installation

1. Clone the repository:
````git clone https://github.com/nataliia-petrushak/hr-helper.git````
2. In the root directory build a docker container:
````docker build --progress=plain -t telegram-bot .````
3. Run the container:
````docker run --name my-bot-container telegram-bot````

DEMO
<img width="1143" alt="Screenshot 2024-02-12 at 10 24 12" src="https://github.com/nataliia-petrushak/hr-helper/assets/87134904/1880ce2a-a02e-4b83-a3c9-eb0e9d53fae5"><br><br>

<img width="1139" alt="Screenshot 2024-02-12 at 10 24 54" src="https://github.com/nataliia-petrushak/hr-helper/assets/87134904/29d9af3e-42c7-4b41-ad05-b4631a9c6f0a">


