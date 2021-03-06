#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import azure
from azure.storage import BlobService
import azure.http
import os.path

import videomanager.fileprocessor as fileprocessor
import videomanager.videostoreoperator as videostoreoperator
import videomanager.config as config
import videomanager.encrypt as encrypt

def upload_chunck(buf, path, storagename, container, key):
    blob_service = BlobService(account_name=storagename, account_key=key)
    loop = 0;
    while True:
        try:
            blob_service.put_block_blob_from_bytes(container,path,buf)
            break
        except (azure.http.HTTPError, TimeoutError) as e:
            loop = loop + 1
            if loop >= 3:
                raise e


def download_chunck(path, storagename, container, key):
    blob_service = BlobService(account_name=storagename, account_key=key)
    loop = 0
    
    while True:
        try:
            return blob_service.get_blob_to_bytes(container, path)
        except (azure.http.HTTPError, TimeoutError) as e:
            loop = loop + 1
            if loop >= 3:
                raise e

def upload_video(file_path):
    vs_operator = videostoreoperator.VideoStoreOperator()
    video_id = vs_operator.create(file_path)
    if video_id == None:
        print("Error occured during creating file")
        return
    video_detils = vs_operator.get(video_id)

    processor = fileprocessor.FileProcessor(file_path)
    count = len(video_detils.chuncks)
    for i in range(count):
        buf = processor.get_chunck(i)
        chk = video_detils.chuncks[i]
        upload_chunck(buf, chk.path, chk.storagename, chk.container, chk.key)
    processor.close()

    vs_operator.updateState(video_id, 1)

def list_videos():
    vs_operator = videostoreoperator.VideoStoreOperator()
    videos = vs_operator.list()
    count = len(videos)
    print ("id\t\t\t\tname")
    for i in range(count):
        print ("{0}\t\t\t\t{1}".format(videos[i].name,videos[i].id))

    return videos

def download_video(id, path=None):
    vs_operator = videostoreoperator.VideoStoreOperator()
    video_detils = vs_operator.get(id)

    if path == None:
        decrypt_path = video_detils.video.name
    elif os.path.isdir(path):
        decrypt_path = os.path.join(path, video_detils.video.name)
    else:
        decrypt_path = path

    path = decrypt_path + ".tmp"

    f = open(path, "wb")
    count = len(video_detils.chuncks)
    for i in range(count):
        chk = video_detils.chuncks[i]
        buf = download_chunck(chk.path, chk.storagename, chk.container, chk.key)
        f.write(buf)
    f.close()

    if config.is_encrypt():
        with open(path, "rb") as in_f, open(decrypt_path, "wb") as out_f:
            encrypt.decrypt(in_f, out_f, config.config["pwd"])
    else:
        shutil.move(path, decrypt_path)

    processor = fileprocessor.FileProcessor(decrypt_path)
    if processor.md5 == video_detils.video.md5:
        print ("download finished. checksum matched")
    else:
        print ("download finished, but checksum doesn't match. Download failed.")
    processor.close()

def delete_video(id):
    vs_operator = videostoreoperator.VideoStoreOperator()
    video_detils = vs_operator.get(id)
    vs_operator.delete(id)
    
    count = len(video_detils.chuncks)
    for i in range(count):
        chk = video_detils.chuncks[i]
        blob_service = BlobService(account_name=chk.storagename, account_key=chk.key)
        try:
            blob_service.delete_blob(chk.container, chk.path)
        except azure.WindowsAzureMissingResourceError:
            pass

def get_files_from_path(file_path):
    if not os.path.isdir(file_path):
        return [file_path]

    results = []
    files = os.listdir(file_path)
    for item in files:
        path = os.path.join(file_path, item)
        if not os.path.isdir(path):
            results.append(path)
        else:
            sub_results = get_files_from_path(path)
            results = results + sub_results
    return results

def upload_cmd(options):
    files = get_files_from_path(options.src)
    print("{0} files need to be uploaded".format(len(files)))

    for index, item in enumerate(files):
        print("progress: {0}/{1}    {2}".format(index, len(files), item))
        try:
            upload_video(item)
        except Exception as e:
            print("An error happened while uploading. {0}".format(e.message))


def download_cmd(options):
    try:
        download_video(options.id, options.dest)
    except Exception as e:
        print("An error happened while downloading. {0}".format(e.message))

def list_cmd(options):
    return list_videos()

def delete_cmd(options):
    delete_video(options.id)