import smtplib, ssl, traceback

def send_mail(sender_email = "patelkarm077@gmail.com",password = "Karma@216",
              receiver_email = "karmpatel216@gmail.com",message = "Hello Karm\nTesting"):
    '''
    Before using this app, make sure you have give permission
    for less secured app in your google account.
    :param sender_email:
    :param password:
    :param receiver_email:
    :param message:
    :return:
    '''
    try:
        port = 465  # For SSL
        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            print("mail sent!")
    except Exception as e:
        print("*****Something is wrong in sending a mail*****")
        traceback.print_exc()