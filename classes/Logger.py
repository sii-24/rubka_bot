import logging


class Logger:
    log: logging.Logger

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)-30s[%(lineno)5d] - %(message)s"
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)
        self.log = logging.getLogger(__name__)

    def __call__(self, msg: str):
        self.log.info(msg)


logger = Logger()
