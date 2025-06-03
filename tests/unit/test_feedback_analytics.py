import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.chatbot.feedback_analytics import FeedbackAnalytics


class TestFeedbackAnalytics:
    """Test feedback analytics functionality"""

    @patch('src.chatbot.feedback_analytics.db.get_session')
    def test_get_feedback_summary(self, mock_get_session):
        """Test generating feedback summary"""
        # Arrange
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        # Mock the query results
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [
            10,  # total_feedback
            7,  # thumbs_up
            3  # thumbs_down
        ]

        analytics = FeedbackAnalytics()

        # Act
        result = analytics.get_feedback_summary(days=7)

        # Assert
        assert result["total_feedback"] == 10
        assert result["thumbs_up"] == 7
        assert result["thumbs_down"] == 3
        assert result["satisfaction_rate"] == 70.0

    @patch('src.chatbot.feedback_analytics.db.get_session')
    def test_get_feedback_summary_no_feedback(self, mock_get_session):
        """Test feedback summary with no feedback"""
        # Arrange
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        # Mock empty results
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [
            0,  # total_feedback
            0,  # thumbs_up
            0  # thumbs_down
        ]

        analytics = FeedbackAnalytics()

        # Act
        result = analytics.get_feedback_summary()

        # Assert
        assert result["total_feedback"] == 0
        assert result["satisfaction_rate"] == 0
