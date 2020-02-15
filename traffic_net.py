from io import open
import requests
import shutil
from zipfile import ZipFile
from imageai.Prediction.Custom import ModelTraining, CustomImagePrediction
import os
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import cv2
import geocoder
from geopy.geocoders import Nominatim


def location():
    g = geocoder.ip('me')
    geolocator = Nominatim(user_agent="locator")
    location = geolocator.reverse(g.latlng)
    return(location.address)


def mail(prediction,path):
    fromaddr = "whitehatersalertservice@gmail.com"
    toaddr = "c.viswaharsha@gmail.com"
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Alert"
    body = prediction
    msg.attach(MIMEText(body, 'plain')) 
    filename = "Capture.jpg"
    attachment = open(path, "rb")
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, "srec@123") 
    text = msg.as_string() 
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


execution_path = os.getcwd()
SOURCE_PATH = "https://github.com/OlafenwaMoses/Traffic-Net/releases/download/1.0/trafficnet_dataset_v1.zip"
FILE_DIR = os.path.join(execution_path, "trafficnet_dataset_v1.zip")
DATASET_DIR = os.path.join(execution_path, "trafficnet_dataset_v1.zip")


def download_traffic_net():
    if (os.path.exists(FILE_DIR) == False):
        print("Downloading trafficnet_dataset_v1.zip")
        data = requests.get(SOURCE_PATH,
                            stream=True)

        with open(FILE_DIR, "wb") as file:
            shutil.copyfileobj(data.raw, file)
        del data

        extract = ZipFile(FILE_DIR)
        extract.extractall(execution_path)
        extract.close()


def train_traffic_net():
    download_traffic_net()

    trainer = ModelTraining()
    trainer.setModelTypeAsResNet()
    trainer.setDataDirectory("trafficnet_dataset_v1")
    trainer.trainModel(num_objects=4, num_experiments=200, batch_size=32, save_full_model=True, enhance_data=True)

def run_predict():
    predictor = CustomImagePrediction()
    predictor.setModelPath(model_path="trafficnet_resnet_model_ex-055_acc-0.913750.h5")
    predictor.setJsonPath(model_json="model_class.json")
    predictor.loadFullModel(num_objects=4)
    count=0
    #path="images/1.jpg"
    videoCaptureObject = cv2.VideoCapture(0)
    ret,frame = videoCaptureObject.read()
    cv2.imwrite("Capture.jpg",frame)
    path="Capture.jpg"
    videoCaptureObject.release()
    cv2.destroyAllWindows()
    predictions, probabilities = predictor.predictImage(image_input=path, result_count=4)
    
    
    for prediction, probability in zip(predictions, probabilities):
           if(probability > 75 ):
              print(prediction,": ",int(probability),"%")
              loc = location()
              predloc="Incident:"+prediction+"\n"+"Location:"+loc
              mail(predloc,path)
           else:
              count=count+1
    if(count>3):
        print('NormalFlow')
        

      
#train_traffic_net()
i=0
while(i<5):
    run_predict()
    i=i+1
    
 
