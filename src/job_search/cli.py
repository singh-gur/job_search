#!/usr/bin/env python
import json
from typing import Optional

import click
from pydantic import ValidationError

from job_search.flows.jod_search import JobSearchFlow, run_job_search_flow
from job_search.main import PoemFlow, plot_flow
from job_search.models import UserProfile, JobSearchParams, JobSearchConfig, Experience, Education


@click.group()
def cli():
    """Job Search CLI - Run flows with customizable parameters"""
    pass


@cli.command()
@click.option("--sentence-count", type=int, help="Number of sentences for the poem")
@click.option("--plot", is_flag=True, help="Plot the flow diagram after execution")
def poem(sentence_count: Optional[int], plot: bool):
    """Run the Poem Flow to generate a poem"""
    flow = PoemFlow()

    if sentence_count is not None:
        flow.state.sentence_count = sentence_count

    click.echo(f"🚀 Starting {flow.__class__.__name__}")
    result = flow.kickoff()

    if plot:
        plot_flow(flow)

    click.echo("✅ Poem Flow completed successfully")
    return result


@cli.command()
@click.option("--name", help="User name")
@click.option("--email", help="User email")
@click.option("--phone", help="User phone number")
@click.option("--location", help="User location")
@click.option("--linkedin", help="LinkedIn profile URL")
@click.option("--skills", help="Comma-separated list of skills")
@click.option("--summary", help="Professional summary")
@click.option("--experience", help="JSON string of experience array")
@click.option("--education", help="JSON string of education array")
@click.option("--certifications", help="Comma-separated list of certifications")
@click.option("--search-term", help="Job search term/title")
@click.option("--search-location", help="Job search location")
@click.option(
    "--results-wanted", type=int, default=10, help="Number of job results wanted"
)
@click.option(
    "--user-profile-json",
    help="JSON file path or JSON string containing complete user profile",
)
@click.option("--plot", is_flag=True, help="Plot the flow diagram after execution")
def job_search(
    name: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    location: Optional[str],
    linkedin: Optional[str],
    skills: Optional[str],
    summary: Optional[str],
    experience: Optional[str],
    education: Optional[str],
    certifications: Optional[str],
    search_term: Optional[str],
    search_location: Optional[str],
    results_wanted: int,
    user_profile_json: Optional[str],
    plot: bool,
):
    """Run the Job Search Flow to find jobs and generate personalized resumes"""

    user_profile_data = {}
    job_search_params_data = {}

    # Handle user profile JSON input
    if user_profile_json:
        try:
            # Try to load as file first
            try:
                with open(user_profile_json, "r") as f:
                    config_data = json.load(f)
                    # Check if it's a full config or just user profile
                    if "user_profile" in config_data:
                        user_profile_data = config_data["user_profile"]
                        job_search_params_data = config_data.get("job_search_params", {})
                    else:
                        user_profile_data = config_data
            except FileNotFoundError:
                # If not a file, try to parse as JSON string
                config_data = json.loads(user_profile_json)
                if "user_profile" in config_data:
                    user_profile_data = config_data["user_profile"]
                    job_search_params_data = config_data.get("job_search_params", {})
                else:
                    user_profile_data = config_data
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing user profile JSON: {e}", err=True)
            return

    # Build user profile from individual options
    if name:
        user_profile_data["name"] = name
    if email:
        user_profile_data["email"] = email
    if phone:
        user_profile_data["phone"] = phone
    if location:
        user_profile_data["location"] = location
    if linkedin:
        user_profile_data["linkedin"] = linkedin
    if summary:
        user_profile_data["summary"] = summary

    if skills:
        user_profile_data["skills"] = [skill.strip() for skill in skills.split(",")]

    if certifications:
        user_profile_data["certifications"] = [
            cert.strip() for cert in certifications.split(",")
        ]

    if experience:
        try:
            user_profile_data["experience"] = json.loads(experience)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing experience JSON: {e}", err=True)
            return

    if education:
        try:
            user_profile_data["education"] = json.loads(education)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing education JSON: {e}", err=True)
            return

    # Build job search parameters
    if search_term:
        job_search_params_data["search_term"] = search_term
    if search_location:
        job_search_params_data["location"] = search_location
    if results_wanted:
        job_search_params_data["results_wanted"] = results_wanted

    try:
        # Validate and create Pydantic models
        if not user_profile_data:
            click.echo("Error: User profile is required. Provide at least name and email.", err=True)
            return

        user_profile = UserProfile(**user_profile_data)
        job_search_params = JobSearchParams(**job_search_params_data)
        
        # Convert back to dict for flow compatibility
        user_profile_dict = user_profile.model_dump()
        job_search_params_dict = job_search_params.model_dump()

        # Run the job search flow
        flow = JobSearchFlow()
        flow.state.user_profile = user_profile_dict
        flow.state.job_search_params = job_search_params_dict

        click.echo(f"🚀 Starting {flow.__class__.__name__}")
        click.echo(f"User: {user_profile.name} ({user_profile.email})")
        click.echo(f"Search: {job_search_params.search_term} in {job_search_params.location}")
        
        result = flow.kickoff()

        if plot:
            plot_flow(flow)

        click.echo("✅ Job Search Flow completed successfully")
        return result
        
    except ValidationError as e:
        click.echo(f"Validation error in user profile or job search parameters:", err=True)
        for error in e.errors():
            click.echo(f"  - {error['loc'][0]}: {error['msg']}", err=True)
        return


@cli.command()
@click.argument("profile_file", type=click.Path(exists=True))
def job_search_from_file(profile_file: str):
    """Run Job Search Flow using a JSON profile file

    PROFILE_FILE: Path to JSON file containing user profile and job search parameters

    Example JSON structure:
    {
        "user_profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "React"],
            "experience": [...],
            "education": [...]
        },
        "job_search_params": {
            "search_term": "Software Developer",
            "location": "Remote",
            "results_wanted": 15
        }
    }
    """
    try:
        with open(profile_file, "r") as f:
            config_data = json.load(f)

        # Validate using Pydantic models
        config = JobSearchConfig(**config_data)
        
        # Convert to dict for flow compatibility
        user_profile = config.user_profile.model_dump()
        job_search_params = config.job_search_params.model_dump()

        click.echo(f"🚀 Starting Job Search Flow")
        click.echo(f"User: {config.user_profile.name} ({config.user_profile.email})")
        click.echo(f"Search: {config.job_search_params.search_term} in {config.job_search_params.location}")

        result = run_job_search_flow(user_profile, job_search_params)
        click.echo("✅ Job Search Flow completed successfully")
        return result

    except ValidationError as e:
        click.echo(f"Validation error in profile file:", err=True)
        for error in e.errors():
            click.echo(f"  - {'.'.join(str(x) for x in error['loc'])}: {error['msg']}", err=True)
    except json.JSONDecodeError as e:
        click.echo(f"Error parsing JSON file: {e}", err=True)
    except Exception as e:
        click.echo(f"Error running job search: {e}", err=True)


@cli.command()
@click.option("--filename", default="example_profile.json", help="Output filename for the example profile")
def example_profile(filename: str):
    """Generate an example profile JSON file"""
    
    # Create example using Pydantic models for validation
    user_profile = UserProfile(
        name="Jane Smith",
        email="jane.smith@email.com",
        phone="+1-555-0123",
        location="San Francisco, CA", 
        linkedin="linkedin.com/in/janesmith",
        skills=["Python", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
        experience=[
            Experience(
                title="Senior Full Stack Developer",
                company="Tech Innovations Inc",
                duration="2021-2024",
                description="Led development of scalable web applications using React and Node.js, deployed on AWS infrastructure"
            ),
            Experience(
                title="Software Developer", 
                company="StartupCorp",
                duration="2019-2021",
                description="Developed RESTful APIs and frontend interfaces for customer-facing applications"
            )
        ],
        education=[
            Education(
                degree="Bachelor of Science in Computer Science",
                school="Stanford University", 
                year="2019"
            )
        ],
        certifications=["AWS Certified Solutions Architect", "React Developer Certification"],
        summary="Experienced full-stack developer with 5+ years building scalable web applications using modern technologies"
    )
    
    job_search_params = JobSearchParams(
        search_term="Senior Full Stack Developer",
        location="San Francisco",
        results_wanted=15
    )
    
    config = JobSearchConfig(
        user_profile=user_profile,
        job_search_params=job_search_params
    )
    
    # Export to JSON
    with open(filename, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
    
    click.echo(f"Example profile saved to {filename}")
    click.echo(f"You can now run: job-search-cli job-search-from-file {filename}")


if __name__ == "__main__":
    cli()
