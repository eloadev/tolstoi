import logging


class Logger:
    def __init__(self, log_file_name, log_level, log_format):
        self.log_file_name = log_file_name
        self.log_level = log_level
        self.log_format = log_format

        self.logger = logging.getLogger(self.log_file_name)
        self.logger.setLevel(self.log_level)
        self.formatter = logging.Formatter(self.log_format)

        self.file_handler = logging.FileHandler(self.log_file_name)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def get_logger(self):
        return self.logger
