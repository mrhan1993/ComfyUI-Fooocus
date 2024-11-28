"""
Calls the worker with the given params.
"""
import asyncio
import os
import uuid

import numpy as np
import torch

from apis.models.base import CurrentTask, GenerateMaskRequest
from apis.models.requests import CommonRequest
from apis.utils.api_utils import params_to_params
from apis.utils.img_utils import (
    narray_to_base64img, read_input_image
)
from apis.utils.pre_process import pre_worker
from extras.inpaint_mask import generate_mask_from_image, SAMOptions
from modules.async_worker import AsyncTask, async_tasks

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(ROOT_DIR, '..', 'input')

async def process_params(request: CommonRequest):
    """
    Processes the params for the worker.
    :param request: The params to be processed.
    :return: The processed params.
    """
    if request.webhook_url is None or request.webhook_url == "":
        request.webhook_url = os.environ.get("WEBHOOK_URL")
    request = await pre_worker(request)
    params = params_to_params(request)
    task_id = uuid.uuid4().hex
    task = AsyncTask(args=params, task_id=task_id)
    async_tasks.append(task)

    return task, task_id


async def binary_output(request: CommonRequest):
    """
    Calls the worker with the given params.
    :param request: The request object containing the params.
    """
    request.image_number = 1

    task, task_id = await process_params(request)

    started = False
    finished = False
    while not finished:
        await asyncio.sleep(0.2)
        if len(task.yields) > 0:
            if not started:
                started = True
                CurrentTask.task = task
            flag, product = task.yields.pop(0)
            if flag == 'preview':
                if len(task.yields) > 0:
                    if task.yields[0][0] == 'preview':
                        continue
                percentage, _, image = product
            if flag == 'finish':
                finished = True
                CurrentTask.task = None
    try:
        image = task.results[0]
        image_array = image.astype(np.float32) / 255.0
        tensor_image = torch.from_numpy(image_array)[None,]
    except Exception:
        black_image_size = (512, 512, 3)  # 高度、宽度和通道数
        black_image_array = np.zeros(black_image_size, dtype=np.float32)
        tensor_image = torch.from_numpy(black_image_array)[None,]
    return tensor_image


# This function copy from webui.py
async def generate_mask(request: GenerateMaskRequest):
    """
    Calls the worker with the given params.
    :param request: The request object containing the params.
    :return: The result of the task.
    """
    extras = {}
    sam_options = None
    image = await read_input_image(request.image)
    if request.mask_model == 'u2net_cloth_seg':
        extras['cloth_category'] = request.cloth_category
    elif request.mask_model == 'sam':
        sam_options = SAMOptions(
            dino_prompt=request.dino_prompt_text,
            dino_box_threshold=request.box_threshold,
            dino_text_threshold=request.text_threshold,
            dino_erode_or_dilate=request.dino_erode_or_dilate,
            dino_debug=request.dino_debug,
            max_detections=request.sam_max_detections,
            model_type=request.sam_model
        )

    mask, _, _, _ = generate_mask_from_image(image, request.mask_model, extras, sam_options)
    return narray_to_base64img(mask)


async def current_task():
    """
    Returns the current task.
    """
    if CurrentTask.ct is None:
        return []
    return [CurrentTask.ct.model_dump()]
