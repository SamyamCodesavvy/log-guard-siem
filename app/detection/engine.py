from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import logging
from app.models.log import Log
from app.models.alert import Alert, AlertSeverity

logger = logging.getLogger(__name__)

def create_alert(db: Session, rule_name: str, severity: str,
                 description: str, log: Log) -> Alert:
    alert = Alert(
        hostname=log.hostname,
        rule_name=rule_name,
        severity=AlertSeverity(severity),
        description=description,
        source_ip=log.source_ip,
        username=log.username,
        log_ids=str([log.id])
    )
    db.add(alert)
    db.commit()
    logger.warning(f"ALERT [{severity.upper()}] {rule_name} — {description}")
    return alert

def run_detection(db: Session, log: Log):
    _rule_brute_force(db, log)
    _rule_sudo_failure(db, log)
    _rule_root_login(db, log)
    _rule_credential_sharing(db, log)
    _rule_web_attack(db, log)


def _rule_brute_force(db: Session, log: Log):
    """Rule 1: 5+ failed SSH logins from same IP in 5 minutes."""
    if log.action != "failed_login" or not log.source_ip:
        return

    five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)

    count = db.query(func.count(Log.id)).filter(
        Log.source_ip == log.source_ip,
        Log.action == "failed_login",
        Log.timestamp >= five_min_ago,
    ).scalar()

    if count >= 5:
        recent = db.query(Alert).filter(
            Alert.source_ip == log.source_ip,
            Alert.rule_name == "SSH Brute Force",
            Alert.timestamp >= five_min_ago,
        ).first()

        if not recent:
            create_alert(
                db,
                "SSH Brute Force",
                "critical",
                f"Possible brute force: {count} failed logins from {log.source_ip} in 5 min",
                log,
            )


def _rule_sudo_failure(db: Session, log: Log):
    """Rule 2: sudo authentication failure."""
    if log.action == "sudo_failure":
        create_alert(
            db,
            "Privilege Escalation Attempt",
            "high",
            f"sudo authentication failed for user {log.username}",
            log,
        )


def _rule_root_login(db: Session, log: Log):
    """Rule 3: root login detected."""
    if (
        log.action == "root_session"
        or (
            log.action == "successful_login"
            and log.username == "root"
        )
    ):
        create_alert(
            db,
            "Root Login Detected",
            "high",
            f"Root session opened from {log.source_ip or 'unknown'}",
            log,
        )


def _rule_credential_sharing(db: Session, log: Log):
    """Rule 4: multiple different users logging in from same IP."""
    if log.action != "successful_login" or not log.source_ip:
        return

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    distinct_users = db.query(
        func.count(Log.username.distinct())
    ).filter(
        Log.source_ip == log.source_ip,
        Log.action == "successful_login",
        Log.timestamp >= one_hour_ago,
    ).scalar()

    if distinct_users >= 3:
        create_alert(
            db,
            "Credential Sharing Detected",
            "medium",
            f"{distinct_users} different users logged in from {log.source_ip}",
            log,
        )


def _rule_web_attack(db: Session, log: Log):
    """Rule 5: Repeated HTTP 401/403 responses."""
    if log.action != "auth_failure" or not log.source_ip:
        return

    ten_min_ago = datetime.now(timezone.utc) - timedelta(minutes=10)

    count = db.query(func.count(Log.id)).filter(
        Log.source_ip == log.source_ip,
        Log.action == "auth_failure",
        Log.source == "nginx",
        Log.timestamp >= ten_min_ago,
    ).scalar()

    if count >= 10:
        create_alert(
            db,
            "Possible Web Attack",
            "high",
            f"{count} HTTP auth failures from {log.source_ip} in 10 min",
            log
        )