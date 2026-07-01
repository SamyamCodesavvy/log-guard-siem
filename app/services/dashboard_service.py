from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertSeverity
from app.models.host import Host
from app.models.log import Log


def get_dashboard_stats(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    total_logs = db.query(func.count(Log.id)).scalar()
    total_hosts = db.query(func.count(Host.id)).scalar()
    total_alerts = db.query(func.count(Alert.id)).scalar()

    critical_alerts = (
        db.query(func.count(Alert.id))
        .filter(Alert.severity == AlertSeverity.critical)
        .scalar()
    )

    todays_logs = (
        db.query(func.count(Log.id)).filter(Log.timestamp >= today_start).scalar()
    )

    logs_per_hour = (
        db.query(
            func.date_part("hour", Log.timestamp).label("hour"),
            func.count(Log.id).label("count"),
        )
        .filter(Log.timestamp >= now - timedelta(hours=24))
        .group_by("hour")
        .all()
    )

    top_ips = (
        db.query(
            Log.source_ip,
            func.count(Log.id).label("count"),
        )
        .filter(
            Log.source_ip.isnot(None),
            Log.action == "failed_login",
        )
        .group_by(Log.source_ip)
        .order_by(func.count(Log.id).desc())
        .limit(10)
        .all()
    )

    top_users = (
        db.query(
            Log.username,
            func.count(Log.id).label("count"),
        )
        .filter(
            Log.username.isnot(None),
            Log.action == "failed_login",
        )
        .group_by(Log.username)
        .order_by(func.count(Log.id).desc())
        .limit(10)
        .all()
    )

    latest_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(5).all()

    latest_logs = db.query(Log).order_by(Log.timestamp.desc()).limit(5).all()

    return {
        "stats": {
            "total_logs": total_logs,
            "total_hosts": total_hosts,
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "todays_logs": todays_logs,
        },
        "logs_per_hour": [
            {
                "hour": int(r.hour),
                "count": r.count,
            }
            for r in logs_per_hour
        ],
        "top_attack_ips": [
            {
                "ip": r.source_ip,
                "count": r.count,
            }
            for r in top_ips
        ],
        "top_failed_users": [
            {
                "user": r.username,
                "count": r.count,
            }
            for r in top_users
        ],
        "latest_alerts": latest_alerts,
        "latest_logs": latest_logs,
    }
