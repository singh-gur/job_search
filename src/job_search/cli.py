#!/usr/bin/env python
import json
from typing import Optional

import click
from pydantic import ValidationError

from job_search.flows.jod_search import run_job_search_flow
from job_search.models import (
    Education,
    Experience,
    JobSearchConfig,
    JobSearchParams,
    UserProfile,
)


@click.group()
def cli():
    """Job Search CLI - Run flows with customizable parameters"""
    pass




@cli.command()
@click.argument("profile_file", type=click.Path(exists=True))
def job_search(profile_file: str):
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
            "results_wanted": 15,
            "fine_tune_search_string": "startups with good work-life balance"
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

        click.echo("🚀 Starting Job Search Flow")
        click.echo(f"User: {config.user_profile.name} ({config.user_profile.email})")
        click.echo(
            f"Search: {config.job_search_params.search_term} in {config.job_search_params.location}"
        )
        if config.job_search_params.fine_tune_search_string:
            click.echo(f"Fine-tune criteria: {config.job_search_params.fine_tune_search_string}")

        result = run_job_search_flow(user_profile, job_search_params)
        click.echo("✅ Job Search Flow completed successfully")
        return result

    except ValidationError as e:
        click.echo("Validation error in profile file:", err=True)
        for error in e.errors():
            click.echo(
                f"  - {'.'.join(str(x) for x in error['loc'])}: {error['msg']}",
                err=True,
            )
    except json.JSONDecodeError as e:
        click.echo(f"Error parsing JSON file: {e}", err=True)
    except Exception as e:
        click.echo(f"Error running job search: {e}", err=True)


@cli.command()
@click.argument("profile_file", type=click.Path(exists=True))
@click.option("--search-term", default="Software Developer", help="Job title or search term")
@click.option("--location", default="Remote", help="Job location")
@click.option("--results-wanted", default=10, type=int, help="Number of job results to retrieve")
@click.option("--fine-tune", help="Additional search criteria for LLM-based fine-tuning")
def job_search_with_params(profile_file: str, search_term: str, location: str, results_wanted: int, fine_tune: Optional[str]):
    """Run Job Search Flow with separate profile file and search parameters

    PROFILE_FILE: Path to JSON file containing only user profile

    Example profile JSON structure:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "React"],
        "experience": [...],
        "education": [...]
    }
    """
    try:
        with open(profile_file, "r") as f:
            profile_data = json.load(f)

        # Validate using Pydantic models
        user_profile = UserProfile(**profile_data)
        job_search_params = JobSearchParams(
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            fine_tune_search_string=fine_tune
        )

        # Convert to dict for flow compatibility
        user_profile_dict = user_profile.model_dump()
        job_search_params_dict = job_search_params.model_dump()

        click.echo("🚀 Starting Job Search Flow")
        click.echo(f"User: {user_profile.name} ({user_profile.email})")
        click.echo(f"Search: {search_term} in {location}")
        click.echo(f"Results wanted: {results_wanted}")
        if fine_tune:
            click.echo(f"Fine-tune criteria: {fine_tune}")

        result = run_job_search_flow(user_profile_dict, job_search_params_dict)
        click.echo("✅ Job Search Flow completed successfully")
        return result

    except ValidationError as e:
        click.echo("Validation error in profile file:", err=True)
        for error in e.errors():
            click.echo(
                f"  - {'.'.join(str(x) for x in error['loc'])}: {error['msg']}",
                err=True,
            )
    except json.JSONDecodeError as e:
        click.echo(f"Error parsing JSON file: {e}", err=True)
    except Exception as e:
        click.echo(f"Error running job search: {e}", err=True)


@cli.command()
@click.option(
    "--filename",
    default="example_profile.json",
    help="Output filename for the example profile",
)
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
                description="Led development of scalable web applications using React and Node.js, deployed on AWS infrastructure",
            ),
            Experience(
                title="Software Developer",
                company="StartupCorp",
                duration="2019-2021",
                description="Developed RESTful APIs and frontend interfaces for customer-facing applications",
            ),
        ],
        education=[
            Education(
                degree="Bachelor of Science in Computer Science",
                school="Stanford University",
                year="2019",
            )
        ],
        certifications=[
            "AWS Certified Solutions Architect",
            "React Developer Certification",
        ],
        summary="Experienced full-stack developer with 5+ years building scalable web applications using modern technologies",
    )

    job_search_params = JobSearchParams(
        search_term="Senior Full Stack Developer",
        location="San Francisco",
        results_wanted=15,
        fine_tune_search_string="startups with good work-life balance and remote-first culture"
    )

    config = JobSearchConfig(
        user_profile=user_profile, job_search_params=job_search_params
    )

    # Export to JSON
    with open(filename, "w") as f:
        json.dump(config.model_dump(), f, indent=2)

    click.echo(f"Example profile saved to {filename}")
    click.echo(f"You can now run: job-search-cli job-search {filename}")


@cli.command()
@click.option(
    "--filename",
    default="user_profile.json",
    help="Output filename for the user profile",
)
def example_user_profile(filename: str):
    """Generate an example user profile JSON file (profile only, no search params)"""

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
                description="Led development of scalable web applications using React and Node.js, deployed on AWS infrastructure",
            ),
            Experience(
                title="Software Developer",
                company="StartupCorp",
                duration="2019-2021",
                description="Developed RESTful APIs and frontend interfaces for customer-facing applications",
            ),
        ],
        education=[
            Education(
                degree="Bachelor of Science in Computer Science",
                school="Stanford University",
                year="2019",
            )
        ],
        certifications=[
            "AWS Certified Solutions Architect",
            "React Developer Certification",
        ],
        summary="Experienced full-stack developer with 5+ years building scalable web applications using modern technologies",
    )

    # Export to JSON
    with open(filename, "w") as f:
        json.dump(user_profile.model_dump(), f, indent=2)

    click.echo(f"Example user profile saved to {filename}")
    click.echo(f"You can now run: job-search-cli job-search-with-params {filename} --search-term 'Senior Developer' --location 'Remote' --fine-tune 'startup culture'")


if __name__ == "__main__":
    cli()
