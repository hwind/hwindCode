#!/usr/bin/env python
# -*- coding: utf-8 -*-
import videomanager.fileprocessor as fileprocessor
import videomanager.videostoreoperator as videostoreoperator
import videomanager.videomanager as videomanager
import videomanager.config as config
import videomanager.encrypt as encrypt

path = "D:\\test.mkv"
"""
processor = FileProcessor(path)

print processor.name
print processor.size
print processor.chuncks


operator = VideoStoreOperator()
storage = operator.get_storage_info()
print storage[0].id
print storage[0].name
print storage[0].container
print storage[0].key

operator.create(path)

videos = operator.list()
print len(videos)
video = videos[0]
print video.id
print video.name
print video.size
print video.md5

video_detils = operator.get(video.id)
print video_detils.video.id
print video_detils.video.name
print video_detils.video.size
print video_detils.video.md5

count = len(video_detils.chuncks)
print count
chk = video_detils.chuncks[0]
print chk.index
print chk.path
print chk.storagename
print chk.container
print chk.key


buf = processor.get_chunck(0)
upload_chunck(buf, chk.path, chk.storagename, chk.container, chk.key)
"""
#upload_video(path)
#videos = list_videos()
#print videos[0].size
#print videos[0].md5
#download_video(videos[0].id, "./helloworldtest")

with open(path, "rb") as in_f, open(path+".tmp", "wb") as out_f:
	encrypt.encrypt(in_f, out_f, "Password01!")

with open(path+".tmp", "rb") as in_f, open(path+".tmp2", "wb") as out_f:
	encrypt.decrypt(in_f, out_f, "Password01!")

with open(path+".tmp", "rb") as in_f, open(path+".tmp3", "wb") as out_f:
	encrypt.decrypt(in_f, out_f, "Password02!")

p1 = fileprocessor.FileProcessor(path)
p2 = fileprocessor.FileProcessor(path+".tmp2")
p3 = fileprocessor.FileProcessor(path+".tmp3")

print (p1.md5)
print (p2.md5)
print (p3.md5)
