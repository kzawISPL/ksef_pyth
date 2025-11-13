from sdk import KSEFSDK

K = KSEFSDK()
print(K.challenge, K.timestamp)
K.session_terminate()
