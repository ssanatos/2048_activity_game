import pygame, os
from _2048.game import Game2048
from _2048.manager import GameManager
import cv2
import mediapipe as mp



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(                 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


EVENTS = [
pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}),   # UP
pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}), # RIGHT
pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}), # DOWN
pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}) # LEFT
]

sound = 'sound.wav'

def run_game(game_class=Game2048, title='2048!', data_dir='save'):

    pygame.init()
    pygame.display.set_caption(title)
    pygame.display.set_icon(game_class.icon(32))
    
    os.makedirs(data_dir, exist_ok=True)

    screen = pygame.display.set_mode((game_class.WIDTH, game_class.HEIGHT))
    
    manager = GameManager(Game2048, screen,
                os.path.join(data_dir, '2048.score'),
                os.path.join(data_dir, '2048.%d.state'))
    
    
    cap = cv2.VideoCapture(0)

    running = True

    e = None
    #event = None
    text = "none"
    
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or text == "Quit" :
                running = False
                cap.release()
                break

            while cap.isOpened():   

                success, image = cap.read()
                
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                mp_drawing.draw_landmarks(
                    image,                          
                    results.pose_landmarks,         
                    mp_pose.POSE_CONNECTIONS,       
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
 
                manager.dispatch(event)

                if cv2.waitKey(5) == 27:
                    running = False
                    text == "Quit"
                    cap.release()
                    break
              
                try :               #카메라에 몸이 다 들어와야 게임 진행
                    r_mouth = results.pose_landmarks.landmark[10]
                    l_mouth = results.pose_landmarks.landmark[9]
                    r_shoulder = results.pose_landmarks.landmark[12]
                    l_shoulder = results.pose_landmarks.landmark[11]
                    r_elbow = results.pose_landmarks.landmark[14]
                    l_elbow = results.pose_landmarks.landmark[13]
                    r_hip = results.pose_landmarks.landmark[24]
                    r_knee = results.pose_landmarks.landmark[26]
                    r_wrist = results.pose_landmarks.landmark[16]
                    l_wrist = results.pose_landmarks.landmark[15]
                    nose = results.pose_landmarks.landmark[0]
                except AttributeError :
                    print("온 몸이 카메라에 들어오게 서세요")
                    continue
                
                if r_knee.y > r_hip.y and l_wrist.y > l_shoulder.y and r_wrist.y > r_shoulder.y :
                    text="Ready"  

                # 얼추 차렷 자세로 돌아오면
                if text == "Ready" :                                        
                    e = None
                    # 위로 : 양팔을 귀에 붙여 들어올림
                    if r_elbow.y < r_mouth.y and l_elbow.y < l_mouth.y :
                        text = "Up"
                        e = EVENTS[0]
                                                
                    # 좌측으로 : 오른팔을 귀에붙여 몸을 스트레칭 
                    elif r_shoulder.y > l_shoulder.y and l_wrist.y < nose.y and l_wrist.x < nose.x :
                        text = "Left"
                        e = EVENTS[2]
                     
                    # 우측으로 : 왼팔을 귀에붙여 몸을 스트레칭
                    elif l_shoulder.y > r_shoulder.y and r_wrist.y < nose.y and r_wrist.x > nose.x :
                        text = "Right"
                        e = EVENTS[3]
                            
                    # 아래로 : 쪼그려앉기
                    elif r_hip.y >= r_knee.y :
                        text = "Down"
                        e = EVENTS[1]
 
                    # 이벤트가 있으면     
                    if e != None :
                        manager.dispatch(e)
                        manager.draw()
                        pygame.mixer.music.load(sound)
                        pygame.mixer.music.play()
                                    
                    # 이벤트가 없으면
                    else :
                        text = "none"
 
                cv2.putText(image, text, (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow('CYCLOPS 2048', image)
                manager.draw()

    pygame.quit()
    manager.close()
   

# 위에서 정의한 run_game 실행
run_game()



