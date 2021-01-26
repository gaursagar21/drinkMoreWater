

# drinkMoreWater 🔵
Code for twitter bot [@_drink_more](https://twitter.com/_drink_more)


I created this bot after failing multiple times to get used to water reminder apps. The fact they are periodic prevents them from being habit-forming.


There are several reminders on my phone for sleep, exercise, drinking water, and whatnot. I've learned to ignore all of them. I anticipate the buzzing of my phone and then not do anything about the reminder. More than that, to even my surprise I go long periods without looking into my phone.

A more random reminder should be more difficult to learn to ignore (I hope).

## How it works?
At its core, the script uses Twitter API to make a tweet.

The tweet is one of the templates I've defined in code. 
e.g. `"Only {water_left} more glasses before you go to sleep!"`

The glasses of water to drink are linearly calculated based on the following conditional function:
```python
if hour_of_the_day >= 8:
  water_consumed = hour_of_the_day - 8 #to simulate an 8am start of the day
  water_left = 15 - water_consumed
```

The waking hours are between 8 am to 11 pm. With one glass of water every hour that's 15 glasses (3.7 liters or a gallon) of water.

### Water Graph
Each tweet has a visual made of emojis to show how many glasses of water should have been consumed at the time of the post. I use 🔵 to indicate progress, and ⚪️ for the remaining day (or glasses of water).

🔵🔵🔵🔵🔵🔵⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️ 2 pm, or 6 glasses.

🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵⚪️⚪️⚪️ 8 pm, or 12 glasses.



### Scheduling the Tweets
The code is executed through an AWS lambda function. The lambda is triggered through AWS Event Bridge.

Event Bridge has the functionality to trigger based on a cron schedule. That's what I've used. 

- The lambda is trigerred at 8am IST `cron(0 3 * * ? *)`. 
- During it's run the lambda updates an Event Bridge rule to trigger anytime in the next 5 hour window
 `cron(random(0-59) current_hour+random(0-4) * * ? *)`. 
- I've divided the day into 3 5-hour windows `9 am to 12 pm`, `1 pm to 6 pm` and finally `7 pm to 11 pm`.
- When the lambda is triggered in the last window, it resets the Eventbridge rule to trigger the next day at 8 am.

PS. The bot tweets in my timezone (IST)


## How to Run?
This code won't be enough to create a similar bot. Some setup of AWS features, as well as registering for a Twitter developer account would be required to run it properly.

I ended up using to use `IAM`, `Lambdas`, `Event Bridge`, `python-twitter`.

As for why I used these services? These are all  AWS forever free tier services.

Using EC2 was also an option, but that doesn't stay free after 12 months.

I originally wanted to use the Heroku scheduler. Although the scheduler is free, it requires `dynos` which aren't free. (There's a $20 hole in my pocket for not realizing that in the past).
