import os
import datetime

cache_folder="cache"
image_name="logo.jpg"
image_name2="t.jpg"
cachetime=5

def delete_image(self, image_name):
    image_path=os.path.join(cache_folder,image_name)
    if os.path.exists(image_path):
        os.remove(image_path)

def check_image_time(self, dict):
    images_to_delete = [] 
    for image_name,timestamp in dict.items():
        time=datetime.datetime.now()
        if time >= timestamp:
            delete_image(image_name)
            images_to_delete.append(image_name)
    for image in images_to_delete:
        del dict[image]

dict={
    image_name : datetime.datetime.now()+datetime.timedelta(seconds=cachetime),
    "key2" : datetime.datetime.now()+datetime.timedelta(seconds=cachetime),
    image_name2: datetime.datetime.now()+datetime.timedelta(seconds=cachetime+2),
}

while True:
    check_image_time(dict)


            
            