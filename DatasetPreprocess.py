import os
from PIL import Image
from tqdm import tqdm_notebook

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-DatasetDir", "--DatasetDir", help="video dataset directory")
parser.add_argument("-DestDir", "--DestDir", help="destination directory")
parser.add_argument("-num_frames", "--num_frames", help="nuber of frames")
parser.add_argument("-fps", "--fps", help="nuber of frames per second")
parser.add_argument("-width", "--width", help="")
parser.add_argument("-height", "--height", help="")
args = parser.parse_args()


class dataset_converter(object):
    """Convert a video folder dataset to frames dataset"""

    def __init__(self):
        pass

    def __call__(self, raw_dataset_directory,
                 destination_dataset_directory,
                 num_frames,
                 fps,
                 width,
                 height,

                 video_formats=['.mp4', '.mpg', '.3gp', '.webm', '.avi']):
        """
        Args:
            raw_dataset_directory (str): source directory which contains some folders of classes
            destination_dataset_directory(str):destination directory for standard dataset
        Returns:
            None
        """
        if os.path.isdir(destination_dataset_directory) and len(os.listdir(destination_dataset_directory)) > 0:
            raise RuntimeError('It seems there is a dataset in the destination folder! Delete it and try again!')
            return

        _, class_to_idx = self._find_classes(raw_dataset_directory)
        videos = []
        raw_dataset_directory = os.path.expanduser(raw_dataset_directory)
        #   make dataset main folder:
        if not os.path.exists(destination_dataset_directory):
            os.mkdir(destination_dataset_directory)
        print('Classes:')
        for target in sorted(os.listdir(raw_dataset_directory)):
            #   make folder for each class:
            if not os.path.exists(os.path.join(destination_dataset_directory, target)):
                os.mkdir(os.path.join(destination_dataset_directory, target))

            d = os.path.join(raw_dataset_directory, target)
        #         print(d)
            if not os.path.isdir(d):
                continue

            for root, _, fnames in sorted(os.walk(d)):
                for fname in tqdm_notebook(sorted(fnames), desc=target, unit='file'):
                    if self._has_file_allowed_extension(fname, video_formats):
                        video_path = os.path.abspath(os.path.join(root, fname))
        #               remove format from filename:
                        for fmt in video_formats:
                            fname = fname.replace(fmt, '')
        #               remove any space from filename:
                        fname = fname.replace(' ', '')
        #               make a folder of frames out of a video:
                        out_path = os.path.abspath(os.path.join(destination_dataset_directory, target, fname))
                        if not os.path.exists(out_path):
                            os.mkdir(out_path)
                        # print('Source Video:',video_path,'>>> Destination Folder:',out_path)
                        self._exctract_frames(video_path, out_path, target, num_frames)
        print('Conversion finished!')
        return

    def _exctract_frames(self, video_path, dest_path, class_name, num_frames=args.num_frames, fps=args.fps, width=args.width, height=args.height, img_format='jpeg'):
        # os.rename(video_path,video_path.replace(' ',''))
        video_path = video_path.replace('\\', '/')
        dest_path = dest_path.replace('\\', '/')
        os.system(f'ffmpeg -i {video_path} -s {width}X{height} -vframes {num_frames} -vf fps={fps} -f image2 {dest_path}/_frame-%02d.{img_format}')

    def _has_file_allowed_extension(self, filename, extensions):
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in extensions)

    def _find_classes(self, dir):
        classes = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
        classes.sort()
        class_to_idx = {classes[i]: i for i in range(len(classes))}
        return classes, class_to_idx


if __name__ == "__main__":

    convert_dataset = dataset_converter()
    convert_dataset(raw_dataset_directory=args.DatasetDir, destination_dataset_directory=args.DestDir, num_frames=args.num_frames, fps=args.fps, width=args.width, height=args.height)
