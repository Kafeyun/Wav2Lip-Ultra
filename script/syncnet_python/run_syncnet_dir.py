#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, pdb, argparse, subprocess, pickle, os, gzip, glob

from SyncNetInstance import *

# ==================== PARSE ARGUMENT ====================

parser = argparse.ArgumentParser(description="SyncNet");
parser.add_argument('--initial_model', type=str, default="data/syncnet_v2.model", help='');
parser.add_argument('--batch_size', type=int, default='20', help='');
parser.add_argument('--vshift', type=int, default='15', help='');
parser.add_argument('--output_root', type=str, default='syncnet_output', help='Output direcotry');
parser.add_argument('--video_root', type=str, default='output/pycrop', help='Input video file');
parser.add_argument('--reference', type=str, default='', help='Video reference');
parser.add_argument('--log_file', help='dataset', default='syncnet_output/complete.txt', type=str);
parser.add_argument('--videofile', type=str, default='', help='');
opt = parser.parse_args();

setattr(opt, 'avi_dir', os.path.join(opt.output_root, 'pyavi'))
setattr(opt, 'tmp_dir', os.path.join(opt.output_root, 'pytmp'))
setattr(opt, 'work_dir', os.path.join(opt.output_root, 'pywork'))
setattr(opt, 'crop_dir', os.path.join(opt.output_root, 'pycrop'))

# ==================== LOAD MODEL AND FILE LIST ====================

s = SyncNetInstance();

s.loadParameters(opt.initial_model);
print("Model %s loaded." % opt.initial_model);

video_root = opt.video_root
output_root = opt.output_root
identities = os.listdir(video_root)
identities = [x for x in identities]
identities.sort()
log_file = opt.log_file
with open(log_file, 'r') as f:
    identityID = f.read().split("\n")
for identity in identities:
    fullPathVideo = os.path.join(video_root, identity)
    if identity in identityID:
        print(f' videosSet {fullPathVideo} was OK')
        continue
    print(f'Processing videosSet {identity}')
    videos = os.listdir(os.path.join(video_root, identity))
    videos = [x if x.endswith('.avi') else os.remove(os.path.join(video_root, x)) for x in videos]
    videosList = []
    for video in videos:
        (shotname, extension) = os.path.splitext(video)
        if shotname.isalnum():
            videosList.append(shotname)
    for idx, fname in enumerate(videosList):
        normalPath = os.path.join(video_root, identity, fname + '.avi')
        hqPath = os.path.join(video_root, identity, fname + '_hq.avi')
        targetPath = os.path.join(output_root, identity + fname + '_hq.avi')
        offset = s.evaluate(opt, videofile=normalPath)

        if offset == 0:
            os.rename(hqPath, targetPath)
        elif abs(offset) <= 5:
            fpss = offset / 25
            cmd = f"ffmpeg -i {hqPath} -itsoffset {fpss} -i {hqPath} -map 0:v -map 1:a -b:v 8000k {targetPath}"
            output = subprocess.call(cmd, shell=True, stdout=None)
            if output != 0:
                pdb.set_trace()
            os.remove(hqPath)
    with open(log_file, 'a') as f:
        f.write(f"{identity}\n")
    print(f' videosSet {fullPathVideo} OK !!!')
