import os
import logging
import requests
import base64
from datetime import datetime
from agents.basic_agent import BasicAgent
from utils.azure_file_storage import AzureFileStorageManager


class ImageGenerationAgent(BasicAgent):
    def __init__(self):
        self.name = "ImageGeneration"
        self.metadata = {
            "name": self.name,
            "description": "Generates images using Azure OpenAI DALL-E API and saves them to Azure File Storage. Can create new images from text prompts or edit existing images.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "The operation to perform: 'generate' for new images or 'edit' for editing existing images",
                        "enum": ["generate", "edit"]
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate or edit instructions"
                    },
                    "size": {
                        "type": "string",
                        "description": "Size of the generated image. Options: '1024x1024', '1792x1024', '1024x1792'",
                        "enum": ["1024x1024", "1792x1024", "1024x1792"]
                    },
                    "quality": {
                        "type": "string",
                        "description": "Quality of the generated image. Options: 'standard' (medium quality), 'hd' (high quality)",
                        "enum": ["standard", "hd"]
                    },
                    "style": {
                        "type": "string",
                        "description": "Style of the generated image. Note: This parameter may not be supported by all API versions.",
                        "enum": ["vivid", "natural"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format of the image. Options: 'png', 'jpeg'",
                        "enum": ["png", "jpeg"]
                    },
                    "output_compression": {
                        "type": "integer",
                        "description": "Compression level for the output image (1-100, where 100 is highest quality)",
                        "minimum": 1,
                        "maximum": 100
                    },
                    "image_file": {
                        "type": "string",
                        "description": "For edit operations: filename of the image to edit (must exist in 'images' directory)"
                    },
                    "mask_file": {
                        "type": "string",
                        "description": "For edit operations: filename of the mask image (optional, must exist in 'images' directory)"
                    },
                    "user_guid": {
                        "type": "string",
                        "description": "Optional user GUID for user-specific storage"
                    },
                    "generate_download_link": {
                        "type": "boolean",
                        "description": "Whether to generate a temporary download link after creating the image",
                        "default": False
                    },
                    "download_link_expiry": {
                        "type": "integer",
                        "description": "Number of minutes the download link should remain valid",
                        "default": 30
                    },
                    "technical_path": {
                        "type": "string",
                        "description": "The technical path to an existing file for generating download links"
                    }
                },
                "required": ["operation", "prompt"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
        self.storage_manager = AzureFileStorageManager()

        # Initialize API configuration
        self._initialize_api_config()

    def _initialize_api_config(self):
        """Initialize API configuration from environment variables."""
        self.api_endpoint = os.environ.get(
            'AZURE_IMAGE_API_ENDPOINT', 'https://.cognitiveservices.azure.com')
        self.api_key = os.environ.get('AZURE_IMAGE_API_KEY', 'YOUR KEY')
        self.deployment_name = os.environ.get(
            'AZURE_IMAGE_DEPLOYMENT', 'gpt-image-1')
        self.api_version = os.environ.get(
            'AZURE_IMAGE_API_VERSION', '2025-04-01-preview')

        # Ensure directories exist
        self.storage_manager.ensure_directory_exists('generated_images')
        self.storage_manager.ensure_directory_exists('images')

    def generate_download_link(self, file_path=None, expiry_minutes=30, **kwargs):
        """
        Generates a temporary download link for a previously created image file.

        Args:
            file_path (str): Path to the file in Azure storage
            expiry_minutes (int): Number of minutes the link should remain valid
            **kwargs: Additional parameters

        Returns:
            dict: Result with download URL if successful
        """
        try:
            # If file_path is not provided directly, try to get it from kwargs
            if not file_path:
                file_path = kwargs.get('technical_path')

            if not file_path:
                return {"status": "error", "message": "No file path provided for download link generation"}

            # Parse the file path to get directory and filename
            path_parts = file_path.split('/')
            filename = path_parts[-1]
            directory = '/'.join(path_parts[:-1])

            # Generate SAS token with expiration time
            from datetime import datetime, timedelta
            expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)

            # Get the download URL with SAS token
            download_url = self.storage_manager.generate_download_url(
                directory,
                filename,
                expiry_time
            )

            if download_url:
                return {
                    "status": "success",
                    "message": f"Download link generated successfully. Valid for {expiry_minutes} minutes.",
                    "download_url": download_url,
                    "expiry_time": expiry_time.isoformat(),
                    "filename": filename
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to generate download link"
                }

        except Exception as e:
            logging.error(f"Error generating download link: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating download link: {str(e)}"
            }

    def _validate_prompt(self, prompt):
        """Validate the generation prompt."""
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Empty prompt provided")

        max_length = 4000
        if len(prompt) > max_length:
            raise ValueError(
                f"Prompt exceeds maximum length of {max_length} characters")

    def _make_api_request(self, endpoint_path, data=None, files=None):
        """Make API request to Azure OpenAI service."""
        url = f"{self.api_endpoint.rstrip('/')}/openai/deployments/{self.deployment_name}/{endpoint_path}?api-version={self.api_version}"

        # Use Api-Key header (note the capital 'A' and 'K') for Azure Cognitive Services
        headers = {
            "Api-Key": self.api_key
        }

        if files:
            # For multipart/form-data requests (image editing)
            response = requests.post(
                url, headers=headers, data=data, files=files, timeout=60)
        else:
            # For JSON requests (image generation)
            headers["Content-Type"] = "application/json"
            response = requests.post(
                url, headers=headers, json=data, timeout=60)

        response.raise_for_status()
        return response.json()

    def _save_image_from_base64(self, base64_data, filename, user_guid=None):
        """Save base64 encoded image to Azure File Storage with organized structure."""
        try:
            image_bytes = base64.b64decode(base64_data)

            # Use organized storage structure similar to PowerPointAgent
            storage_root = "generated_images"

            if user_guid:
                # User-specific storage
                self.storage_manager.set_memory_context(user_guid)
                storage_dir = f"{storage_root}/users/{user_guid}"
            else:
                # Shared storage
                storage_dir = f"{storage_root}/shared"

            # Add date-based subdirectory for better organization
            date_subdir = datetime.now().strftime('%Y-%m')
            storage_dir = f"{storage_dir}/{date_subdir}"

            # Ensure directory exists
            self.storage_manager.ensure_directory_exists(storage_dir)

            success = self.storage_manager.write_file(
                storage_dir, filename, image_bytes)

            if success:
                return {
                    "success": True,
                    "technical_path": f"{storage_dir}/{filename}",
                    "display_path": f"{'Your' if user_guid else 'Shared'} Generated Images > {date_subdir}",
                    "filename": filename
                }
            else:
                return {"success": False}

        except Exception as e:
            logging.error(f"Error saving image: {str(e)}")
            return {"success": False}

    def _load_image_file(self, filename):
        """Load an image file from Azure File Storage for editing."""
        try:
            file_content = self.storage_manager.read_file('images', filename)
            if file_content is None:
                raise FileNotFoundError(
                    f"Image file '{filename}' not found in 'images' directory")
            return file_content
        except Exception as e:
            logging.error(f"Error loading image file: {str(e)}")
            raise

    def generate_image(self, prompt, size="1024x1024", quality="standard", style="vivid",
                       output_format="png", output_compression=100, user_guid=None):
        """Generate a new image from a text prompt."""
        self._validate_prompt(prompt)

        # Map quality parameter to match API expectations
        api_quality = "medium"  # Default
        if quality == "standard":
            api_quality = "medium"
        elif quality == "hd":
            api_quality = "high"

        data = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": api_quality,  # Use mapped quality
            "output_format": output_format
            # Note: style and output_compression are not in the working API example
        }

        logging.info(f"Generating image with prompt: {prompt}")
        result = self._make_api_request("images/generations", data)

        if not result or 'data' not in result or not result['data']:
            raise ValueError(f"No data in API response: {result}")

        if 'b64_json' not in result['data'][0]:
            raise ValueError(f"No base64 image data in API response: {result}")

        # Save the generated image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'generated_{timestamp}.{output_format}'

        base64_data = result['data'][0]['b64_json']
        save_result = self._save_image_from_base64(
            base64_data, filename, user_guid)

        if not save_result["success"]:
            raise RuntimeError(
                "Failed to save generated image to Azure File Storage")

        return save_result

    def edit_image(self, image_file, prompt, mask_file=None, size="1024x1024",
                   output_format="png", output_compression=100, user_guid=None):
        """Edit an existing image using a text prompt."""
        self._validate_prompt(prompt)

        # Load the image file
        image_data = self._load_image_file(image_file)

        # Prepare files for multipart upload
        files = {
            'image': (image_file, image_data, 'image/png')
        }

        # Load mask file if provided
        if mask_file:
            mask_data = self._load_image_file(mask_file)
            files['mask'] = (mask_file, mask_data, 'image/png')

        # Prepare form data - match the working API example format
        data = {
            'prompt': prompt,
            'n': '1',
            'size': size,
            'quality': 'medium'  # Use medium as default to match working example
        }

        logging.info(f"Editing image '{image_file}' with prompt: {prompt}")
        result = self._make_api_request("images/edits", data, files)

        if not result or 'data' not in result or not result['data']:
            raise ValueError(f"No data in API response: {result}")

        if 'b64_json' not in result['data'][0]:
            raise ValueError(f"No base64 image data in API response: {result}")

        # Save the edited image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'edited_{timestamp}.{output_format}'

        base64_data = result['data'][0]['b64_json']
        save_result = self._save_image_from_base64(
            base64_data, filename, user_guid)

        if not save_result["success"]:
            raise RuntimeError(
                "Failed to save edited image to Azure File Storage")

        return save_result

    def perform(self, **kwargs):
        """
        Perform image generation or editing operation.

        Returns:
            str: Status message with details about the operation
        """
        try:
            # Check if we're only generating a download link for an existing file
            if kwargs.get('technical_path') and not kwargs.get('prompt'):
                return self.generate_download_link(**kwargs)

            operation = kwargs.get('operation', 'generate')
            prompt = kwargs.get('prompt')
            user_guid = kwargs.get('user_guid')
            generate_download_link = kwargs.get(
                'generate_download_link', False)
            download_link_expiry = kwargs.get('download_link_expiry', 30)

            if not prompt:
                return "Error: No prompt provided for image operation."

            # Common parameters
            size = kwargs.get('size', '1024x1024')
            output_format = kwargs.get('output_format', 'png')
            output_compression = kwargs.get('output_compression', 100)

            result_data = None

            if operation == 'generate':
                quality = kwargs.get('quality', 'standard')
                style = kwargs.get('style', 'vivid')

                result_data = self.generate_image(
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style=style,
                    output_format=output_format,
                    output_compression=output_compression,
                    user_guid=user_guid
                )

                success_message = f"Successfully generated image: {result_data['filename']}\nPrompt: {prompt}\nSize: {size}\nQuality: {quality}\nStyle: {style}\nLocation: {result_data['display_path']}"

            elif operation == 'edit':
                image_file = kwargs.get('image_file')
                mask_file = kwargs.get('mask_file')

                if not image_file:
                    return "Error: No image_file specified for edit operation."

                result_data = self.edit_image(
                    image_file=image_file,
                    prompt=prompt,
                    mask_file=mask_file,
                    size=size,
                    output_format=output_format,
                    output_compression=output_compression,
                    user_guid=user_guid
                )

                mask_info = f"\nMask file: {mask_file}" if mask_file else "\nNo mask file used"
                success_message = f"Successfully edited image: {result_data['filename']}\nOriginal: {image_file}{mask_info}\nEdit prompt: {prompt}\nSize: {size}\nLocation: {result_data['display_path']}"

            else:
                return f"Error: Unsupported operation '{operation}'. Use 'generate' or 'edit'."

            # Generate download link if requested
            if generate_download_link and result_data and result_data.get('technical_path'):
                download_result = self.generate_download_link(
                    file_path=result_data['technical_path'],
                    expiry_minutes=download_link_expiry
                )

                # Add download link information to the success message
                if download_result and download_result.get('status') == 'success':
                    success_message += f"\n\nDownload link: {download_result.get('download_url')}"
                    success_message += f"\nLink expires in {download_link_expiry} minutes"

            return success_message

        except ValueError as e:
            logging.error(
                f"Validation error in ImageGenerationAgent: {str(e)}")
            return f"Validation error: {str(e)}"
        except FileNotFoundError as e:
            logging.error(f"File not found in ImageGenerationAgent: {str(e)}")
            return f"File error: {str(e)}"
        except requests.exceptions.RequestException as e:
            logging.error(
                f"API request error in ImageGenerationAgent: {str(e)}")
            return f"API error: {str(e)}"
        except Exception as e:
            logging.error(
                f"Unexpected error in ImageGenerationAgent: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"
