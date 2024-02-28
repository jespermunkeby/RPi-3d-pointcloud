import os
import sys
import numpy as np
import cv2
import json

ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.05
MARKER_LENGTH = 0.0255

def get_camera_matrix_distortion_coeffs(image_path):
    # Define the aruco dictionary and charuco board
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()

    # Load JPG images from folder
    image_files = [os.path.join(image_path, f) for f in os.listdir(image_path) if f.endswith(".jpg")]
    image_files.sort()  # Ensure files are in order

    all_charuco_corners = []
    all_charuco_ids = []

    for image_file in image_files:
        image = cv2.imread(image_file)
        image_copy = image.copy()
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(image, dictionary, parameters=params)
        
        # If at least one marker is detected
        if len(marker_ids) > 0:
            cv2.aruco.drawDetectedMarkers(image_copy, marker_corners, marker_ids)
            charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, image, board)
            if charuco_retval and len(charuco_ids) >= 4:
                all_charuco_corners.append(charuco_corners)
                all_charuco_ids.append(charuco_ids)
            else:
                print(f"Skipping image {image_file} due to insufficient corner detections.")

    # camera calibration
    _, camera_matrix, dist_coeffs, _, _= cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, board, image.shape[:2], None, None)

    return camera_matrix, dist_coeffs

def detect_pose(image, camera_matrix, dist_coeffs):
    # Undistort the image
    undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)

    # Define the aruco dictionary and charuco board
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()

    # Detect markers in the undistorted image
    marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(undistorted_image, dictionary, parameters=params)

    # If at least one marker is detected
    if len(marker_ids) > 0:
        # Interpolate CharUco corners
        charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, undistorted_image, board)

        # If enough corners are found, estimate the pose
        if charuco_retval:
            retval, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(charuco_corners, charuco_ids, board, camera_matrix, dist_coeffs, None, None)

            # If pose estimation is successful, draw the axis
            if retval:
                cv2.drawFrameAxes(undistorted_image, camera_matrix, dist_coeffs, rvec, tvec, length=0.1, thickness=15)
                return undistorted_image, rvec, tvec # here
    return undistorted_image, None, None # here

def main(image_path):
    camera_matrix, dist_coeffs = get_camera_matrix_distortion_coeffs(image_path)
    #camera_matrix = np.load('camera_matrix.npy')
    #dist_coeffs = np.load('dist_coeffs.npy')

    image_files = [os.path.join(image_path, f) for f in os.listdir(image_path) if f.endswith(".jpg")]
    image_files.sort()  # Ensure files are in order

    pos_img_dir = os.path.join('Posed_Images')
    os.makedirs(pos_img_dir, exist_ok=True)  


    # Dictionary to hold image filename and its vectors
    image_vectors = {}

    for image_file in image_files:
        image = cv2.imread(image_file)
        pose_image, rvec, tvec = detect_pose(image, camera_matrix, dist_coeffs)

        if rvec is not None and tvec is not None:
            # Convert vectors to lists for JSON serialization
            image_vectors[os.path.basename(image_file)] = {
                "rotation_vector": rvec.tolist(),
                "translation_vector": tvec.tolist()
            }

        #cv2.imshow('Pose Image', pose_image)
        #cv2.waitKey(0)

        cv2.imwrite(os.path.join(pos_img_dir, os.path.basename(image_file)), pose_image)

    # Save the vectors to a JSON file
    with open('image_vectors.json', 'w') as f:
        json.dump(image_vectors, f, indent=4)

    #cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n\t'python3 calibrate.py path/to/images/'\n")
        sys.exit(1)

    main(sys.argv[1])

