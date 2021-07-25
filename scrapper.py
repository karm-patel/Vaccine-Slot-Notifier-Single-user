import time
import pytz
import json
import requests
import os
from datetime import datetime
import traceback
from sendGmail import send_mail


class VaccineSlot:

    def __init__(self,data):
        '''
        :param data: ["by_district", "district_id", "pin", "min_age"]:
        '''
        self.data = data
        if data["by_district"] == 1:
            self.dist_id = data["district_id"]

    def get_available_slots(self,interest):
        today = datetime.today().date()
        day = str(today.day)
        month = str(today.month)
        year = str(today.year)
        day = day if len(day) == 2 else "0"+day
        month = month if len(day) == 2 else "0"+month

        date = day + "-" + month + "-" + year
        if self.data["by_district"] == 1:
            self.url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={self.dist_id}&date={date}"
        else:
            pin = self.data["pin"]
            self.url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pin}&date={date}"

        proxies = {
         "http": "http://14.140.131.82:3128",
         "https": "http://14.140.131.82:3128"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}
        available = {}

        try:
            resp = requests.get(self.url, headers=headers).content
            resp = resp.decode('utf-8')
            resp = resp.replace("true", "True")
            resp = resp.replace("false", "False")
            resp = eval(resp)

            #print("responce:", type(resp),resp,)
            all_centers = resp['centers']

            if len(all_centers) > 0:
                district_name =  resp["centers"][0]["district_name"]
            min_age = self.data['min_age']
            #print("age=",min_age)

            for each in all_centers:
                center_name = each["name"].strip()
                present = 0
                matches = sum([int(each in center_name.lower()) for each in interest])
                if matches and each['sessions']:
                    for sess in each['sessions']:
                        #print(sess)

                        if sess["available_capacity_dose2"]>=2:
                            data = {"available_capacity_dose2": sess["available_capacity_dose2"]
                                , "date": sess["date"]}
                            if center_name not in available:
                                available[center_name] = [data]
                            else:
                                available[center_name].append(data)
                        elif sess["available_capacity"] >= 2:
                            data = {"available_capacity": sess["available_capacity"]
                                , "date": sess["date"]}
                            if center_name not in available:
                                available[center_name] = [data]
                            else:
                                available[center_name].append(data)

                            #print("available!")
        except Exception as e:
            traceback.print_exc()
            return [e,"error"]


        return [available,district_name]

UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

def format_slots(slots):
    formatted = ""
    for each in slots:
        formatted = "\n" + formatted + each + "\n"
        formatted += str(slots[each]) + "\n"
    return formatted


current_path = os.getcwd()
with open(os.path.join(current_path,"district_ids.json"), "r") as fp:
    district_ids = json.load(fp)

with open("input.txt","r") as fp:
    state, district,keywords, age, email = [each.strip() for each in fp.readlines()]
    keywords = keywords.split(" ")
    print(keywords)

with open("email_pass.txt","r") as fp:
    sender_email,password = [each.strip() for each in fp.readlines()]
    #print(sender_email,password)


waiting_time = 1
continuous_sent = 0
minitue_flag = 1
while True:

    district_id = district_ids[state][district]
    data = {"by_district":1, "district_id":district_id,"pin":"0","min_age":age}
    obj = VaccineSlot(data)


    print(f"{datetime.now(IST)} - {email}")

    slots,dist_name = obj.get_available_slots(interest=keywords)
    if district == "error":
        send_mail(message=f"Karm!, I can not scrape the slots, Something is wrong, Can you please check "
                          f"it?\n{slots}",receiver_email=email,sender_email=sender_email,password=password)
        time.sleep(60*waiting_time)
        waiting_time*=1.5
        continuous_sent+=1
    elif slots != {}:
        send_mail(message=f"Run Karm!, Book your slot in {district}!\n{slots}",receiver_email=email,
                  sender_email=sender_email,password=password)
        continuous_sent+=1

    if minitue_flag and datetime.now().minute == 0:
        send_mail(message=f"Karm, I'm alive, Chill !!", receiver_email=
        "karmasmart216@gmail.com", sender_email=sender_email, password=password)
        minitue_flag = 0
    if datetime.now().minute > 0:
        minitue_flag = 1

    time.sleep(5)



    print("*********************************")

