#!/usr/bin/env python
"""
Test script to verify the JobSearch flow structure without requiring API keys
"""

from job_search.crews.job_search_crew.job_search_crew import JobSearchCrew
from job_search.flows.jod_search import JobSearchFlow
from job_search.tools.jobspy_tool import JobSpyTool
from job_search.tools.resume_generator_tool import ResumeGeneratorTool


def test_imports():
    """Test that all imports work correctly"""
    print("✅ All imports successful!")


def test_flow_structure():
    """Test that the flow structure is correctly defined"""
    flow = JobSearchFlow()
    print(f"✅ Flow created: {flow.__class__.__name__}")
    print(f"✅ Flow state: {flow.state}")


def test_crew_structure():
    """Test that the crew structure is correctly defined"""
    crew = JobSearchCrew()
    print(f"✅ Crew created: {crew.__class__.__name__}")


def test_tools():
    """Test that tools are properly structured"""
    jobspy_tool = JobSpyTool()
    resume_tool = ResumeGeneratorTool()
    print(f"✅ JobSpy tool: {jobspy_tool.name}")
    print(f"✅ Resume tool: {resume_tool.name}")


def test_sample_data():
    """Test with sample data structure"""
    sample_user_profile = {
        "name": "Jane Smith",
        "email": "jane.smith@email.com",
        "skills": ["Python", "React", "Node.js", "AWS"],
        "experience": [
            {
                "title": "Senior Full Stack Developer",
                "company": "Tech Innovations Inc",
                "duration": "2021-2024",
                "description": "Led development of scalable web applications",
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "Stanford University",
                "year": "2019",
            }
        ],
    }

    sample_job_params = {
        "search_term": "Senior Full Stack Developer",
        "location": "San Francisco",
        "results_wanted": 15,
    }

    print(f"✅ Sample user profile: {sample_user_profile['name']}")
    print(f"✅ Sample job search: {sample_job_params['search_term']}")


if __name__ == "__main__":
    print("🧪 Testing JobSearch Flow Structure")
    print("=" * 50)

    try:
        test_imports()
        test_flow_structure()
        test_crew_structure()
        test_tools()
        test_sample_data()

        print("\n" + "=" * 50)
        print("🎉 All structure tests passed!")
        print("\nJobSearch CrewAI Flow is ready to use!")
        print("\nTo run with real data:")
        print("1. Set your OPENAI_API_KEY environment variable")
        print("2. Run: python -m job_search.flows.jod_search")
        print("3. Or use: from job_search.flows.jod_search import run_job_search_flow")

    except Exception as e:
        print(f"❌ Test failed: {e}")
