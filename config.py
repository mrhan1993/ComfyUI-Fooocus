listen = '127.0.0.1'
host = listen
port = 8888
base_url = '127.0.0.1'
log_level = 'info'

always_gpu = True
share = False
preset = None
language = 'default'
disable_offload_from_vram = False
theme = None
disable_image_log = True
disable_analytics = False
disable_preset_download = False
disable_metadata = False
always_download_new_model = False
disable_cuda_malloc = True
in_browser = False

# hf_mirror = 'https://hf-mirror.com'
hf_mirror = None
rebuild_hash_cache = False
disable_header_check = None
web_upload_size = 100
external_working_path = None
output_path = None
temp_path = None
cache_path = None
in_browser = False
disable_in_browser = True
gpu_device_id = None
disable_attention_upcast = False
vae_in_cpu = False
directml = None  # float
disable_ipex_hijack = False
disable_xformers = False
always_offload_from_vram = False
pytorch_deterministic = False
disable_server_log = False
debug_mode = False
is_windows_embedded_python = False
disable_server_info = False
multi_user = False
enable_auto_describe_image = False

# none auto fast taesd
preview_option = 'none'

# async_cuda_allocation disable_async_cuda_allocation
cm_choice = ''

# all_in_fp32, all_in_fp16
fp_choice = ''

# unet_in_bf16 unet_in_fp16 unet_in_fp8_e4m3fn unet_in_fp8_e5m2
unet_choice = ''

# vae_in_fp16 vae_in_fp32 vae_in_bf16
vae_choice = ''

# clip_in_fp8_e4m3fn clip_in_fp8_e5m2 clip_in_fp16 clip_in_fp32
clip_fp_choice = ''

# attention_split attention_quad attention_pytorch
attn_choice = ''

# always_gpu always_high_vram always_normal_vram always_low_vram always_no_vram always_cpu
vram_choice = ''

defaults = {
    'async_cuda_allocation': False,
    'disable_async_cuda_allocation': False,
    'all_in_fp32': False,
    'all_in_fp16': False,
    'unet_in_bf16': False,
    'unet_in_fp16': False,
    'unet_in_fp8_e4m3fn': False,
    'unet_in_fp8_e5m2': False,
    'vae_in_fp16': False,
    'vae_in_fp32': False,
    'vae_in_bf16': False,
    'clip_in_fp8_e4m3fn': False,
    'clip_in_fp8_e5m2': False,
    'clip_in_fp16': False,
    'clip_in_fp32': False,
    'attention_split': False,
    'attention_quad': False,
    'attention_pytorch': False,
    'always_gpu': None,
    'always_high_vram': False,
    'always_normal_vram': False,
    'always_low_vram': False,
    'always_no_vram': False,
    'always_cpu': False,
    'cm_choice': None,
    'fp_choice': None,
    'unet_choice': None,
    'vae_choice': None,
    'clip_fp_choice': None,
    'attn_choice': None,
    'vram_choice': None
}
