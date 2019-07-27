# Pose estimator to VJ
A simple script based on TF Pose Estimation by [@ildoonet](https://github.com/ildoonet) for capture video from webcamera with sending JSON and CSV data of points of body parts to VJ software like Resolume Arena and TouchDesigner via UDP and OSC.

![blackpink with deepface(vgg model)](./etc/example_blackpink.png)

## Features
- Actually, two points of tracking
- Included body parts index list
- Simple configure
- Jupiter Notebook run (no terminal needed)
- Comprehensive comments
## Configure features
- Choose a front (selfie) or rear camera
- Setting up of IP and PORT for sending data
- Setting of necessary points
- Choose a data format for Touch Designer (JSON or CSV)
- Debug mode (with fake data)
- Swithing on/off video mode

## Install & Run
### Install
Just a copy files to root directory of correctly installed TF Pose Estimation
### Run
```bash
$ python WEBCAM.py
```
Or execute WEBCAM.ipynb from Jupiter Notebook

### Requirements
- tensorflow >= 1.8.0
- opencv >= 3.4.1
- TfPoseEstimator
