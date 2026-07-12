from sqlalchemy.orm import Session
from app.models.models import AuditLog, Notification

class AuditService:
    @staticmethod
    def log_action(db: Session, user_id: int, action: str, entity: str, entity_id: int = None, ip: str = None):
        log = AuditLog(user_id=user_id, action=action, entity=entity, entity_id=entity_id, ip_address=ip)
        db.add(log)
        db.commit()

class NotificationService:
    @staticmethod
    def get_notifications(db: Session, limit: int = 10):
        return db.query(Notification).order_by(Notification.created_at.desc()).limit(limit).all()
