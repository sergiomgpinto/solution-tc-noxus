import hashlib
from typing import Optional, Dict, Any
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from chatbot.db.database import db
from chatbot.db.models import ABTest, ABTestAssignment, Configuration, Feedback, Message, Conversation
from chatbot.config_manager import config_manager
from chatbot.config_schemas import ChatbotConfiguration


class ABTestManager:
    def create_ab_test(
            self,
            name: str,
            control_config_id: int,
            treatment_config_id: int,
            traffic_percentage: int = 50,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            # Verify both configs exist
            control = session.query(Configuration).filter_by(id=control_config_id).first()
            treatment = session.query(Configuration).filter_by(id=treatment_config_id).first()

            if not control or not treatment:
                raise ValueError("Both configurations must exist")

            # Create test
            ab_test = ABTest(
                name=name,
                description=description,
                control_config_id=control_config_id,
                treatment_config_id=treatment_config_id,
                traffic_percentage=traffic_percentage,
                is_active=True
            )

            session.add(ab_test)
            session.commit()

            return {
                "id": ab_test.id,
                "name": ab_test.name,
                "control": control.name,
                "treatment": treatment.name,
                "traffic_percentage": traffic_percentage
            }
        finally:
            session.close()

    def get_config_for_user(self, user_identifier: str) -> Configuration:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            # Check for active A/B tests
            active_test = session.query(ABTest).filter_by(is_active=True).first()

            if not active_test:
                # No active test, return default active config
                return config_manager.get_active_configuration()

            # Check if user already assigned
            assignment = session.query(ABTestAssignment).filter_by(
                user_identifier=user_identifier,
                test_id=active_test.id
            ).first()

            if not assignment:
                # Assign user to variant based on hash
                hash_value = int(hashlib.md5(
                    f"{user_identifier}:{active_test.id}".encode()
                ).hexdigest(), 16)

                variant = "treatment" if (hash_value % 100) < active_test.traffic_percentage else "control"

                assignment = ABTestAssignment(
                    user_identifier=user_identifier,
                    test_id=active_test.id,
                    variant=variant
                )
                session.add(assignment)
                session.commit()

            # Return appropriate config
            config_id = (
                active_test.treatment_config_id
                if assignment.variant == "treatment"
                else active_test.control_config_id
            )

            config = session.query(Configuration).filter_by(id=config_id).first()
            return ChatbotConfiguration(**config.config_json)

        finally:
            session.close()

    def get_test_results(self, test_id: int) -> Dict[str, Any]:
        session_gen = db.get_session()
        session: Session = next(session_gen)

        try:
            # Get assignments
            assignments = session.query(
                ABTestAssignment.variant,
                func.count(ABTestAssignment.id).label('count')
            ).filter_by(test_id=test_id).group_by(ABTestAssignment.variant).all()

            # Get feedback by variant
            results = {}
            for variant, count in assignments:
                # Complex query to get satisfaction rate per variant
                # Join assignments -> conversations -> messages -> feedback
                feedback_stats = session.query(
                    func.count(Feedback.id).label('total'),
                    func.sum(case((Feedback.feedback_type == 'thumbs_up', 1), else_=0)).label('positive')
                ).join(
                    Message
                ).join(
                    Conversation
                ).join(
                    ABTestAssignment,
                    ABTestAssignment.user_identifier == Conversation.id  # Simplified
                ).filter(
                    ABTestAssignment.test_id == test_id,
                    ABTestAssignment.variant == variant
                ).first()

                results[variant] = {
                    "users": count,
                    "total_feedback": feedback_stats.total or 0,
                    "satisfaction_rate": (
                        (feedback_stats.positive / feedback_stats.total * 100)
                        if feedback_stats.total else 0
                    )
                }

            return results

        finally:
            session.close()


ab_test_manager = ABTestManager()
