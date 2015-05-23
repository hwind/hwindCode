#!/usr/bin/env python
# -*- coding: utf-8 -*-
from azure.storage import BlobService
from FileProcessor import FileProcessor
from VideoStoreOperator import *

def upload_chunck(buf, path, storagename, container, key):
	blob_service = BlobService(account_name=storagename, account_key=key)
	blob_service.put_block_blob_from_bytes(
		container,
		path,
		buf
    )

def  download_chunck(path, storagename, container, key):
	blob_service = BlobService(account_name=storagename, account_key=key)
	return blob_service.get_blob_to_bytes(container, path)

def upload_video(file_path):
	vs_operator = VideoStoreOperator()
	video_id = vs_operator.create(file_path)
	video_detils = vs_operator.get(video_id)

	processor = FileProcessor(file_path)
	count = len(video_detils.chuncks)
	for i in range(count):
		buf = processor.get_chunck(i)
		chk = video_detils.chuncks[i]
		upload_chunck(buf, chk.path, chk.storagename, chk.container, chk.key)
		
def list_videos():
	vs_operator = VideoStoreOperator()
	videos = vs_operator.list()
	count = len(videos)
	print u"id\t\t\t\tname"
	for i in range(count):
		print u"{0}\t\t\t\t{1}".format(videos[i].id, videos[i].name)

	return videos

def download_video(id, path=None):
	vs_operator = VideoStoreOperator()
	video_detils = vs_operator.get(id)

	if path == None:
		path = video_detils.video.name
	f = open(path, "wb")
	count = len(video_detils.chuncks)
	for i in range(count):
		chk = video_detils.chuncks[i]
		buf = download_chunck(chk.path, chk.storagename, chk.container, chk.key)
		f.write(buf)
	f.close()
	
	processor = FileProcessor(path)
	md5 = processor.getMD5()
	if md5 == video_detils.video.md5:
		print "download finished. checksum matched"
	else:
		print "download finished, but checksum doesn't match. Download failed."

def delete_video(id):
	vs_operator = VideoStoreOperator()
	video_detils = vs_operator.get(id)
	vs_operator.delete(id)
	
	count = len(video_detils.chuncks)
	for i in range(count):
		chk = video_detils.chuncks[i]
		blob_service = BlobService(account_name=chk.storagename, account_key=chk.key)
		blob_service.delete_blob(chk.container, chk.path)

def upload_cmd(options):
	upload_video(options.src)

def download_cmd(options):
	download_video(options.id, options.dest)

def list_cmd(options):
	return list_videos()

def delete_cmd(options):
	delete_video(options.id)