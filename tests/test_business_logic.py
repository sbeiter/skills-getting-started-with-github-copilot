"""
Unit tests for business logic and data validation.

Tests validation logic for:
- Activity existence
- Participant status checks
- Edge cases (empty strings, special characters, etc.)
"""

import pytest
from fastapi.testclient import TestClient


class TestActivityValidation:
    """Tests for activity validation logic."""

    def test_valid_activity_exists(self, client):
        """Test that valid activities can be retrieved."""
        response = client.get("/activities")
        activities = response.json()
        
        valid_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Track and Field",
            "Art Club",
            "Music Ensemble",
            "Science Club",
            "Debate Team"
        ]
        
        for activity in valid_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that all activities have required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

    def test_activity_max_participants_is_integer(self, client):
        """Test that max_participants is an integer."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_invalid_activity_returns_404(self, client):
        """Test that invalid activity names return 404."""
        invalid_names = [
            "Invalid Club",
            "Nonexistent Activity",
            "Random Team",
            "",  # Empty string
        ]
        
        for invalid_name in invalid_names:
            # Test signup
            response = client.post(
                f"/activities/{invalid_name}/signup",
                params={"email": "test@example.com"}
            )
            assert response.status_code == 404
            
            # Test unregister
            response = client.delete(
                f"/activities/{invalid_name}/unregister",
                params={"email": "test@example.com"}
            )
            assert response.status_code == 404


class TestParticipantValidation:
    """Tests for participant status validation."""

    def test_participant_added_to_list(self, client, sample_activity_name, sample_email):
        """Test that a new participant is added to the activity's participant list."""
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[sample_activity_name]["participants"])
        
        # Signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Get new participant count
        response = client.get("/activities")
        new_count = len(response.json()[sample_activity_name]["participants"])
        
        assert new_count == initial_count + 1

    def test_participant_removed_from_list(self, client, sample_activity_name, sample_email):
        """Test that a participant is removed from the activity's participant list."""
        # Signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Get participant count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()[sample_activity_name]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Get participant count after unregister
        response = client.get("/activities")
        count_after_unregister = len(response.json()[sample_activity_name]["participants"])
        
        assert count_after_unregister == count_after_signup - 1

    def test_duplicate_signup_error(self, client, sample_activity_name):
        """Test that duplicate signup returns error."""
        email = "unique_test@mergington.edu"
        
        # First signup should succeed
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Second signup should fail
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_existing_participant_cannot_signup_again(self, client, sample_activity_name):
        """Test that existing participants cannot signup again."""
        # Use an initially existing participant
        existing_email = "michael@mergington.edu"
        
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": existing_email}
        )
        assert response.status_code == 400


class TestEmailValidation:
    """Tests for email format and handling."""

    def test_signup_with_various_email_formats(self, client, sample_activity_name):
        """Test signup with different email formats."""
        emails = [
            "simple@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "test123@subdomain.example.com",
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

    def test_unregister_with_special_chars_in_email(self, client, sample_activity_name):
        """Test unregister with special characters in email."""
        email = "user+test@example.com"
        
        # Signup
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200


class TestResponseFormats:
    """Tests for response message formats."""

    def test_signup_response_format(self, client, sample_activity_name, sample_email):
        """Test that signup response has correct format."""
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_unregister_response_format(self, client, sample_activity_name, sample_email):
        """Test that unregister response has correct format."""
        # Signup first
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Unregister
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_error_response_has_detail(self, client, invalid_activity_name, sample_email):
        """Test that error responses have detail field."""
        response = client.post(
            f"/activities/{invalid_activity_name}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
