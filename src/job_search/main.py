#!/usr/bin/env python
from random import randint

from crewai.flow import Flow, listen, start
from pydantic import BaseModel

from job_search.crews.poem_crew.poem_crew import PoemCrew


class PoemState(BaseModel):
    sentence_count: int | None = None
    poem: str = ""


class PoemFlow(Flow[PoemState]):
    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        if self.state.sentence_count is None:
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


def kickoff_flow(flow):
    """Main entry point - runs the specified flow"""
    print(f"🚀 Starting {flow.__class__.__name__}")
    flow.kickoff()


def plot_flow(flow):
    """Plot flow diagrams"""
    print(f"📊 Plotting {flow.__class__.__name__}")


if __name__ == "__main__":
    poem_flow = PoemFlow()
    kickoff_flow(poem_flow)
    plot_flow(poem_flow)
    print("✅ Flow completed successfully")
