import asyncio
import os

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from config.logging_config import setup_logging
from filters import (
    filter_employees_without_salary,
    filter_candidates_by_experience,
    filter_candidates_by_salary_expectations,
    get_available_salary_expectations,
    get_available_candidates_experience,
    scrap_all_candidates,
)

load_dotenv()


class BotSession:
    """A class representing a session with the Telegram bot."""

    def __init__(self) -> None:
        self.__bot_token = os.getenv("BOT_TOKEN")
        self.bot = telebot.TeleBot(self.__bot_token)
        self.all_user_answers = {}
        self.user_answer = {}
        self.salary = ""
        self.candidates = None
        self.count = 0
        self.messages = {
            "Welcome": "Welcome to HR-Helper!",
            "Start": "Let's find the best candidates! Push the button to begin.",
            "Filter": "Please, choose the filters which you want to specify. If you have finished with filters "
            "- push the button 'Continue'.",
            "position": "Please, write for what position are you looking for candidates:",
            "location": "Please write, where are you looking for candidates (in ukrainian language):",
            "Experience_question": "Would you like to specify experience?",
            "Experience": "Please, choose the desired work experience:",
            "skills": "Please, write skills or keyword (write them with a comma: ex. Django, Flask):",
            "Continue": "Let's move to the next step...",
            "Salary_question": "Would you like to specify salary expectation?",
            "Minimum_salary": "Please, choose the the MINIMUM salary value.",
            "Maximum_salary": "Please, choose the the MAXIMUM salary value.",
            "Waiting": "Please wait, it will take a minute...",
            "Finish": "Here is the list of candidates you were looking for!",
        }
        setup_logging()

    def start(self) -> None:
        self.register_handlers()
        self.bot.polling()

    def register_handlers(self) -> None:
        """Register message and callback query handlers."""

        @self.bot.message_handler(commands=["start"], content_types=["text"])
        def handle_message_responses(message) -> None:
            """Handle message responses."""

            self.send_welcome(message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback_query(call) -> None:
            """Handle callback queries."""

            if call.data == "Start_search":
                self.position_question(call.message)
            elif call.data in ["location", "skills", "continue"]:
                self.select_filters_handler(call)
            elif call.data in ["experience_yes", "experience_no"]:
                self.experience_question_handler(call)
            elif call.data in ["salary_yes", "salary_no"]:
                self.salary_question_handler(call)
            elif call.data in [
                "без досвіду",
                "до 1 року",
                "від 1 до 2 років",
                "від 2 до 5 років",
                "понад 5 років",
            ]:
                self.filter_by_experience(call)
            elif self.count == 2:
                self.filter_by_salary(call)
            else:
                self.salary_handler(call)

    @staticmethod
    def generate_markup(
            button_names: list[str], call_data: list[str] = None
    ) -> InlineKeyboardMarkup:
        """Generate inline keyboard markup."""

        buttons = []
        for name, data in zip(button_names, call_data or button_names):
            buttons.append(InlineKeyboardButton(name, callback_data=data.lower()))
        markup = InlineKeyboardMarkup()
        markup.add(*buttons, row_width=2)
        return markup

    def send_options(
            self,
            button_names: [str],
            message_key: str,
            message,
            call_data: [str] = None
    ) -> None:
        """Send options with inline keyboard markup."""

        markup = self.generate_markup(button_names, call_data)
        self.bot.send_message(
            message.chat.id,
            self.messages[message_key],
            reply_markup=markup,
        )

    def update_user_answer(self, message) -> None:
        """Update user answer."""

        if "current_filter" in self.user_answer:
            key = self.user_answer["current_filter"]
            self.all_user_answers[key] = message.text

    def send_welcome(self, message) -> None:
        """Send welcome message."""

        self.bot.send_message(
            message.chat.id,
            self.messages["Welcome"],
        )
        self.start_button(message)

    def start_button(self, message) -> None:
        """Send start button."""
        self.all_user_answers = {}
        self.user_answer = {}
        self.salary = ""
        self.candidates = None
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Start Search", callback_data="Start_search"))
        self.bot.send_message(
            message.chat.id, self.messages["Start"], reply_markup=markup
        )

    def position_question(self, message) -> None:
        """Ask position question."""

        self.bot.send_message(message.chat.id, self.messages["position"])
        self.bot.register_next_step_handler(message, self.position_handler)

    def position_handler(self, message) -> None:
        """Handle position response."""

        self.all_user_answers["position"] = message.text
        self.select_filters(message)

    def select_filters(self, message) -> None:
        """Select filters."""

        button_names = ["Location", "Skills", "Continue"]
        self.update_user_answer(message)
        self.send_options(button_names, "Filter", message)

    def select_filters_handler(self, call) -> None:
        """Handle the selection of filters."""

        if call.data in ["location", "skills"]:
            self.user_answer["current_filter"] = call.data
            self.bot.send_message(
                call.message.chat.id,
                self.messages[call.data],
            )
            self.bot.register_next_step_handler(call.message, self.select_filters)
        elif call.data == "continue":
            self.continue_with_selected_filters(call.message)

    def continue_with_selected_filters(self, message) -> None:
        """Continue with the selected filters."""

        self.bot.send_message(message.chat.id, self.messages["Waiting"])
        position = self.all_user_answers.get("position", None)
        location = self.all_user_answers.get("location", None)
        skills = self.all_user_answers.get("skills", None)

        self.candidates = filter_employees_without_salary(position, location, skills)
        self.experience_question(message)

    def experience_question(self, message) -> None:
        """Ask about the candidate's experience."""

        self.send_options(
            ["Yes", "No"],
            "Experience_question",
            message,
            ["experience_yes", "experience_no"],
        )

    def experience_question_handler(self, call) -> None:
        """Handle the response to the experience question."""

        if call.data == "experience_yes":
            experience = get_available_candidates_experience(self.candidates)
            buttons = [value for value in experience]
            self.send_options(buttons, "Experience", call.message)

        elif call.data == "experience_no":
            self.salary_question(call)

    def filter_by_experience(self, call) -> None:
        """Filter candidates based on experience."""

        self.bot.send_message(
            call.message.chat.id,
            self.messages["Waiting"],
        )
        self.candidates = filter_candidates_by_experience(self.candidates, call.data)
        self.salary_question(call)

    def salary_question(self, call) -> None:
        """Ask about salary expectation."""

        self.send_options(
            ["Yes", "No"], "Salary_question", call.message, ["salary_yes", "salary_no"]
        )

    def salary_question_handler(self, call) -> None:
        """Handle the response to the salary question."""

        if call.data == "salary_yes":
            self.salary_handler(call)
        elif call.data == "salary_no":
            self.get_candidate_list(call.message)

    def salary_handler(self, call) -> None:
        """Handle salary input."""

        salary = get_available_salary_expectations(self.candidates)
        if self.count == 1:
            self.salary = call.data
            self.candidates = filter_candidates_by_salary_expectations(
                self.candidates, self.salary
            )
            salary = get_available_salary_expectations(self.candidates, max_salary=True)
        self.bot.send_message(call.message.chat.id, self.messages["Waiting"])

        message_key = "Maximum_salary" if self.count == 1 else "Minimum_salary"
        self.send_options(salary, message_key, call.message)
        self.count += 1

    def filter_by_salary(self, call) -> None:
        """Filter candidates by salary."""

        self.candidates = filter_candidates_by_salary_expectations(
            self.candidates, call.data, max_salary=True
        )
        self.get_candidate_list(call.message)
        self.stop_bot()

    def get_candidate_list(self, message) -> None:
        """Get the list of candidates."""

        self.bot.send_message(message.chat.id, self.messages["Waiting"])
        asyncio.run(scrap_all_candidates(self.candidates))

        with open("candidates.csv", "rb") as file:
            self.bot.send_document(
                message.chat.id,
                file,
                caption=self.messages["Finish"],
            )

    def stop_bot(self) -> None:
        self.bot.stop_polling()


bot_session = BotSession()
bot_session.start()
