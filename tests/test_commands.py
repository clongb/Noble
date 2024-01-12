from commands import on_ready
import asyncio
import discord
import pytest
import pytest_asyncio
import discord.ext.test as dpytest

@pytest.mark.asyncio
async def test_roll(bot):
    dpytest.configure(bot)
    await dpytest.message("-roll")
    assert dpytest.verify().message().contains("You rolled a")

@pytest.mark.asyncio
async def test_help(bot):
    dpytest.configure(bot)
    await dpytest.message("-help")
    assert dpytest.verify().message().embed(discord.Embed(
        title='Noble commands (prefix -)',
        colour=discord.Color.blurple()))

@pytest.mark.asyncio
async def test_onready(bot):
    dpytest.configure(bot, guilds=2)
    await on_ready()
    assert dpytest.verify().activity().name("Running on 2 servers")

@pytest.mark.asyncio
async def test_stats(bot):
    dpytest.configure(bot)
    await dpytest.message("-stats https://osu.ppy.sh/community/matches/111271525 mrekk 0")
    assert dpytest.verify().message().embed(discord.Embed(
        title="OWC2023",
        description="(Poland) VS (Australia)",
        colour=discord.Color.blue()))
    assert len(dpytest.get_embed) == 11

@pytest.mark.asyncio
async def test_map(bot):
    dpytest.configure(bot)
    await dpytest.message("-map https://osu.ppy.sh/community/matches/111271525 kizan 0")
    assert dpytest.verify().message().embed(discord.Embed(
        title="OWC2023",
        description="(Poland) VS (Australia)",
        colour=discord.Color.blue()))
    assert len(dpytest.get_embed) == 8

@pytest.mark.asyncio
async def test_roles(bot):   
    dpytest.configure(bot, guilds=["testguild"], members=["testuser"])
    guild = bot.guilds[0]
    dpytest.make_role("testrole", guild=guild, color=1)
    await dpytest.message("-roles testrole")
    assert dpytest.verify().message().content("Added roles to 1 members.")

@pytest.mark.asyncio
async def test_claim(bot):
    dpytest.configure(bot, guilds=["testguild"], members=["testuser", "testuser2"])
    guild = bot.guilds[0]
    dpytest.add_role(guild.members[0], dpytest.make_role("Mapper", guild=guild, color=1))
    await dpytest.message("-claim qf nm1", member=guild.members[0])
    assert dpytest.verify().message().contains("has been claimed by")
    await dpytest.message("-claim qf nm1", member=guild.members[1])
    assert dpytest.verify().message().contains("you do not have permissions to do that!")

@pytest.mark.asyncio
async def test_drop(bot):
    dpytest.configure(bot, guilds=["testguild"], members=["testuser", "testuser2"])
    guild = bot.guilds[0]
    dpytest.add_role(guild.members[0], dpytest.make_role("Mapper", guild=guild, color=1))
    await dpytest.message("-claim qf nm2", member=guild.members[0])
    assert dpytest.verify().message().contains("has been claimed by")
    await dpytest.message("-drop qf nm2", member=guild.members[0])
    assert dpytest.verify().message().contains("has been dropped.")
    await dpytest.message("-drop qf nm2", member=guild.members[1])
    assert dpytest.verify().message().contains("you do not have permissions to do that!")


