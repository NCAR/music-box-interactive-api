import os
import subprocess


def setup_run():
    if interface_solo:
        return JsonResponse({'model_connected': False})
    
    copy(config_path, config_dest)
    if os.path.isfile(out_path):
        copy(out_path, copy_path)
        os.remove(out_path)
    if os.path.isfile(error_path):
        os.remove(error_path)
    process = subprocess.Popen(
        [r'./music_box', r'/music-box-interactive/interactive/dashboard/static/config/my_config.json'], cwd=mb_dir)
