"""Video generation and Cloud Storage tool for PrimeCuts Agent.

Generates culinary and cut preparation showcase videos using Google's Omni model
(gemini-omni-flash-preview) in the global region via Vertex AI Interactions API.
Saves the artifact to ADK ToolContext (Playground Artifacts panel) and uploads
to the public Cloud Storage bucket, returning a live public https URL.
"""

import base64
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded bucket name and GCP project as strings
GCP_PROJECT_ID = "qwiklabs-gcp-03-698d519bd637"
BUCKET_NAME = "primecuts-media-qwiklabs-gcp-03-698d519bd637"


async def generate_cut_showcase_video(
    item_name: str,
    tool_context: ToolContext,
) -> str:
    """Generates a short showcase video for a fresh meat cut or gourmet dish using gemini-omni-flash-preview.

    Saves the video as a session artifact in ADK and uploads it to the public Cloud Storage bucket.

    Args:
        item_name: Name of the meat cut or gourmet meat dish (e.g., 'Special Goat Biryani Cut',
                   'Fresh Farm Chicken Curry Cut', 'Tandoori Chicken Drumsticks').
        tool_context: ADK ToolContext used to save session artifacts.

    Returns:
        Public HTTPS URL of the uploaded video in Cloud Storage.
    """
    try:
        # 1. Initialize GenAI client on Vertex AI in the global region
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location="global",
        )

        prompt = (
            f"Cinematic close-up video of gourmet {item_name}. "
            "Artisan butcher counter presentation with fresh herbs, pristine marbling, "
            "natural lighting, high detail food cinematography, 720p."
        )

        # 2. Call gemini-omni-flash-preview model via interactions API
        response = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=[{"type": "text", "text": prompt}],
            response_format=[{"type": "video", "duration": "4s"}],
        )

        # 3. Extract generated video bytes
        video_bytes = None
        if hasattr(response, "output_video") and response.output_video and response.output_video.data:
            video_bytes = base64.b64decode(response.output_video.data)
        elif hasattr(response, "steps") and response.steps:
            for step in response.steps:
                if getattr(step, "type", None) == "model_output" and hasattr(step, "content"):
                    for content_item in step.content:
                        if getattr(content_item, "type", None) == "video" and getattr(content_item, "data", None):
                            video_bytes = base64.b64decode(content_item.data)
                            break
        
        if not video_bytes:
            return f"Error: Could not retrieve video bytes from model response for {item_name}."

        filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

        # 4. (1) Save video artifact to ToolContext for the Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
        try:
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
                custom_metadata={"item_name": item_name, "model": "gemini-omni-flash-preview"},
            )
        except Exception as e:
            # Fallback if artifact service isn't active in standalone mode
            print(f"[Warning] Failed to save artifact via tool_context: {e}")

        # 5. (2) Upload the same video bytes directly to the public Cloud Storage bucket
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"videos/{filename}")
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/videos/{filename}"
        return public_url

    except Exception as exc:
        return f"Error generating video for {item_name}: {exc}"
