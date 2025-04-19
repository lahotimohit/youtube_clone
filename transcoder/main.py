from pathlib import Path
from secret_keys import SecretKeys
import os
import requests
import boto3
import subprocess

secret_keys=SecretKeys()

class VideoTranscoder:
    def __init__(self):
        self.client = boto3.client(
            "s3", 
            region_name=secret_keys.REGION_NAME,
            aws_access_key_id=secret_keys.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=secret_keys.AWS_SECRET_ACCESS_KEY)

    def _get_content_type(self, file_path:str):
        if file_path.endswith(".m3u8"):
            return "application/vnd.apple.mpegurl"
        elif file_path.endswith(".ts"):
            return "video/MP2T"
        elif file_path.endswith(".mpd"):
            return "application/dash+xml"
        elif file_path.endswith(".m4s"):
            return "video/mp4"
    
    def download_video(self, local_path):
        self.client.download_file(
            secret_keys.S3_BUCKET,
            secret_keys.S3_KEY,
            local_path
        )

    def transcode_video(self, input_path, output_dir):
        cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-filter_complex",
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=640:360:flags=fast_bilinear[360p];"
            "[v2]scale=1280:720:flags=fast_bilinear[720p];"
            "[v3]scale=1920:1080:flags=fast_bilinear[1080p]",
            # 360p video stream
            "-map",
            "[360p]",
            "-c:v:0",
            "libx264",
            "-b:v:0",
            "1000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 720p video stream
            "-map",
            "[720p]",
            "-c:v:1",
            "libx264",
            "-b:v:1",
            "4000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 1080p video stream
            "-map",
            "[1080p]",
            "-c:v:2",
            "libx264",
            "-b:v:2",
            "8000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # Audio stream
            "-map",
            "0:a",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            # DASH specific settings
            "-use_timeline",
            "1",
            "-use_template",
            "1",
            "-window_size",
            "5",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-f",
            "dash",
            f"{output_dir}/manifest.mpd",
        ]
        process=subprocess.run(cmd)

        if process.returncode != 0:
            raise Exception("Transcodig Failed...")
        
    def upload_files(self, prefix:str, local_dir):
        for root,_,files in os.walk(local_dir):
            for file in files:
                local_path=os.path.join(root, file)
                s3_key=f"{prefix}/{os.path.relpath(local_path, local_dir)}"
                self.client.upload_file(
                    local_path,
                    secret_keys.S3_PROCESSED_VIDEOS_BUCKET,
                    s3_key,
                    ExtraArgs={
                        "ACL":"public-read",
                        "ContentType":self._get_content_type(local_path)
                    })
    
    def process_video(self):
        workdir=Path("/tmp/workspace")
        workdir.mkdir(exist_ok=True)
        input_path=workdir/"input.mp4"
        output_path=workdir/"output"
        output_path.mkdir(exist_ok=True)
        try:
            self.download_video(input_path)
            self.transcode_video(str(input_path), str(output_path))
            self.upload_files(secret_keys.S3_KEY, str(output_path))
            self.update_video()
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                import shutil
                shutil.rmtree(output_path)

    def update_video(self):
        try:
            response = requests.put(f"{secret_keys.BACKEND_URL}/videos?id={secret_keys.S3_KEY}")
            return response.json()
        except Exception as e:
            print(e)

VideoTranscoder().process_video() 