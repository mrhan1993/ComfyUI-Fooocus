import enum
import config as args

class LatentPreviewMethod(enum.Enum):
    NoPreviews = "none"
    Auto = "auto"
    Latent2RGB = "fast"
    TAESD = "taesd"

# 设置默认值
for key, value in args.defaults.items():
    setattr(args, key, value)

# 处理配置项
choices = [args.cm_choice, args.fp_choice, args.unet_choice, args.vae_choice, args.clip_fp_choice, args.attn_choice, args.vram_choice]
for choice in choices:
    if not choice:
        continue

    try:
        setattr(args, choice, True)
    except AttributeError as e:
        print(f"Error setting attribute {choice}: {e}")
