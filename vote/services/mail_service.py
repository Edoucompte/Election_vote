from django.core.mail import send_mail

class MailService:
    def sendMail(subject, body, from_, to):
        '''
            - to: is a list
        '''
        send_mail(
            subject= subject,#'Welcome to our platform!',
            message= body, #'Thank you for registering.',
            from_email= from_, # 'noreply@example.com',
            recipient_list=to,
            fail_silently=False,
        )