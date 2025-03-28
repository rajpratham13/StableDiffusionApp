import os
import torch
import torch.multiprocessing as mp
from flask import Flask, request, jsonify, render_template, send_from_directory
from diffusers import StableDiffusionPipeline
import atexit

app = Flask(__name__)

# ---- CONFIG ----
STATIC_FOLDER = "static/generated_images"
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ---- SET MULTIPROCESSING METHOD ----
mp.set_start_method("fork", force=True)

# ---- LOAD PIPELINE ----
device = "mps" if torch.backends.mps.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")

# Use float32 on MPS to avoid precision issues
pipe.to(device, torch.float32)

# Enable attention slicing and VAE slicing for memory optimization
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()

# ---- RENDER HOMEPAGE ----
@app.route("/")
def index():
    return render_template("index.html")


# ---- IMAGE GENERATION ENDPOINT ----
@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.json
        prompt = data.get("prompt", "A beautiful landscape")
        negative_prompt = data.get("negative_prompt", None)
        num_inference_steps = int(data.get("num_inference_steps", 50))
        height = int(data.get("height", 512))
        width = int(data.get("width", 512))
        num_images_per_prompt = int(data.get("num_images_per_prompt", 1))

        # Clear MPS memory before running
        if device == "mps":
            torch.mps.empty_cache()

        # Generate the image(s) with optimal settings
        images = pipe(
            prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
            num_images_per_prompt=num_images_per_prompt,
            guidance_scale=7.5  # Keeps default guidance scale
        ).images

        image_paths = []
        for i, image in enumerate(images):
            image_path = f"{STATIC_FOLDER}/generated_image_{i + 1}.png"
            image.save(image_path)
            image_paths.append(f"/static/generated_images/generated_image_{i + 1}.png")

        # Clear cache after generation to avoid memory leak
        if device == "mps":
            torch.mps.empty_cache()

        return jsonify({"success": True, "paths": image_paths})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- SERVE STATIC IMAGES ----
@app.route("/static/generated_images/<path:filename>")
def get_image(filename):
    return send_from_directory(STATIC_FOLDER, filename)


# ---- CLEANUP FUNCTION ----
def cleanup():
    """Release GPU/MPS resources and terminate processes."""
    print("Cleaning up resources...")
    if device == "mps":
        torch.mps.empty_cache()
    for p in mp.active_children():
        p.terminate()
    print("Resources released successfully!")


# ---- REGISTER CLEANUP ----
atexit.register(cleanup)

# ---- RUN FLASK APP ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
