# FEATURES

This app use Django and face recognition for stuff time tracking, you can simply add company and persons via admin panel. 
When you've create company just add door instance with camera, and set what should that camera do: 
`start tracking/stop tracking/nothing`. When you setting up doors, use REST api for sending frame and door_id from camera 
All stats appear at the next day at dashboard.

*Dashboard with stats about tracked time -* `localhost:8000/`

*Admin panel localhost:8000/admin*

*First, create company and users, in admin panel. Add some training data (photo/video) to person*

*Example of using api for recognition and start/stop tracking time*

```
image = "some_person.jpg"
with open(image, 'rb') as file:
    files = {
        'file': file,
        'Content-Type': 'image/jpeg'
    }
    r = requests.post(
        'http://0.0.0.0:8000/api/recognizer/persons/',
        verify=False, files=files, data={"door": 1}
    )
```

 

# BUILD

*For production:* `docker-compose -f docker-compose-prod.yml build`

*For local:* `docker-compose build`

# RUN

*For production:* `docker-compose -f docker-compose-prod.yml up`

*For local:* `docker-compose up`

*Also you should rename env.example to .env*



## Deploying in venv:

*dlib installation:* 

1) `apt-get install build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev`

*Additional dependencies when install on Raspberry:*

1) `apt-get install libopenjp2-7 libwebp-dev libjasper-dev libIlmbase-dev libopenexr-dev libgstreamer1.0-dev libavcodec-dev libavformat-dev libswscale-dev libqt4-dev`

*Install pip dependencies:*

`pip3 install -r requirements.txt`

**Note: FOR CODE DEMONSTRATION ONLY.**
