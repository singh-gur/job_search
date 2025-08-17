from typing import List, Type

from crewai.tools import BaseTool
from jobspy import scrape_jobs
from pydantic import BaseModel, Field


class JobSpyInput(BaseModel):
    site_name: List[str] = Field(
        default=["indeed", "linkedin", "glassdoor"],
        description="Job sites to search on",
    )
    search_term: str = Field(description="Job title or keywords to search for")
    location: str = Field(default="", description="Location to search in")
    results_wanted: int = Field(
        default=20, description="Number of job results to return"
    )
    hours_old: int = Field(
        default=72, description="How recent the job postings should be in hours"
    )
    country_indeed: str = Field(default="USA", description="Country for Indeed search")
    is_remote: bool = Field(
        default=False, description="Whether to search for remote jobs"
    )


class JobSpyTool(BaseTool):
    name: str = "JobSpy Job Search Tool"
    description: str = "Search for job listings using JobSpy across multiple job boards"
    args_schema: Type[BaseModel] = JobSpyInput

    def _run(
        self,
        site_name: List[str],
        search_term: str,
        location: str,
        results_wanted: int,
        hours_old: int,
        country_indeed: str,
        is_remote: bool,
    ) -> str:
        try:
            jobs_df = scrape_jobs(
                site_name=site_name,
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed=country_indeed,
                is_remote=is_remote,
            )

            if jobs_df.empty:
                return "No jobs found matching the search criteria."

            job_listings = []
            for _, job in jobs_df.iterrows():
                job_info = {
                    "title": job.get("title", "N/A"),
                    "company": job.get("company", "N/A"),
                    "location": job.get("location", "N/A"),
                    "job_url": job.get("job_url", "N/A"),
                    "description": job.get("description", "N/A")[:500] + "..."
                    if len(str(job.get("description", ""))) > 500
                    else job.get("description", "N/A"),
                    "salary_min": job.get("min_amount", "N/A"),
                    "salary_max": job.get("max_amount", "N/A"),
                    "date_posted": job.get("date_posted", "N/A"),
                    "site": job.get("site", "N/A"),
                }
                job_listings.append(job_info)

            # Format output for the agent
            formatted_output = f"Found {len(job_listings)} job listings:\n\n"
            for i, job in enumerate(job_listings, 1):
                formatted_output += f"Job {i}:\n"
                formatted_output += f"Title: {job['title']}\n"
                formatted_output += f"Company: {job['company']}\n"
                formatted_output += f"Location: {job['location']}\n"
                formatted_output += (
                    f"Salary: ${job['salary_min']} - ${job['salary_max']}\n"
                )
                formatted_output += f"Posted: {job['date_posted']}\n"
                formatted_output += f"Description: {job['description']}\n"
                formatted_output += f"URL: {job['job_url']}\n"
                formatted_output += f"Source: {job['site']}\n"
                formatted_output += "-" * 50 + "\n\n"

            return formatted_output

        except Exception as e:
            return f"Error searching for jobs: {str(e)}"
