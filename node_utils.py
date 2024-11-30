"""Convert ComfyUI params to Fooocus params"""
from typing import List

from apis.models.requests import (
    CommonRequest,
    ImagePrompt,
    EnhanceCtrlNets,
    Lora
)


def str_bool(s: str) -> bool:
    """
    Convert enable or disable to True or False.
    Args:
        s: str of enable or disable
    Returns: bool of True or False
    """
    return s.lower() in ("enable", "true")

def get_loras(loras: list) -> List[Lora]:
    """Convert ComfyUI loras to Fooocus loras"""
    return [Lora(
        enabled=str_bool(lora[0]),
        model_name=lora[1],
        weight=lora[2]
    ) for lora in loras]

def get_outpaint_selections(outpaint_params: dict) -> List[str]:
    """Convert ComfyUI outpaint params to Fooocus outpaint selections"""
    try:
        left = str_bool(outpaint_params.get("outpaint_left", "disable"))
        right = str_bool(outpaint_params.get("outpaint_right", "disable"))
        top = str_bool(outpaint_params.get("outpaint_top", "disable"))
        bottom = str_bool(outpaint_params.get("outpaint_bottom", "disable"))

        selection = [
            "Left" if left else None,
            "Right" if right else None,
            "Top" if top else None,
            "Bottom" if bottom else None
        ]
        return [select for select in selection if select is not None]
    except Exception:
        return []

def get_image_prompts(image_prompts: dict) -> List[ImagePrompt]:
    """Convert ComfyUI image prompts to Fooocus image prompts"""
    i_prompts = []
    for i in range(1, 5):
        i_prompts.append(ImagePrompt(
            cn_img=image_prompts.get(f"cn_img_{i}", "None"),
            cn_stop=image_prompts.get(f"cn_stop_{i}", 0.6),
            cn_weight=image_prompts.get(f"cn_weight_{i}", 0.6),
            cn_type=image_prompts.get(f"cn_type_{i}", "ImagePrompt")
        ))

    return i_prompts


def get_enhance_ctrls(enhance_controls: list[dict]) -> List[EnhanceCtrlNets]:
    """Convert ComfyUI enhance controls to Fooocus enhance controls"""
    ctrls = []
    for enhance in enhance_controls:
        enhance["enhance_enabled"] = str_bool(enhance.get("enhance_enabled", "disable"))
        enhance["enhance_inpaint_disable_initial_latent"] = str_bool(enhance.get("enhance_disable_initial_latent", "disable"))
        enhance["enhance_mask_invert"] = str_bool(enhance.get("enhance_mask_invert", "disable"))
        ctrls.append(EnhanceCtrlNets(**enhance))
    return ctrls


def params_to_params(params: dict) -> CommonRequest:
    """Convert ComfyUI params to Fooocus params"""
    request = CommonRequest(
        prompt=params.get("prompt", ""),
        negative_prompt=params.get("negative_prompt", ""),
        style_selections=[s.strip() for s in params.get("style_selections", "Fooocus V2, Fooocus Enhance, Fooocus Sharp").split(",")],
        performance_selection=params.get("performance_selection", "Speed"),
        aspect_ratios_selection=params.get("aspect_ratios_selection", "1152*896"),
        image_number=params.get("image_number", 1),
        output_format=params.get("settings").get("output_format", "png"),
        image_seed=params.get("seed", -1),
        read_wildcards_in_order=str_bool(params.get("settings").get("read_wildcards_in_order", "disable")),
        sharpness=params.get("sharpness", 2.0),
        guidance_scale=params.get("guidance_scale", 7.0),
        base_model_name=params.get("base_model_name", "juggernautXL_v8Rundiffusion.safetensors"),
        refiner_model_name=params.get("refiner_model_name", "None"),
        refiner_switch=params.get("refiner_switch", 0.8),
        sampler_name=params.get("sampler_name", "dpmpp_2m_sde_gpu"),
        scheduler_name=params.get("scheduler_name", "karras"),
        vae_name=params.get("vae_name", "Default (model)"),
        loras=get_loras(params.get("loras", [])),

        # todo
        # current_tab=pass

        input_image_checkbox=True,
        uov_method=params.get("upscale_vary").get("uov_method", "Disabled"),
        uov_input_image=params.get("upscale_vary").get("uov_input_image", ""),
        upscale_multiple=params.get("upscale_vary").get("upscale_multiple", 2),

        outpaint_selections=get_outpaint_selections(params.get("inpaint_outpaint", {})),
        outpaint_distance=[
            params.get("inpaint_outpaint", {}).get("outpaint_distance_left", 0),
            params.get("inpaint_outpaint", {}).get("outpaint_distance_top", 0),
            params.get("inpaint_outpaint", {}).get("outpaint_distance_right", 0),
            params.get("inpaint_outpaint", {}).get("outpaint_distance_bottom", 0)
        ],
        inpaint_input_image=params.get("inpaint_outpaint", {}).get("input_image", ""),
        inpaint_mask_image_upload=params.get("inpaint_outpaint", {}).get("input_mask", ""),
        inpaint_additional_prompt=params.get("inpaint_outpaint", {}).get("inpaint_prompt", ""),
        debugging_inpaint_preprocessor=False,
        inpaint_disable_initial_latent=str_bool(params.get("inpaint_outpaint", {}).get("inpaint_disable_initial_latent", "disable")),
        inpaint_engine=params.get("inpaint_outpaint", {}).get("inpaint_engine", "v2.6"),
        inpaint_strength=params.get("inpaint_outpaint", {}).get("inpaint_strength", 1),
        inpaint_respective_field=params.get("inpaint_outpaint", {}).get("inpaint_respective_field", 0.618),
        inpaint_erode_or_dilate=params.get("inpaint_outpaint", {}).get("inpaint_erode_or_dilate", 0),
        invert_mask_checkbox=str_bool(params.get("inpaint_outpaint", {}).get("inpaint_mask_invert", "disable")),

        disable_preview=str_bool(params.get("settings").get("disable_preview", "disable")),
        disable_intermediate_results=str_bool(params.get("settings").get("disable_intermediate_results", "disable")),
        disable_seed_increment=str_bool(params.get("settings").get("disable_seed_increment", "disable")),
        black_out_nsfw=str_bool(params.get("settings").get("black_out_nsfw", "disable")),

        adm_scaler_positive=params.get("settings").get("adm_scaler_positive", 1.5),
        adm_scaler_negative=params.get("settings").get("adm_scaler_negative", 0.8),
        adm_scaler_end=params.get("settings").get("adm_scaler_end", 0.3),
        adaptive_cfg=params.get("settings").get("adaptive_cfg", 7),
        clip_skip=params.get("settings").get("clip_skip", 2),

        overwrite_step=params.get("settings").get("overwrite_step", -1),
        overwrite_switch=params.get("settings").get("overwrite_switch", -1),
        overwrite_width=params.get("settings").get("overwrite_width", -1),
        overwrite_height=params.get("settings").get("overwrite_height", -1),
        overwrite_vary_strength=params.get("settings").get("overwrite_vary_strength", -1),
        overwrite_upscale_strength=params.get("settings").get("overwrite_upscale_strength", -1),

        mixing_image_prompt_and_inpaint=str_bool(params.get("settings").get("mixing_image_prompt_and_inpaint", "disable")),
        mixing_image_prompt_and_vary_upscale=str_bool(params.get("settings").get("mixing_image_prompt_and_vary_upscale", "disable")),

        debugging_cn_preprocessor=str_bool(params.get("settings").get("debugging_cn_preprocessor", "disable")),
        skipping_cn_preprocessor=str_bool(params.get("settings").get("skipping_cn_preprocessor", "disable")),
        canny_low_threshold=params.get("settings").get("canny_low_threshold", 64),
        canny_high_threshold=params.get("settings").get("canny_high_threshold", 128),
        refiner_swap_method=params.get("refiner_swap_method", "joint"),
        controlnet_softness=params.get("settings").get("controlnet_softness", 0.25),

        freeu_enabled=str_bool(params.get("settings").get("freeu_enabled", "disable")),
        freeu_b1=params.get("settings").get("freeu_b1", 1.01),
        freeu_b2=params.get("settings").get("freeu_b2", 1.02),
        freeu_s1=params.get("settings").get("freeu_s1", 0.99),
        freeu_s2=params.get("settings").get("freeu_s2", 0.95),

        controlnet_image=get_image_prompts(params.get("image_prompts", {})),

        save_final_enhanced_image_only=True,
        save_metadata_to_images=True,
        metadata_scheme="fooocus",

        debugging_dino = str_bool(params.get("settings").get("debugging_dino", "disable")),
        dino_erode_or_dilate=params.get("settings").get("dino_erode_or_dilate", 0),
        debugging_enhance_masks_checkbox=False,

        enhance_input_image=params.get("enhance_ctrls", {}).get("enhance_input_image", ""),
        enhance_checkbox=str_bool(params.get("enhance_ctrls", {}).get("enhance_enable", "disable")),
        enhance_uov_method=params.get("enhance_ctrls", {}).get("enhance_uov_method", "Disabled"),
        enhance_uov_processing_order=params.get("enhance_ctrls", {}).get("enhance_uov_processing_order", "Before First Enhancement"),
        enhance_uov_prompt_type=params.get("enhance_ctrls", {}).get("enhance_uov_prompt_type", "Original Prompts"),
        enhance_ctrls=get_enhance_ctrls(enhance_controls=[
            params.get("enhance_ctrls", {}).get("enhance_ctrl_1", {}),
            params.get("enhance_ctrls", {}).get("enhance_ctrl_2", {}),
            params.get("enhance_ctrls", {}).get("enhance_ctrl_3", {})
        ]),

        generate_image_grid=False,
        save_name="None",
        preset=params.get("preset", "initial"),
        stream_output=False,
        require_base64=False,
        async_process=False,
        webhook_url=""
    )

    return request
