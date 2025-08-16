#!/usr/bin/env python
from typing import Any, Dict

from crewai.flow import Flow, listen, start
from pydantic import BaseModel

from job_search.crews.job_search_crew.job_search_crew import JobSearchCrew


class JobSearchState(BaseModel):
    user_profile: Dict[str, Any] = {}
    job_search_params: Dict[str, Any] = {}
    job_listings: str = ""
    skills_analysis: str = ""
    resume_path: str = ""


class JobSearchFlow(Flow[JobSearchState]):
    """
    JobSearch Flow that takes user career+skills info,
    compares with job listings from JobSpy, and generates personalized resumes
    """

    @start()
    def collect_user_info(self):
        """Collect user career and skills information"""
        print("Starting JobSearch Flow...")
        print("User profile and job search parameters ready")

        # The user_profile and job_search_params should be set before starting the flow
        if not self.state.user_profile:
            print("Warning: No user profile provided. Using default values.")
            self.state.user_profile = {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "skills": ["Python", "Machine Learning", "Data Analysis"],
                "experience": [
                    {
                        "title": "Data Scientist",
                        "company": "Tech Corp",
                        "duration": "2022-2024",
                        "description": "Developed ML models and analyzed large datasets",
                    }
                ],
                "education": [
                    {
                        "degree": "Master of Science in Computer Science",
                        "school": "University of Technology",
                        "year": "2022",
                    }
                ],
                "summary": "Experienced data scientist with expertise in machine learning and data analysis",
            }

        if not self.state.job_search_params:
            print("Warning: No job search parameters provided. Using default values.")
            self.state.job_search_params = {
                "search_term": "Data Scientist",
                "location": "Remote",
                "results_wanted": 10,
            }

    @listen(collect_user_info)
    def search_and_analyze_jobs(self):
        """Search for jobs using JobSpy and analyze skill gaps"""
        print("Searching for relevant job listings...")

        # Prepare inputs for the crew
        crew_inputs = {
            "user_profile": self.state.user_profile,
            "job_search_params": self.state.job_search_params,
            "search_term": self.state.job_search_params.get(
                "search_term", "Software Developer"
            ),
            "location": self.state.job_search_params.get("location", ""),
            "results_wanted": self.state.job_search_params.get("results_wanted", 10),
            "fine_tune_search_string": self.state.job_search_params.get(
                "fine_tune_search_string", ""
            ),
        }

        # Run the job search crew
        result = JobSearchCrew().crew().kickoff(inputs=crew_inputs)

        print("Job search and analysis completed")
        self.state.skills_analysis = result.raw

    @listen(search_and_analyze_jobs)
    def generate_personalized_resume(self):
        """Generate personalized resume based on job analysis"""
        print("Generating personalized resume...")

        # The resume generation is already handled by the crew's resume_writer agent
        # The result contains information about the generated resume
        self.state.resume_path = "personalized_resume.docx"
        print(f"Resume generated successfully: {self.state.resume_path}")

    @listen(generate_personalized_resume)
    def finalize_results(self):
        """Finalize and present results"""
        print("\nJobSearch Flow completed successfully!")
        print("Skills analysis: Available in flow state")
        print(f"Resume generated: {self.state.resume_path}")
        print("\n" + "=" * 50)
        print("FLOW SUMMARY:")
        print("=" * 50)
        print(f"User: {self.state.user_profile.get('name', 'N/A')}")
        print(f"Search Term: {self.state.job_search_params.get('search_term', 'N/A')}")
        print(f"Location: {self.state.job_search_params.get('location', 'N/A')}")
        print(f"Resume Output: {self.state.resume_path}")
        print("=" * 50)


def run_job_search_flow(
    user_profile: Dict[str, Any] | None = None,
    job_search_params: Dict[str, Any] | None = None,
):
    """
    Run the JobSearch flow with user-provided parameters

    Args:
        user_profile: Dictionary containing user's career information
        job_search_params: Dictionary containing job search parameters
    """
    flow = JobSearchFlow()

    if user_profile:
        flow.state.user_profile = user_profile
    if job_search_params:
        flow.state.job_search_params = job_search_params

    return flow.kickoff()


if __name__ == "__main__":
    # Example usage
    sample_user_profile = {
        "name": "Jane Smith",
        "email": "jane.smith@email.com",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/janesmith",
        "skills": ["Python", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
        "experience": [
            {
                "title": "Senior Full Stack Developer",
                "company": "Tech Innovations Inc",
                "duration": "2021-2024",
                "description": "Led development of scalable web applications using React and Node.js, deployed on AWS infrastructure",
            },
            {
                "title": "Software Developer",
                "company": "StartupCorp",
                "duration": "2019-2021",
                "description": "Developed RESTful APIs and frontend interfaces for customer-facing applications",
            },
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "Stanford University",
                "year": "2019",
            }
        ],
        "certifications": [
            "AWS Certified Solutions Architect",
            "React Developer Certification",
        ],
        "summary": "Experienced full-stack developer with 5+ years building scalable web applications using modern technologies",
    }

    sample_job_params = {
        "search_term": "Senior Full Stack Developer",
        "location": "San Francisco",
        "results_wanted": 15,
        "fine_tune_search_string": "startups with good work-life balance and remote-first culture",
    }

    run_job_search_flow(sample_user_profile, sample_job_params)
