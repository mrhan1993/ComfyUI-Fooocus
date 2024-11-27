"""
Do something after generate
"""
import datetime
import os

from apis.models.base import CurrentTask
from apis.utils.file_utils import change_filename, url_path
from apis.utils import file_utils
from modules.async_worker import AsyncTask
from modules.config import path_outputs, temp_path


ROOT_DIR = file_utils.SCRIPT_PATH
INPUT_PATH = os.path.join(ROOT_DIR, 'input')


async def post_worker(task: AsyncTask, target_name: str, ext: str):
    """
    Posts the task to the worker.
    :param task: The task to post.
    :param target_name:
    :param ext:
    :return: The task.
    """
    final_enhanced = []
    task_status = "finished"
    if task.save_final_enhanced_image_only:
        for item in task.results:
            if temp_path not in item:
                final_enhanced.append(item)
        task.results = final_enhanced

    if task.last_stop in ['stop', 'skip']:
        task_status = task.last_stop
    try:
        results = change_filename(task.results, target_name, ext)
        task.results = results
    except Exception as e:
        print(e)
    CurrentTask.ct = None
