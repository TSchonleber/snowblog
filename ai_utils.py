import os
import fal_client
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests
import base64

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

def generate_image_fal(prompt, fal_model, max_steps=50):
    print(f"Attempting to generate image with FAL AI. Model: {fal_model}, Prompt: {prompt}")
    
    try:
        result = fal_client.run(
            fal_model,
            arguments={
                "prompt": prompt,
                "image_size": "landscape_16_9",
                "num_inference_steps": max_steps,
                "guidance_scale": 7.5,
                "enable_safety_checker": False
            }
        )
        image_url = result['images'][0]['url']
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating image with FAL AI: {str(e)}")
        print(f"Full error details: {e.response.text if hasattr(e, 'response') else 'No additional details'}")
        return None

def generate_image_openai(prompt):
    print(f"Attempting to generate image with DALL-E. Prompt: {prompt}")
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating image with DALL-E: {str(e)}")
        return None

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
        if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-turbo"]:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content
        elif model in ["gpt-4o-mini", "chatgpt-4o-latest"]:
            response = fal_client.run(
                "fal-ai/gpt4all",
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            ai_message = response['choices'][0]['message']['content']
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        history.append((message, ai_message))
        return history
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        history.append((message, error_message))
        return history

def generate_image(prompt, model):
    print(f"generate_image called with prompt: '{prompt}', model: '{model}'")
    if model.startswith("fal-") or model == "flux-dev":
        if model == "fal-flux-dev1" or model == "flux-dev":
            fal_model = "fal-ai/flux"
        elif model == "fal-flux-schnell":
            fal_model = "fal-ai/flux/schnell"
        elif model == "fal-sd-v3-medium":
            fal_model = "fal-ai/stable-diffusion-v3-medium"
        elif model == "fal-flux-realism":
            fal_model = "fal-ai/flux-realism"
        elif model == "fal-ai/flux-lora":
            fal_model = "fal-ai/flux-lora"
        else:
            fal_model = "fal-ai/flux"  # Default to flux if not recognized
        image_data = generate_image_fal(prompt, fal_model)
    else:
        # For any non-FAL model, default to FAL's flux
        image_data = generate_image_fal(prompt, "fal-ai/flux")
    
    if image_data is None:
        return None
    
    # Convert base64 string to PIL Image
    image_data = image_data.split(",")[1]  # Remove the "data:image/png;base64," part
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    
    return image