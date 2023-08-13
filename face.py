import sensor,image,lcd  # import ��ؿ�
import KPU as kpu
import time
from Maix import FPIOA,GPIO
#task_fd = kpu.load(0x200000) # ��flash 0x200000 �����������ģ��
#task_ld = kpu.load(0x300000) # ��flash 0x300000 �����������ؼ�����ģ��
#task_fe = kpu.load(0x400000) # ��flash 0x400000 ��������196ά����ֵģ��
 
#��SD���м���ģ��
task_fd = kpu.load("/sd/FD_face.smodel") # �����������ģ��
task_ld = kpu.load("/sd/KP_face.smodel") # �����������ؼ�����ģ��
task_fe = kpu.load("/sd/FE_face.smodel") # ��������196ά����ֵģ��
 
clock = time.clock()  # ��ʼ��ϵͳʱ�ӣ�����֡��
key_pin=16 # ���ð������� FPIO16
fpioa = FPIOA()
fpioa.set_function(key_pin,FPIOA.GPIO7)
key_gpio=GPIO(GPIO.GPIO7,GPIO.IN)
last_key_state=1
key_pressed=0 # ��ʼ���������� ����GPIO7 �� FPIO16
def check_key(): # ������⺯����������ѭ���м�ⰴ���Ƿ��£��½�����Ч
    global last_key_state
    global key_pressed 
    val=key_gpio.value()
    if last_key_state == 1 and val == 0:
        key_pressed=1
    else:
        key_pressed=0
    last_key_state = val
 
lcd.init() # ��ʼ��lcd
sensor.reset() #��ʼ��sensor ����ͷ
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(1) #��������ͷ����
sensor.set_vflip(1)   #��������ͷ��ת
sensor.run(1) #ʹ������ͷ
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025) #anchor for face detect ������������Anchor
dst_point = [(44,59),(84,59),(64,82),(47,105),(81,105)] #standard face key point position ��׼������5�ؼ������� �ֱ�Ϊ ���� ���� ���� ����� �����
a = kpu.init_yolo2(task_fd, 0.5, 0.3, 5, anchor) #��ʼ���������ģ��
img_lcd=image.Image() # ������ʾbuf
img_face=image.Image(size=(128,128)) #���� 128 * 128 ����ͼƬbuf
a=img_face.pix_to_ai() # ��ͼƬתΪkpu���ܵĸ�ʽ
record_ftr=[] #���б� ���ڴ洢��ǰ196ά����
record_ftrs=[] #���б� ���ڴ洢������¼������������ ���Խ�������txt���ļ���ʽ���浽sd���󣬶�ȡ�����б�����ʵ�������ϵ�洢��
names = ['Mr.1', 'Mr.2', 'Mr.3', 'Mr.4', 'Mr.5', 'Mr.6', 'Mr.7', 'Mr.8', 'Mr.9' , 'Mr.10'] # ������ǩ���������б�����ֵһһ��Ӧ��
while(1): # ��ѭ��
    check_key() #�������
    img = sensor.snapshot() #������ͷ��ȡһ��ͼƬ
    clock.tick() #��¼ʱ�̣����ڼ���֡��
    code = kpu.run_yolo2(task_fd, img) # �����������ģ�ͣ���ȡ��������λ��
    if code: # �����⵽����
        for i in code: # ���������
            # Cut face and resize to 128x128
            a = img.draw_rectangle(i.rect()) # ����Ļ��ʾ��������
            face_cut=img.cut(i.x(),i.y(),i.w(),i.h()) # �ü���������ͼƬ�� face_cut
            face_cut_128=face_cut.resize(128,128) # ���ó�������ͼƬ ���ŵ�128 * 128����
            a=face_cut_128.pix_to_ai() # ���³�ͼƬת��Ϊkpu���ܵĸ�ʽ
            #a = img.draw_image(face_cut_128, (0,0))
            # Landmark for face 5 points
            fmap = kpu.forward(task_ld, face_cut_128) # ��������5��ؼ�����ģ��
            plist=fmap[:] # ��ȡ�ؼ���Ԥ����
            le=(i.x()+int(plist[0]*i.w() - 10), i.y()+int(plist[1]*i.h())) # ��������λ�ã� ������w����-10 ��������ģ��ת�������ľ�����ʧ
            re=(i.x()+int(plist[2]*i.w()), i.y()+int(plist[3]*i.h())) # ��������λ��
            nose=(i.x()+int(plist[4]*i.w()), i.y()+int(plist[5]*i.h())) #�������λ��
            lm=(i.x()+int(plist[6]*i.w()), i.y()+int(plist[7]*i.h())) #���������λ��
            rm=(i.x()+int(plist[8]*i.w()), i.y()+int(plist[9]*i.h())) #�����λ��
            a = img.draw_circle(le[0], le[1], 4)
            a = img.draw_circle(re[0], re[1], 4)
            a = img.draw_circle(nose[0], nose[1], 4)
            a = img.draw_circle(lm[0], lm[1], 4)
            a = img.draw_circle(rm[0], rm[1], 4) # ����Ӧλ�ô���СԲȦ
            # align face to standard position
            src_point = [le, re, nose, lm, rm] # ͼƬ�� 5 �����λ��
            T=image.get_affine_transform(src_point, dst_point) # ���ݻ�õ�5���������׼���������ȡ����任����
            a=image.warp_affine_ai(img, img_face, T) #��ԭʼͼƬ����ͼƬ���з���任���任Ϊ����ͼ��
            a=img_face.ai_to_pix() # ������ͼ��תΪkpu��ʽ
            #a = img.draw_image(img_face, (128,0))
            del(face_cut_128) # �ͷŲü���������ͼƬ
            # calculate face feature vector
            fmap = kpu.forward(task_fe, img_face) # ��������ͼƬ��196ά����ֵ
            feature=kpu.face_encode(fmap[:]) #��ȡ������
            reg_flag = False
            scores = [] # �洢�����ȶԷ���
            for j in range(len(record_ftrs)): #�����Ѵ�����ֵ
                score = kpu.face_compare(record_ftrs[j], feature) #���㵱ǰ��������ֵ���Ѵ�����ֵ�ķ���
                scores.append(score) #��ӷ����ܱ�
            max_score = 0
            index = 0
            for k in range(len(scores)): #�������бȶԷ������ҵ�������������ֵ
                if max_score < scores[k]:
                    max_score = scores[k]
                    index = k
            if max_score > 85: # �������������85�� ���Ա��϶�Ϊͬһ����
                a = img.draw_string(i.x(),i.y(), ("%s :%2.1f" % (names[index], max_score)), color=(0,255,0),scale=2) # ��ʾ���� �� ����
            else:
                a = img.draw_string(i.x(),i.y(), ("X :%2.1f" % (max_score)), color=(255,0,0),scale=2) #��ʾδ֪ �� ����
            if key_pressed == 1: #�����⵽����
                key_pressed = 0 #���ð���״̬
                record_ftr = feature 
                record_ftrs.append(record_ftr) #����ǰ������ӵ���֪�����б�
            break
    fps =clock.fps() #����֡��
    print("%2.1f fps"%fps) #��ӡ֡��
    a = lcd.display(img) #ˢ����ʾ
    #kpu.memtest()
 
#a = kpu.deinit(task_fe)
#a = kpu.deinit(task_ld)
#a = kpu.deinit(task_fd)