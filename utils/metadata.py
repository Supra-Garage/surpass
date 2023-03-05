
import google.auth
import requests

METADATA_URI = "http://metadata.google.internal/computeMetadata/v1/"


def get_project_id() -> str:
    """Use the 'google-auth-library' to make a request to the metadata server or
    default to Application Default Credentials in your local environment."""
    _, project = google.auth.default()
    return project


def get_service_region() -> str:
    """Get region from local metadata server
    Region in format: projects/PROJECT_NUMBER/regions/REGION"""
    slug = "instance/region"
    data = requests.get(METADATA_URI + slug, headers={"Metadata-Flavor": "Google"})
    return data.content


def authenticated_request(url: str, method: str) -> str:
    """Make a request with an ID token to a protected service
    https://cloud.google.com/functions/docs/securing/authenticating#functions-bearer-token-example-python"""

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)

    resp = requests.request(
        method, url, headers={"Authorization": f"Bearer {id_token}"}
    )
    return resp.content
