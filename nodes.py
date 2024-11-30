"""Nodes for fooocus using in ComfyUI"""
import asyncio
import uuid

import folder_paths
import os
from modules.patch import PatchSettings, patch_all, patch_settings
patch_all()
# 会重写 modules.model_sampling.ModelSamplingDiscrete._register_schedule
# 不执行 patch_all() 会导致报错

from modules.flags import scheduler_list, sampler_list
from node_utils import params_to_params
from apis.utils.call_worker import binary_output



root_dir = os.path.dirname(os.path.realpath(__file__))
preset_list = [p.split('.')[0] for p in os.listdir(f'{root_dir}/presets') if p.endswith('json')]
preset_list.append("initial")

preset_list = list(set(preset_list))

upscale_method = [
    "Disabled",
    "Vary (Subtle)",
    "Vary (Strong)",
    "Upscale (1.5x)",
    "Upscale (2x)",
    "Upscale (Fast 2x)",
    "Upscale (Custom)"
]
mask_model = [
    "u2net",
    "u2netp",
    "u2net_human_seg",
    "u2net_cloth_seg",
    "silueta",
    "isnet-general-use",
    "isnet-anime",
    "sam"
]


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
                'dino_erode_or_dilate': ("INT", {"default": 0, "min": -64, "max": 64}),
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
                'skipping_cn_preprocessor': (["enable", "disable"], {"default": "disable"})
            }
        }

    RETURN_TYPES = ("FOOOCUS_SETTINGS",)
    RETURN_NAMES = ("settings",)

    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


class LoraStacks:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        max_lora_num = 5
        inputs = {
            "required": {
                "num_loras": ("INT", {"default": 5, "min": 1, "max": max_lora_num}),
            },
            "optional": {
                "optional_lora_stack": ("LORA_STACKS",),
            },
        }

        for i in range(1, max_lora_num+1):
            inputs["optional"][f"lora_{i}_enable"] = (
                ["enable", "disable"], {"default": "disable"})
            inputs["optional"][f"lora_{i}_name"] = (
                ["None"] + folder_paths.get_filename_list("loras"), {"default": "None"})
            inputs["optional"][f"lora_{i}_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
        return inputs

    RETURN_TYPES = ("LORA_STACKS",)
    RETURN_NAMES = ("lora_stacks",)
    FUNCTION = "stack"

    CATEGORY = "Fooocus"

    def stack(self, num_loras, optional_lora_stack=None, **kwargs):

        loras = []

        if optional_lora_stack is not None:
            loras.extend([l for l in optional_lora_stack if l[0] != "None"])

        # Import Lora values
        for i in range(1, num_loras + 1):
            lora_name = kwargs.get(f"lora_{i}_name")

            if not lora_name or lora_name == "None":
                continue

            lora_enable = kwargs.get(f"lora_{i}_enable")
            lora_strength = kwargs.get(f"lora_{i}_strength")
            loras.append((lora_enable, lora_name, lora_strength))

        return (loras,)


class ImagePrompts:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        image_prompts = {
            "optional": {
                "image_prompts": ("IMAGE_PROMPTS",)
            }
        }

        for i in range(1, 5):
            image_prompts["optional"][f"cn_img_{i}"] = ("STRING", {"default": "None", "multiline": False})
            image_prompts["optional"][f"cn_stop_{i}"] = ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01})
            image_prompts["optional"][f"cn_weight_{i}"] = ("FLOAT", {"default": 0.6, "min": 0.0, "max": 2.0, "step": 0.01})
            image_prompts["optional"][f"cn_type_{i}"] = (
                ["ImagePrompt", "FaceSwap", "PyraCanny", "CPDS"], {"default": "ImagePrompt"})
        return image_prompts

    RETURN_TYPES = ("IMAGE_PROMPTS",)
    RETURN_NAMES = ("image_prompts",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


class EnhanceControl:
    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(cls):
        control = {
            "required": {
                "enhance_enabled": (["enable", "disable"], {"default": "disable"}),
                "enhance_mask_dino_prompt": ("STRING", {"default": "", "multiline": False}),
                "enhance_prompt": ("STRING", {"default": "", "multiline": False}),
                "enhance_negative_prompt": ("STRING", {"default": "", "multiline": False}),
                "enhance_mask_model": (mask_model, {"default": "sam"}),
                "enhance_mask_cloth_category": ("STRING", {"default": "full", "multiline": False}),
                "enhance_mask_sam_model": (["vit_b", "vit_h", "vit_l"], {"default": "vit_b"}),
                "enhance_mask_text_threshold": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0}),
                "enhance_mask_box_threshold": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
                "enhance_mask_sam_max_detections": ("INT", {"default": 0, "min": 0, "max": 10}),
                "enhance_inpaint_disable_initial_latent": (["enable", "disable"], {"default": "disable"}),
                "enhance_inpaint_engine": (["v2.6",], {"default": "v2.6"}),
                "enhance_inpaint_strength": ("FLOAT", {"default": 1, "min": 0.0, "max": 1.0}),
                "enhance_inpaint_respective_field": ("FLOAT", {"default": 0.618, "min": 0.0, "max": 1.0}),
                "enhance_inpaint_erode_or_dilate": ("INT", {"default": 0, "min": -64, "max": 64}),
                "enhance_mask_invert": (["enable", "disable"], {"default": "disable"})
            },
        }
        return control
    RETURN_TYPES = ("ENHANCE_CONTROL",)
    RETURN_NAMES = ("enhance_control",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"
    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


class EnhanceControls:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        enhance_control = {
            "required": {
                "enhance_image": ("STRING", {"default": "", "multiline": False}),
                "enhance_enable": (["enable", "disable"], {"default": "disable"}),
                "enhance_uov_method": (upscale_method, {"default": "Disabled"}),
                "enhance_uov_processing_order": (["Before First Enhancement", "After Last Enhancement"], {"default": "Before First Enhancement"}),
                "enhance_uov_prompt_type": (["Last Filled Enhancement Prompts", "Original Prompts"], {"default": "Original Prompts"})
            },
            "optional": {
                "enhance_ctrl_1": ("ENHANCE_CONTROL",),
                "enhance_ctrl_2": ("ENHANCE_CONTROL",),
                "enhance_ctrl_3": ("ENHANCE_CONTROL",)
            }
        }
        return enhance_control
    RETURN_TYPES = ("ENHANCE_CONTROLS",)
    RETURN_NAMES = ("enhance_controls",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


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
                'performance_selection': (["Quality", "Speed", "Extreme Speed", "Lightning", "Hyper-SD"], {"default": "Speed"}),
                'image_number': ("INT", {"default": 1, "min": 1, "max": 999}),
                'image_seed': ("INT", {"default": -1, "min": -1, "max": 2**63-1}),
                'sharpness': ("FLOAT", {"default": 2.0, "min": 0.0, "max": 30.0}),
                'guidance_scale': ("FLOAT", {"default": 7.0, "min": 1.0, "max": 30.0}),
                'base_model_name': ("STRING", {"default": "juggernautXL_v8Rundiffusion.safetensors", "multiline": False}),
                'refiner_model_name': ("STRING", {"default": "None", "multiline": False}),
                'refiner_switch': ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1}),
                'refiner_swap_method': (["joint", "separate", "vae"], {"default": "joint"}),
                'preset': (preset_list, {"default": "initial"}),
                'sampler_name': (sampler_list, {"default": "dpmpp_2m_sde_gpu"}),
                'scheduler_name': (scheduler_list, {"default": "karras"}),
                'vae_name': ("STRING", {"default": "Default (model)", "multiline": False}),
                'loras': ("LORA_STACKS",),
                'inpaint_outpaint': ("INPAINT_OUTPAINT",),
                'upscale_vary': ("UPSCALE_VARY",),
                'image_prompts': ("IMAGE_PROMPTS",),
                'enhance_ctrls': ("ENHANCE_CONTROLS",),
                'settings': ("FOOOCUS_SETTINGS",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        request = params_to_params(kwargs)
        image = asyncio.run(binary_output(request))
        return (image,)


class InpaintOutpaint:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        inpaint_outpaint = {
            "required": {
                "input_image": ("STRING", {"default": "", "multiline": False}),
                "input_mask": ("STRING", {"default": "", "multiline": False}),
                "inpaint_prompt": ("STRING", {"default": "", "multiline": False}),
                "inpaint_disable_initial_latent": (["enable", "disable"], {"default": "disable"}),
                "inpaint_engine": (["v2.6",], {"default": "v2.6"}),
                "inpaint_strength": ("FLOAT", {"default": 1, "min": 0.0, "max": 1.0}),
                "inpaint_respective_field": ("FLOAT", {"default": 0.618, "min": 0.0, "max": 1.0}),
                "inpaint_erode_or_dilate": ("INT", {"default": 0, "min": -64, "max": 64}),
                "inpaint_mask_invert": (["enable", "disable"], {"default": "disable"}),
                "outpaint_left": (["enable", "disable"], {"default": "disable"}),
                "outpaint_left_distance": ("INT", {"default": 0, "min": 0}),
                "outpaint_right": (["enable", "disable"], {"default": "disable"}),
                "outpaint_right_distance": ("INT", {"default": 0, "min": 0}),
                "outpaint_top": (["enable", "disable"], {"default": "disable"}),
                "outpaint_top_distance": ("INT", {"default": 0, "min": 0}),
                "outpaint_bottom": (["enable", "disable"], {"default": "disable"}),
                "outpaint_bottom_distance": ("INT", {"default": 0, "min": 0}),
            }
        }
        return inpaint_outpaint

    RETURN_TYPES = ("INPAINT_OUTPAINT",)
    RETURN_NAMES = ("inpaint_outpaint",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


class UpscaleVary:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "uov_input_image": ("STRING", {"default": "", "multiline": False}),
                "uov_method": (upscale_method, {"default": "Disabled"}),
                "upscale_multiple": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0})
            }
        }

    RETURN_TYPES = ("UPSCALE_VARY",)
    RETURN_NAMES = ("upscale_vary",)
    FUNCTION = "process"
    CATEGORY = "Fooocus"

    @staticmethod
    def process(**kwargs):
        return (kwargs,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return uuid.uuid4().hex


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "FooocusSettings": FooocusSettings,
    "FooocusSampler": FooocusSampler,
    "LoraStacks": LoraStacks,
    "ImagePrompts": ImagePrompts,
    "EnhanceControl": EnhanceControl,
    "EnhanceControls": EnhanceControls,
    "InpaintOutpaint": InpaintOutpaint,
    "UpscaleVary": UpscaleVary,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "FooocusSettings": "Fooocus Settings",
    "FooocusSampler": "Fooocus Sampler",
    "LoraStacks": "LoraStacks",
    "ImagePrompts": "Image Prompts",
    "EnhanceControl": "Enhance Control",
    "EnhanceControls": "Enhance Controls",
    "InpaintOutpaint": "Inpaint Outpaint",
    "UpscaleVary": "Upscale Vary",
}
