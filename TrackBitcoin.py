import requests
import time
import sys
import smtplib
import os
from time import localtime,strftime

def get_recievers():
    f = open("recievers.txt","r")
    return(f.readlines())

def send_email(body,subject,reciever,email,password):
     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        print("\nEstablishing connection with google servers")
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        print("Secure connection to google servers is achieved")

        smtp.login(email,password)

        msg = f'Subject: {subject}\n\n{body}'
        
        for i in reciever:
            smtp.sendmail(email, i, msg)

def special_log(log_msg,sp_file):
    special = open(sp_file,"w+")
    special.write(log_msg)
    special.close()

def get_price():
    r = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    return r.json()['time']['updateduk'],r.json()['bpi']['GBP']['rate_float'],r.json()['bpi']['GBP']['rate']

def get_str_time():
    a=(strftime("%H-%M-%S %d-%m-%Y", localtime()))

    return str(a)

def get_current_time():
    a=(strftime("%H", localtime()))
    b=(strftime("%M", localtime()))
    c=(strftime("%S", localtime()))

    return str(a+b+c)

def logg(log_msg,file_name):
     loggs = open(file_name,"a")
     loggs.write(log_msg)
     loggs.close()

try:
    os.mkdir("Logs")
except(FileExistsError):
    print("File 'Logs' allready exists")
    
email = "bitcoin.updater.bot@gmail.com"
password = "124816Binary"


rate = get_price()

rate_str = rate[2]
rate_float = rate[1]

highest_today = rate_float
lowest_today = rate_float

highest_today_str = rate_str
lowest_today_str = rate_str

net_error_count = 0
new_error_count = 0

last_price = 0
today_count = 0
today_cost = 0

while True:
    try:
        sp_file = "Logs/special_event_logs.txt"
        file_name = "Logs/logs " + strftime("%d-%m-%Y", localtime())+".txt"
        reciever = get_recievers()
        rate = get_price()
        
        rate_str = rate[2]
        rate_float = rate[1]
        rate_time = rate[0]

        str_time = get_str_time()
        current_time = get_current_time()
        current_price = rate_float
        
        today_cost = today_cost + current_price
        today_count = today_count + 1
        average_today = today_cost/today_count

        extra = ""
        e_exception = False

        



        if current_price != last_price:
            
            if current_price > highest_today:
               
                highest_today = current_price
                highest_today_str = rate_str

                extra = "\n\nNew highest price " + str(highest_today_str)

            elif current_price < lowest_today:
                
                lowest_today = current_price
                lowest_today_str = rate_str

                extra = "\n\nNew lowest price " + str(lowest_today_str)
            
            log_msg = "\n\n\n" + rate_time + " *** Bitcoin price is: £" + rate_str + " *** Highest Today:" +str(highest_today_str)+ " *** Lowest Today:" +str(lowest_today_str) + extra
            logg(log_msg,file_name)
            print(log_msg)
            

            if current_price > last_price:
                r = current_price - last_price
                percent = round((r/last_price)*100,2)

                if percent > 10:
                    body = str(rate_time)+"The bitcoin price has risen by " + str(percent) + "!\nIt was :" + str(last_price) + "\nCurrent price: " + str(current_price)
                    subject = "BITCOIN RISES BY:" + str(percent)                    
                    send_email(body,subject,reciever,email,password)
                    log_msg = body + " *** Email Sent"
                    special_log(log_msg,sp_file)

                else:
                    print("small chage " +str(percent))
                
            else:
                r = last_price - current_price
                percent = round((r/last_price)*100,2)

                if percent > 10:
                    body = str(rate_time)+"The bitcoin price has droped by " + str(percent) + "!\nIt was :" + str(last_price) + "\nCurrent price: " + str(current_price)
                    subject = "BITCOIN DROPS BY:" + str(percent)                    
                    send_email(body,subject,reciever,email,password)
                    log_msg = body + " *** Email Sent"
                    special_log(log_msg,sp_file)

                else:
                      print("small chage " +str(percent))
                    

            

        if  current_time == "000000":
            time.sleep(2)
            
            rang = highest_today-lowest_today
            rang = round(rang,4)
            average_today = round(average_today,4)
            
            subject = "Bitcoin Bot Daily Summary"
            body = "Here is the summary of bitcoin prices today:\n\nThe lowest cost today: " +str(lowest_today_str) + " pounds.\nThe highest was: " +str(highest_today_str) + " pounds.\nAverage today: " +str(average_today) + " pounds.\nPrice range: " + str(rang) + " pounds."
            send_email(body,subject,reciever,email,password)
            today_cost = 0
            today_count = 0
            


        if current_time == "120000":
            time.sleep(2)
            
            rang = highest_today-lowest_today
            rang = round(rang,4)
            average_today = round(average_today,4)
            
            subject = "Bitcoin Bot 12pm Price Update"
            body = "Here is the summary of bitcoin prices today:\n\nThe lowest cost today: " +str(lowest_today_str) + " pounds.\nThe highest was: " +str(highest_today_str) + " pounds.\nAverage today: " +str(average_today) + " pounds.\nPrice range: " + str(rang) + " pounds."
            send_email(body,subject,reciever,email,password)


        last_price = current_price


    except Exception as e:
        if today_count == 1:
            last_price = current_price

        else:
            if net_error_count < 21:
                x = 60
            else:
                x = 120
                if  e_exception == False:

                    subject = str(str_time) + " Something is preventing the bot from working"
                    body = str(str_time) + " Unknown error has casued an exeption, after trying for 20 minutes the issue haven't being resolved. Retrying every 2 minutes.\n\n\nQuote of the exception: " + str(e)
                    send_email(body,subject,reciever,email,password)
                    log_msg = str(str_time) + " An Email was sent quoting the folowing exception: " + str(e)
                    special_log(log_msg,sp_file)
                    e_exception == True
                else:
                    print("email aready sent")
                    
            
            log_msg = str(str_time) + " Some error prevented the programm from working properly. Trying again in " + str(x) + " seconds"
            print(log_msg)
            print(e)
            logg(log_msg,file_name)
            net_error_count = net_error_count + 1

            time.sleep(x)
           
        
        
        
       
sys.exit()



    






        
        
                   
        
        
        
        
    

    

        
    











 
