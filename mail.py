from email.mime.text import MIMEText
import smtplib
from mail_config import *  

def SendEmail(t): 
	mailserver=smtplib.SMTP(smtpserver,587);
	mailserver.login(sender,passcode);
	mes=MIMEText(t,'plain','utf-8');
	mes['Subject']='Arxiv Paper';
	mes['From']=sender;
	mes['To']=receiver;
	mailserver.sendmail(sender,[receiver],mes.as_string());
	mailserver.quit();

if __name__ == "__main__":
	SendEmail("Test")