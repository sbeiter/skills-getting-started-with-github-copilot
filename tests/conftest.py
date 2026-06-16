"""
Pytest configuration and shared fixtures for the FastAPI test suite.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient
import os
from pathlib import Path


@pytest.fixture
def client():
    """
    Provides a TestClient instance with a fresh app and isolated test data.
    
    This fixture:
    - Creates a fresh FastAPI app for each test
    - Initializes a clean activities database
    - Ensures complete test isolation
    """
    # Create a fresh app instance for this test
    test_app = FastAPI(title="Mergington High School API",
                      description="API for viewing and signing up for extracurricular activities")
    
    # Mount static files
    test_app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent.parent,
              "src", "static")), name="static")
    
    # Create fresh activities data for this test
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and JV levels",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "marcus@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Join our soccer team and compete in regional leagues",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "chris@mergington.edu"]
        },
        "Track and Field": {
            "description": "Sprint, distance running, and field events",
            "schedule": "Monday through Friday, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["natalie@mergington.edu", "ryan@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, sculpture, and mixed media",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in concerts",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["grace@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Define routes on the test app
    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")
    
    @test_app.get("/activities")
    def get_activities():
        return activities
    
    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        # Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]
        # Check if student is already signed up
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        # Add student
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @test_app.delete("/activities/{activity_name}/unregister")
    def unregister_from_activity(activity_name: str, email: str):
        """Unregister a student from an activity"""
        # Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]

        # Remove student
        if email in activity["participants"]:
            activity["participants"].remove(email)
            return {"message": f"Unregistered {email} from {activity_name}"}
        else:
            raise HTTPException(status_code=404, detail="Participant not found in activity")
    
    return TestClient(test_app)


@pytest.fixture
def sample_email():
    """Provides a sample email for testing signup functionality."""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provides a sample activity name that exists in the app."""
    return "Chess Club"


@pytest.fixture
def invalid_activity_name():
    """Provides an activity name that does not exist."""
    return "Nonexistent Activity"


@pytest.fixture
def sample_emails():
    """Provides a list of sample emails for testing multiple participants."""
    return [
        "test1@mergington.edu",
        "test2@mergington.edu",
        "test3@mergington.edu",
    ]
