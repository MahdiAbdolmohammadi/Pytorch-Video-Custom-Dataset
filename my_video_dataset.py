import torch
import torch.utils.data as data
import glob
import sys
import os
from PIL import Image
import numpy as np
import random
from torchvision import transforms
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from video_transforms import *

def find_classes(dir):
    classes = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    classes.sort()
    class_to_idx = {classes[i]: i for i in range(len(classes))}
    return classes, class_to_idx

def make_dataset(directory, class_to_idx):
    video_frames_dirs = []
    directory = os.path.expanduser(directory)
    for target in sorted(os.listdir(directory)):
        d = os.path.join(directory, target)
        if not os.path.isdir(d):
            continue

        for root,dirs,_ in sorted(os.walk(d)):
            for dirname in sorted(dirs):
                path = os.path.abspath(os.path.join(root,dirname))
                _ , class_to_idx=find_classes(directory)
                item = (path, class_to_idx[target])
                video_frames_dirs.append(item)

    return video_frames_dirs

def pil_frame_loader(path):
    frames_pathes = glob.glob(f'{path}/*.png')
    frames=[]
    for frame_path in frames_pathes:        
        with open(frame_path, 'rb') as f:
            frames.append(Image.open(f).convert('RGB'))
    return frames_pathes,frames


    
# class section:

class videofolderdataset(data.Dataset):
    """Generates a video dataset out of a folder containing several folders of video frames"""
    def __init__(self, root, loader=pil_frame_loader, transform=None):
        classes, class_to_idx = find_classes(root)
        samples=make_dataset(root, class_to_idx)
        if len(samples) == 0:
                    raise(RuntimeError("Found 0 files in subfolders of: " + root))
        self.root = root
        self.loader = loader
        self.classes = classes
        self.class_to_idx = class_to_idx
        self.samples = samples
        self.transform = transform
        
    def __getitem__(self, index):
        video_frames_path, video_class = self.samples[index]
        _,clip = self.loader(video_frames_path)
        if self.transform is not None:
            self.transform.randomize_parameters()
            clip = [self.transform(img) for img in clip]
            clip = torch.stack(clip, 0).permute(1, 0, 2, 3)
        return clip, video_class 

    def __len__(self):
        return len(self.samples)  
    
    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of videos in dataset: {}\n'.format(self.__len__())
        fmt_str += '    Root Location: {}\n'.format(self.root)
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str
    
    def plot_video_frames(self,video_index):
        # #     plot frames of a video
        vid,target=self.__getitem__(video_index)
#         print(vid.size())
        print(vid.permute(1, 0, 2, 3).size())
        vid = vid.permute(1, 0, 2, 3)
        print(len(vid))
        print('Video Class=',self.classes[target],f'({target})')
        plt.figure(figsize=(8,2*len(vid)))
        for i,frame in enumerate(vid):
#             print(frame.size())
#             print(i)
            frame = frame.permute(1,2,0)
#             frame = frame.squeeze()
            print(frame.size())
#             plt.subplot(len(vid),1,i+1)
            plt.imshow(np.array(frame))
        return
    def new_plot(self, video_index):
        vid,target=self.__getitem__(video_index)
        fig, ax = plt.subplots()
        vid = vid.permute(1,2,3,0) # Permuting to (Bx)HxWxC format
        frames = [[ax.imshow(vid[i])] for i in range(len(vid))]

        ani = animation.ArtistAnimation(fig, frames)
        ani

if __name__ == "__main__":
    train_dataset=videofolderdataset('./testdata/',transform=Compose([Resize_Crop((224,224)),
                                                                                     RandomHorizontalFlip(),
                                                                                     ToTensor(),
                                                                                     Normalize([0.45, 0.42, 0.39], [1, 1, 1])]))
    print(len(train_dataset))
    # print(train_dataset.__getitem__(1)[0].size())
    print(train_dataset.class_to_idx)