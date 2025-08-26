import logging
from copy import copy
import re

MAPPING = {
    'DEBUG'   : 36, # cyan
    'INFO'    : 32, # green
    'WARNING' : 33, # yellow
    'ERROR'   : 31, # red
    'CRITICAL': 41, # white on red bg
}
 
PREFIX = '\033['
SUFFIX = '\033[0m'

def replace_sql_keywords(sql):
    keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IS', 'NULL', 'LIKE', 'IN', 'EXISTS', 'ALL', 'ANY', 'BETWEEN', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET']
    for keyword in keywords:
        sql = re.sub(r'\b' + keyword + r'\b', r'\033[38;2;253;182;0m' + keyword + r'\033[0m', sql, flags=re.IGNORECASE)
    return sql

class ColoredFormatter(logging.Formatter):
    
    # The rest of the formatter still has to be initiated
    def __init__(
        self,
        fmt,
        datefmt
    ):
        super().__init__(fmt, datefmt)
    
    def format(self, record):
        colored_record = copy(record)
        levelname = colored_record.levelname
        seq = MAPPING.get(levelname, 37) # default white
        colored_levelname = ('{0}{1}m{2}{3}') \
            .format(PREFIX, seq, levelname, SUFFIX)
        colored_record.levelname = colored_levelname
        
        if hasattr(record, 'sql'):
            colored_record.args = tuple([record.args[0], replace_sql_keywords(record.args[1]), record.args[2], record.args[3]])
            # Uncomment if you want custom log level name for sql print-outs
            # colored_record.levelname = '\033[38;2;253;182;0mDB_DEBUG\033[0m'
        
        return logging.Formatter.format(self, colored_record)