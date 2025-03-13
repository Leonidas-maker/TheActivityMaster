from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from pathlib import Path
import asyncio
from typing import Optional
from rich.console import Console
import os

from schemas import s_email
from config.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, TESTING



class EmailManager:
    __BASE_CONFIG = ConnectionConfig(
            MAIL_FROM_NAME="TheActivityMaster",
            MAIL_FROM="information@domain.com",

            MAIL_USERNAME=EMAIL_USERNAME,
            MAIL_PASSWORD=EMAIL_PASSWORD,
            MAIL_PORT=EMAIL_PORT,
            MAIL_SERVER=EMAIL_HOST,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            TEMPLATE_FOLDER=Path(__file__).parents[1] / "data/email_templates"
        )

    def __init__(self, config: Optional[ConnectionConfig] = None):
        """
        Initialize the EmailManager with the provided configuration.
        
        :param config: The configuration to use for sending emails (default is None). 
        """
        self.fm = FastMail(config or self.__BASE_CONFIG)
        self.console = Console()


    @staticmethod
    def get_subject(template_name: str, language: str = "en") -> str:
        """
        Get the subject of the email template.
        
        :param template_name: The name of the template file.
        :param language: The language of the email template (default is "en").
        :return: The subject of the email template.
        """     
        return "The Activity Master - " + s_email.EMAIL_SUBJECTS.get(template_name, {}).get(language, "No Subject")

    async def send_mail(self, message_data: s_email.TEmail): # type: ignore
        if TESTING:
            return

        template_name = message_data.get_template_name()
        message = MessageSchema(
            subject=EmailManager.get_subject(template_name, message_data.language),
            recipients=[message_data.user_email],
            subtype=MessageType.html,
            template_body=message_data.model_dump()
        )
        email_sent = False
        for attempt in range(3):
            if email_sent:
                break
            try:
                await self.fm.send_message(message, template_name=f"{template_name}.html")
                email_sent = True
            except Exception as e:
                self.console.log("[red][ERROR][/red]\t\tFailed to send email")
                self.console.print_exception()
                self.console.log(f"[yellow]Retrying in 5 seconds... Attempt: {attempt + 1}[/yellow]")
                await asyncio.sleep(5)