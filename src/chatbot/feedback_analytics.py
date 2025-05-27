from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from .db.database import db
from .db.models import Feedback, Message


class FeedbackAnalytics:
    def get_feedback_summary(
            self,
            session: Optional[Session] = None,
            days: int = 7
    ) -> Dict[str, any]:
        if not session:
            session_gen = db.get_session()
            session = next(session_gen)
            should_close = True
        else:
            should_close = False

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            total_feedback = session.query(func.count(Feedback.id)).filter(
                Feedback.created_at >= cutoff_date
            ).scalar()

            thumbs_up = session.query(func.count(Feedback.id)).filter(
                and_(
                    Feedback.feedback_type == "thumbs_up",
                    Feedback.created_at >= cutoff_date
                )
            ).scalar()

            thumbs_down = session.query(func.count(Feedback.id)).filter(
                and_(
                    Feedback.feedback_type == "thumbs_down",
                    Feedback.created_at >= cutoff_date
                )
            ).scalar()

            satisfaction_rate = (thumbs_up / total_feedback * 100) if total_feedback > 0 else 0

            return {
                "period_days": days,
                "total_feedback": total_feedback,
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "satisfaction_rate": round(satisfaction_rate, 2),
                "as_of": datetime.utcnow().isoformat()
            }
        finally:
            if should_close:
                session.close()

    def get_conversation_feedback(
            self,
            conversation_id: int,
            session: Optional[Session] = None
    ) -> List[Dict[str, any]]:
        if not session:
            session_gen = db.get_session()
            session = next(session_gen)
            should_close = True
        else:
            should_close = False

        try:
            feedbacks = session.query(
                Feedback.id,
                Feedback.feedback_type,
                Feedback.created_at,
                Message.content,
                Message.role
            ).join(
                Message
            ).filter(
                Message.conversation_id == conversation_id
            ).order_by(
                Feedback.created_at.desc()
            ).all()

            return [
                {
                    "feedback_id": f.id,
                    "feedback_type": f.feedback_type,
                    "created_at": f.created_at.isoformat(),
                    "message_content": f.content[:100] + "..." if len(f.content) > 100 else f.content,
                    "message_role": f.role
                }
                for f in feedbacks
            ]
        finally:
            if should_close:
                session.close()

    def get_worst_performing_messages(
            self,
            limit: int = 10,
            session: Optional[Session] = None
    ) -> List[Dict[str, any]]:
        if not session:
            session_gen = db.get_session()
            session = next(session_gen)
            should_close = True
        else:
            should_close = False

        try:
            messages_with_negative = session.query(
                Message.id,
                Message.content,
                Message.conversation_id,
                func.count(Feedback.id).label('negative_count')
            ).join(
                Feedback
            ).filter(
                and_(
                    Message.role == "assistant",
                    Feedback.feedback_type == "thumbs_down"
                )
            ).group_by(
                Message.id
            ).order_by(
                func.count(Feedback.id).desc()
            ).limit(limit).all()

            return [
                {
                    "message_id": msg.id,
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                    "conversation_id": msg.conversation_id,
                    "negative_feedback_count": msg.negative_count
                }
                for msg in messages_with_negative
            ]
        finally:
            if should_close:
                session.close()


feedback_analytics = FeedbackAnalytics()
