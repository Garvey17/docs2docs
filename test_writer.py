# from organiser.schema import ClassifiedContent, OrganisedDocs
from organiser.schema import ClassifiedContent, OrganisedDocs
from writer.writer import write_section

# Dummy ClassifiedContent objects with realistic text
installation_content = ClassifiedContent(
    url="https://docs.example.com/install",
    section="installation",
    source_title="Installation Guide",
    raw_text="""
    To install ExampleLib, you need Python 3.8 or higher.

    Prerequisites:
    - Python 3.8+
    - pip package manager

    Installation:
    Run the following command to install ExampleLib:

    pip install examplelib

    To verify the installation:

    python -c "import examplelib; print(examplelib.__version__)"
    """
)

getting_started_content = ClassifiedContent(
    url="https://docs.example.com/quickstart",
    section="getting_started",
    source_title="Quick Start",
    raw_text="""
    Getting started with ExampleLib is straightforward.

    First, import the library:

    import examplelib

    Create a client instance:

    client = examplelib.Client(api_key="your_api_key")

    Make your first request:

    response = client.run(task="hello world")
    print(response.output)
    """
)

features_content = ClassifiedContent(
    url="https://docs.example.com/features",
    section="features",
    source_title="Features Overview",
    raw_text="""
    ExampleLib provides several powerful features:

    Async Support:
    ExampleLib supports async/await out of the box.

    async def main():
        client = examplelib.AsyncClient(api_key="your_api_key")
        response = await client.run(task="hello world")

    Streaming:
    Stream responses token by token for real-time output.

    for chunk in client.stream(task="tell me a story"):
        print(chunk.text, end="")

    Retry Logic:
    Automatic retries with exponential backoff on failed requests.

    client = examplelib.Client(api_key="your_api_key", max_retries=3)

    Caching:
    Built-in response caching to avoid redundant API calls.

    client = examplelib.Client(api_key="your_api_key", cache=True)
    """
)

# Construct OrganisedDocs
organised = OrganisedDocs(
    installation=[installation_content],
    getting_started=[getting_started_content],
    features=[features_content]
)

# Run writer
sections = write_section(organised)

from services.output_service import render
output_path = render(sections, "example_doc")
print(output_path)

# Print results
# for section in sections:
#     print(f"\n{'='*60}")
#     print(f"SECTION: {section.section.upper()}")
#     print(f"REVISIONS: {section.revision_count}")
#     print(f"{'='*60}")
#     print(section.content)