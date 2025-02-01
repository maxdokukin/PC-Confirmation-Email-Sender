import re
import smtplib
import logging
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from icalendar import Calendar, Event
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def send_email(data):
    """Sends an email with the given data."""
    try:
        message = MIMEMultipart()
        message["From"] = data['sender_email']
        message["To"] = data['recipient_email']
        message["Subject"] = data['subject']
        message.attach(MIMEText(data['body'], "plain"))

        with smtplib.SMTP("smtp.mail.me.com", 587) as server:
            server.starttls()
            server.login(data['sender_email'], os.getenv("EMAIL_PASS"))
            server.sendmail(data['sender_email'], data['recipient_email'], message.as_string())
            server.sendmail(data['sender_email'], data['sender_email'], message.as_string())

        logging.info("Email sent successfully to %s", data['recipient_email'])

    except Exception as e:
        logging.error("Failed to send email: %s", e)


def create_calendar_event(data):
    """Creates a calendar event and saves it as an .ics file."""
    try:
        # Parse date and time
        start_time, end_time = parse_datetime(data['date_time'])

        # Set timezone (Pacific Time)
        timezone = pytz.timezone("America/Los_Angeles")
        start_time = timezone.localize(start_time)
        end_time = timezone.localize(end_time)

        # Create calendar event
        cal = Calendar()
        event = Event()
        event.add('summary', "PC: Shift Booked")
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now(timezone))
        event.add('location', data['calendar_location'])
        event.add('description', f"{data['name']}\n{data['recipient_email']}\n{data['topic']}")

        cal.add_component(event)

        # Save to .ics file
        file_path = "event.ics"
        with open(file_path, "wb") as f:
            f.write(cal.to_ical())

        logging.info("Calendar event created successfully: %s", file_path)
        return file_path

    except Exception as e:
        logging.error("Failed to create calendar event: %s", e)
        return None


def parse_datetime(event_date_time):
    """Parses and extracts start and end times from the event date string."""
    try:
        date_parts = event_date_time.split(" - ")
        start_time = datetime.strptime(date_parts[0], "%b %d %Y %I:%M%p")
        end_time = datetime.strptime(date_parts[1], "%I:%M%p").replace(
            year=start_time.year, month=start_time.month, day=start_time.day
        )
        return start_time, end_time
    except Exception as e:
        logging.error("Failed to parse date and time: %s", e)
        return None, None


def extract_data(email_text, recipient_email):
    """Extracts relevant details from the email text using regex."""
    try:
        name_match = re.search(r'Attendees\n(.+?)\n', email_text)
        datetime_match = re.search(r'An appointment has been scheduled for (.+?) PT', email_text)
        topic_match = re.search(r'Topic\n(.+?)\n', email_text)
        meeting_type_match = re.search(r'Meeting Type\n(.+?)\n', email_text)

        missing_fields = []
        if not name_match:
            missing_fields.append("Attendee Name")
        if not datetime_match:
            missing_fields.append("Appointment Date & Time")
        if not topic_match:
            missing_fields.append("Topic")
        if not meeting_type_match:
            missing_fields.append("Meeting Type")

        if missing_fields:
            logging.error("Failed to extract the following required details: %s", ', '.join(missing_fields))
            return None

        data = {
            'name': name_match.group(1).strip(),
            'recipient_email': recipient_email.strip(),
            'date_time': datetime_match.group(1).strip(),
            'topic': topic_match.group(1).strip().split(", ")[-1],
            'meeting_type': meeting_type_match.group(1).strip(),
        }

        # Determine location based on meeting type
        if data['meeting_type'].lower() == "in person":
            data['location'] = "This session will be in BBC 303."
            data['calendar_location'] = "BBC 303"
        else:
            zoom_link = os.getenv("ZOOM_LINK", "Zoom link unavailable")
            data['location'] = f"This session will be on Zoom: {zoom_link}"
            data['calendar_location'] = zoom_link

        return data

    except Exception as e:
        logging.error("Error while extracting data: %s", e)
        return None


def generate_email_content(data):
    """Generates the email subject and body."""
    try:
        data['subject'] = f"Confirmed: Tutoring for {data['topic']}, {data['date_time']}"
        data['body'] = f"""Hi {data['name'].split(" ")[0]},

My name is Max, and I'll be the tutor working with you for your upcoming appointment.
An appointment has been scheduled for {data['date_time']}. {data['location']}

Please let me know what your goal(s) are for the upcoming appointment so I can prepare myself ahead of time and better support you. Feel free to send over the questions you would like to work on and any relevant notes and documents as well.

I look forward to working with you.

Best,
Max Dokukin"""
        return data
    except Exception as e:
        logging.error("Failed to generate email content: %s", e)
        return None


def enter_data():
    """Prompts user for confirmation email input and extracts relevant details."""
    try:
        print("Copy-paste confirmation email below and press Enter, then type 'xxx' on a new line and press Enter:")
        email_text = []
        while True:
            line = input()
            if line.strip().lower() == "xxx":
                break
            email_text.append(line)

        email_text = "\n".join(email_text).strip()
        recipient_email = input("Enter recipient email:\n").strip().replace("mailto:", "")

        data = extract_data(email_text, recipient_email)
        if data:
            return data
        else:
            logging.error("Data extraction failed. Please re-enter the confirmation email.")
            return None

    except Exception as e:
        logging.error("Error while entering data: %s", e)
        return None


if __name__ == "__main__":
    sender_email = os.getenv("SENDER_EMAIL")
    if not sender_email:
        logging.error("SENDER_EMAIL is not set in the environment variables.")
        exit(1)

    data = enter_data()
    if data:
        data['sender_email'] = sender_email
        data = generate_email_content(data)

        if data:
            send_email(data)
            create_calendar_event(data)
        else:
            logging.error("Failed to generate email content. Exiting.")
    else:
        logging.error("Failed to process input data. Exiting.")
