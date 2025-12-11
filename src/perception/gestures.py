"""
Gesture Recognition Module for OMNI.
Uses MediaPipe to track hands and identify gestures.
"""

import cv2
import cv2
import math
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"MediaPipe not available: {e}")
    MP_AVAILABLE = False

class HandTracker:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.is_active = MP_AVAILABLE
        if not self.is_active:
            return

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky

    def find_hands(self, img, draw=True):
        """Find hands in an image and optionally draw landmarks."""
        if not self.is_active: return img
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def get_position(self, img, hand_no=0):
        """Get landmark positions for a specific hand."""
        lm_list = []
        if not self.is_active: return lm_list

        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
        return lm_list

    def detect_gesture(self, lm_list) -> Optional[str]:
        """
        Detect simple gestures based on landmark positions.
        Returns: 'OPEN_PALM', 'FIST', 'POINTING', or None
        """
        if len(lm_list) == 0:
            return None

        # Check fingers up
        fingers = []
        
        # Thumb (check x pos relative to IP joint depending on hand side, simplified here)
        # For simplicity, we'll just check if tip is to the left/right of knuckle
        # Better: Check distance to other fingers or use y-axis for "thumbs up"
        # Let's stick to 4 fingers for now to be robust
        
        # 4 Fingers
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1) # Up
            else:
                fingers.append(0) # Down

        total_fingers = fingers.count(1)

        # Logic
        if total_fingers == 4: # 4 fingers up (Thumb ignored for simplicity)
            return "OPEN_PALM"
        elif total_fingers == 0:
            return "FIST"
        elif total_fingers == 1 and fingers[0] == 1: # Index only
            return "POINTING"
        
        return None
