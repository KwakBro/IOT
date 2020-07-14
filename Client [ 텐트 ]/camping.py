import socket
import threading
from threading import Lock
from multiprocessing import Queue
import RPi.GPIO as GPIO
from time import sleep
import sys
import spidev
import time
import serial
from operator import eq
from mq import *

sat = serial.Serial(
	port='/dev/ttyAMA0',
	baudrate = 9600,
	parity = serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout = 1
)
	# 원래 UART port인 /dev/ttyAMA0 은 Bluetooth로 할당이 되어 있다. 
	# 때문에 UART port를 사용하기 위해서는 Bluetooth Controller 정지 필요.
	# sudo systemctl disable hciuart

GPIO.setwarnings(False)

ENA = 7     # its for distributer A ( with FAN , LED )
ENB = 16

IN1 = 5    # this is LED
IN1_F = 11

IN2 = 12    # this is FAN
IN2_F = 13

IN_Boo = 37 # 14??
IN_Boo_F = 38

MASTER_INDEX = 0    # setting MASTER INDEX
Client_addr = list()

CO_critical_lock = Lock()
O2_critical_lock = Lock()
EM_critical_lock = Lock()

CO_value = 0.0
O2_value = 200.0
EM_value = 0
check_switch = 0

check_for_send = 0

client = list() 
client_thread = list()

index = 0
HOST_NAME = " TENT "
HOST = ""

def LED_level1_GPIO(pwm):	# setting LED level 1
    GPIO.output(IN1, True)
    pwm.ChangeDutyCycle(90)
    sleep(0.3)
    pwm.ChangeDutyCycle(30)

def LED_level2_GPIO(pwm):	# setting LED level 2
    GPIO.output(IN1, True)
    pwm.ChangeDutyCycle(90)
    sleep(0.3)
    pwm.ChangeDutyCycle(45)

def LED_level3_GPIO(pwm):	# setting LED level 3
    GPIO.output(IN1, True)
    pwm.ChangeDutyCycle(100)

def FAN_level1_GPIO(pwm):	# setting FAN_Speed low
    GPIO.output(IN2, True)
    pwm.ChangeDutyCycle(90)
    sleep(0.3)
    pwm.ChangeDutyCycle(30)

def FAN_level2_GPIO(pwm):	# setting FAN_Speed normal
    GPIO.output(IN2, True)
    pwm.ChangeDutyCycle(90)
    sleep(0.3)
    pwm.ChangeDutyCycle(45)

def FAN_level3_GPIO(pwm):	# setting FAN_Speed high
    GPIO.output(IN2, True)
    pwm.ChangeDutyCycle(90)

def Boozer_ON_GPIO():	# BOOZER ON
    #global IN_Boo
    GPIO.output(IN_Boo,True)
    
def Boozer_OFF_GPIO():	# BOOZER OFF
    #global IN_Boo
    GPIO.output(IN_Boo,False )
    
def cleanall(pwm1,pwm2):	# Stop all motion
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    sys.exit()

def thread_RX_TX(number): 	#Receive Control data from user
    global MASTER_INDEX
    global check_switch
    global check_for_send
    
    try :
        while True:
            
            #sleep(0.2)
            
            data = client[number].recv(4) 	# Receive 4 byte data.
            if len(data) < 2:
                continue
                
            
            enc_data = data.decode('utf-8')
            print("you have " , len(enc_data)," byte")
            print('socket '+str(number)+' receive '+ enc_data)
            
	# bit 1 : User[1] or Master[2] or EXIT[3]
	# bit 2 : LED[1] or FAN[2] or BOOZER[3]
	# bit 3 : Level of Power, Weakly[1] or Normaly[2] or Strong[3] or OFF[4]

            if enc_data[0] == '1':
                print('User mode ')
                if enc_data[1] == '1':
                    if enc_data[2] == '1':
                        # LED level 1 ON
                        LED_level1_GPIO(pwm_a)
                        print('turn ON LED level 1')
                    elif enc_data[2] == '2':
                        # LED level 2 ON
                        LED_level2_GPIO(pwm_a)
                        print('turn ON LED level 2')
                    elif enc_data[2] == '3':
                        # LED level 3 ON
                        LED_level3_GPIO(pwm_a)
                        print('turn ON LED level 3')
                    elif enc_data[2] == '4':
                        # LED OFF
                        GPIO.output(IN1, False)
                        print('turn OFF LED ')

                elif enc_data[1] == '2':
                    if enc_data[2] == '1':
                        # FAN level 1 ON
                        FAN_level1_GPIO(pwm_b)
                        print('turn ON FAN level 1')
                    elif enc_data[2] == '2':
                        # FAN level 2 ON
                        FAN_level2_GPIO(pwm_b)
                        print('turn ON FAN level 2')
                    elif enc_data[2] == '3':
                        # FAN level 3 ON
                        FAN_level3_GPIO(pwm_b)
                        print('turn ON FAN level 3')
                    elif enc_data[2] == '4':
                        # FAN OFF
                        GPIO.output(IN2, False)
                        print('turn OFF FAN ')

                elif enc_data[1] == '3':
                    if enc_data[2] == '1':
                        # Boozer ON
                        Boozer_ON_GPIO()
                        print('turn ON boozer')
                    elif enc_data[2] == '2':
                        # Boozer OFF
                        Boozer_OFF_GPIO()
                        print('turn OFF boozer')

            elif enc_data[0] == '2':
                MASTER_INDEX = number
                print('Master mode ')
                if enc_data[1] == '1':
                    if enc_data[2] == '1':
                        # turn on CO censor switch 
                        check_switch = 1
                        check_for_send = 1
                        print('turn ON sensor')
                        
                    elif enc_data[2] == '2':
                        # end check CO censor switch
                        check_switch = 0
                        print('turn OFF sensor')    

                if enc_data[1] == '2':
                    if enc_data[2] == '1':
                        # turn on FAN by MASTER
                        FAN_level3_GPIO(pwm_b)
                        print('TURN ON FAN BY MASTER')
                    elif enc_data[2] == '2':
                        # turn off FAN by MASTER
                        GPIO.output(IN2, False)
                        print('TURN OFF FAN BY MASTER')    
                    

            elif enc_data[0] == '3':
                print('client said -> Im EXIT! bye~ ')
                #sys.exit()


    except KeyboardInterrupt:
        #cleanall(pwm)
        print('error')

    client[number].close()

def EMERGENCY():    #Emergency situcation
    while True:
        global EM_value 
        
        EM_critical_lock.acquire()
        
        if EM_value == 1:	#if global variable EM_value == 1, it is emergency
            LED_level3_GPIO(pwm_a)
            FAN_level3_GPIO(pwm_b)
            Boozer_ON_GPIO()
            
            print(" EMERGENCY TIME !! " )
            while EM_value == 1:	#check EM_value while situation is over
                EM_critical_lock.release()
                sleep(3)		
                EM_critical_lock.acquire()

            GPIO.output(IN1, False)
            GPIO.output(IN2, False)
            Boozer_OFF_GPIO()
            print(" now ON SAFE !! ")
                    
        EM_critical_lock.release()
        sleep(1)

def checking_CO_thread(): 	#checking CO value in time ( thread )
			#using SPI 
    
    global check_switch 
    global CO_value
    mq = MQ(); 

    while True:
        perc = mq.MQPercentage()
        
        try:
            f_num = (perc["CO"])
        except:
            f_num = 0.0

        f_num = round(f_num,1)
        
        
        CO_critical_lock.acquire()
        
        if CO_value != f_num:
            CO_value = f_num
            if CO_value >= 9999.99:
                CO_value = 9999.99
            print('CO update ==> '+ str(CO_value));
            
        CO_critical_lock.release()
        
        
        sleep(0.3)
    
def checking_O2_thread(): 	#checking O2 value ( thread )
			#using UART serial communication
    sat.flushInput()
    sat.flushOutput()
    
    global check_switch 
    global O2_value
 
    while True:
        data = "O\r\n"  #give me data!
        
        sat.write(data)
        data = sat.readline()

        c_data = data[3:8]
        
        try:
            O2_critical_lock.acquire()
            if O2_value != float(c_data):
                O2_value = float(c_data)
                if O2_value < 100.0:
                    O2_value = 100.0
                print("O2 update ==> " + c_data)
                send_data = c_data[0:3]+c_data[4]   # 209.4 ==> 2094 ( 1~3rd = integral , 4 = down pointer )
                send_count = 1
            O2_critical_lock.release()
        except:
            O2_value = 200.0
            O2_critical_lock.release()

        sleep(0.3)
            
    sat.close()
    
def thread_Check_CO_O2():   #EMERGENCY state check
    while True:
    
        A_int = 0
        B_int = 0
        
        global CO_value
        global O2_value
        global EM_value 
        global check_switch 
        global send_data
        global MASTER_INDEX
        global Client_addr
        global check_for_send
        
        
        CO_critical_lock.acquire()
        
        if CO_value > 100.0:    # when high CO
            print("CAMP NAME ( "+ HOST_NAME +" ) IS now HIGH CO !!!!! ")
            
            data = "222222222\n" #EMERGENCY SIGNAL
            try:
                client[MASTER_INDEX].sendall(data)		#alram to master
            except:
                print(" there is no MASTER " )
            A_int = 1
            
        else:
            A_int = 0

        CO_critical_lock.release()




        O2_critical_lock.acquire()
        
        if O2_value < 195.0:     # low O2 ( under 195.0 = EMERGENCY ) 
            print("CAMP NAME ( "+ HOST_NAME +" ) IS now LOW O2!!!!! ")
            
            data = "222222222\n" #EMERGENCY SIGNAL
            try:
                client[MASTER_INDEX].sendall(data)
            except:
                print(" there is no MASTER " )
            B_int = 1
            
        else:
            B_int = 0
            
        O2_critical_lock.release()
        
        
        
        
        EM_critical_lock.acquire()
        
        if (A_int + B_int) > 0 :
            EM_value = 1
        else:
            EM_value = 0
        
        EM_critical_lock.release()
        
        s_data = ""
        ################################################
        if check_switch == 1:
            
            if CO_value >= 1000.0:
                s_data = str(int(CO_value/1)) + str(int((CO_value*10)%10)) + str(int(O2_value/1)) + str(int((O2_value*10)%10))
            elif CO_value >= 100.0:
                s_data = "0" + str(int(CO_value/1)) + str(int((CO_value*10)%10)) + str(int(O2_value/1)) + str(int((O2_value*10)%10))
            elif CO_value >= 10.0:
                s_data = "00" + str(int(CO_value/1)) + str(int((CO_value*10)%10)) + str(int(O2_value/1)) + str(int((O2_value*10)%10))
            elif CO_value >= 0.0:
                s_data = "000" + str(int(CO_value/1)) + str(int((CO_value*10)%10)) + str(int(O2_value/1)) + str(int((O2_value*10)%10))
            
            #if check_for_send == 1:    
            s_data = s_data+"\n"
            error_code_number = client[MASTER_INDEX].sendall(s_data)
            print("error_code_number", error_code_number)
            print("Master number", MASTER_INDEX, "addr", client[MASTER_INDEX].getpeername())
            
            #print("client call realtime\t")
            print(s_data)
                
            #   check_for_send = check_for_send + 1
        ################################################
        sleep(0.1)
        
PORT = 8088
#GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

#set 12pin output mode
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN1_F, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN2_F, GPIO.OUT)
GPIO.setup(IN_Boo, GPIO.OUT)
GPIO.setup(IN_Boo_F, GPIO.OUT)

#GPIO.setwanings(False)
pwm_a=GPIO.PWM(ENA,10)
pwm_b=GPIO.PWM(ENB,10)
pwm_a.start(10)
pwm_b.start(10)
GPIO.output(IN1, False)
GPIO.output(IN1_F, False)
GPIO.output(IN2, False)
GPIO.output(IN2_F, False)
GPIO.output(IN_Boo, False)
GPIO.output(IN_Boo_F, False)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
# To Socket communication

handle_EM = threading.Thread(target=EMERGENCY, args=())
handle_EM.start()
checkingCO2 = threading.Thread(target=thread_Check_CO_O2, args=())
checkingCO2.start()
ch_CO = threading.Thread(target=checking_CO_thread, args=())
ch_CO.start()
ch_O2 = threading.Thread(target=checking_O2_thread, args=())
ch_O2.start()

try:
    while True:
        (client_socket, addr) = server_socket.accept() #wait access
        client.append(client_socket)
        print('Connecting with', addr )

        client_thread.append( threading.Thread(target=thread_RX_TX, args=(index,)) )
        Client_addr.append(addr)
        client_thread[index].start()
        index = index + 1
except KeyboardInterrupt:
    cleanall(pwm_a,pwm_b)
    server_socket.close()
    for i in range(0,index):
        client[i].close
    sys.exit()
        
