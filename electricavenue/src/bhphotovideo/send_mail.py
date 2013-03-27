# Import smtplib for the actual sending function
import smtplib

from email.mime.multipart import MIMEMultipart
# Import the email modules we'll need
from email.mime.text import MIMEText
from MimeWriter import MimeWriter
from email.MIMEBase import MIMEBase
from email import Encoders
from email.mime.application import MIMEApplication
# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
#fp = open('2013-03-25CanonCameras.csv', 'rb')
## Create a text/plain message
#attach = MimeWriter(fp.read())
#fp.close()
class send_mail:
    def __init__(self):
        self.fileName=''
        
    def send(self,fileName):
        attach = MIMEApplication(open(fileName,"rb").read())
        attach.add_header('Content-Disposition', 'attachment', filename=fileName)
        
        
        
        body = MIMEText("automatically generated message with the differences in the prices of B & H and Electricavenue's Magento \n file has the following structure :\n \t date,mfr,code,name,BHspecial_price,BHprice,ShowType,BHprice_rebate,BHdate_rebate,magentoEspecialPrice,magentoPrice \nQuestions, consult the administrator")
        
        
        
        
        msg = MIMEMultipart()
        # me == the sender's email address
        # you == the recipient's email address
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
        s.sendmail('cespinosadelosmonteros@gmail.com', ['cespinosadelosmonteros@gmail.com','raymond@electricavenue.net'], msg.as_string())
        s.quit()


