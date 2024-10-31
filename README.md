# Miniature Self-Driving Car with Raspberry Pi, OpenCV, and CNN

## Table of Contents
- [Overview](#overview)
- [Components](#components)
- [Setup](#setup)
- [Implementation](#implementation)
  - [1. Lane Detection](#1-lane-detection)
  - [3. Steering and Control](#3-steering-and-control)
- [Testing and Evaluation](#testing-and-evaluation)
- [Future Improvements](#future-improvements)
- [References](#references)

---

## Overview
This project involves building a miniature self-driving car using a Raspberry Pi, OpenCV, and a Convolutional Neural Network (CNN). The car is designed to follow lanes, avoid obstacles, and make real-time driving decisions based on computer vision techniques.

## Components
- **Raspberry Pi 4 Model B**
- **Pi Camera**: To capture the road images.
- **Motor Driver Module**: For controlling the car’s wheels.
- **DC Motors**: To drive the car’s movement.
- **Battery Pack**
- **SD Card**: With Raspberry Pi OS installed.
- **USB Power Bank**: For powering the Raspberry Pi.
- **Jumper Wires**

## Setup

### Step 1: Set Up the Raspberry Pi
1. Install the Raspberry Pi OS on an SD card.
2. Boot up the Raspberry Pi and set up the system (enable SSH, camera, and GPIO).
3. Connect the Pi Camera to the CSI port on the Raspberry Pi.

### Step 2: Install Required Libraries
Open a terminal and enter the following commands to set up the environment:
```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```
