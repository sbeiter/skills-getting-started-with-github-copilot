"""
Integration tests for FastAPI endpoints.

Tests all three API endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify expected activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_includes_activity_details(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_populated(self, client):
        """Test that activities have initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        assert len(activities["Chess Club"]["participants"]) > 0
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, sample_activity_name, sample_email):
        """Test successful signup for an activity."""
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity_name in data["message"]

    def test_signup_adds_email_to_participants(self, client, sample_activity_name, sample_email):
        """Test that signup actually adds the email to participants."""
        # First, verify email is not in the list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email not in activities[sample_activity_name]["participants"]
        
        # Signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Verify email is now in the list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email in activities[sample_activity_name]["participants"]

    def test_signup_activity_not_found(self, client, invalid_activity_name, sample_email):
        """Test signup returns 404 for non-existent activity."""
        response = client.post(
            f"/activities/{invalid_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self, client, sample_activity_name):
        """Test signup returns 400 when student is already signed up."""
        # Use an existing participant
        existing_email = "michael@mergington.edu"
        
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": existing_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client, sample_activity_name, sample_emails):
        """Test signing up multiple different students."""
        for email in sample_emails:
            response = client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all emails are in participants
        response = client.get("/activities")
        activities = response.json()
        for email in sample_emails:
            assert email in activities[sample_activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, sample_activity_name, sample_email):
        """Test successful unregistration from an activity."""
        # First signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity_name in data["message"]

    def test_unregister_removes_from_participants(self, client, sample_activity_name, sample_email):
        """Test that unregister actually removes the email from participants."""
        # Signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Verify email is in the list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email in activities[sample_activity_name]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Verify email is no longer in the list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email not in activities[sample_activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, invalid_activity_name, sample_email):
        """Test unregister returns 404 for non-existent activity."""
        response = client.delete(
            f"/activities/{invalid_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self, client, sample_activity_name, sample_email):
        """Test unregister returns 404 when email is not a participant."""
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_existing_participant(self, client, sample_activity_name):
        """Test unregistering an existing participant from the initial data."""
        existing_email = "michael@mergington.edu"
        
        # Verify email is in participants
        response = client.get("/activities")
        activities = response.json()
        assert existing_email in activities[sample_activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": existing_email}
        )
        assert response.status_code == 200
        
        # Verify email is removed
        response = client.get("/activities")
        activities = response.json()
        assert existing_email not in activities[sample_activity_name]["participants"]
