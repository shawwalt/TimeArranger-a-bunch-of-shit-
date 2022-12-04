import logging
import datetime


class LoggerHandler(logging.Logger):

    # 初始化 Logger
    def __init__(self,
                 name='root',
                 logger_level='DEBUG',
                 logger_format="'%(name)s:%(asctime)s  %(module)s in the %(lineno)d line : %(levelname)s  %(message)s'"
                 ):
        super().__init__(name)

        self.setLevel(logger_level)
        fmt = logging.Formatter(logger_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logger_level)
        stream_handler.setFormatter(fmt)
        self.addHandler(stream_handler)

    def set_file_handler(self, file, logger_level, fmt):
        file_handler = logging.FileHandler(file + '//' + '%s.log' % str(datetime.date.today()))
        file_handler.setLevel(logger_level)
        fmt = logging.Formatter(fmt)
        file_handler.setFormatter(fmt)
        self.addHandler(file_handler)

