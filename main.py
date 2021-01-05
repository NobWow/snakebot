import discord, asyncio, sys, logging
from discord.ext import commands

log = logging.getLogger("discord")

main = sys.modules['__main__']

langtemplate = {
    'name': 'English (US)',
    'contents': {
        'messages': {
            'notifications': {
                'definitions': {
                    'announcement_from_author': {
                        'title': 'Announcement from bot author',
                        'description': '%(message)s'
                    },
                    'guild_announce': {
                        'title': 'Announcement: %(topic)s',
                        'description': '%(message)s'
                    }
                }
            }
        }
    }
}
langvalid = {
    'name': str,
    'contents': {
        'messages': {
            'notifications': {
                'definitions': {
                    'announcement_from_author': dict
                }
            }
        }
    }
}
class ServerAnnouncements(commands.Cog):
    def __init__(self, bot):
        #super().__init__(self, bot)
        self.bot = bot
        self.lang, missing_fields, insufficient_fields = self.bot.loadModLangs(bot.langfold + '/additions', langvalid, langtemplate, 'en_US')
    async def broadcast_author_announcement(self, text):
        async def message_sender(guild, channel):
            try:
                await channel.send(**self.bot.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.bot.conf, main.conftemplate, definition_required=True, definition='announcement_from_author', message=text))
            except Exception as exc:
                log.warning('Failed to send an announce to the %s guild (%s), channel #%s (%s): %s' % (guild.name, guild.id, channel.name, channel.id, exc))
        for guild in self.bot.guilds:
            _lang = self.bot.getLanguage(None, guild.id, self.lang)
            if guild.id != 569260355704848385:
                channel = self.bot.getNotifyChannel(guild)
                #we don't need to wait until announcement message appears
                asyncio.create_task(message_sender(guild, channel))
    async def post_guild_announcement(self, guild, topic, text, additive = ""):
        _lang = self.bot.getLanguage(None, guild.id, self.lang)
        channel = self.bot.getNotifyChannel(guild)
        message_body = self.bot.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.bot.conf, main.conftemplate, definition='guild_announce', definition_required=True, topic=topic, message=text)
        if additive:
            message_body['content'] = additive
        await channel.send(**message_body)
    @commands.command()
    @commands.is_owner()
    async def aannounce(self, ctx, *, text):
        #if not text:
        #    _lang = self.bot.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.bot.lang)
        #    await ctx.send(**self.bot.renderMessage(self.bot.lang[_lang], self.bot.langtemplate, 'common_errors', self.bot.conf, self.bot.conftemplate, definition='NotFound', ))
        await self.broadcast_author_announcement(text)
    @commands.command()
    async def announce(self, ctx, topic, text, guild = None, *, additive = ""):
        self.bot.debug_print('announce: command used with arguments: %s %s %s' % (topic, text, guild), 'mod_commands')
        if guild and guild != '-':
            targetguild = await self.bot.wrapped_convert(ctx, main.GuildConverter, main.GuildConverter, guild)
            if not targetguild:
                pass
        elif not ctx.guild:
            _lang = self.bot.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.bot.lang)
            await ctx.send(**self.renderMessage(self.bot.lang[_lang], main.langtemplate, 'command_errors', self.bot.conf, main.conftemplate, 'MissingRequiredArgument', param='guild'))
            return
        else:
            targetguild = ctx.guild
        if not (ctx.author.id == self.bot.owner_id and self.bot.conf['owner_permission_bypass']):
            self.bot.runtime_check_authorban_guild(targetguild, ctx.author)
            #self.bot.runtime_check_guild_authoradminban(targetguild, ctx.author)
            self.bot.runtime_check_guild_lpl(targetguild, ctx.author, 1)
        await self.post_guild_announcement(targetguild, topic, text, additive)
def getCogs():
    return [ServerAnnouncements]
