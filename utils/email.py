import aiosmtplib
from email.message import EmailMessage
from config import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from pathlib import Path

async def send_email_smtp_async(
    recipient: str,
    subject: str,
    html_content: str
):
    message = EmailMessage()
    message["From"] = settings.MAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content("This email requires HTML support.")
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        start_tls=True
    )

BASE_DIR = Path(__file__).resolve().parent  # utils/

env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

def render_email_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    context.update({
        "app_name": "My app",
        "year": datetime.utcnow().year,
    })
    return template.render(**context)
