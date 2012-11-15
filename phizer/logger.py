import logging
import syslog

USE_SYSLOG = False

def configure(config, level=None,
              fmt='%(asctime)-15s %(clientip)s %(user)-8s %(message)s'):
    global USE_SYSLOG
    if config.syslog_facility:
        USE_SYSLOG = True
        facility = getattr(syslog, config.syslog_facility, None)
        assert facility != None, "invalid facility specified"
        syslog.openlog('phizer', syslog.LOG_PID, facility)
    else:
        logging.basicConfig(level=level, fmt=fmt)

def critical(msg, *args, **kwargs):
    """Log a message with severity 'CRITICAL' on the root logger."""
    if USE_SYSLOG:
        level = syslog.LOG_CRIT
    else:
        level = logging.CRITICAL
    self.log(level, msg, args)
    raise SystemExit("critical error")

fatal = critical

def debug(msg, *args, **kwargs):
    """Log a message with severity 'DEBUG' on the root logger."""
    if USE_SYSLOG:
        level = syslog.LOG_DEBUG
    else:
        level = logging.DEBUG
    self.log(level, msg, args)

def error(msg, *args, **kwargs):
    """Log a message with severity 'ERROR' on the root logger."""
    if USE_SYSLOG:
        level = syslog.LOG_ERR
    else:
        level = logging.ERROR
    self.log(level, msg, args)

def info(msg, *args, **kwargs):
    """Log a message with severity 'INFO' on the root logger."""
    if USE_SYSLOG:
        level = syslog.LOG_INFO
    else:
        level = logging.INFO
    self.log(level, msg, args)

def log(level, msg, *args, **kwargs):
    """Log 'msg % args' with the integer severity 'level' on the
    root logger."""
    if USE_SYSLOG:
        syslog.syslog(level, msg % args)
    else:
        logging.log(level, msg, args)

def warning(msg, *args, **kwargs):
    """Log a message with severity 'WARNING' on the root logger."""
    if USE_SYSLOG:
        level = syslog.LOG_WARNING
    else:
        level = logging.WARN
    self.log(level, msg, args)

warn = warning
