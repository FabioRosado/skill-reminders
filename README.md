# opsdroid skill reminders

This is a reminder skill for [opsdroid](https://github.com/opsdroid/opsdroid), add **one** reminder per day and you will get notified at midnight for it..

## Requirements

- word2number
- database set up in opsdroid config

## Configuration

```yaml
- name: reminders
```

## Usage

#### `remind me of <reminder> <date>`

Adds reminder to the list. Date can be in date format like _12-01-2000_ or you can type when, for example (in a day, tomorrow, next month, in 5 days)

> user: remind me of things in 12-01-2019
>
> opsdroid: Done added 'things' to reminders in 12-01-2019

> user: remind me of things in a day
>
> opsdroid: Done added 'things' to reminders in a day

> user: remind me of things today
>
> opsdroid: Done added 'things' to reminders today

> user: remind me of things in two months
>
> opsdroid: Done added 'things' to reminders in two months

#### `show all reminders`

Shows all reminders saved on to the database

> user: show all reminders
>
> opsdroid: Okay, here is a list of all the reminders:
>
>           {'2019-07-03': 'to do things', '2019-07-05': 'things', '2019-07-06': 'music', '2019-08-02': 'phone', '2019-09-02': 'blahblah', '2019-07-02': 'things'}

#### `clear all reminders`

Clears all reminders from the database


> user: clear all reminders
>
> opsdroid: Done! All reminders are deleted.

#### `Cronjob - daily at midnight`

Shows reminders for today and removes it from the database.

_Note: If you would like to get details from all partitions let me know and I'll add it._

> opsdroid: I've found a reminder for today:
>
>
> Water plants