import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class send_mail:
    def __init__(self):
        self.fileName=''
        
    def send(self,fileName):
        attach = MIMEApplication(open(fileName,"rb").read())
        attach.add_header('Content-Disposition', 'attachment', filename=fileName)
        body = MIMEText("automatically generated message with the differences in the prices of B & H and Electricavenue's Magento \n file has the following structure :\n \t date,mfr,code,name,BHspecial_price,BHprice,ShowType,BHprice_rebate,BHdate_rebate,magentoEspecialPrice,magentoPrice \nQuestions, consult the administrator")
        msg = MIMEMultipart()
        msg['Subject'] = 'PH Magento comparation'
        msg['From'] = 'cespinosadelosmonteros@gmail.com'
        msg['To'] = 'cespinosadelosmonteros@gmail.com'
        msg.attach(body)
        msg.attach(attach)
        username = 'cespinosadelosmonteros@gmail.com'
        password = '@5M0K137'
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(username,password)
        s.sendmail('cespinosadelosmonteros@gmail.com', ['cespinosadelosmonteros@gmail.com','Guillermo@electricavenue.net','raymond@electricavenue.net'], msg.as_string())
        s.quit()
