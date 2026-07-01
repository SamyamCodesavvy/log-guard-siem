import re
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser


class ParsedLog:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.hostname: Optional[str] = None
        self.program: Optional[str] = None
        self.pid: Optional[int] = None
        self.username: Optional[str] = None
        self.source_ip: Optional[str] = None
        self.action: Optional[str] = None
        self.severity: str = "info"
        self.message: str = ""


PATTERNS = {
    # Example:
    # Jun 21 08:20:44 ubuntu sshd[1234]:
    # Failed password for admin from 1.2.3.4
    "syslog": re.compile(
        r"(?P<month>\w+)\s+"
        r"(?P<day>\d+)\s+"
        r"(?P<time>[\d:]+)\s+"
        r"(?P<host>\S+)\s+"
        r"(?P<prog>\S+?)(?:\[(?P<pid>\d+)\])?:\s+"
        r"(?P<msg>.*)"
    ),
    "failed_password": re.compile(
        r"Failed password for (?:invalid user )?(?P<user>\S+) " r"from (?P<ip>[\d.]+)"
    ),
    "accepted_password": re.compile(
        r"Accepted password for (?P<user>\S+) " r"from (?P<ip>[\d.]+)"
    ),
    "sudo_failure": re.compile(r"sudo:.*authentication failure.*user=(?P<user>\S+)"),
    "root_login": re.compile(r"session opened for user root"),
    "nginx_access": re.compile(
        r'(?P<ip>[\d.]+).*"(?P<method>\w+) ' r'(?P<path>\S+).*" (?P<status>\d{3})'
    ),
}


def parse_log(raw: str, source: str = "syslog") -> ParsedLog:
    result = ParsedLog()
    result.message = raw.strip()

    m = PATTERNS["syslog"].match(raw)

    if m:
        try:
            ts_str = (
                f"{m.group('month')} "
                f"{m.group('day')} "
                f"{m.group('time')} "
                f"{datetime.now().year}"
            )
            result.timestamp = date_parser.parse(ts_str)

        except Exception:
            result.timestamp = datetime.utcnow()

        result.hostname = m.group("host")
        result.program = m.group("prog").rstrip(":")

        if m.group("pid"):
            result.pid = int(m.group("pid"))

        msg = m.group("msg")

    else:
        result.timestamp = datetime.utcnow()
        msg = raw

    if PATTERNS["failed_password"].search(msg):
        fm = PATTERNS["failed_password"].search(msg)

        result.username = fm.group("user")
        result.source_ip = fm.group("ip")
        result.action = "failed_login"
        result.severity = "medium"

    elif PATTERNS["accepted_password"].search(msg):
        fm = PATTERNS["accepted_password"].search(msg)

        result.username = fm.group("user")
        result.source_ip = fm.group("ip")
        result.action = "successful_login"
        result.severity = "info"

    elif PATTERNS["sudo_failure"].search(msg):
        fm = PATTERNS["sudo_failure"].search(msg)

        result.username = fm.group("user")
        result.action = "sudo_failure"
        result.severity = "high"

    elif PATTERNS["root_login"].search(msg):
        result.username = "root"
        result.action = "root_session"
        result.severity = "high"

    elif source == "nginx" and PATTERNS["nginx_access"].search(msg):
        fm = PATTERNS["nginx_access"].search(msg)

        result.source_ip = fm.group("ip")
        status = int(fm.group("status"))

        if status >= 500:
            result.action = "server_error"
            result.severity = "high"

        elif status in (401, 403):
            result.action = "auth_failure"
            result.severity = "medium"

    return result
