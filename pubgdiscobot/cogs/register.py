from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable, PlayersTable
from pubg_python import PUBG
from pubg_python.exceptions import NotFoundError
from pubgdiscobot.config import (
    _pubg_token_, _pubg_shard_
)

MSG_ADDED = '{} registered as {}'
MSG_NAME_EQUAL = '{}, you already registered as {}'
MSG_PUBG_IGN_NOT_FOUND = '{}, player {} not found in STEAM PUBG'


class RegisterCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_players = PlayersTable()
        self.pubg = PUBG(_pubg_token_, _pubg_shard_)

    @commands.command(name='reg', aliases=['add', 'track'])
    @commands.guild_only()
    async def add_command(self, ctx, player_name=None):
        if player_name is None:
            return

        user_id = ctx.author.id
        user_name = ctx.author.name
        user_mention = ctx.author.mention
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        player_from_db = False

        if self.db_players.exists(player_name, "name"):
            players = self.db_players.find({"name": player_name}).limit(1)
            player_id = players[0]['id']
            player_from_db = True
        else:
            try:
                player = self.pubg.players().filter(
                    player_names=[player_name])[0]
            except NotFoundError:
                await ctx.send(MSG_PUBG_IGN_NOT_FOUND.format(
                    ctx.author.mention, player_name))
                return
            player_id = player.id

        if self.db_users.exists(user_id):
            user = self.db_users.find({'id': user_id}).limit(1)
            current_player_id = user[0]['player_id']
            if player_id == current_player_id:
                await ctx.send(MSG_NAME_EQUAL.format(user_mention,
                                                     player_name))
                return
            if self.db_users.count_documents({'player_id': current_player_id}) == 1:  # noqa: E501
                self.db_players.delete_one({'id': current_player_id})
            self.db_users.update({'id': user_id, 'guild_id': guild_id},
                                 {'$set': {'player_id': player_id}})
        else:
            self.db_users.add(id=user_id, name=user_name, shard='steam',
                              player_id=player_id, guild_id=guild_id,
                              channel_id=channel_id)
        if not player_from_db:
            self.db_players.add(id=player_id, name=player_name, shard='steam',
                                last_check=0, matches=list())
        await ctx.send(MSG_ADDED.format(ctx.author.mention, player_name))

    def delete_unused_player(self, player_id):
        if self.db_users.count_documents({'player_id': player_id}) == 0:
            self.db_players.delete_one({'id': player_id})


def setup(bot):
    bot.add_cog(RegisterCommand(bot))
