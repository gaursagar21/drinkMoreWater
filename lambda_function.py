import boto3
import twitter
import datetime
import pytz
import json
import random
import os


class DrinkMore:
    # Timezone
    timezone = os.getenv('DRINK_MORE_TIMEZONE')

    # Twitter keys
    consumer_key = os.getenv('DRINK_MORE_TWITTER_ACCESS_TOKEN_KEY')
    consumer_secret = os.getenv('DRINK_MORE_TWITTER_ACCESS_TOKEN_SECRET')
    access_token_key = os.getenv('DRINK_MORE_TWITTER_APP_ACCESS_TOKEN')
    access_token_secret = os.getenv('DRINK_MORE_TWITTER_APP_ACCESS_SECRET')

    # Message constants
    full = '🔵'
    empty = '⚪️'

    # dynamoDB table client
    table = None

    # eventbridge stuff
    eb_rule_name = os.getenv('DRINK_MORE_EB_RULE')

    # Scheduling Related Constants
    # 8am IST = 2:30am GMT
    posting_window_start = [8, 13, 18]
    # Rest after cutoff_hour
    cutoff_hour = 22
    hour_window = 4
    current_time = datetime.datetime.now(pytz.timezone(timezone))
    current_hour = current_time.hour

    # GMT Correction for cron
    gmt_correction = 5

    # Water Related stuff
    max_water = 15
    start_of_day = 8
    '''Glasses of hour so far:
    f(water) = (current_hour - 8)
    Drink 1 glass water every hour from 8am to 11pm
    for a total of 15 glasses, 3.7l or 1 gallon
    '''
    water_consumed = current_hour - start_of_day
    water_left = max_water - water_consumed
    printable_time = current_time.strftime('%-I:%M %p')
    printable_hour = current_time.strftime('%-I %p')

    def __init__(self):
        pass

    def getNextScheduledHour(self):
        next_hour = 7
        for i in self.posting_window_start:
            if i - self.current_hour >= 0:
                next_hour = i
                break

        next_scheduled_hour = random.randint(0, 5) + next_hour
        print("Next scheduled hour before GMT Correction:" + str(next_scheduled_hour))
        return next_scheduled_hour - self.gmt_correction

    def updateEventBridgeRule(self):
        cwevents = boto3.client('events')

        minute = random.randint(0, 59)

        schedule_expression = 'cron({minute} 2 * * ? *)'.format(minute=minute)

        if self.current_hour + self.hour_window <= self.cutoff_hour:
            hour = self.getNextScheduledHour()

            schedule_expression = 'cron({minute} {hour} * * ? *)'.format(
                minute=minute,
                hour=hour
            )
        cwevents.put_rule(
            Name=self.eb_rule_name,
            ScheduleExpression=schedule_expression
        )
        return schedule_expression

    def getTwitterAPI(self):
        self.twitterAPI = twitter.Api(consumer_key=self.consumer_key,
                                      consumer_secret=self.consumer_secret,
                                      access_token_key=self.access_token_key,
                                      access_token_secret=self.access_token_secret)
        return self.twitterAPI

    def postToTwitter(self, message):
        # print(message)
        self.getTwitterAPI().PostUpdate(message)

    def generateTweetText(self):
        waterRelatedText = []

        # 1
        message = "It's {printable_time}  🕰, you should have drank {water_consumed}"\
            " glasses of water so far.".format(
                printable_time=self.printable_time,
                water_consumed=self.water_consumed
            )
        waterRelatedText.append(message)

        # 2
        message = "If you are at less than {water_consumed} glasses at"\
            " {printable_hour} you are dehydrated. 🥤".format(
                water_consumed=self.water_consumed,
                printable_hour=self.printable_hour
            )
        waterRelatedText.append(message)

        # 3
        message = "Your ancestors were fish 🐠 and you can't drink {water_consumed} "\
            "glasses?"\
            """
            """\
            "Shame on you -_+".format(
            water_consumed=self.water_consumed
        )
        waterRelatedText.append(message)

        # 4
        message = "Only {water_left} more glasses before you go to sleep! 💤".format(
            water_left=self.water_left
        )
        waterRelatedText.append(message)

        # 5
        message = "My skin thanks me for drinking {water_consumed} glasses 💁🏻.".format(
            water_consumed=self.water_consumed
        )
        waterRelatedText.append(message)

        # 6
        message = "Drink up sunflower 🌻. It's only {printable_hour}. You need {water_left} glasses more!".format(
            water_left=self.water_left,
            printable_hour=self.printable_hour
        )
        waterRelatedText.append(message)

        # 7
        message = "How many glasses today 🤨? {water_consumed}? Chug more!".format(
            water_consumed=self.water_consumed,
        )
        waterRelatedText.append(message)

        # 8
        message = "Thousands have lived without love not one without water 🪴"
        waterRelatedText.append(message)

        # 9
        message = "Everyday I'm guzzling 😎."
        waterRelatedText.append(message)

        # 10
        message = "psst. how's your water drinking going? 🐙"
        waterRelatedText.append(message)

        # 11
        message = "No you aren't hungry you are dehydrated 🦆! Drink {water_left} more glasses!".format(
            water_left=self.water_left
        )
        waterRelatedText.append(message)

        # 12
        message = "I look this good because I drink water. 🐧"
        waterRelatedText.append(message)

        # 13
        message = "Stressed 😓? Take a shot of water. 🐶"
        waterRelatedText.append(message)

        # 14
        message = "1 minute until this event: Drink glass # {water_left} of water. 🙆🏻".format(
            water_left=self.water_left
        )
        waterRelatedText.append(message)

        # 15
        message = "If you drink a gallon of water everday, you won't have time for other people's drama because you'll be too busy peeing. 👆🏻"
        waterRelatedText.append(message)

        # Final Message
        tweet = random.choice(waterRelatedText) + """

      """ + self.full * self.water_consumed + self.empty * self.water_left

        return tweet

    def canTweet(self):
        if self.water_consumed <= 1 or self.water_left <= 0 or self.water_consumed >= self.max_water:
            return False
        if self.current_hour >= self.cutoff_hour or self.current_hour <= self.start_of_day:
            return False
        return True


def lambda_handler(event, context):
    """Entrypoint
    - update event bridge schedule
    - quit by a probability of 1/4
    - generate a tweet worthy post
    - tweet it
    """
    drink_more = DrinkMore()

    newSchedule = drink_more.updateEventBridgeRule()

    if not drink_more.canTweet():
        msg = "Not Tweeting. Will try next time." + newSchedule
        print(msg)
        return {
            'statusCode': 200,
            'body': json.dumps(msg)
        }

    tweetText = drink_more.generateTweetText()
    drink_more.postToTwitter(tweetText)
    print("Ending. " + tweetText + newSchedule)
    return {
        'statusCode': 200,
        'body': json.dumps(tweetText + newSchedule)
    }


# zip -g my-deployment-package.zip lambda_function.py
