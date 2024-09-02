import os
import fal_client
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests
import base64
import traceback  # Add this import

# Load environment variables
load_dotenv()

# Use environment variables for API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
fal_api_key = os.getenv("FAL_API_KEY")

if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")
if not fal_api_key:
    raise ValueError("FAL_API_KEY not found in environment variables")

client = OpenAI(api_key=openai_api_key)

fal_client.api_key = os.getenv("FAL_API_KEY")

fal_models = {
    "flux-dev": "fal-ai/flux/dev",
    "flux-schnell": "fal-ai/flux/schnell",
    "sd-v3-medium": "fal-ai/stable-diffusion-v3-medium",
    "flux-realism": "fal-ai/flux-realism",
    "flux-lora": "fal-ai/flux-lora"
}

def generate_image_fal(prompt, model, image_size="landscape_16_9", inference_steps=50, guidance_scale=7.5, nsfw_allowed=False):
    print(f"Generating image. Model: {model}, Prompt: {prompt}, Size: {image_size}, Steps: {inference_steps}, Guidance: {guidance_scale}, NSFW Allowed: {nsfw_allowed}")
    
    try:
        fal_model = fal_models.get(model, "fal-ai/flux")
        
        arguments = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": int(inference_steps),
            "guidance_scale": float(guidance_scale),
            "safety_checker": False,
            "nsfw_filter": False,
            "censor_nsfw": False,
            "use_karras_sigmas": True,
            "clip_skip": 2,
            "disable_safety_checker": True,
            "filter_nsfw": False,
        }

        print(f"Sending arguments to FAL AI: {arguments}")

        result = fal_client.run(
            fal_model,
            arguments=arguments,
            timeout=120
        )
        print(f"FAL AI result: {result}")
        
        image_url = result['images'][0]['url']
        
        # Instead of relying on 'has_nsfw_concepts', we'll assume NSFW content if nsfw_allowed is True
        nsfw_detected = nsfw_allowed
        
        return image_url, nsfw_detected
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        raise

def text_chat(message, history, model):
    print(f"text_chat called with message: '{message}', model: '{model}'")
    history = history or []
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for human, ai in history:
        messages.append({"role": "user", "content": human})
        if ai:
            messages.append({"role": "assistant", "content": ai})
    messages.append({"role": "user", "content": message})
    
    try:
        if model in ['gpt-4o', 'chatgpt-4o-latest', 'gpt-4o-mini']:
            print(f"Using OpenAI for model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        history.append((message, ai_message))
        return history
    except Exception as e:
        print(f"Error in text_chat: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

def generate_image(prompt, model_name, input_images=None,):
    print(f"generate_image called with prompt: '{prompt}', model: '{model_name}', input_images: {input_images}")
    
    if model_name in fal_model_mapping:
        fal_model = fal_model_mapping[model_name]
        if model_name == "fal-ai/flux/dev/image-to-image":
            if input_images:
                image_data = generate_image_fal_image_to_image(prompt or "", fal_model, input_images)
            else:
                raise ValueError("No input images provided for image-to-image generation")
        else:
            if not prompt:
                raise ValueError("No prompt provided for text-to-image generation")
            image_data = generate_image_fal(prompt, fal_model)
    elif model_name == "dall-e":
        if not prompt:
            raise ValueError("No prompt provided for DALL-E generation")
        image_data = generate_image_openai(prompt)
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    
    if image_data is None:
        return None
    
    # Convert base64 string to PIL Image
    image_data = image_data.split(",")[1]  # Remove the "data:image/png;base64," part
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    
    return image

def generate_image_fal_image_to_image(prompt, fal_model, input_images, max_steps=50,):
    print(f"Attempting to generate image with FAL AI image-to-image. Model: {fal_model}, Prompt: {prompt}")
    
    try:
        if not input_images:
            raise ValueError("No input images provided for image-to-image generation")

        # Use the first image as the primary input
        with open(input_images[0], "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        result = fal_client.run(
            fal_model,
            arguments={
                "prompt": prompt,
                "image_url": f"data:image/png;base64,{image_data}",
                "image_size": "landscape_16_9",
                "num_inference_steps": max_steps,
                "guidance_scale": 7.5,
            },
            timeout=60  # Add a timeout of 60 seconds
        )
        print(f"FAL AI result: {result}")
        image_url = result['images'][0]['url']
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except requests.exceptions.Timeout:
        print("Request to FAL AI timed out")
        raise TimeoutError("The request to the image generation service timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        print("Connection error occurred while contacting FAL AI")
        raise ConnectionError("Unable to connect to the image generation service. Please check your internet connection and try again.")
    except Exception as e:
        print(f"Error generating image with FAL AI image-to-image: {str(e)}")
        print(f"Full error details: {e.response.text if hasattr(e, 'response') else 'No additional details'}")
        raise