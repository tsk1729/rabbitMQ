import logging
from rfc5424logging import Rfc5424SysLogHandler

def setup_logger():
    logger = logging.getLogger("fastapi_papertrail")
    logger.setLevel(logging.INFO)  # Set log level (DEBUG, INFO, WARNING, ERROR)

    # Papertrail syslog handler
    papertrail_handler = Rfc5424SysLogHandler(
        address=('logs2.papertrailapp.com', 30446),  # Use your Papertrail destination
        hostname="FastAPI-App",  # Optional: to identify your app
        appname="FastAPI-Logger"
    )

    papertrail_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Attach the handler to the logger
    logger.addHandler(papertrail_handler)
    logger.addHandler(console_handler)

    return logger
logger = setup_logger()

