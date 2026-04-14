import cv2
import mediapipe as mp
import math
from pythonosc import udp_client

osc_client = udp_client.SimpleUDPClient("192.168.1.11",7000)

BaseOption = mp.tasks.BaseOptions
HandLandmarker= mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode= mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(base_options=BaseOption(model_asset_path='hand_landmarker.task'),running_mode= VisionRunningMode.IMAGE, num_hands=2)

cap= cv2.VideoCapture(1)

def draw_hand_skeleton(frame, hand, h, w, colour, handedness, dist):
    def point(idx):
        return (int(hand[idx].x * w), int(hand[idx].y * h))
    cv2.line(frame, point(0), point(1), colour, 2)
    cv2.line(frame, point(1), point(2), colour, 2)
    cv2.line(frame, point(2), point(3), colour, 2)
    cv2.line(frame, point(3), point(4), colour, 2)
    cv2.line(frame, point(0), point(5), colour, 2)
    cv2.line(frame, point(5), point(6), colour, 2)
    cv2.line(frame, point(6), point(7), colour, 2)
    cv2.line(frame, point(7), point(8), colour, 2)
    cv2.line(frame, point(5),  point(9),  colour, 2)
    cv2.line(frame, point(9),  point(10), colour, 2)
    cv2.line(frame, point(10), point(11), colour, 2)
    cv2.line(frame, point(11), point(12), colour, 2)
    cv2.line(frame, point(9),  point(13), colour, 2)
    cv2.line(frame, point(13), point(14), colour, 2)
    cv2.line(frame, point(14), point(15), colour, 2)
    cv2.line(frame, point(15), point(16), colour, 2)
    cv2.line(frame, point(13), point(17), colour, 2)
    cv2.line(frame, point(17), point(18), colour, 2)
    cv2.line(frame, point(18), point(19), colour, 2)
    cv2.line(frame, point(19), point(20), colour, 2)
    cv2.line(frame, point(0),  point(17), colour, 2)
"""
    if handedness=='Right':
        cv2.line(frame, point(8),  point(4), colour, 2)
        midpt_x= int((hand[4].x+ hand[8].x)*w/2)
        midpt_y= int((hand[4].y+ hand[8].y)*h/2)
        cv2.putText(frame, f'{round(dist,2)}', (midpt_x - 50, midpt_y ),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 2)
"""

def get_distance(lm1, lm2):
    dx = lm2.x - lm1.x
    dy = lm2.y - lm1.y
    dist = math.sqrt(dx*dx + dy*dy)
    #dist = max(0, min(0.4, dist))
    #print(f'ditance between index and thumb is {dist}')
    return dist


with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = landmarker.detect(mp_image)

        if result.hand_landmarks:
            for hand_idx, hand in enumerate(result.hand_landmarks):
                h, w, _ = frame.shape

                # Get which hand this is
                handedness = result.handedness[hand_idx][0].category_name
                if handedness == "Right":
                    handedness = "Left"
                else:
                    handedness = "Right"

                # Different colours for each hand
                # Right = blue, Left = green
                colour = (255, 100, 0) if handedness == "Right" else (0, 100, 255)

                # Draw dots
                for lm in hand:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, colour, -1)

                # Draw skeleton with hand colour
                #draw_hand_skeleton(frame, hand, h, w, colour)

                # Label on screen
                wrist_x = int(hand[0].x * w)
                wrist_y = int(hand[0].y * h)
                cv2.putText(frame, handedness, (wrist_x - 20, wrist_y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
                
                dist = 0
                if handedness== 'Right':
                    dist=get_distance(hand[4], hand[8])
                    #print (f'{dist}')
                

                #if handedness== 'Left':
                    #print (f'index X {hand[8].x} : index Y {hand[8].y}')
                
                draw_hand_skeleton(frame, hand, h, w, colour, handedness, dist)

                osc_client.send_message(f'/{handedness}/index_tip/x', hand[8].x)
                osc_client.send_message(f'/{handedness}/index_tip/y', hand[8].y)
                osc_client.send_message(f'/{handedness}/wrist/x',     hand[0].x)
                osc_client.send_message(f'/{handedness}/wrist/y',     hand[0].y)
                osc_client.send_message(f'/{handedness}/thumb/x',     hand[0].x)
                osc_client.send_message(f'/{handedness}/thumb/y',     hand[0].y)



        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()