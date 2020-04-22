import logging

import discord
from discord.ext.commands.view import StringView
from discord.ext import commands
from datetime import datetime, timedelta

from pymongo import MongoClient

DATE_MSG = (
    "lunes", 
    "martes", 
    "miercoles", 
    "jueves", 
    "viernes", 
    "sabado", 
    "domingo")

TIME_MSG = (
    "am", 
    "pm")

logger = logging.getLogger("root")


class AnimalCrossing(commands.Cog):

    def __init__(self):
        self.client = MongoClient(
            'mongo',
            username='root',
            password='password')

        self.db = self.client.get_database("animal_crossing")


    async def show_info(self, ctx: commands.Context, tags):
        logger.debug("AC:")
        logger.debug("  author: " + str(ctx.author))
        logger.debug("  channel: " + str(ctx.channel))
        logger.debug("  guild: " + str(ctx.guild))
        logger.debug("  me: " + str(ctx.me))

        for i in range(len(tags)):
            logger.debug("   arg[" + str(i) + "]: " + tags[i])

    async def get_data(
            self, 
            ctx: commands.Context, 
            target: discord.Member, 
            year: int, week: int):
        logger.debug("get_data:")
        logger.debug("  target: " + str(target))
        logger.debug("  date: " + str(year) + " " + str(week))

        week_data = self.db["stalk_market"].find_one({
            "user": str(target),
            "year": year,
            "week": week
        })

        logger.debug("  result: " + str(week_data))

        if week_data is not None:
            await ctx.send("```" + str(week_data) + "```")

    async def get_plot(
            self, 
            ctx: commands.Context, 
            target: discord.Member, 
            year: int, week: int):
        logger.debug("get_plot:")
        logger.debug("  target: " + str(target))
        logger.debug("  date: " + str(year) + " " + str(week))

    async def update_data(
            self, 
            ctx: commands.Context, 
            target: discord.Member, 
            year: int, week: int, day: int, time: int,
            cant: int):

        logger.debug("update_data:")
        logger.debug("  target: " + str(target))
        logger.debug("  date: " + str(year) + " " + str(week))
        logger.debug("  time: " + str(day) + " " + str(time))
        logger.debug("  cant: " + str(cant))

        week_data = self.db["stalk_market"].find_one({
            "user": str(target),
            "year": year,
            "week": week
        })
        
        if week_data is None:
            logger.debug("  creating!")
            self.db["stalk_market"].insert({
                "user": str(target),
                "year": year,
                "week": week,
                "data": {
                    "d" + str(day) + "-" + str(time) : cant
                }
            })
            week_data = self.db["stalk_market"].find_one({
                "user": str(target),
                "year": year,
                "week": week
            })
        else:
            logger.debug("  updating!")
            self.db["stalk_market"].find_one_and_update(
                {
                    "user": str(target),
                    "year": year,
                    "week": week
                },
                {"$set": {"data.d" + str(day) + "-" + str(time): cant}}
                )
        await ctx.send("```" + str(week_data) + "```")

    def get_target(self, ctx: commands.Context, member_info, default_result=None):
        logger.debug("get_target:")
        logger.debug("  info:" + str(member_info))
        targets = [
            member for member in ctx.channel.members if (
                member_info.lower() in member.display_name.lower()
                ) or (
                    str(member.id) in member_info)]

        if(len(targets) != 1):
            # couldnt find target
            logger.debug("  GAAHH " + targets)
            return default_result

        logger.debug("  found: " + str(targets[0]))
        return targets[0]
    
    def get_date(self, timestamp: datetime):
        logger.debug("get_date:")
        logger.debug("  timestamp: " + str(timestamp))
        iso_week = timestamp.isocalendar()

        save_year = iso_week[0] if iso_week[2] < 7 else (
            timestamp + timedelta(days=7)).isocalendar()[0]
        save_week = iso_week[1] if iso_week[2] < 7 else (
            timestamp + timedelta(days=7)).isocalendar()[1]

        save_day = iso_week[2] if iso_week[2] < 7 else 0
        save_time = 0 if timestamp.hour < 12 or save_day == 0 else 1

        logger.debug("  result: " + str((save_year, save_week, save_day, save_time)))
        return (save_year, save_week, save_day, save_time)

    @commands.command()
    async def AC(self, ctx: commands.Context, *, stock_command: str):
        """Animal Crossing."""
        tags = []
        view = StringView(stock_command)
        while not view.eof:
            tag = view.get_word()
            tags.append(tag)
            view.skip_ws()

        self.show_info(ctx, tags)

        if len(tags) == 0:
            return

        target = ctx.author
        timestamp = ctx.message.created_at()

        if tags[0].lower() == "plot":
            tag = tags.pop(0)
            while len(tags) > 0:
                tag = tags.pop(0)
                ts = None
                try:
                    ts = datetime.strptime(tag, "%Y-%m-%d")
                except ValueError:
                    ts = None
                if ts is not None:
                    timestamp = ts
                else:
                    target = self.get_target(ctx, tag, None)
                    if target is None:
                        return

            (save_year, save_week, _, _) = self.get_date(timestamp)
            await self.get_plot(ctx, target, save_year, save_week)
            return

        if tags[0].lower() == "dump":
            tag = tags.pop(0)
            while len(tags) > 0:
                tag = tags.pop(0)
                ts = None
                try:
                    ts = datetime.strptime(tag, "%Y-%m-%d")
                except ValueError:
                    ts = None
                if ts is not None:
                    timestamp = ts
                else:
                    target = self.get_target(ctx, tag, None)
                    if target is None:
                        return

            (save_year, save_week, _, _) = self.get_date(timestamp)
            await self.get_data(ctx, target, save_year, save_week)
            return

        # Es insersion de datos
        stalk_count = tags.pop()
        if not stalk_count.isdigit():
            return

        stalk_count = int(stalk_count)

        while len(tags) > 0:
            tag = tags.pop(0)
            ts = None
            try:
                ts = datetime.strptime(tag, "%Y-%m-%d")
            except ValueError:
                ts = None

            if tag.lower() in TIME_MSG:
                save_time = 0 if tag.lower() == "am" else 1
            elif tag.lower() in DATE_MSG:
                count = 1
                for day in DATE_MSG:
                    if tag.lower() == day:
                        save_day = count
                        break
                    count += 1
            elif ts is not None:
                timestamp = ts
            else:
                target = self.get_target(ctx, tag, None)
                if target is None:
                    return

        (
            save_year, 
            save_week, 
            save_day, 
            save_time) = self.get_date(timestamp)

        self.update_data(
            ctx, target, 
            save_year, save_week, save_day, save_time, 
            int(tags[0]))

