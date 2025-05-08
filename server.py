from fastmcp import FastMCP, Context
import httpx
from typing import Dict, Optional

# Base URLs
METADATA_BASE_URL = "https://datadashboard.health.gov.il/api/content/dashboard"
DATA_BASE_URL = "https://datadashboard.health.gov.il/api"

# Available subjects with descriptions
SUBJECTS_INFO = {
    "warCasualties": {
        "name": "War Casualties",
        "description": "Information about war-related medical cases and emergency support contacts"
    },
    "medicalServices": {
        "name": "Medical Services Availability",
        "description": "Information about availability of various medical services including pharmacies, HMO services, family health centers"
    },
    "beaches": {
        "name": "Beaches",
        "description": "Information about beach conditions and facilities"
    },
    "HMO_insured_main": {
        "name": "HMO Insurance",
        "description": "Information about health insurance through HMOs"
    },
    "childKi": {
        "name": "Child Development",
        "description": "Information about child development services"
    },
    "childCheckup": {
        "name": "Child Checkups",
        "description": "Information about child medical checkup services"
    },
    "serviceQuality": {
        "name": "Service Quality",
        "description": "Quality measurements, patient experience surveys, and service complaints across medical facilities"
    }
}

# Available subjects list
SUBJECTS = list(SUBJECTS_INFO.keys())

mcp = FastMCP("ILHealth", dependencies=["httpx", "typing"])
client = httpx.Client(timeout=30.0)

@mcp.tool(
    "get_available_subjects",
    "Get a list of all available subject areas with descriptions",
    {}
)
async def get_available_subjects() -> Dict:
    """Get a list of all available subject areas with descriptions"""
    return {
        "status": "success",
        "data": {
            "subjects": [
                {
                    "id": subject_id,
                    "name": info["name"],
                    "description": info["description"]
                }
                for subject_id, info in SUBJECTS_INFO.items()
            ]
        }
    }


@mcp.tool(
    "get_metadata",
    "Get metadata about available data endpoints for a specific subject. Some endpoints may include an embedLink field that provides access to an interactive GIS map for data visualization.",
    {
        "subject": {
            "type": "string",
            "description": "The subject area to get metadata for",
            "enum": SUBJECTS
        }
    }
)
async def get_metadata(subject: str) -> Dict:
    """Get metadata about available data endpoints for a specific subject"""
    if subject not in SUBJECTS:
        raise ValueError(f"Invalid subject. Must be one of: {', '.join(SUBJECTS)}")
    
    url = f"{METADATA_BASE_URL}/{subject}"
    response = client.get(url)
    response.raise_for_status()
    
    metadata = response.json()
    
    # Clean any newlines from values in the response JSON
    def clean_json(obj):
        if isinstance(obj, dict):
            return {k: clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json(item) for item in obj]
        elif isinstance(obj, str):
            return obj.strip()  # This will remove both leading and trailing whitespace/newlines
        return obj

    # Clean the metadata before processing
    metadata = clean_json(metadata)

    # Transform the response to be more LLM-friendly
    available_endpoints = []
    for card in metadata.get("cards", []):
        # Create a cleaned version of the card data
        cleaned_card = {
            "id": card["id"].strip(),
            "endPointName": card["endPointName"].strip(),
            "apiSrc": card["apiSrc"].strip(),
            "transportProject": card["transportProject"].strip(),
            "section": card["sectionId"].strip(),
            "componentName": card["componentName"].strip(),
            "embedLink": card.get("embedLink", "").strip() if card.get("embedLink") else None
        }
        available_endpoints.append(cleaned_card)

    # Clean the sections data
    cleaned_sections = []
    for section in metadata.get("sections", []):
        cleaned_section = {k: v.strip() if isinstance(v, str) else v for k, v in section.items()}
        cleaned_sections.append(cleaned_section)

    return {
        "status": "success",
        "data": {
            "availableEndpoints": available_endpoints,
            "sections": cleaned_sections
        }
    }

@mcp.tool(
    "get_data",
    "Get specific data from an endpoint. If the response includes an embedLink field, it provides access to an interactive GIS map where you can visualize this data - consider suggesting the user to open this map for a better understanding of the information.",
    {
        "subject": {
            "type": "string",
            "description": "The subject area",
            "enum": SUBJECTS
        },
        "transportProject": {
            "type": "string",
            "description": "The project identifier"
        },
        "endPointName": {
            "type": "string",
            "description": "The specific endpoint to query"
        }
    }
)
async def get_data(subject: str, transportProject: str, endPointName: str) -> Dict:
    """Get specific data from an endpoint"""
    if subject not in SUBJECTS:
        raise ValueError(f"Invalid subject. Must be one of: {', '.join(SUBJECTS)}")
    
    url = f"{DATA_BASE_URL}/{endPointName}"
    response = client.get(url)
    response.raise_for_status()
    
    # Clean any newlines from values in the response JSON
    def clean_json(obj):
        if isinstance(obj, dict):
            return {k: clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json(item) for item in obj]
        elif isinstance(obj, str):
            return obj.strip()  # This will remove both leading and trailing whitespace/newlines
        return obj

    # Clean the response data before returning
    data = clean_json(response.json())
    
    return {
        "status": "success",
        "metadata": {
            "subject": subject,
            "transportProject": transportProject,
            "endpoint": endPointName,
        },
        "data": data
    }

@mcp.tool(
    "get_links",
    "Get relevant links and documentation for a subject area",
    {
        "subject": {
            "type": "string",
            "description": "The subject area to get links for",
            "enum": SUBJECTS
        },
        "sectionId": {
            "type": "string",
            "description": "Optional section ID to filter links",
            "optional": True
        }
    }
)
async def get_links(subject: str, sectionId: Optional[str] = None) -> Dict:
    """Get relevant links and documentation for a subject area"""
    if subject not in SUBJECTS:
        raise ValueError(f"Invalid subject. Must be one of: {', '.join(SUBJECTS)}")
    
    # First get metadata to access links
    url = f"{METADATA_BASE_URL}/{subject}"
    response = client.get(url)
    response.raise_for_status()
    
    # Clean any newlines from values in the response JSON
    def clean_json(obj):
        if isinstance(obj, dict):
            return {k: clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json(item) for item in obj]
        elif isinstance(obj, str):
            return obj.strip()  # This will remove both leading and trailing whitespace/newlines
        return obj

    # Clean the metadata before processing
    metadata = clean_json(response.json())
    
    links = metadata.get("links", [])
    if sectionId:
        links = [link for link in links if link["sectionId"] == sectionId]
    
    return {
        "status": "success",
        "data": {
            "links": links
        }
    }

if __name__ == "__main__":
    mcp.run()
