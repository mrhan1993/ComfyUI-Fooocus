from ldm_patched.modules.args_parser import args

# (Disable by default because of issues like https://github.com/lllyasviel/Fooocus/issues/724)
args.always_offload_from_vram = True
