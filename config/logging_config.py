import logging

LOG_FILE = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\logs\example.log"

def setup_log():
    logging.basicConfig(
        filename=LOG_FILE,
        encoding="utf-8",
        level=logging.INFO
    )