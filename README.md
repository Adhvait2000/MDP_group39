# MDP Group39 AY24/25 
This mono-repository contains the entire codebase for MDP.
The main objective of this project is to build a robotic system that can autonomously explore/ traverse a known area and detect images displayed on the area. The system should also be able to avoid obstacles by detecting visual markers such as "bulls eyes". This project involves both hardware and software components and the combination of the two is needed to complete the following tasks:
1. Fastest Car
2. Image Recognition
There are 5 components to this project:
1. Android - the mobile device that is required for transmitting and receiving control signals. 
2. Algorithm - to develop a path finding algorithm that allows the robot to travers through the known area 
3. STM - responsible for the movement of the robot 
4. Raspberry Pi - orchestrator and message passing between different components
5. Image Recognition - a model used to allow the robot to detect images on the obstacles
