class CalUser:

    def __init__(self):
        """
        Calculate relative time functions and initiate the class.
        """
        import datetime as dt
        import dateutil as du
        from dateutil import relativedelta

        #Initial date calculations
        self.right_now = dt.datetime.utcnow()
        self.beginDelta = -2
        self.endDelta = 365
        self.timeDeltaCashBegin = du.relativedelta.relativedelta(months=self.beginDelta)
        self.timeDeltaCashEnd = dt.timedelta(days=self.endDelta)
        self.begin_date = self.right_now + self.timeDeltaCashBegin
        self.end_date = self.right_now + self.timeDeltaCashEnd

        #today's date to initialize the Cash event
        self.today_date = str(dt.datetime.date(self.right_now))

        #time variable for event creation // included date list to decipher cash update days
        self.create_begin = dt.datetime.fromisoformat(self.right_now.date().isoformat()).isoformat() + 'Z'
        self.create_end = self.end_date.isoformat() + 'Z'
        self.create_duration = (self.end_date - self.right_now).days
        self.iterate_days = self.iterateList(self.create_duration)

        #time variables used in deletion code
        self.clear_begin = self.begin_date.isoformat() + 'Z'
        self.clear_end = self.end_date.isoformat() + 'Z'

        #Smaller size for event creation/deleting testing
        self.test_duration = 40
        self.test_days = self.iterateList(self.test_duration)
        
        #Store old event list to check if changes need to be made
        self.check_for_updates = []
        self.cash_history = []

        self.creds = self.getUsrCreds()
        self.service = self.buildAPICal(self.creds)
        self.usrCals = self.getUsrCals(self.service)

        #Check if Calendar is Present and get the details -- if not, build one
        if self.checkCashCal(self.usrCals) == False:
            self.usr_csh_id, self.usr_csh_cal = self.buildCashCal(self.usrCals)
        else:
            self.usr_csh_id = self.getCshID(self.usrCals)
            self.usr_csh_cal = self.getCshCal(self.usrCals)

    def iterateList(self, numDays):
        """
        Create working List of days.
        """
        import dateutil as du
        self.daysList = []
        for pull_date in range(numDays):
            self.daysList.append(str((self.right_now + du.relativedelta.relativedelta(days=pull_date)).date()))
        return self.daysList

    def getUsrCreds(self):
        """
        Authenticate Application for User's Calendar.
        """
        import pickle
        import os.path
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as self.token:
                self.creds = pickle.load(self.token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', scopes = SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as self.token:
                pickle.dump(self.creds, self.token)

        return self.creds

    def buildAPICal(self, credentials):
        """
        Construct a resource for API interaction.
        """
        from googleapiclient.discovery import build
        return build('calendar', 'v3', credentials=self.creds)

    def checkCashCal(self, usrCals):
        """
        Check if Cash Calendar is already present.
        """
        self.check_cal = False
        for calen in usrCals['items']:
            if 'Cash Flow' in calen['summary']:
                self.check_cal = True
        return self.check_cal

    def buildCashCal(self, usrCals):
        """
        Create Calendar and insert into user's active calendars.
        """
        self.csh_flw_id = ''
        cash_cal = {
            'summary': 'Cash Flow',
            'timeZone': 'America/New_York'
        }
        self.csh_flw_cal = self.service.calendars().insert(body=cash_cal).execute()
        self.csh_flw_id = self.csh_flw_cal['id']
        return self.csh_flw_id, self.csh_flw_cal

    def getUsrCals(self, service):
        """
        Get user's calendar list.
        """
        return self.service.calendarList().list().execute()

    def getCshID(self, usrCals):
        """
        Get existing Cash Calendar's ID.
        """
        assert self.checkCashCal(self.usrCals) is True
        for calen in usrCals['items']:
            if 'Cash Flow' in calen['summary']:
                return calen['id']
    
    def getCshCal(self, usrCals):
        """
        Get existing Cash Calendar.
        """
        assert self.checkCashCal(self.usrCals) is True
        for calen in usrCals['items']:
            if 'Cash Flow' in calen['summary']:
                return calen