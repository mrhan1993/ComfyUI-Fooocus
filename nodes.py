"""Nodes for fooocus using in ComfyUI"""


class FooocusSettings:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                'adaptive_cfg': ("FLOAT", {"default": 7.0, "min": 1.0, "max": 30.0, 'step': 0.1}),
                'adm_scaler_positive': ("FLOAT", {"default": 1.5, "min": 0.0, "max": 3.0, 'step': 0.1}),
                'adm_scaler_negative': ("FLOAT", {"default": 0.8, "min": 0.0, "max": 3.0, 'step': 0.1}),
                'adm_scaler_end': ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, 'step': 0.1}),
                'black_out_nsfw': (["enable", "disable"], {"default": "disable"}),
                'canny_low_threshold': ("INT", {"default": 64, "min": 1, "max": 255}),
                'canny_high_threshold': ("INT", {"default": 128, "min": 1, "max": 255}),
                'controlnet_softness': ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, 'step': 0.01}),
                'clip_skip': ("INT", {"default": 2, "min": 1, "max": 12}),
                'debugging_cn_preprocessor': (["enable", "disable"], {"default": "disable"}),
                'debugging_dino': (["enable", "disable"], {"default": "disable"}),
                'debugging_enhance_masks_checkbox': (["enable", "disable"], {"default": "disable"}),
                'debugging_inpaint_preprocessor': (["enable", "disable"], {"default": "disable"}),
                'disable_preview': (["enable", "disable"], {"default": "disable"}),
                'disable_intermediate_results': (["enable", "disable"], {"default": "disable"}),
                'disable_seed_increment': (["enable", "disable"], {"default": "disable"}),
                'freeu_enabled': (["enable", "disable"], {"default": "disable"}),
                'freeu_b1': ("FLOAT", {"default": 1.01}),
                'freeu_b2': ("FLOAT", {"default": 1.02}),
                'freeu_s1': ("FLOAT", {"default": 0.99}),
                'freeu_s2': ("FLOAT", {"default": 0.95}),
                'generate_image_grid': (["enable", "disable"], {"default": "disable"}),
                'mixing_image_prompt_and_vary_upscale': (["enable", "disable"], {"default": "disable"}),
                'mixing_image_prompt_and_inpaint': (["enable", "disable"], {"default": "disable"}),
                'output_format': (["png", "jpeg", "webp"], {"default": "png", "multiline": False}),
                'overwrite_step': ("INT", {"default": -1, "min": -1, "max": 999999}),
                'overwrite_switch': ("INT", {"default": -1, "min": -1, "max": 999999}),
                'overwrite_width': ("INT", {"default": -1, "min": -1, "max": 2048}),
                'overwrite_height': ("INT", {"default": -1, "min": -1, "max": 2048}),
                'overwrite_vary_strength': ("FLOAT",  {"default": -1, "min": -1, "max": 1.0}),
                'overwrite_upscale_strength': ("FLOAT",  {"default": -1, "min": -1, "max": 1.0}),
                'read_wildcards_in_order': (["enable", "disable"], {"default": "disable"}),
                'skipping_cn_preprocessor': (["enable", "disable"], {"default": "disable"}),
                'webhook_url': ("STRING", {"default": "None", "multiline": False}),
            }
        }


    IS_CHANGED = True
    RETURN_TYPES = ("FOOOCUS_SETTINGS",)
    RETURN_NAMES = ("settings",)

    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)


class FooocusSampler:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                'prompt': ("STRING", {"default": "A beautiful girl", "multiline": True}),
                'negative_prompt': ("STRING", {"default": "", "multiline": True}),
                'style_selections': ("STRING", {"default": "Fooocus V2, Fooocus Enhance, Fooocus Sharp", "multiline": False}),
                'aspect_ratios_selection': ("STRING", {"default": "1152*896", "multiline": False}),
                'image_number': ("INT", {"default": 1, "min": 1, "max": 32}),
                'image_seed': ("INT", {"default": -1, "min": -1, "max": 0xFFFFFFFF}),
                'sharpness': ("FLOAT", {"default": 2.0, "min": 0.0, "max": 30.0}),
                'guidance_scale': ("FLOAT", {"default": 7.0, "min": 1.0, "max": 30.0}),
                'base_model_name': ("STRING", {"default": "juggernautXL_v8Rundiffusion.safetensors", "multiline": False}),
                'refiner_model_name': ("STRING", {"default": "None", "multiline": False}),
                'refiner_switch': ("INT", {"default": 0.8, "min": 0, "max": 1}),
                'loras': ("LORAS",),
                'image_prompts': ("IMAGE_PROMPTS",),
                'enhance_ctrls': ("ENHANCE_CTRLS",),
                'settings': ("FOOOCUS_SETTINGS",),
            }
        }

    IS_CHANGED = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sampler",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(settings):
        print(settings)
        return ("fooocus_sampler",)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "FooocusSettings": FooocusSettings,
    "FooocusSampler": FooocusSampler
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "FooocusSettings": "Fooocus Settings",
    "FooocusSampler": "Fooocus Sampler"
}

