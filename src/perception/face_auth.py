"""
Face Authentication Module for OMNI.
Uses face_recognition to verify user identity.
"""

import os
import cv2
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class FaceAuth:
    def __init__(self, faces_dir: str = "data/faces"):
        self.faces_dir = faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.is_active = False
        
        # Try importing face_recognition
        try:
            import face_recognition
            self.fr = face_recognition
            self.is_active = True
            self.load_known_faces()
        except ImportError:
            logger.warning("face_recognition not installed. Face Auth disabled.")
            self.is_active = False

    def load_known_faces(self):
        """Load all .jpg/.png files from faces dir."""
        if not os.path.exists(self.faces_dir):
            os.makedirs(self.faces_dir, exist_ok=True)
            return

        logger.info(f"Loading faces from {self.faces_dir}...")
        for filename in os.listdir(self.faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(self.faces_dir, filename)
                try:
                    image = self.fr.load_image_file(path)
                    encodings = self.fr.face_encodings(image)
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        name = os.path.splitext(filename)[0].capitalize()
                        self.known_face_names.append(name)
                        logger.info(f"Loaded face: {name}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")

    def verify_face(self, frame_rgb: np.ndarray) -> Optional[str]:
        """
        Check if any face in the frame matches known faces.
        Returns the name of the first match, or None.
        """
        if not self.is_active or not self.known_face_encodings:
            return None

        try:
            # Resize for speed (1/4 size)
            small_frame = cv2.resize(frame_rgb, (0, 0), fx=0.25, fy=0.25)
            
            # Find faces
            face_locations = self.fr.face_locations(small_frame)
            face_encodings = self.fr.face_encodings(small_frame, face_locations)

            for face_encoding in face_encodings:
                # Check matches
                matches = self.fr.compare_faces(self.known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    return self.known_face_names[first_match_index]
            
            return None
        except Exception as e:
            logger.error(f"Face verification error: {e}")
            return None
