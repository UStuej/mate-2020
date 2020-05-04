import cv2
import imutils

class SubwayArranger:
    def __init__(self):
        self.faces = [] # List of faces
    def add_face(self, face):
        # TODO: Some OpenCV enhancement stuff here
        self.faces.append(face)
