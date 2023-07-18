from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

import client
import json



startHistoryId = data['historyId']

######################################################################################
#                        (print token for debugging purposes)                        #
######################################################################################
client.delegated_credentials.refresh(Request())

print(client.delegated_credentials.token)


######################################################################################
#                                SYNC        MAILBOX                                 #
######################################################################################

