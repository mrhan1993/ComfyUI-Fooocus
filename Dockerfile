# FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# WORKDIR /ComfyUI

# RUN apt update && apt install -y \
#     python3 \
#     python3-pip \
#     git && \
#     apt clean

# RUN cd / && git clone https://github.com/ComfyUI/ComfyUI.git ComfyUI && cd /ComfyUI && \
#     git clone https://github.com/yolain/ComfyUI-Easy-Use custom_nodes/ComfyUI-Easy-Use && \
#     git clone https://github.com/mrhan1993/ComfyUI-Fooocus custom_nodes/ComfyUI-Fooocus && \
#     git clone https://github.com/rgthree/rgthree-comfy custom_nodes/rgthree-comfy && \
#     git clone https://github.com/theUpsider/ComfyUI-Logic custom_nodes/ComfyUI-Logic && \
#     git clone https://github.com/miaoshouai/ComfyUI-Miaoshouai-Tagger custom_nodes/ComfyUI-Miaoshouai-Tagger && \
#     git clone https://github.com/chrisgoringe/cg-use-everywhere custom_nodes/cg-use-everywhere && \
#     git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack custom_nodes/ComfyUI-Impact-Pack && \
#     pip install -r requirements.txt && \
#     pip install gradio && \
#     pip install -r custom_nodes/ComfyUI-Easy-Use/requirements.txt && \
#     pip install -r custom_nodes/ComfyUI-Fooocus/requirements.txt && \
#     pip install -r custom_nodes/rgthree-comfy/requirements.txt && \
#     pip install -r custom_nodes/ComfyUI-Logic/requirements.txt && \
#     pip install -r custom_nodes/ComfyUI-Miaoshouai-Tagger/requirements.txt && \
#     pip install -r custom_nodes/cg-use-everywhere/requirements.txt && \
#     pip install -r custom_nodes/ComfyUI-Impact-Pack/requirements.txt && \
#     pip cache purge

# EXPOSE 8188

# CMD ["python3", "main.py", "--listen"]


FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

WORKDIR /ComfyUI

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    git && \
    apt clean

RUN cd / && git clone https://github.com/comfyanonymous/ComfyUI ComfyUI && cd /ComfyUI && \
    git clone https://github.com/yolain/ComfyUI-Easy-Use custom_nodes/ComfyUI-Easy-Use && \
    git clone https://github.com/mrhan1993/ComfyUI-Fooocus custom_nodes/ComfyUI-Fooocus && \
    git clone https://github.com/rgthree/rgthree-comfy custom_nodes/rgthree-comfy && \
    git clone https://github.com/theUpsider/ComfyUI-Logic custom_nodes/ComfyUI-Logic && \
    git clone https://github.com/miaoshouai/ComfyUI-Miaoshouai-Tagger custom_nodes/ComfyUI-Miaoshouai-Tagger && \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack custom_nodes/ComfyUI-Impact-Pack && \
    pip config set global.index-url https://mirror.nju.edu.cn/pypi/web/simple && \
    pip install -r requirements.txt && \
    pip install gradio && \
    pip install -r custom_nodes/ComfyUI-Easy-Use/requirements.txt && \
    pip install -r custom_nodes/ComfyUI-Fooocus/requirements.txt && \
    pip install -r custom_nodes/rgthree-comfy/requirements.txt && \
    pip install -r custom_nodes/ComfyUI-Miaoshouai-Tagger/requirements.txt && \
    pip install -r custom_nodes/ComfyUI-Impact-Pack/requirements.txt && \
    pip cache purge

EXPOSE 8188

CMD ["python3", "main.py", "--listen"]
