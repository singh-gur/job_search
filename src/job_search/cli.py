#!/usr/bin/env python
import json
from typing import Optional

import click
from pydantic import ValidationError

from job_search.flows.jod_search import run_job_search_flow
from job_search.main import PoemFlow, plot_flow
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

        click.echo("🚀 Starting Job Search Flow")
        click.echo(f"User: {config.user_profile.name} ({config.user_profile.email})")
        click.echo(
            f"Search: {config.job_search_params.search_term} in {config.job_search_params.location}"
        )

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
    )

    config = JobSearchConfig(
        user_profile=user_profile, job_search_params=job_search_params
    )

    # Export to JSON
    with open(filename, "w") as f:
        json.dump(config.model_dump(), f, indent=2)

    click.echo(f"Example profile saved to {filename}")
    click.echo(f"You can now run: job-search-cli job-search-from-file {filename}")


if __name__ == "__main__":
    cli()
