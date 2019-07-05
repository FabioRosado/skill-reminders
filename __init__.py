import re
import arrow
import logging
from word2number import w2n

from opsdroid.skill import Skill
from opsdroid.matchers import match_regex, match_crontab
from opsdroid.events import Message

_LOGGER = logging.getLogger(__name__)


class Reminders(Skill):
    def __init__(self, opsdroid, config):
        super(Reminders, self).__init__(opsdroid, config)
        self.opsdroid = opsdroid
        self.config = config
        self.today = arrow.now('Europe/London')

    @staticmethod
    def get_weekday(message):
        """Get weekday from message"""
        message = re.sub(r"[^a-zA-Z]+", " ", message.lower()).split(' ')

        if 'monday' in message:
            return 0
        elif 'tuesday' in message:
            return 1
        elif 'wednesday' in message:
            return 2
        elif 'thursday' in message:
            return 3
        elif 'friday' in message:
            return 4
        elif 'saturday' in message:
            return 5
        elif 'sunday' in message:
            return 6
        else:
            return -1

    async def parse_days(self, message, time):
        try:
            days = w2n.word_to_num(time)
        except ValueError:
            days = re.findall(r'(in a day|tomorrow|next day)', time)
            if days:
                days = 1
            else:
                days = re.findall(r'\d', time)[0]

        await self.remind_in_x_days(message, int(days))

    async def parse_month(self, message, time):
        try:
            months = w2n.word_to_num(time)
        except ValueError:
            months = re.findall(r'(in a month|next month)', time)
            if months:
                months = 1
            else:
                months = re.findall(r'\d', time)[0]
          
        await self.remind_in_x_month(message, int(months))
        return months

    async def remind_in_x_days(self, message, number):
        """Add reminder in x days"""
        date = self.today.shift(days=+number)
        reminders = await self.opsdroid.memory.get('reminders')

        reminders[str(date.date())] = message

        await self.opsdroid.memory.put('reminders', reminders)

    async def remind_in_x_month(self, message, number):
        """Add reminder in x days"""
        date = self.today.shift(months=+number)
        reminders = await self.opsdroid.memory.get('reminders')
        reminders[str(date.date())] = message

        await self.opsdroid.memory.put('reminders', reminders)

    async def remind_on_date(self, message, date):
        """Add reminder to date"""
        reminders = await self.opsdroid.memory.get('reminders')
        reminders[str(date.date())] = message

        await self.opsdroid.memory.put('reminders', reminders)

    @match_regex(r'remind me of ([\w+|\d+\s+]+) ((in|tomorrow|next|today).*)', case_sensitive=False)
    async def remind_of(self, message):
        """Handle reminders logic"""
        reminders = await self.opsdroid.memory.get('reminders')
        if not reminders:
            await self.opsdroid.memory.put('reminders', dict())
        
        reminder = message.regex.group(1)
        time = message.regex.group(2)

        try:
            date = arrow.get(time, 'DD-MM-YYYY')
            await self.remind_on_date(reminder, date)

        except arrow.parser.ParserError:
            days = re.search(r'\bdays?\b', time)
            months = re.search(r'months?', time)
            today = re.search(r'today', time)

            if today:
                await self.remind_on_date(reminder, self.today)
            if days:
                await self.parse_days(reminder, time)

            if months:
                await self.parse_month(reminder, time)

        await message.respond(
            "Done added '{task}' to reminders {dt}".format(
                task=reminder, dt=time
            )
        )

    @match_regex(r'clear all reminders', case_sensitive=False)
    async def clear_reminders(self, message):
        reminders = dict()
        await self.opsdroid.memory.put('reminders', reminders)
        await message.respond("Done! All reminders are deleted.")

    @match_regex(r'show all reminders', case_sensitive=False)
    async def show_reminders(self, message):
        """Shows list of reminders"""
        reminders = await self.opsdroid.memory.get('reminders')
        await message.respond(
            "Okay, here is a list of all the reminders: \n\n {}".format(
                reminders
            ))

    @match_crontab('0 0 * * *', timezone='Europe/London')
    async def trigger_daily_reminder(self, message):
        """Trigger get reminders at midnight of everyday"""
        reminders = await self.opsdroid.memory.get('reminders')
        connector = self.opsdroid.default_connector
        room = connector.default_target
        message = Message("", None, room, connector)

        if self.today.date() in reminders.keys():

            await message.respond(
                "I've found a reminder for today: \n\n -{reminder}".format(
                    reminder=reminders[self.today.date()]))

            del reminders[str(self.today.date())]

            await self.opsdroid.memory.put('reminders', reminders)
