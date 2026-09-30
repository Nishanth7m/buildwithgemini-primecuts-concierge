"""Image generation and public Cloud Storage tool for PrimeCuts Agent."""

import os
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from app.firestore_client import FIRESTORE_PROJECT_ID

BUCKET_NAME = os.getenv("PRIMECUTS_STORAGE_BUCKET", f"primecuts-media-{FIRESTORE_PROJECT_ID}")


def generate_recipe_plating_visual(cut_name: str, dish_name: str) -> str:
    """Generates a culinary food photography visual for a dish using fresh meat cuts and uploads to Cloud Storage.

    Args:
        cut_name: Name of the meat cut (e.g. 'Special Goat Biryani Cut', 'Chicken Drumsticks').
        dish_name: Name of the prepared dish (e.g. 'Hyderabadi Dum Biryani', 'Tandoori Roast').

    Returns:
        Public HTTP image URL and presentation description.
    """
    try:
        # 1. Initialize GenAI client on Vertex AI
        client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="us-central1",  # Imagen 3 is widely supported on us-central1
        )

        prompt = (
            f"Professional culinary food photography of freshly prepared {dish_name} "
            f"made with premium {cut_name}. Served on an artisan plate with fresh coriander garnish, "
            f"warm moody restaurant lighting, shallow depth of field, 8k resolution, photorealistic."
        )

        # 2. Generate image using Imagen 3
        result = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="4:3",
            ),
        )

        if not result.generated_images:
            return f"Could not generate visual for {dish_name}."

        image_bytes = result.generated_images[0].image.image_bytes

        # 3. Upload to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        file_id = f"plating_{uuid.uuid4().hex[:8]}.jpg"
        blob = bucket.blob(f"recipes/{file_id}")
        blob.upload_from_string(image_bytes, content_type="image/jpeg")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/recipes/{file_id}"
        return (
            f"📸 Plating Visual Generated for **{dish_name}** ({cut_name})!\n"
            f"• Public URL: {public_url}\n"
            f"• Presentation: Freshly cooked and styled with artisan garnish."
        )
    except Exception as e:
        return f"Error generating visual: {str(e)}"
