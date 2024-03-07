# Background
This is our project for the IK1332 IOT course at KTH. The parts of the code and system is *really* messy and hacky, but this is to be considered a "Proof of Concept" project.

Monitoring spaces can be done with many modalities, but 3d is an uncommon one as it often requires expensive and specialized hardware components. We propose a system that uses regular monocular cameras mounted at arbitrary positions in a room to create a 3d point reconstruction of the site. We use a deep learning based method that allows our system to be applied indoor as well as outdoor, which is often a challenge even for specialized hardware. Our system consists of a BLE mesh network[] of Raspberry Pis equipped with cameras, a backend server for data processing and deep learning inference, and a frontend server to visualize the 3D information along with an API reference to interact with the system. As an open API endpoint is provided, the system can easily be used for a multitude of applications and integrations, for example scene awareness for indoor robots or real-time progress insights at a construction site or renovation projects.

# Running the project
The project is structured in 3 components - the RPi (in the RPi folder) code, the frontend server (in the Frontend folder), and the backend API server (server.py).

## Running the RPi code

## Running the frontend server
1. `cd frontend`
2. `npm i`
3. `npm run`

## Running the backend API server
To run the backend API you need a CUDA Nvidia GPU.

1. Download the weights for metric finetune of depth-anything. Choose if you want the outdoor or indoor finetune based on your use case. The weights are availiable at [text](https://huggingface.co/spaces/LiheYoung/Depth-Anything/tree/main/checkpoints_metric_depth)

2. Open `/Depth-Anything/metric_depth/zoedepth/models/base_models/depth_anything.py` and change line 341 to `state_dict = torch.load('YOUR_CHECKPOINT_PATH_HERE', map_location='cpu')`

3. Open `/Depth-Anything/metric_depth/depth_to_pointcloud.py` and change line 76 to `parser.add_argument("-p", "--pretrained_resource", type=str, default='local::YOUR_CHECKPOINT_PATH_HERE', help="Pretrained resource to use for fetching weights.")`

4. create a backend conda env with `conda env create -f backend-server-env.yml`
5. create a depth-anything env with `conda env create -f depth-anything-env.yml`
6. activate the backend server env with `conda activate backend-server`
7. run the server `python server.py`
