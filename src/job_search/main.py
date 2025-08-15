#!/usr/bin/env python
from random import randint

from crewai.flow import Flow, listen, start
from pydantic import BaseModel

from job_search.crews.poem_crew.poem_crew import PoemCrew
from job_search.flows.jod_search import JobSearchFlow, run_job_search_flow


class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


class PoemFlow(Flow[PoemState]):
    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = (
            PoemCrew()
            .crew()
            .kickoff(inputs={"sentence_count": self.state.sentence_count})
        )

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)


def kickoff():
    """Main entry point - runs JobSearch flow by default"""
    print("🚀 Starting JobSearch Application")
    print("Choose an option:")
    print("1. Run JobSearch Flow (default)")
    print("2. Run Poem Flow")

    try:
        choice = input("Enter your choice (1-2, default=1): ").strip()
        if choice == "2":
            poem_flow = PoemFlow()
            poem_flow.kickoff()
        else:
            # Run JobSearch flow with sample data
            run_job_search_flow()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


def plot():
    """Plot flow diagrams"""
    print("Choose flow to plot:")
    print("1. JobSearch Flow")
    print("2. Poem Flow")

    choice = input("Enter your choice (1-2): ").strip()
    if choice == "1":
        job_search_flow = JobSearchFlow()
        job_search_flow.plot()
    else:
        poem_flow = PoemFlow()
        poem_flow.plot()


if __name__ == "__main__":
    kickoff()
