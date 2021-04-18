#!/usr/bin/env python3
import asyncio
import datetime
import importlib
import importlib.util
import inspect
import json
import logging
import os
import sys
import time
import traceback
from typing import Union

import discord
from discord.ext import commands

conff = 'conf.json'
dataf = 'data.json'
langfold = 'languages'
logfold: str = 'logs'
modfold = 'mods'
conf = {}
data = {}
lang = {}


# Logic primitives

class Never:
    pass


class Forever:
    pass


class Partially:
    pass


class State:
    def __init__(self, state: bool):
        self.state = bool(state)

    def __bool__(self):
        return self.state

    def __repr__(self):
        if self.state:
            return 'On'
        else:
            return 'Off'

    def __str__(self):
        if self.state:
            return 'On'
        else:
            return 'Off'


# TODO: move templates to the separate file

# Default configuration.

ctfd = open('conftemplate.json')
conftemplate = json.loads(ctfd.read())
ctfd.close()
# Default language (english)
ltfd = open('langtemplate.json')
langtemplate = json.loads(ltfd.read())
ltfd.close()
# Used to validate all keys
# 'key': class or dict
# The validator DOES NOT ALLOW LISTS!
langvalid = {
    'name': str,
    'contents': {
        'formats': {
            'date_format': str,
            'duration': {
                'seconds': {
                    "1": str
                },
                'secs': {
                    "1": str
                },
                'minutes': {
                    "1": str
                },
                'mins': {
                    "1": str
                },
                'hours': {
                    "1": str
                },
                'hs': {
                    "1": str
                },
                'days': {
                    "1": str
                },
                'ds': {
                    "1": str
                },
                'weeks': {
                    "1": str
                },
                'ws': {
                    "1": str
                },
                'months': {
                    "1": str
                },
                'mons': {
                    "1": str
                },
                'years': {
                    "1": str
                },
                'ys': {
                    "1": str
                },
                'direction': {
                    'before': str,
                    'after': str
                }
            },
            'days_of_week': {
                "1": str,
                "2": str,
                "3": str,
                "4": str,
                "5": str,
                "6": str,
                "7": str
            },
            'dow': {
                "1": str,
                "2": str,
                "3": str,
                "4": str,
                "5": str,
                "6": str,
                "7": str
            },
            'months': {
                "1": str,
                "2": str,
                "3": str,
                "4": str,
                "5": str,
                "6": str,
                "7": str,
                "8": str,
                "9": str,
                "10": str,
                "11": str,
                "12": str
            },
            'mons': {
                '1': str,
                '2': str,
                '3': str,
                '4': str,
                '5': str,
                '6': str,
                '7': str,
                '8': str,
                '9': str,
                '10': str,
                '11': str,
                '12': str
            },
            'logic': {
                'true': str,
                'false': str,
                'partially': str,
                'none': str
            },
            'date_relative': {
                'today': str,
                'tomorrow': str,
                'yesterday': str,
                'never': str,
                'forever': str,
                'now': str,
                'in_exact_time': str
            },
            'switch': {
                'on': str,
                'off': str
            }
        },
        'messages': {
            'check_failures': {
                'definitions': {
                    'AuthorBan': dict,
                    'AuthorAdministrationBan': dict,
                    'AuthorBanHere': dict,
                    'AuthorBanGuild': dict,
                    'GuildAdminBan': dict,
                    'GuildAdminBanHere': dict,
                    'GuildAdminBlockChannel': dict,
                    'GuildAdminBlockCategory': dict,
                    'NotOwner': dict,
                    'InsufficientPoints': dict,
                    'InsufficientGuildPoints': dict,
                    'NoPrivateMessage': dict,
                    'PrivateMessageOnly': dict,
                    'MissingPermissions': dict,
                    'BotMissingPermissions': dict,
                    'NSFWChannelRequired': dict,
                    'NotAllowed': dict,
                    'NotAllowedBypass': dict,
                    'MissingRole': dict,
                    'BotMissingRole': dict,
                    'MissingAnyRole': dict,
                    'BotMissingAnyRole': dict,
                }
            },
            'command_errors': {
                'definitions': {
                    'MissingRequiredArgument': dict,
                    'TooManyArguments': dict,
                    'UnexpectedQuoteError': dict,
                    'InvalidEndOfQuotedStringError': dict,
                    'ExpectedClosingQuoteError': dict,
                    'CommandNotFound': dict,
                    'DisabledCommand': dict,
                    'CommandOnCooldown': dict,
                    'InvalidDuration': dict,
                    'InvalidNumber': dict,
                    'Busy': dict
                }
            },
            'common_errors': {
                'definitions': {
                    'Forbidden': dict,
                    'NotFound': dict
                }
            },
            'custom_errors': {
                'definitions': {
                    'no_langs': dict,
                    'non_abanned': dict,
                    'non_banned': dict,
                    'non_aadminbanned': dict,
                    'non_abanned_guild': dict,
                    'non_banned_here': dict,
                    'no_ban_self': dict,
                    'no_ban_guild_owner': dict,
                    'no_ban_higher_lpl': dict,
                    'no_block_channel': dict,
                    'no_block_category': dict,
                    'abort_nothing': dict,
                    'no_with_owner': dict,
                    'no_with_higher_lpl': dict
                }
            },
            'response': {
                'description': str,
                'definitions': {
                    'lang': dict,
                    'lang_of_user': dict,
                    'lang_of_guild': dict,
                    'notify_channel': dict
                }
            },
            'info': {
                'definitions': {
                    'abort': dict,
                    'lang_list': dict,
                    'lang_set': dict,
                    'lang_set_user': dict,
                    'lang_set_guild': dict,
                    'authorban_banned': dict,
                    'authorban_unbanned': dict,
                    'authorban_list': dict,
                    'authorban_banned_here': dict,
                    'authorban_unbanned_here': dict,
                    'authorban_places_list': dict,
                    'authoradminban_banned': dict,
                    'authoradminban_unbanned': dict,
                    'authoradminban_list': dict,
                    'authorban_banned_guild': dict,
                    'authorban_unbanned_guild': dict,
                    'authorban_guild_list': dict,
                    'guild_admin_ban': dict,
                    'guild_admin_ban_here': dict,
                    'guild_admin_unban': dict,
                    'guild_admin_unban_here': dict,
                    'guild_admin_ban_list': dict,
                    'guild_admin_channel_blocked': dict,
                    'guild_admin_category_blocked': dict,
                    'guild_admin_channel_unblocked': dict,
                    'guild_admin_category_unblocked': dict,
                    'lpl_set': dict,
                    'lpl_role_set': dict,
                    'remote_toggle': dict,
                    'remote_list': dict,
                    'notify_channel_set': dict
                }
            },
            'notifications': {
                'definitions': {
                    'authorban_banned': dict,
                    'authorban_unbanned': dict,
                    'authorban_banned_here': dict,
                    'authorban_unbanned_here': dict,
                    'authoradminban_banned_ownerdm': dict,
                    'authoradminban_unbanned_ownerdm': dict,
                    'authoradminban_banned': dict,
                    'authoradminban_unbanned': dict,
                    'authorban_banned_guild_ownerdm': dict,
                    'authorban_unbanned_guild_ownerdm': dict,
                    'authorban_banned_guild': dict,
                    'authorban_unbanned_guild': dict,
                    'guild_admin_ban': dict,
                    'guild_admin_unban': dict,
                    'guild_admin_ban_here': dict,
                    'moderator_warning': dict
                }
            }
        },
        'permissions': {
            'create_instant_invite': str,
            'kick_members': str,
            'ban_members': str,
            'administrator': str,
            'manage_channels': str,
            'manage_guild': str,
            'add_reactions': str,
            'view_audit_log': str,
            'priority_speaker': str,
            'stream': str,
            'read_messages': str,
            'send_messages': str,
            'send_tts_messages': str,
            'manage_messages': str,
            'embed_links': str,
            'attach_files': str,
            'read_message_history': str,
            'mention_everyone': str,
            'external_emojis': str,
            'connect': str,
            'speak': str,
            'mute_members': str,
            'deafen_members': str,
            'use_voice_activation': str,
            'change_nickname': str,
            'manage_nicknames': str,
            'manage_roles': str,
            'manage_webhooks': str,
            'manage_emojis': str
        },
        'audit_log_actions': {
            'guild_update': str,
            'channel_create': str,
            'channel_update': str,
            'channel_delete': str,
            'overwrite_create': str,
            'overwrite_update': str,
            'overwrite_delete': str,
            'kick': str,
            'member_prune': str,
            'ban': str,
            'unban': str,
            'member_update': str,
            'member_role_update': str,
            'role_create': str,
            'role_update': str,
            'role_delete': str,
            'invite_create': str,
            'invite_update': str,
            'invite_delete': str,
            'webhook_create': str,
            'webhook_update': str,
            'webhook_delete': str,
            'emoji_create': str,
            'emoji_update': str,
            'emoji_delete': str,
            'message_delete': str
        },
        'audit_log_action_category': {
            'create': str,
            'update': str,
            'delete': str
        }
    }
}


# Exceptions
class ProcessingIdle(commands.CheckFailure):
    # This shouldn't send any error messages, it just blocks the command
    pass


class AuthorBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class AuthorBanHere(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class AuthorAdministrationBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class AuthorBanGuild(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


# --- DEPRECATED (however they have been removed from validator) --- #
class AuthorBanCategory(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class AuthorBanRole(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class AuthorBanChannel(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


# ------------------------------------------------------------------ #
class GuildAdminBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class GuildAdminBanHere(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        super().__init__(description)
        self.reason = reason
        self.date_exp = date_exp


class GuildAdminBlockChannel(commands.CheckFailure):
    pass


class GuildAdminBlockCategory(commands.CheckFailure):
    pass


class InsufficientPoints(commands.CheckFailure):
    def __init__(self, description=None, *, insuf=0, price=0):
        super().__init__(description)
        self.insuf = insuf
        self.price = price


class InsufficientGuildPoints(commands.CheckFailure):
    def __init__(self, description=None, *, insuf=0, price=0):
        super().__init__(description)
        self.insuf = insuf
        self.price = price


class NotAllowed(commands.CheckFailure):
    pass


class NotAllowedBypass(commands.CheckFailure):
    pass


class IncorrectDuration(commands.CommandError):
    def __init__(self, description=None, *, node=""):
        super().__init__(description)
        self.node = node


class InvalidNumber(commands.CommandError):
    def __init__(self, description=None, *, invalid_number=0):
        super().__init__(description)
        self.invalid_number = invalid_number


class Busy(commands.CommandError):
    pass


class NotFound(discord.NotFound):
    def __init__(self, response, message, item=""):
        self.response = response
        self.item = item
        self.message = message


# NotFound exceptions DEPRECATED
# class UserNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class MemberNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class RoleNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class GuildNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class ChannelNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class VoiceChannelNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class EmojiNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name
# class MessageNotFound(commands.CommandError):
#     def __init__(self, description=None, *, id=0):
#         self.id = id
# class InviteNotFound(commands.CommandError):
#     def __init__(self, description=None, *, name=""):
#         self.name = name

logger = logging.getLogger('discord')


# Basic shortcut functions
def enzero(num, count=2):
    snum = str(num)
    if len(snum) >= count:
        return snum
    return '0' * (count - len(snum)) + snum


def nearList(order, num):
    _ord = [int(x) for x in order]
    _ord.sort(reverse=True)
    for x in _ord:
        if num >= x:
            return x
    return None


#
def loadConf():
    logger.info('Loading configuration file...')
    global conf
    try:
        if os.path.isfile(conff):
            fl = open(conff, 'r')
            conf = json.loads(fl.read())
        else:
            fl = open(conff, 'x')
            fl.write(json.dumps(conftemplate, indent=True))
            fl.close()
            print('The example configuration has been created, enter bot token in them')
            exit(0)
    except json.JSONDecodeError as exc:
        print('The configuration file is broken.')
        print(exc)
        print('Please check the correctness of the configuration: ' + os.path.abspath(conff))
        fl.close()
        exit(1)
    else:
        logger.info('Successfully read the config')
        fl.close()


def loadData():
    logger.info('Loading data...')
    global data
    try:
        if not os.path.isfile(dataf):
            print('It seems that data file has never been created, creating an empty file.')
            datafile = open(dataf, 'x')
            # TODO
            data_tmpl = {'templates': {'guilds': [], 'roles': [], 'channels': []}, 'user_data': {}, 'guild_data': {}}
            datafile.write(json.dumps(data_tmpl, indent=True))
            datafile.close()
            data = data_tmpl
        else:
            datafile = open(dataf, 'r')
            data = json.loads(datafile.read())
    except json.JSONDecodeError as exc:
        print('The data file is broken.')
        print(exc)
        print('Please check the correctness of the configuration: ' + os.path.abspath(dataf))
        exit(1)
    else:
        logger.info('Successfully read the data')
        datafile.close()


def validateLang(langdict, c_langvalid, prefix=''):
    _missing_fields = []
    _insuf_fields = []
    for entry in c_langvalid.keys():
        assert not type(
            c_langvalid[entry]) == 'list', 'The language validate template is damaged, it shouldn\'t contain any lists'
        if not str(entry) in langdict.keys():
            _missing_fields.append(prefix + str(entry))
        else:
            if c_langvalid[entry].__class__.__name__ == 'dict':
                # this is a section, perform recursion.
                if langdict[str(entry)].__class__.__name__ != 'dict':
                    _insuf_fields.append(
                        prefix + entry + '("dict" expected, got "%s")' % langdict[entry].__class__.__name__)
                _rmf, _rif = validateLang(langdict[entry], c_langvalid[entry], prefix + str(entry) + '.')
                _missing_fields.extend(_rmf)
                _insuf_fields.extend(_rif)
            elif langdict[entry].__class__ != c_langvalid[entry]:
                # if the node is not a section, then just validate the type.
                _insuf_fields.append(prefix + str(entry) + '("%s" expected, got "%s")' % (
                    c_langvalid[entry].__name__, langdict[entry].__class__.__name__))
    return _missing_fields, _insuf_fields


def loadLangs():
    logger.info('Loading language settings...')
    if not os.path.isdir(langfold):
        print('FATAL: %s directory not found!' % langfold)
        logger.critical('Directory "%s" was not found!' % langfold)
        return False
    else:
        if 'default_lang' not in conf:
            logger.warning('The "default_lang" option is not set in the configuration, using "en_US" as the default.')
            conf['default_lang'] = "en_US"
        _files = []
        with os.scandir(langfold) as files:
            file: os.DirEntry
            for file in files:
                if file.name.endswith('.json') and file.is_file():
                    _files.append(file)

        if 'en_US.json' not in [x.name for x in _files]:
            print(
                'No language settings was found! Generating default language file...\n - You can copy&paste, '
                'rename it and edit them to create your own translation.')
            logger.error(
                'Directory "%s" does not contain any language sets! Loading default built-in language...' % langfold)
            _missing_fields, _insuf_fields = validateLang(langtemplate, langvalid)
            if _missing_fields or _insuf_fields:
                logger.critical('Correctness test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.' % (
                    len(_missing_fields), ', '.join(_missing_fields), len(_insuf_fields), ', '.join(_insuf_fields)))
                print('FATAL: The program is corrupted (the language template is invalid). Please check the log.')
                return False
            lang['en_US'] = langtemplate
            lang['default'] = lang['en_US']
            logger.info('Dumping built-in language into "%s" ...' % os.path.abspath(langfold))
            langfl = open(langfold + '/en_US.json', 'x')
            langfl.write(json.dumps(langtemplate, indent=True))
            langfl.close()
            logger.info('Successfully created default language.')
            return True
            # We're allowed to start bot.
        if not conf['default_lang'] + '.json' in [x.name for x in _files]:
            print('Language settings "%s" was not found! Please check your configuration!' % (
                    conf['default_lang'] + '.json'))
            logger.critical('Directory "%s" does not contain the "%s" file, check your configuration!' % (
                langfold, conf['default_lang'] + '.json'))
            return False
        else:
            _error_enc = False
            logger.info('Reading language content...')
            for file in _files:
                # fl = None
                # ld = None
                try:
                    langfl = open(langfold + '/' + file.name, 'r')
                    ld = json.loads(langfl.read())
                except json.JSONDecodeError as exc:
                    _exctext = traceback.format_exc()
                    print('Error: language file "%s" is damaged.\n%s' % (file.name, _exctext))
                    logger.critical('Language file "%s" is corrupted and unable to load. Exception traceback:\n%s' % (
                        file.name, _exctext))
                    print(exc)
                    print('It is strongly recommended to turn your bot off.')
                    langfl.close()
                    _error_enc = True
                else:
                    _flabel = file.name.split('.')[0]
                    # We are successfully got the language content, so we can validate them with validator pattern
                    # and by recursive function. The validation is need to keep out our program from KeyError or
                    # TypeError exceptions and notify the bot's owner about missing translation.
                    logger.info('Validating %s...' % _flabel)
                    _missing_fields, _insuf_fields = validateLang(ld, langvalid)
                    if len(_missing_fields) + len(_insuf_fields) > 0:
                        logger.critical(
                            'Correctness test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.' % (
                                len(_missing_fields), ', '.join(_missing_fields), len(_insuf_fields),
                                ', '.join(_insuf_fields)))
                        print('%s: lang file is invalid. Please check the log.' % _flabel)
                        _error_enc = True
                    else:
                        lang[_flabel] = ld
                        logger.info('Successful correctness test! Language "%s" loaded.' % _flabel)
            if conf['default_lang'] not in lang:
                return False
            lang['default'] = lang[conf['default_lang']]  # self-reference
            return not _error_enc


class GuildConverter(commands.Converter):
    def __init__(self):
        commands.Converter.__init__(self)

    async def convert(self, ctx, arg):
        if ctx.guild and (arg == "" or arg == "-"):
            return ctx.guild
        # arg = str(arg)
        if arg.isnumeric():
            # search by id
            for guild in ctx.bot.get_visible_guilds(ctx.author):
                # print(str(guild.id))
                if str(guild.id) == arg:
                    return guild
        # search by name
        for guild in ctx.bot.get_visible_guilds(ctx.author):
            # print(str(guild.name))
            if guild.name == arg:
                return guild
        # failed, raise
        raise commands.BadArgument('Guild with name "%s" not found.' % arg, arg)


class PtDiscordBot(commands.Bot):
    def debug_print(self, message, where='unknown'):
        if where in self.debug_prints:
            if self.debug_prints[where]:
                logger.debug(where + ": " + str(message))
                print(where + ": " + str(message))
        else:
            if self.debug_prints['other']:
                logger.debug('(missing key %s): ' % where + str(message))
                print('(missing key %s): ' % where + str(message))

    def __init__(self, logger_obj: logging.Logger, conf_obj: dict, data_dict: dict, lang_dict: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_prints = {"checks": False, "author_commands": True, "guild_owner_commands": True,
                             "message_rendering": False, "unknown": False, "other": True}
        self.logger = logger_obj
        self.conf = conf_obj
        self.data = data_dict
        self.mods = []
        self.modfold = modfold
        self.mod_dict = {}
        self.mod_exc_dict = {}
        self.lang = lang_dict
        self.langfold = langfold
        self.validateLang = validateLang
        self.loadLangs = loadLangs
        self.tasks = {'ab': {}, 'aab': {}, 'abh': {}, 'abg': {}, 'gab': {}, 'gabh': {}, 'sched': {}, 'longcmd': {}}
        self.local_tz: datetime.timezone = datetime.timezone(datetime.timedelta(seconds=0))
        self.loadMods()

        # Global checks
        @self.check
        def check_author_ban(ctx):
            """Example of date:
            {
                'user_data': {
                    '1002868442760284': {
                        'author_ban': {
                            'reason': 'Bot abuse',
                            'date_exp': {
                                'year': 2019,
                                'month': 10,
                                'day': 15,
                                'hour': 10,
                                'minute': 0
                            }
                        }
                    }
                }
            }
            """
            self.debug_print('Checking for author ban', 'checks')
            self.debug_print('ctx.author.id = %s, self.owner_id = %s' % (ctx.author.id, self.owner_id), 'checks')
            # I'll always pass the bot author through, even if it is banned.
            if ctx.author.id == self.owner_id:
                self.debug_print('is the owner', 'checks')
                return True
            else:
                self.debug_print('not owner', 'checks')
            try:
                if self.data['user_data'][str(ctx.author.id)]['author_ban']:
                    self.debug_print("%s has author-ban" % ctx.author.id, 'checks')
                    if 'date_exp' in self.data['user_data'][str(ctx.author.id)]['author_ban']:
                        date_exp = datetime.datetime(
                            **self.data['user_data'][str(ctx.author.id)]['author_ban']['date_exp'])
                        self.debug_print('date_exp present: %s' % date_exp, 'checks')
                    else:
                        self.debug_print('date_exp not present', 'checks')
                        date_exp = Never
                    if 'reason' in self.data['user_data'][str(ctx.author.id)]['author_ban']:
                        reason = self.data['user_data'][str(ctx.author.id)]['author_ban']['reason']
                        self.debug_print('reason present: %s' % reason, 'checks')
                    else:
                        self.debug_print('reason not present', 'checks')
                        reason = '--'
                    raise AuthorBan('You have been banned by author. Reason: %s' % reason, reason=reason,
                                    date_exp=date_exp)
                else:
                    return True
            except (AttributeError, KeyError) as exc:
                self.debug_print('check passed due to the missing fields: %s' % exc, 'checks')
                return True

        @self.check
        def check_author_ban_here(ctx):
            """Example of data:

            REDO:
            {
                'user_data': {
                    '1002868442760284': {
                        'author_ban_places': {
                            '25245794287592487': {
                                '23847239857948759': {
                                    'reason': 'Command spam',
                                    'date_exp': {
                                        'year': 9999,
                                        'month': 2,...
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            # I'll always pass the bot author through, even if it is banned.
            self.debug_print('checking for author ban in specific channel, here: %s' % ctx.channel.id, 'checks')
            if ctx.author.id == self.owner_id or not ctx.guild:
                self.debug_print('it is the owner of the bot', 'checks')
                return True
            self.debug_print('not the owner', 'checks')
            try:
                if self.data['user_data'][str(ctx.author.id)]['author_ban_places']:
                    # check if we have the guild.
                    self.debug_print('this user has some banned places', 'checks')
                    place = self.data['user_data'][str(ctx.author.id)]['author_ban_places'][str(ctx.guild.id)][
                        str(ctx.channel.id)]
                    self.debug_print('we have this ban in the database', 'checks')
                    # if we didn't got a KeyError exception, we ran on the place.
                    if 'date_exp' in place:
                        date_exp = datetime.datetime(**place['date_exp'])
                        self.debug_print('date_exp present: %s' % date_exp, 'checks')
                    else:
                        self.debug_print('date_exp is not present', 'checks')
                        date_exp = Never
                    if 'reason' in place:
                        reason = place['reason']
                        self.debug_print('reason is present: %s' % reason, 'checks')
                    else:
                        self.debug_print('reason is not present', 'checks')
                        reason = '--'
                    self.debug_print('author ban here check failed', 'checks')
                    raise AuthorBanHere('You have been banned by author in that place. Reason: %s' % reason,
                                        reason=reason, date_exp=date_exp)
                else:
                    self.debug_print('this user doesn\'t have any banned place', 'checks')
                    return True
            except (AttributeError, KeyError) as exc:
                self.debug_print('This check passed due to some fields are missing: %s' % exc, 'checks')
                return True

        @self.check
        def check_author_ban_guild(ctx):
            self.debug_print('check if the guild banned', 'checks')
            if not ctx.guild:
                self.debug_print('command used in DMs, check passed', 'checks')
                return True
            try:
                if self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                    self.debug_print('yeah, this guild (ID %s, name %s) is banned' % (ctx.guild.id, ctx.guild.name),
                                     'checks')
                    if 'date_exp' in self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                        date_exp = datetime.datetime(
                            **self.data['guild_data'][str(ctx.guild.id)]['author_ban']['date_exp'])
                        self.debug_print('date_exp is present: %s' % date_exp, 'checks')
                    else:
                        self.debug_print('date_exp is not present', 'checks')
                        date_exp = Never
                    if 'reason' in self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                        reason = self.data['guild_data'][str(ctx.guild.id)]['author_ban']['reason']
                        self.debug_print('reason is present: %s' % reason, 'checks')
                    else:
                        self.debug_print('reason is not present', 'checks')
                        reason = '--'
                    self.debug_print('author ban guild check failed', 'checks')
                    raise AuthorBanGuild('This guild has been banned by the author. Reason: %s' % reason, reason=reason,
                                         date_exp=date_exp)
            except (AttributeError, KeyError) as exc:
                self.debug_print(
                    'Guild (ID %s, name %s) is not banned, check passed: %s' % (ctx.guild.id, ctx.guild.name, exc),
                    'checks')
                return True

        @self.check
        def check_guild_admin_ban_here(ctx):
            self.debug_print('check if the user (ID %s, name %s#%s) is banned on specific place by moderator.' % (
                ctx.author.id, ctx.author.name, ctx.author.discriminator), 'checks')
            if not ctx.guild:
                self.debug_print('test passed because command issued at DMs', 'checks')
                return True
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                self.debug_print('author is the bot owner', 'checks')
                if bool(self.conf['owner_permission_bypass']):
                    self.debug_print('passing this check because owner_permission_bypass enabled', 'checks')
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    self.debug_print('passing this check because the author is the guild owner', 'checks')
                    return True
                if str(ctx.author.id) in self.data['guild_data'][str(ctx.guild.id)]['placebanned_users'][
                            str(ctx.channel.id)]:
                    self.debug_print('this user is banned on channel (ID %s, name %s) of the guild (ID %s, name %s)' % (
                        ctx.channel.id, ctx.channel.name, ctx.guild.id, ctx.guild.name), 'checks')
                    _ban = self.data['guild_data'][str(ctx.guild.id)]['placebanned_users'][str(ctx.channel.id)][
                        str(ctx.author.id)]
                    if 'date_exp' in _ban:
                        date_exp = datetime.datetime(**_ban['date_exp'])
                        self.debug_print('date_exp is present: %s' % date_exp, 'checks')
                    else:
                        date_exp = Never
                        self.debug_print('date_exp is not present', 'checks')
                    if 'reason' in _ban:
                        reason = _ban['reason']
                        self.debug_print('reason is present: %s' % reason, 'checks')
                    else:
                        reason = '--'
                        self.debug_print('reason is not present', 'checks')
                    self.debug_print('guild admin ban here check failed', 'checks')
                    raise GuildAdminBanHere(
                        'You have been banned by the guild\'s administrator here. Reason: %s' % reason, reason=reason,
                        date_exp=date_exp)
            except (AttributeError, KeyError) as exc:
                self.debug_print('check passed due to the missing fields: %s' % exc, 'checks')
                return True

        @self.check
        def check_guild_admin_block_category(ctx):
            self.debug_print('checking if the category of channels is blocked', 'checks')
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                self.debug_print('bot owner issued the command', 'checks')
                if bool(self.conf['owner_permission_bypass']):
                    self.debug_print('check passed because owner_permission_bypass enabled', 'checks')
                    return True
            if not ctx.guild:
                self.debug_print('check passed because command issued in DM\'s', 'checks')
                return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    self.debug_print('check passed: guild owner uses the command', 'checks')
                    return True
                if ctx.channel.category_id in self.data['guild_data'][str(ctx.guild.id)]['denied_categories']:
                    self.debug_print(
                        'this category (ID %s, name %s) is blocked on the guild (ID %s, name %s), guild admin block '
                        'category check failed' % (
                            ctx.channel.category_id, ctx.channel.category.name, ctx.guild.id, ctx.guild.name), 'checks')
                    raise GuildAdminBlockCategory('You cannot use bot commands here.')
                else:
                    self.debug_print('check passed: this category is not blocked', 'checks')
                    return True
            except (AttributeError, KeyError) as exc:
                self.debug_print('check passed: some of the fields are missing: %s' % exc, 'checks')
                return True

        @self.check
        def check_guild_admin_block_channel(ctx):
            self.debug_print('check if this channel is blocked on the guild', 'checks')
            if not ctx.guild:
                self.debug_print('check skipped: command used in DMs', 'checks')
                return True
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                self.debug_print('author is the bot owner', 'checks')
                if bool(self.conf['owner_permission_bypass']):
                    self.debug_print('check skipped: owner_permission_bypass is enabled', 'checks')
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    self.debug_print('guild owner used the command, check passed', 'checks')
                    return True
                if ctx.channel.id in self.data['guild_data'][str(ctx.guild.id)]['denied_channels']:
                    self.debug_print(
                        'this channel (ID %s, name %s) is blocked on the guild (ID %s, name %s), guild admin block '
                        'channel failed' % (
                            ctx.channel.id, ctx.channel.name, ctx.guild.id, ctx.guild.name), 'checks')
                    raise GuildAdminBlockChannel('You cannot use bot commands here.')
                else:
                    self.debug_print('check passed: this channel is not blocked.', 'checks')
                    return True
            except (AttributeError, KeyError) as exc:
                self.debug_print('check passed due to the missing fields: %s' % exc, 'checks')
                return True

        # TODO: help
        # TODO: command usage, description etc.
        # - Commands -
        # Language
        @commands.command()
        async def abort(ctx):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if ctx.author.id in self.tasks['longcmd']:
                if not self.tasks['longcmd'][ctx.author.id].done():
                    self.tasks['longcmd'][ctx.author.id].cancel()
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'abort'))
                else:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                             'abort_nothing'))
                del self.tasks['longcmd'][ctx.author.id]
            else:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'abort_nothing'))

        @self.check
        def check_processing_idle(ctx):
            if ctx.command is abort:
                return True
            if ctx.author.id in self.tasks['longcmd']:
                if self.tasks['longcmd'][ctx.author.id].done():
                    return True
                else:
                    raise ProcessingIdle()
            else:
                return True

        # Language control
        @commands.command()
        async def langs(ctx):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            if not self.lang:
                self.debug_print('non-possible error occurred ._.', 'other')
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_langs'))
            else:
                _lngs = list()
                for lngcode in self.lang:
                    if lngcode != 'default':
                        _lngs.append('%s (%s)' % (self.lang[lngcode]['name'], lngcode))
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_list',
                                         count=len(_lngs), list=(', '.join(_lngs))))

        @commands.command(usage="[language code]")
        async def setlang(ctx, language, user=None):
            if user is not None and ctx.author.id != self.owner_id:
                # raise commands.NotOwner("You are not allowed to change language for another user.")
                user = None
            # _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            langslc = [x.lower() for x in self.lang.keys()]
            if language.lower() not in langslc:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate,
                                         'NotFound', item=language))
            else:
                langcode = list(self.lang.keys())[langslc.index(language.lower())]
                if user is not None:
                    targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
                    if not targetuser:
                        return None
                    if str(targetuser.id) not in self.data['user_data']:
                        self.data['user_data'][str(targetuser.id)] = {}
                    self.data['user_data'][str(targetuser.id)]['language'] = langcode
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                        'lang_set_user', name=self.lang[langcode]['name'],
                                                        langcode=langcode, user_name=targetuser.name,
                                                        user_discriminator=targetuser.discriminator,
                                                        user_id=targetuser.id))
                else:
                    if str(ctx.author.id) not in self.data['user_data']:
                        self.data['user_data'][str(ctx.author.id)] = dict()
                    self.data['user_data'][str(ctx.author.id)]['language'] = langcode
                    self.savedata()
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                        'lang_set', name=self.lang[langcode]['name'],
                                                        langcode=langcode))

        @commands.command(name='lang')
        async def lang_cmd(ctx, user=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if user is not None and ctx.author.id != self.owner_id:
                # raise commands.NotOwner("You are not allowed to get current language for another user.")
                user = None
            if user is not None:
                targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
                if not targetuser:
                    return None
                if str(targetuser.id) not in self.data['user_data']:
                    langcode = 'default'
                else:
                    langcode = self.data['user_data'][str(targetuser.id)]['language']
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate,
                                                    'lang_of_user', name=self.lang[langcode]['name'], langcode=langcode,
                                                    user_id=targetuser.id, user_name=targetuser.name,
                                                    user_discriminator=targetuser.discriminator))
            else:
                langcode = _lang
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate, 'lang',
                                         name=self.lang[langcode]['name'], langcode=langcode))

        @commands.command(usage="[language code]")
        async def setguildlang(ctx, language, guild=None):
            if guild is not None and ctx.author.id != self.owner_id:
                guild = None
            # _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            langslc = [x.lower() for x in self.lang.keys()]
            if language.lower() not in langslc:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate,
                                         'NotFound', item=language))
            else:
                langcode = list(self.lang.keys())[langslc.index(language.lower())]
                if guild is not None:
                    targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                    if not targetguild:
                        return None
                    if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                        self.runtime_check_guild_lpl(targetguild, ctx.author, 3)
                        self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                    if str(targetguild.id) not in self.data['guild_data']:
                        self.data['guild_data'][str(targetguild.id)] = {}
                    self.data['guild_data'][str(targetguild.id)]['language'] = langcode
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                        'lang_set_guild', name=self.lang[langcode]['name'],
                                                        langcode=langcode, guild_name=targetguild.name))
                else:
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    if not ctx.guild:
                        await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf,
                                                            conftemplate, 'MissingRequiredArgument', param='guild'))
                        return None
                    self.runtime_check_guild_lpl(ctx.guild, ctx.author, 3)
                    if str(ctx.guild.id) not in self.data['guild_data']:
                        self.data['guild_data'][str(ctx.guild.id)] = dict()
                    self.data['guild_data'][str(ctx.guild.id)]['language'] = langcode
                    self.savedata()
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                        'lang_set_guild', name=self.lang[langcode]['name'],
                                                        langcode=langcode, guild_name=ctx.guild.name))

        @commands.command()
        async def guildlang(ctx, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return None
                if ctx.author.id not in [m.id for m in targetguild.members] and ctx.author.id != self.owner_id:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate,
                                             'NotFound', item=guild))
                    return None
                if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                    self.runtime_check_guild_admin_ban(targetguild, ctx.author)
                if str(targetguild.id) not in self.data['guild_data']:
                    langcode = 'default'
                else:
                    langcode = self.data['guild_data'][str(targetguild.id)]['language'] if 'language' in \
                                                                                           self.data['guild_data'][str(
                                                                                               targetguild.id)] else \
                        'default'
                # _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate,
                                                    'lang_of_guild', name=self.lang[langcode]['name'],
                                                    langcode=langcode, guild_name=targetguild.name))
            else:
                # _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                if not ctx.guild:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                             'MissingRequiredArgument', param='guild'))
                    return None
                self.runtime_check_guild_admin_ban(ctx.guild, ctx.author)
                try:
                    langcode = self.data['guild_data'][str(ctx.guild.id)]['language'] if 'language' in \
                                                                                         self.data['guild_data'][str(
                                                                                             ctx.guild.id)] else \
                        'default'
                except (AttributeError, KeyError):
                    langcode = 'default'
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate,
                                                    'lang_of_guild', name=self.lang[langcode]['name'],
                                                    langcode=langcode, guild_name=ctx.guild.name))

        # Local permission level
        @commands.command()
        async def setpermlevel(ctx, user, value, guild=None):
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            # ...
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_guild_ownership(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
            if not str(targetguild.id) in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'user_permission_levels' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['user_permission_levels'] = {}
            try:
                self.data['guild_data'][str(targetguild.id)]['user_permission_levels'][str(targetuser.id)] = int(value)
                self.savedata()
            except ValueError:
                raise InvalidNumber('Invalid number: %s' % value, invalid_number=value)
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            await ctx.send(
                **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lpl_set',
                                     user_id=targetuser.id, user_name=targetuser.name,
                                     user_discriminator=targetuser.discriminator, guild_name=targetguild.name,
                                     guild_id=targetguild.id, lpl_value=int(value)))

        # Local permission level, but for role
        @commands.command()
        async def setrolelevel(ctx, role, value, guild=None):
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            # ...
            ctx.guild = targetguild
            #
            targetrole = await self.wrapped_convert(ctx, commands.RoleConverter, commands.RoleConverter, role)
            if not targetrole:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_guild_ownership(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'role_settings' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['role_settings'] = {}
            if str(targetrole.id) not in self.data['guild_data'][str(targetguild.id)]['role_settings']:
                self.data['guild_data'][str(targetguild.id)]['role_settings'][str(targetrole.id)] = {}
            try:
                self.data['guild_data'][str(targetguild.id)]['role_settings'][str(targetrole.id)][
                    'local_permission_level'] = int(value)
                self.savedata()
            except ValueError:
                raise InvalidNumber('Invalid number: %s' % value, invalid_number=value)
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            await ctx.send(
                **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lpl_role_set',
                                     role_id=targetrole.id, role_name=targetrole.name, guild_name=targetguild.name,
                                     guild_id=targetguild.id, lpl_value=int(value)))

        # Remote access
        @commands.command()
        async def setremote(ctx, logic, user=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 3)
            if user:
                targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
                if not targetuser:
                    return
            else:
                targetuser = ctx.author
            if bool(logic):
                if 'remote_users' not in self.data['guild_data'][str(targetguild.id)]:
                    self.data['guild_data'][str(targetguild.id)]['remote_users'] = []
                elif str(targetuser.id) not in self.data['guild_data'][str(targetguild.id)]['remote_users']:
                    self.data['guild_data'][str(targetguild.id)]['remote_users'].append(str(targetuser.id))
            elif str(targetuser.id) in self.data['guild_data'][str(targetguild.id)]['remote_users']:
                self.data['guild_data'][str(targetguild.id)]['remote_users'].remove(str(targetuser.id))
            self.savedata()
            await ctx.send(
                self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'remote_toggle',
                                   user_id=targetuser.id, user_name=targetuser.name,
                                   user_discriminator=targetuser.discriminator, switch=State(bool(logic))))

        # Guild settings
        @commands.command()
        async def setnotifychannel(ctx, channel=None, guild=None):
            self.debug_print('setnotifychannel: command used with arguments given: %s %s' % (channel, guild),
                             'guild_owner_commands')
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)

            if guild:
                self.debug_print('setnotifychannel: guild specified: %s' % guild, 'guild_owner_commands')
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    self.debug_print('setnotifychannel: targetguild is invalid', 'guild_owner_commands')
                    return
                self.debug_print(
                    'setnotifychannel: targetguild specified: ID %s NAME %s' % (targetguild.id, targetguild.name),
                    'guild_owner_commands')
                targetchannel = self.findchannel(targetguild, channel)
                self.debug_print(
                    'setnotifychannel: targetchannel ID %s NAME %s' % (targetchannel.id, targetchannel.name),
                    'guild_owner_commands')
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='channel'))
                return
            else:
                targetguild = ctx.guild
                if channel:
                    self.debug_print('hmm this place is problem')
                    targetchannel = self.findchannel(targetguild, channel)
                    self.debug_print('and its ok weird')
                else:
                    targetchannel = ctx.channel
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 3)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['notify_channel'] = targetchannel.id
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'notify_channel_set', guild_id=targetguild.id,
                                                guild_name=targetguild.name, channel_id=targetchannel.id,
                                                channel_name=targetchannel.name))

        # Ban
        @commands.command(hidden=True)
        @commands.is_owner()
        async def aban(ctx, user, date='', *, reason=''):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if str(targetuser.id) not in self.data['user_data']:
                self.data['user_data'][str(targetuser.id)] = {}
            self.data['user_data'][str(targetuser.id)]['author_ban'] = {'reason': reason}
            _never = self.lang[_lang]['contents']['formats']['date_relative']['never'].lower()
            _date = date.lower()
            _never2 = self.lang[_lang]['contents']['formats']['date_relative']['never']
            if _date != '' or _date != _never or _date != _never2:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['user_data'][str(targetuser.id)]['author_ban']['date_exp'] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            if targetuser.id in self.tasks['longcmd']:
                self.tasks['longcmd'][targetuser.id].cancel()
                del self.tasks['longcmd'][targetuser.id]
            if targetuser.id in self.tasks['ab']:
                self.tasks['ab'][targetuser.id].cancel()
            self.tasks['ab'][targetuser.id] = asyncio.create_task(self.authorban_expiry_timer(str(targetuser.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authorban_banned', reason=reason, date_exp=date_exp,
                                                user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            # notification
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_banned', reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass

        # Unban
        @commands.command(hidden=True)
        @commands.is_owner()
        async def unaban(ctx, user):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if str(targetuser.id) not in self.data['user_data']:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator))
                return None
            elif 'author_ban' not in self.data['user_data'][str(targetuser.id)]:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator))
                return None
            del self.data['user_data'][str(targetuser.id)]['author_ban']
            self.savedata()
            if targetuser.id in self.tasks['ab']:
                self.tasks['ab'][targetuser.id].cancel()
                del self.tasks['ab'][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authorban_unbanned', user_name=targetuser.name,
                                                user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_unbanned'))
            except discord.Forbidden:
                pass

        @commands.command(hidden=True)
        @commands.is_owner()
        async def abanhere(ctx, user, channel='', date='', *, reason=''):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if channel:
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter,
                                                           commands.TextChannelConverter, channel)
                if not targetchannel:
                    return None
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='channel'))
                return None
            else:
                targetchannel = ctx.channel
            if str(targetuser.id) not in self.data['user_data']:
                self.data['user_data'][str(targetuser.id)] = {}
            if 'author_ban_places' not in self.data['user_data'][str(targetuser.id)]:
                self.data['user_data'][str(targetuser.id)]['author_ban_places'] = {}
            if str(targetchannel.guild.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places']:
                self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)] = {}
            self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][
                str(targetchannel.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != self.lang[_lang]['contents']['formats']['date_relative'][
                'never'].lower() or date.lower() != self.lang[_lang]['contents']['formats']['date_relative'][
                            'never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][
                    str(targetchannel.id)]['date_exp'] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            if targetchannel.guild.id not in self.tasks['abh']:
                self.tasks['abh'][targetchannel.guild.id] = {}
            if targetchannel.id not in self.tasks['abh'][targetchannel.guild.id]:
                self.tasks['abh'][targetchannel.guild.id][targetchannel.id] = {}
            if targetuser.id in self.tasks['abh'][targetchannel.guild.id][targetchannel.id]:
                self.tasks['abh'][targetchannel.guild.id][targetchannel.id][targetuser.id].cancel()
            self.tasks['abh'][targetchannel.guild.id][targetchannel.id][targetuser.id] = asyncio.create_task(
                self.authorbanplace_expiry_timer(str(targetuser.id), targetchannel.guild.id, targetchannel.id))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authorban_banned_here', reason=reason, date_exp=date_exp,
                                                user_name=targetuser.name, user_discriminator=targetuser.discriminator,
                                                user_id=targetuser.id, guild_id=targetchannel.guild.id,
                                                guild_name=targetchannel.guild.name, channel_id=targetchannel.id,
                                                channel_name=targetchannel.name))
            # notification
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_banned_here', reason=reason, date_exp=date_exp,
                                         guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name,
                                         channel_id=targetchannel.id, channel_name=targetchannel.name))
            except discord.Forbidden:
                pass

        @commands.command(hidden=True)
        @commands.is_owner()
        async def unabanhere(ctx, user, channel):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if channel:
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter,
                                                           commands.TextChannelConverter, channel)
                if not targetchannel:
                    return None
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='channel'))
                return None
            else:
                targetchannel = ctx.channel
            if str(targetuser.id) not in self.data['user_data']:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if 'author_ban_places' not in self.data['user_data'][str(targetuser.id)]:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if str(targetchannel.guild.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places']:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if str(targetchannel.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places'][
                            str(targetchannel.guild.id)]:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            del self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][
                str(targetchannel)]
            try:
                self.tasks['abh'][targetuser.id][targetchannel.guild.id][targetchannel.id].cancel()
                del self.tasks['abh'][targetuser.id][targetchannel.guild.id][targetchannel.id]
            except (KeyError, AttributeError):
                pass
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authorban_unbanned_here', user_name=targetuser.name,
                                                user_discriminator=targetuser.discriminator, user_id=targetuser.id,
                                                guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name,
                                                channel_id=targetchannel.id, channel_name=targetchannel.name))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_unbanned_here', guild_id=targetchannel.guild.id,
                                         guild_name=targetchannel.guild.name, channel_id=targetchannel.id,
                                         channel_name=targetchannel.name))
            except discord.Forbidden:
                pass

        @commands.command(hidden=True)
        @commands.is_owner()
        async def aadminban(ctx, guild='', date='', *, reason=''):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return None
            else:
                if not ctx.guild:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                             'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['author_administration_ban'] = {'reason': reason}
            if date.lower() != '' or date.lower() != self.lang[_lang]['contents']['formats']['date_relative'][
                'never'].lower() or date.lower() is not self.lang[_lang]['contents']['formats'][
                            'date_relative']['never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['guild_data'][str(targetguild.id)]['author_administration_ban']['date_exp'] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            if targetguild.id in self.tasks['aab']:
                self.tasks['aab'][targetguild.id].cancel()
            self.tasks['aab'][targetguild.id] = asyncio.create_task(
                self.authorbanguild_expiry_timer(str(targetguild.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authoradminban_banned', guild_id=targetguild.id,
                                                guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authoradminban_banned', guild_id=targetguild.id, guild_name=targetguild.name,
                                         reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authoradminban_banned_ownerdm', reason=reason, date_exp=date_exp,
                                         guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        @commands.command(hidden=True)
        @commands.is_owner()
        async def unaadminban(ctx, guild=''):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return None
            else:
                if not ctx.guild:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                             'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'author_administration_ban' not in self.data['guild_data'][str(targetguild.id)]:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_aadminbanned', guild_id=targetguild.id, guild_name=targetguild.name))
            if not self.tasks['aab'][targetguild.id].done():
                self.tasks['aab'][targetguild.id].cancel()
            del self.tasks['aab'][targetguild.id]
            del self.data['guild_data'][str(targetguild.id)]['author_administration_ban']
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authoradminban_unbanned', guild_id=targetguild.id,
                                         guild_name=targetguild.name))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authoradminban_unbanned_ownerdm', guild_id=targetguild.id,
                                         guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        @commands.command()
        @commands.is_owner()
        async def abanguild(ctx, guild='', date='', *, reason=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['author_ban'] = {'reason': reason}
            _date = date.lower()
            _never = self.lang[_lang]['contents']['formats']['date_relative']['never']
            if _date != '' or _date != _never.lower() or _date is not _never:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['guild_data'][str(targetguild.id)]['author_ban']['date_exp'] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            if targetguild.id in self.tasks['abg']:
                self.tasks['abg'][targetguild.id].cancel()
            self.tasks['abg'][targetguild.id] = asyncio.create_task(
                self.authorbanguild_expiry_timer(str(targetguild.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'authorban_banned_guild', guild_id=targetguild.id,
                                                guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_banned_guild', guild_id=targetguild.id, guild_name=targetguild.name,
                                         reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_banned_guild_ownerdm', reason=reason, date_exp=date_exp,
                                         guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        @commands.command()
        @commands.is_owner()
        async def unabanguild(ctx, guild=''):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return None
            else:
                if not ctx.guild:
                    await ctx.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                             'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'author_ban' not in self.data['guild_data'][str(targetguild.id)]:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_abanned_guild', guild_id=targetguild.id, guild_name=targetguild.name))
                return None
            if not self.tasks['abg'][targetguild.id].done():
                self.tasks['abg'][targetguild.id].cancel()
            del self.tasks['abg'][targetguild.id]
            del self.data['guild_data'][str(targetguild.id)]['author_ban']
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_unbanned_guild', guild_id=targetguild.id,
                                         guild_name=targetguild.name))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'authorban_unbanned_guild_ownerdm', guild_id=targetguild.id,
                                         guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        @commands.command()
        async def blockchannel(ctx, channel=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if channel:
                targetchannel = self.findchannel(targetguild, channel)
            else:
                targetchannel = ctx.channel
            if not targetchannel:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 5)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'denied_channels' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['denied_channels'] = []
            if targetchannel.id not in self.data['guild_data'][str(targetguild.id)]['denied_channels']:
                self.data['guild_data'][str(targetguild.id)]['denied_channels'].append(targetchannel.id)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                definition='guild_admin_channel_blocked', definition_required=True,
                                                channel=targetchannel.mention, channel_name=targetchannel.name,
                                                channel_id=targetchannel.id))

        @commands.command()
        async def blockcategory(ctx, category=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if category:
                targetcategory = self.findcategory(targetguild, category)
            else:
                targetcategory = ctx.channel
            if not targetcategory:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 5)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'denied_categories' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['denied_categories'] = []
            if targetcategory.id not in self.data['guild_data'][str(targetguild.id)]['denied_categories']:
                self.data['guild_data'][str(targetguild.id)]['denied_categories'].append(targetcategory.id)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                definition='guild_admin_category_blocked', definition_required=True,
                                                category=targetcategory, category_name=targetcategory.name,
                                                category_id=targetcategory.id))

        @commands.command()
        async def unblockchannel(ctx, channel=None, guild=None):
            self.debug_print("unblockchannel is used with arguments: %s %s" % (channel, guild), 'guild_owner_commands')
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                self.debug_print("command argument guild specified", 'guild_owner_commands')
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                self.debug_print("command used in DMs and no guild argumemnt", 'guild_owner_commands')
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                self.debug_print("command used in guild and no arguments", 'guild_owner_commands')
                targetguild = ctx.guild
            if channel:
                self.debug_print("channel specified", 'guild_owner_commands')
                targetchannel = self.findchannel(targetguild, channel)
            else:
                self.debug_print("channel not specified", 'guild_owner_commands')
                targetchannel = ctx.channel
            if not targetchannel:
                self.debug_print("channel not found", 'guild_owner_commands')
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate,
                                         'NotFound', item=channel))
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.debug_print("performing checks", 'guild_owner_commands')
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.debug_print("performing check 2", 'guild_owner_commands')
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.debug_print("performing check 3", 'guild_owner_commands')
                self.runtime_check_guild_lpl(targetguild, ctx.author, 5)
                self.debug_print("checks are done", 'guild_owner_commands')
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'denied_channels' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['denied_channels'] = []
            if targetchannel.id not in self.data['guild_data'][str(targetguild.id)]['denied_channels']:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         definition='no_block_channel', definition_required=True,
                                         channel=targetchannel.mention, channel_id=targetchannel.id,
                                         channel_name=targetchannel.name))
                return
            else:
                self.data['guild_data'][str(targetguild.id)]['denied_channels'].remove(targetchannel.id)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                definition='guild_admin_channel_unblocked', definition_required=True,
                                                channel=targetchannel.mention, channel_name=targetchannel.name,
                                                channel_id=targetchannel.id))

        @commands.command()
        async def unblockcategory(ctx, category=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if category:
                targetcategory = self.findcategory(targetguild, category)
            else:
                targetcategory = ctx.channel
            if not targetcategory:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 5)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'denied_categories' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['denied_categories'] = []
            if targetcategory.id not in self.data['guild_data'][str(targetguild.id)]['denied_categories']:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         definition='no_block_category', definition_required=True,
                                         category=targetcategory.mention, category_id=targetcategory.id,
                                         category_name=targetcategory.name))
                return
            else:
                self.data['guild_data'][str(targetguild.id)]['denied_categories'].remove(targetcategory.id)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                definition='guild_admin_category_unblocked', definition_required=True,
                                                category=targetcategory, category_name=targetcategory.name,
                                                category_id=targetcategory.id))

        @commands.command()
        async def ban(ctx, user, date='', guild=None, *, reason=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            # hmm...
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if targetuser.id == ctx.author.id:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_self'))
                return
            if targetuser.id == targetguild.owner.id:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_guild_owner'))
                return
            if not self.runtime_check_guild_higher_lpl(targetguild, targetuser, ctx.author):
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_higher_lpl'))
                return
            if 'banned_users' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['banned_users'] = {}
            self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != self.lang[_lang]['contents']['formats']['date_relative'][
                            'never'].lower():
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)]['date_exp'] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            await targetguild.ban(targetuser, reason=reason)
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
            self.tasks['gab'][targetguild.id][targetuser.id] = asyncio.create_task(
                self.guildadminban_expiry_timer(targetguild.id, targetuser.id))
            await ctx.send(
                **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_ban',
                                     user_id=targetuser.id, user_name=targetuser.name,
                                     user_discriminator=targetuser.discriminator, guild_name=targetguild.name,
                                     guild_id=targetguild.id, reason=reason, date_exp=date_exp))
            # notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'guild_admin_ban', guild_id=targetguild.id, guild_name=targetguild.name,
                                         reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass

        @commands.command()
        async def banhere(ctx, user, date='', channel=None, guild=None, *, reason=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if channel:
                targetchannel = self.findchannel(targetguild, channel)
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='channel'))
                return
            else:
                targetchannel = ctx.channel
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            # wait... this is illegal
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if targetuser.id == ctx.author.id:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_self'))
                return
            if targetuser.id == targetguild.owner.id:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_guild_owner'))
                return
            if not self.runtime_check_guild_higher_lpl(targetguild, targetuser, ctx.author):
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'no_ban_higher_lpl'))
                return
            if 'placebanned_users' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['banned_users'] = {}
            if str(targetchannel.id) not in self.data['guild_data'][str(targetguild.id)]['placebanned_users']:
                self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)][
                str(targetuser.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != self.lang[_lang]['contents']['formats']['date_relative'][
                            'never'].lower():
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'],
                                                                        date.lower())
                self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)][
                    str(targetuser.id)] = {
                    'year': date_exp.year,
                    'month': date_exp.month,
                    'day': date_exp.day,
                    'hour': date_exp.hour,
                    'minute': date_exp.minute,
                    'second': date_exp.second,
                    'microsecond': date_exp.microsecond
                }
            else:
                date_exp = Never
            # BANNED
            self.savedata()
            if targetuser.id in self.tasks['gabh'][targetguild.id][targetchannel.id]:
                self.tasks['gabh'][targetguild.id][targetchannel.id][targetuser.id].cancel()
            self.tasks['gabh'][targetguild.id][targetchannel.id][targetuser.id] = asyncio.create_task(
                self.guildadminbanhere_expiry_timer(targetguild.id, targetchannel.id, targetuser.id))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'guild_admin_ban_here', user_id=targetuser.id,
                                                user_name=targetuser.name, user_discriminator=targetuser.discriminator,
                                                guild_name=targetguild.name, guild_id=targetguild.id, reason=reason,
                                                date_exp=date_exp))
            # notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'guild_admin_ban_here', guild_id=targetguild.id, guild_name=targetguild.name,
                                         channel_id=targetchannel.id, channel_name=targetchannel.name, reason=reason,
                                         date_exp=date_exp))
            except discord.Forbidden:
                pass

        @commands.command()
        async def unban(ctx, user, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    pass
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            # NOW this is really bad
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            try:
                del self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)]
            except KeyError:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_banned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, guild_id=targetguild.id,
                                         guild_name=targetguild.name))
                return None
            self.savedata()
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
                del self.tasks['ab'][targetguild.id][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'guild_admin_unban', user_name=targetuser.name,
                                                user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'guild_admin_unban'))
            except discord.Forbidden:
                pass

        @commands.command()
        async def unbanhere(ctx, user, channel=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    pass
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            # NOW this is really bad
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if channel:
                targetchannel = await self.findchannel(targetguild, channel)
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='channel'))
                return
            else:
                targetchannel = ctx.channel
            try:
                del self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)][
                    str(targetuser.id)]
            except KeyError:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate,
                                         'non_banned', user_name=targetuser.name,
                                         user_discriminator=targetuser.discriminator, guild_id=targetguild.id,
                                         guild_name=targetguild.name))
                return None
            self.savedata()
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
                del self.tasks['ab'][targetguild.id][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'guild_admin_unban', user_name=targetuser.name,
                                                user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                         'guild_admin_unban'))
            except discord.Forbidden:
                pass

        @commands.command()
        @commands.is_owner()
        async def abans(ctx, channel=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            fields = []
            if channel:
                targetchannel = self.wrapped_convert(ctx, commands.TextChannelConverter, commands.TextChannelConverter,
                                                     channel)
                if not targetchannel:
                    return
                # TODO: continuing code here: requires change to the SQL
            for userid in self.data['user_data']:
                if 'author_ban' in self.data['user_data'][userid]:
                    _ban = self.data['user_data'][userid]['author_ban']
                    banned = await self.fetch_user(int(userid))
                    if banned:  # if user actually exists
                        try:
                            date_exp = datetime.datetime(**_ban['date_exp'])
                        except (KeyError, AttributeError):
                            date_exp = Never
                        fields.append({'name': {'user_name': banned.name, 'user_discriminator': banned.discriminator,
                                                'user_id': banned.id},
                                       'value': {'reason': _ban['reason'], 'date_exp': date_exp}})
                    else:
                        try:
                            date_exp = datetime.datetime(**_ban['date_exp'])
                        except (KeyError, AttributeError):
                            date_exp = Never
                        fields.append({'name': {'user_name': ('Unknown User (%s)' % userid),
                                                'user_discriminator': '0000', 'user_id': userid},
                                       'value': {'reason': _ban['reason'], 'date_exp': date_exp}})
            await ctx.send(
                **self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'author_ban_list',
                                     fields=fields, banned_count=len(fields)))

        @commands.command()
        async def bans(ctx, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            fields = []
            if 'banned_users' not in self.data['guild_data'][str(targetguild.id)].keys():
                self.data['guild_data'][str(targetguild.id)]['banned_users'] = {}
            for each_ban in await targetguild.bans():
                self.data['guild_data'][str(targetguild.id)]['banned_users'][str(each_ban.user.id)] = {
                    'reason': each_ban.reason}
            for userid in self.data['guild_data'][str(targetguild.id)]['banned_users']:
                _ban = self.data['guild_data'][str(targetguild.id)]['banned_users'][userid]
                banned = await self.fetch_user(int(userid))
                if banned:  # if user actually exists
                    try:
                        date_exp = datetime.datetime(**_ban['date_exp'])
                    except (KeyError, AttributeError):
                        date_exp = Never
                    fields.append({'name': {'user_name': banned.name, 'user_discriminator': banned.discriminator,
                                            'user_id': banned.id},
                                   'value': {'reason': _ban['reason'] if 'reason' in _ban else None,
                                             'date_exp': date_exp}})
                else:
                    try:
                        date_exp = datetime.datetime(**_ban['date_exp'])
                    except (KeyError, AttributeError):
                        date_exp = Never
                    fields.append({'name': {'user_name': ('Unknown User (%s)' % userid), 'user_discriminator': '0000',
                                            'user_id': userid},
                                   'value': {'reason': _ban['reason'] if 'reason' in _ban else None,
                                             'date_exp': date_exp}})
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate,
                                                'guild_admin_ban_list', fields=fields, banned_count=len(fields)))

        # Load internal commands
        @commands.command()
        async def bansin(ctx, channel=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(
                    **self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate,
                                         'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #
            ctx.guild = targetguild
            #
            if channel:
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter,
                                                           commands.TextChannelConverter, channel)
                if not targetchannel:
                    return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            # fields = []

        self.add_command(langs)
        self.add_command(setlang)
        self.add_command(lang_cmd)
        self.add_command(setguildlang)
        self.add_command(guildlang)
        self.add_command(aban)
        self.add_command(unaban)
        self.add_command(abanhere)
        self.add_command(unabanhere)
        self.add_command(aadminban)
        self.add_command(unaadminban)
        self.add_command(abanguild)
        self.add_command(unabanguild)
        self.add_command(ban)
        self.add_command(unban)
        self.add_command(bans)
        self.add_command(banhere)
        self.add_command(unbanhere)
        self.add_command(setpermlevel)
        self.add_command(setrolelevel)
        self.add_command(setnotifychannel)
        self.add_command(blockchannel)
        self.add_command(blockcategory)
        self.add_command(unblockchannel)
        self.add_command(unblockcategory)

        # Command groups
        @commands.group(invoke_without_command=True)
        async def testgroup(ctx):
            await ctx.send('no subcommand')

        @testgroup.command()
        async def subcmd1(ctx):
            await ctx.send('This is subcmd1')

        @testgroup.command()
        async def subcmd2(ctx):
            await ctx.send('This is a subcommand two')

        self.add_command(testgroup)

    # TODO: command helper chains for mod development & shrink this code
    async def chc_lang(self, ctx, guild=None):
        pass

    async def wrapped_convert(self, ctx, converter1, converter2, arg):
        try:
            if ctx.guild:
                target = await converter1().convert(ctx, arg)
            else:
                target = await converter2().convert(ctx, arg)
            return target
        except (commands.ConversionError, commands.BadArgument):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            await ctx.send(
                **self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate,
                                     'NotFound', item=arg))
            return None

    def savedata(self):
        fl = open(dataf, 'w')
        fl.write(json.dumps(self.data, indent=True))
        fl.close()

    def findchannel(self, guild, channel):
        self.debug_print('findchannel: utility used with arguments: %s, %s' % (guild, channel), 'bot_utility')
        if str(channel).isnumeric():
            self.debug_print('findchannel: Channel ID is given, retrieving channel by ID', 'bot_utility')
            targetchannel = discord.utils.get(guild.text_channels, id=int(channel))
            if not targetchannel:
                self.debug_print('findchannel: channel not found', 'bot_utility')
                raise NotFound(message='Channel with ID %s not found' % channel, response=404, item=channel)
        elif str(channel).startswith('<#') and str(channel).endswith('>'):
            self.debug_print('findchannel: channel mention is given', 'bot_utility')
            try:
                channel_id = int(str(channel)[2:-1])
            except ValueError:
                self.debug_print('findchannel: something went wrong', 'bot_utility')
                raise NotFound(message='Channel with mention %s not found' % channel, response=404, item=channel)
            self.debug_print('findchannel: retrieving channel by ID: %s' % channel_id, 'bot_utility')
            targetchannel = guild.get_channel(channel_id)
            if not targetchannel:
                self.debug_print('findchannel: channel not found', 'bot_utility')
                raise NotFound(message='Channel with ID %s not found' % channel, response=404, item=channel)
            self.debug_print('findchannel: success', 'bot_utility')
            return targetchannel
        else:
            self.debug_print('findchannel: channel name is given', 'bot_utility')
            targetchannel = discord.utils.get(guild.text_channels, name=channel)
            if not targetchannel:
                self.debug_print('findchannel: channel not found', 'bot_utility')
                raise NotFound(message='Channel with name %s not found' % channel, response=404, item=channel)
            return targetchannel

    def findcategory(self, guild, category):
        self.debug_print('findcategory: utility used with arguments: %s, %s' % (guild, category), 'bot_utility')
        if str(category).isnumeric():
            self.debug_print('findcategory: category ID is given, retrieving category by ID', 'bot_utility')
            targetcategory = discord.utils.get(guild.categories, id=int(category))
            if not targetcategory:
                self.debug_print('findcategory: category not found', 'bot_utility')
                raise NotFound(message='category with ID %s not found' % category, response=404, item=category)
        elif str(category).startswith('<#') and str(category).endswith('>'):
            self.debug_print('findcategory: channel mention is given', 'bot_utility')
            try:
                channel_id = int(str(category)[2:-1])
            except ValueError:
                self.debug_print('findcategory: something went wrong', 'bot_utility')
                raise NotFound(message='channel with mention %s not found' % category, response=404, item=category)
            self.debug_print('findcategory: retrieving channel by ID: %s' % channel_id, 'bot_utility')
            targetcategory = guild.get_channel(channel_id).category
            if not targetcategory:
                self.debug_print('findcategory: category not found', 'bot_utility')
                raise NotFound(message='category with ID %s not found' % category, response=404, item=category)
            else:
                self.debug_print('fundcategory: from channel category retrieved: ID %s NAME %s' % (
                    targetcategory.id, targetcategory.name))
            self.debug_print('findcategory: success', 'bot_utility')
            return targetcategory
        else:
            self.debug_print('findcategory: category name is given', 'bot_utility')
            targetcategory = discord.utils.get(guild.categories, name=category)
            if not targetcategory:
                self.debug_print('findcategory: category not found', 'bot_utility')
                raise NotFound(message='category with name %s not found' % category, response=404, item=category)
            return targetcategory

    def is_in_guild(self, guild, user):
        if guild.get_member(user.id):
            return True
        else:
            return guild in self.get_visible_guilds(user)

    def get_visible_guilds(self, user):
        if user.id == self.owner_id and self.conf['owner_permission_bypass']:
            return self.guilds
        _guilds = []
        for guild in self.guilds:
            try:
                isremote = str(user.id) in self.data['guild_data'][str(guild.id)]['remote_users']
            except KeyError:
                isremote = False
            if guild.get_member(user.id) or isremote or user.id == self.owner_id:
                _guilds.append(guild)
        return _guilds

    async def authorban_expiry_timer(self, t_id):
        async def notify():
            try:
                targetuser = self.get_user(int(t_id)) or await self.fetch_user(int(t_id))
                if targetuser:
                    _lang = self.getLanguage(int(t_id), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authorban_unbanned'))
            except discord.Forbidden:
                pass

        if 'date_exp' not in self.data['user_data'][str(t_id)]['author_ban']:
            return False
        trg = datetime.datetime(**self.data['user_data'][str(t_id)]['author_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['user_data'][str(t_id)]['author_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_ban' in self.data['user_data'][str(t_id)]:
            del self.data['user_data'][str(t_id)]['author_ban']
            self.savedata()
            await notify()
        return True

    async def authorbanplace_expiry_timer(self, t_id, guildid, channelid):
        async def notify():
            try:
                targetuser = self.get_user(int(t_id)) or await self.fetch_user(int(t_id))
                targetguild = self.get_guild(int(guildid)) or await self.fetch_guild(int(guildid))
                targetchannel = targetguild.get_channel(int(channelid))
                if targetuser and targetguild and targetchannel:
                    _lang = self.getLanguage(int(t_id), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authorban_unbanned_here', guild_name=targetguild.name, guild_id=guildid,
                                             channel_name=targetchannel.name, channel_id=channelid))
            except discord.Forbidden:
                pass

        if 'date_exp' not in self.data['user_data'][str(t_id)]['author_ban_places'][str(guildid)][str(channelid)]:
            return False
        trg = datetime.datetime(
            **self.data['user_data'][str(t_id)]['author_ban_places'][str(guildid)][str(channelid)]['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['user_data'][str(t_id)]['author_ban_places'][str(guildid)][str(channelid)]
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if str(channelid) in self.data['user_data'][str(t_id)]['author_ban_places'][str(guildid)]:
            del self.data['user_data'][str(t_id)]['author_ban_places'][str(guildid)][str(channelid)]
            self.savedata()
            await notify()
        return True

    async def authoradminban_expiry_timer(self, t_id):
        async def notify():
            try:
                targetguild = self.get_guild(int(t_id)) or await self.fetch_guild(int(t_id))
                targetuser = targetguild.owner
                if targetguild:
                    _lang = self.getLanguage(None, int(t_id), self.lang)
                    await self.getNotifyChannel(targetguild).send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authoradminban_unbanned'))
                if targetuser:
                    _lang = self.getLanguage(int(t_id), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authoradminban_unbanned_ownerdm', guild_id=targetguild.id,
                                             guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        if 'date_exp' not in self.data['guild_data'][str(t_id)]['author_administration_ban']:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(t_id)]['author_administration_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(t_id)]['author_administration_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_administration_ban' in self.data['guild_data'][str(t_id)]:
            del self.data['guild_data'][str(t_id)]['author_administration_ban']
            self.savedata()
            await notify()
        return True

    async def authorbanguild_expiry_timer(self, t_id):
        async def notify():
            try:
                targetguild = self.get_guild(int(t_id))
                targetuser = targetguild.owner
                if targetguild:
                    _lang = self.getLanguage(None, int(t_id), self.lang)
                    await self.getNotifyChannel(targetguild).send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authorban_unbanned_guild'))
                if targetuser:
                    _lang = self.getLanguage(int(t_id), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'authorban_unbanned_guild_ownerdm', guild_id=targetguild.id,
                                             guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        if 'date_exp' not in self.data['guild_data'][str(t_id)]['author_ban']:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(t_id)]['author_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(t_id)]['author_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_ban' in self.data['guild_data'][str(t_id)]:
            del self.data['guild_data'][str(t_id)]['author_ban']
            self.savedata()
            await notify()
        return True

    async def guildadminban_expiry_timer(self, guildid, userid):
        async def notify():
            try:
                targetuser = self.get_user(int(userid))
                targetguild = self.get_guild(int(guildid))
                if targetuser and targetguild:
                    _lang = self.getLanguage(int(userid), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'guild_admin_unban', guild_id=guildid, guild_name=targetguild.name))
            except discord.Forbidden:
                pass

        async def member_unban():
            try:
                targetguild = self.get_guild(int(guildid))
                await targetguild.unban(self.get_user(userid))
            except (discord.Forbidden, discord.NotFound):
                pass

        if 'date_exp' not in self.data['guild_data'][str(guildid)]['banned_users'][str(userid)]:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(guildid)]['banned_users'][str(userid)]['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(guildid)]['banned_users'][str(userid)]
            self.savedata()
            await member_unban()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if str(userid) in self.data['guild_data'][str(guildid)]['banned_users']:
            del self.data['guild_data'][str(guildid)]['banned_users'][str(userid)]
            self.savedata()
            await member_unban()
            await notify()
        return True

    async def guildadminbanhere_expiry_timer(self, guildid, channelid, userid):
        async def notify():
            try:
                targetuser = self.get_user(int(userid))
                targetguild = self.get_guild(int(guildid))
                targetchannel = self.get_channel(int(channelid))
                if targetuser and targetguild and targetchannel:
                    _lang = self.getLanguage(int(userid), None, self.lang)
                    await targetuser.send(
                        **self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate,
                                             'guild_admin_unban_here', guild_id=guildid, guild_name=targetguild.name,
                                             channel_id=channelid, channel_name=targetchannel.name))
            except discord.Forbidden:
                pass

        if 'date_exp' not in self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)][str(userid)]:
            return False
        trg = datetime.datetime(
            **self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)]['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)][str(userid)]
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if str(userid) in self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)]:
            del self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)][str(userid)]
            self.savedata()
            await notify()
        return True

    # Runtime checks shouldn't be used as decorators: it should be used as regular functions and they MAY also require
    # context
    # Runtime checks allows the commands to perform checks by using custom arguments.
    # When runtime check has passed successfully, it just returns True, otherwise raises an exception.
    def runtime_check_longcmd(self, user_id):
        if not self.tasks['longcmd'][user_id].done():
            pass

    def runtime_check_points(self, ctx, cost, withdraw=True):
        if cost <= 0 or ctx.author_id == self.owner_id:
            return True
        try:
            _user_points = int(self.data['user_data'][str(ctx.author.id)]['points'])
            if cost > _user_points:
                raise InsufficientPoints('Not enough points.', insuf=(cost - _user_points), price=cost)
            else:
                if withdraw:
                    self.data['user_data'][str(ctx.author.id)]['points'] -= cost
                return True
        except (AttributeError, KeyError):
            self.logger.error('The user %s may not been intialized, exception traceback:%s\n' % (
                ctx.author.id, traceback.format_exc()))
            raise InsufficientPoints('Not enough points.', insuf=cost, price=cost)

    def runtime_check_guild_points(self, ctx, guild, cost, withdraw=True):
        if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
            if bool(self.conf['owner_permission_bypass']):
                return True
        if not guild:
            return False
        if cost <= 0:
            return True
        try:
            _user_points = int(self.data['guild_data'][str(guild.id)]['points'][str(ctx.author.id)])
            if cost > _user_points:
                raise InsufficientGuildPoints('Not enough points on this guild.', insuf=(cost - _user_points),
                                              price=cost)
            else:
                if withdraw:
                    self.data['guild_data'][str(guild.id)]['points'][str(ctx.author.id)] -= cost
                return True
        except (AttributeError, KeyError):
            self.logger.error('The user %s may not been intialized, exception traceback:%s\n' % (
                ctx.author.id, traceback.format_exc()))
            raise InsufficientGuildPoints('Not enough points on this guild.', insuf=cost, price=cost)

    # Checks the local permission level of the user in a certain guild.
    # Current default of the lplvalue levels:
    # -1 (Unverified member: if the guild have a private mode and this member is unverified:
    #    unable to write messages and view some channels)
    #  0 (Regular member: default permissions)
    #  1 (Message moderator: able to mute someone and manage messages, manage warnings, but
    #    not permitted to ban or kick someone.)
    #  2 (Member moderator: able to change nicknames, ban, kick, voice mute/deafen)
    #  3 (Guild controller: exclusive, able to modify some basic bot-side guild settings, but
    #    not permitted to manage channels/guild/roles etc.)
    #  4 (Channel editor: able to change the channels/categories name and description, excluding their overwrites)
    #  5 (Channel manager: same as above, but also allows to create/delete channels or categories
    #    and manage overwrites, refers to Manage Channels permission)
    #  6 (Guild editor: refers to Manage Guild permission)
    #  7 (Guild manager: refers to Manage Guild, Manage Roles, Manage Emojis, Manage Webhooks permissions)
    #  8 or more (Guild administrator: all possible permissions is granted, including Administrator,
    #    View Audit Log permissions)
    def runtime_check_guild_lpl(self, guild, user, lplvalue, raisee=True):
        if user.id == self.owner_id and 'owner_permission_bypass' in self.conf:
            if bool(self.conf['owner_permission_bypass']):
                return True

        # shortcut
        def fail():
            if user.id == self.owner_id:
                if raisee:
                    raise NotAllowedBypass(
                        'Regardless of the authority, you still don\'t have the permission to perform this action on '
                        'that guild.')
                else:
                    return False
            else:
                if raisee:
                    raise NotAllowed('You don\'t have the permission to perform this action on that guild.')
                else:
                    return False

        if not guild:
            return False
        elif guild.owner.id == user.id:
            return True
        try:
            if self.data['guild_data'][str(guild.id)]['user_permission_levels'][str(user.id)] >= lplvalue:
                return True
            member = guild.get_member(user.id)
            if member:
                for _role in member.roles:
                    if self.data['guild_data'][str(guild.id)]['role_settings'][str(_role.id)][
                                    'local_permission_level'] >= lplvalue:
                        return True
                fail()
            else:
                fail()
        except (AttributeError, KeyError):
            fail()

    def runtime_check_authorban(self, user, raisee=True):
        if user.id == self.owner_id:
            return True
        try:
            if self.data['user_data'][str(user.id)]['author_ban']:
                if 'date_exp' in self.data['user_data'][str(user.id)]['author_ban']:
                    date_exp = datetime.datetime(**self.data['user_data'][str(user.id)]['author_ban']['date_exp'])
                else:
                    date_exp = Never
                if 'reason' in self.data['user_data'][str(user.id)]['author_ban']:
                    reason = self.data['user_data'][str(user.id)]['author_ban']['reason']
                else:
                    reason = '--'
                if raisee:
                    raise AuthorBan('You have been banned by author. Reason: %s' % reason, reason=reason,
                                    date_exp=date_exp)
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True

    def runtime_check_authorban_here(self, user, guild, channel, raisee=True):
        if user.id == self.owner_id:
            return True
        try:
            if self.data['user_data'][str(user.id)]['author_ban_places']:
                # check if we have the guild.
                place = self.data['user_data'][str(user.id)]['author_ban_places'][str(guild.id)][str(channel.id)]
                # if we didn't got a KeyError exception, we ran on the place.
                if 'date_exp' in place:
                    date_exp = datetime.datetime(**place['date_exp'])
                else:
                    date_exp = Never
                if 'reason' in place:
                    reason = place['reason']
                else:
                    reason = '--'
                if raisee:
                    raise AuthorBanHere('You have been banned by author in that place. Reason: %s' % reason,
                                        reason=reason, date_exp=date_exp)
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True

    def runtime_check_guild_authoradminban(self, guild, user, raisee=True):
        if user.id == self.owner_id:
            return True
        if not guild:
            return True
        try:
            if self.data['guild_data'][str(guild.id)]['author_administration_ban']:
                _ban = self.data['guild_data'][str(guild.id)]['author_administration_ban']
                if raisee:
                    raise AuthorAdministrationBan(
                        'Administration of this guild has been forbidden. Reason: %s.' % _ban['reason'],
                        reason=_ban['reason'],
                        date_exp=(datetime.datetime(**_ban['date_exp']) if 'date_exp' in _ban else Never))
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True

    def runtime_check_authorban_guild(self, guild, user, raisee=True):
        if user.id == self.owner_id:
            return True
        if not guild:
            return True
        try:
            if self.data['guild_data'][str(guild.id)]['author_ban']:
                _ban = self.data['guild_data'][str(guild.id)]['author_ban']
                if raisee:
                    raise AuthorBanGuild('This guild has been banned by the author. Reason: %s.' % _ban['reason'],
                                         reason=_ban['reason'], date_exp=(
                            datetime.datetime(**_ban['date_exp']) if 'date_exp' in _ban else Never))
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True

    def runtime_check_guild_admin_ban(self, guild, user, raisee=True):
        if user.id == self.owner_id:
            return True
        if not guild:
            return True
        try:
            if self.data['guild_data'][str(guild.id)]['banned_users'][str(user.id)]:
                _ban = self.data['guild_data'][str(guild.id)]['banned_users'][str(user.id)]
                if raisee:
                    raise GuildAdminBan(
                        'You has been banned from this guild by guild\'s owner. Reason: %s.' % _ban['reason'],
                        reason=_ban['reason'], date_exp=datetime.datetime(**_ban['date_exp']))
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True

    def runtime_check_guild_ownership(self, guild, user, raisee=True):
        if user.id == self.owner_id:
            if 'owner_permission_bypass' in self.data:
                if self.data['owner_permission_bypass']:
                    return True
                else:
                    fail = True
            else:
                fail = True
            if user.id == guild.owner_id:
                fail = False
            if fail:
                if raisee:
                    raise NotAllowedBypass(
                        'Regardless of the authority, you still don\'t have the permission to perform this action on '
                        'that guild.')
                return False
        if user.id != guild.owner_id:
            if raisee:
                raise NotAllowed('This action is only allowed to guild\'s owner')
            return False

    def runtime_check_guild_higher_lpl(self, guild, user1, user2, raisee=True):
        if user1.id == self.owner_id and 'owner_permission_bypass' in self.conf:
            if bool(self.conf['owner_permission_bypass']):
                return True
        if user1 == user2:
            return False
        try:
            lpl1 = int(self.data['guild_data'][str(guild.id)]['user_permission_levels'][str(user1.id)])
        except (KeyError, ValueError, AttributeError):
            lpl1 = 0
        try:
            if user1.top_role:
                lpl1_ = int(self.data['guild_data'][str(guild.id)]['role_settings'][str(user1.top_role.id)][
                                'local_permission_level'])
                if lpl1_ > lpl1:
                    lpl1 = lpl1_
        except (KeyError, ValueError, AttributeError):
            pass
        try:
            lpl2 = int(self.data['guild_data'][str(guild.id)]['user_permission_levels'][str(user2.id)])
        except (KeyError, ValueError, AttributeError):
            lpl2 = 0
        try:
            if user2.top_role:
                lpl2_ = int(self.data['guild_data'][str(guild.id)]['role_settings'][str(user2.top_role.id)][
                                'local_permission_level'])
                if lpl2_ > lpl2:
                    lpl2 = lpl2_
        except (KeyError, ValueError, AttributeError):
            pass
        if lpl1 < lpl2:
            return True
        else:
            if user1.id == self.owner_id:
                if raisee:
                    raise NotAllowedBypass(
                        'Regardless of the authority, you still don\'t have the permission to perform this action'
                        ' on that guild.')
                else:
                    return False
            else:
                if raisee:
                    raise NotAllowed('You don\'t have the permission to perform this action on that guild.')
                else:
                    return False

    def loadMods(self):
        if not os.path.isdir(self.modfold):
            os.mkdir(self.modfold)
        self.logger.info('Loading modules from %s...' % os.path.abspath(self.modfold))
        # this is a modules.
        # I have discovered that this library (discord.py) is already have a modding solution (but it's too late), it is
        # called "extensions".
        # But instead of using this, I've made my own solution (oh why?)
        # TODO: depends and soft depends sort mechanism
        try:
            files = list()
            with os.scandir(self.modfold) as it:
                entry: os.DirEntry
                for entry in it:
                    if entry.is_file() and entry.name.endswith('.py'):
                        files.append(entry.name)
            if len(files) == 0:
                self.logger.warning('No mods has been loaded.')
                print('Warning! No mods has been loaded.')
            else:
                self.logger.info('{0} mods in order to load: {1}'.format(len(files), ', '.join(files)))
                for name in files:
                    self.loadMod(name)
        except (ImportError, IOError) as exc:
            tr = traceback.format_exc(exc)
            self.logger.critical('Failed to load mods: ' + str(exc) + '\n' + tr)
            print('Failed to load : ' + str(exc) + '\n' + tr)
            return False
        else:
            self.logger.info('Successfully loaded modules.')
            return True

    def loadMod(self, name):
        _flabel = name.split('.')[0]
        self.logger.info('Attempting to load \"%s\"...' % _flabel)
        _cspec = importlib.util.spec_from_file_location(_flabel, os.path.abspath('mods') + '/' + name)
        _mod = importlib.util.module_from_spec(_cspec)
        try:
            _loader = _cspec.loader
            _loader.exec_module(_mod)
        except Exception as exc:
            print('Failed to load module \"' + _flabel + '\": ' + str(exc))
            _exception = traceback.format_exc()
            self.logger.error('Module "' + _flabel + '" was failed to load. Exception traceback: ' + _exception)
            return False
        else:
            print('Module \"%s\" loaded successfully.' % _flabel)
            self.mods.append(_mod)
            self.mod_dict[_mod] = []
            print('Loading cogs in module %s...' % _mod.__name__)
            self.logger.info('Loading cogs in module %s...' % _mod.__name__)
            try:
                _cogs = _mod.getCogs()
                for cog in _cogs:
                    print('Loading cog %s...' % cog.__name__)
                    self.logger.info('Loading cog %s...' % cog.__name__)
                    try:
                        _cog = cog(self)
                        self.add_cog(_cog)
                        self.mod_dict[_mod].append(_cog)
                    except Exception:
                        print('Failed to load cog {0}:\n{1}'.format(cog.__name__, traceback.format_exc()))
                        self.logger.error('Failed to load cog {0}:\n{1}'.format(cog.__name__, traceback.format_exc()))
                        return False
            except AttributeError:
                print('Error: This module does not have getCogs function.')
                self.logger.error(
                    'Module "%s" does not have getCogs function.' % _mod.__name__ + '\n' + traceback.format_exc())
                return False
            else:
                print('Cogs loaded!')
                self.logger.info('Cogs for module "%s" loaded.' % _mod.__name__)
            try:
                _exceptions = _mod.getExceptions()
                self.mod_exc_dict[_mod] = _exceptions
                self.logger.info(
                    'Got %d exceptions to the ignorelist from module %s' % (len(_exceptions), _mod.__name__))
            except Exception:
                pass
            return True

    def unloadMod(self, modName):
        if modName not in [x.__name__ for x in self.mods]:
            self.logger.error('unloadMod: Module with name %s not found!' % modName)
            print('Module with name %s not found!' % modName)
            return False
        else:
            # current module
            _mod = self.mods[[x.__name__ for x in self.mods].index(modName)]
            self.logger.info('Preparing to unload module "%s"...' % _mod.__name__)
            # remove matching cogs from the bot
            _mod_classes = _mod.getCogs()
            _loaded_classes = [x.__class__ for x in self.cogs.values()]
            # perform the intersection between module cogs classes and loaded cogs
            # and then convert them into the module qualified names.
            _intersection = list([set(_mod_classes) & set(_loaded_classes)])
            for cog in _intersection:
                _qualif_name = list(self.cogs.keys())[list(_loaded_classes).index(list(cog)[0])]
                self.logger.info('Unloading cog {0} (class {1})'.format(_qualif_name, list(cog)[0].__name__))
                self.remove_cog(_qualif_name)
            del self.mods[self.mods.index(_mod)]
            del self.mod_dict[_mod]
            try:
                del self.mod_exc_dict[_mod]
            except KeyError:
                pass
            return True

    def remove_cog(self, name):
        if name in self.cogs:
            if hasattr(self.cogs[name], 'on_unload'):
                asyncio.create_task(self.cogs[name].on_unload())
        super().remove_cog(name)

    def reloadMod(self, modName):
        _file = str(modName) + '.py'
        if modName not in [x.__name__ for x in self.mods]:
            self.logger.error('unloadMod: Module with name %s not found!' % modName)
            print('Module with name %s not found!' % modName)
            return False
        elif not os.path.isfile('mods/' + _file):
            print('The file of the module %s has been moved or deleted, reload failed.' % modName)
            self.logger.warning('reloadMod: The file of the module %s is not found, reload failed.' % modName)
            return False
        else:
            self.logger.info('Reloading module %s' % modName)
            if not self.unloadMod(modName):
                self.logger.error('reloadMod: Module %s didn\'t unloaded. Reload failed.' % modName)
                return False
            if not self.loadMod(_file):
                self.logger.error('reloadMod: Module %s refused to load after unloading. Reload failed.' % modName)
                return False
            self.logger.info('Module %s reloaded successfully.' % modName)
            return True

    def loadModLangs(self, langfold_v, langvalid_v, langtemplate_v, default_lang_name='en_US'):
        """
        Loads and validates language files for modules. Returns a tuple (dict, dict, dict)
        First is a language dictionary, second is a dict of lists of missing fields, third is a dict of lists of
        insufficient (with wrong type) fields.
        """
        _langs = {}
        self.logger.info('Loading language settings for this cog...')
        if not os.path.isdir(langfold_v):
            os.mkdir(langfold_v)
        if 'default_lang' not in self.conf:
            self.logger.warning(
                '%s: The "default_lang" option is not set in the configuration, using "en_US" as the default.')
            self.conf['default_lang'] = "en_US"
        _files = []
        missing_fields = {}
        insuf_fields = {}
        with os.scandir(langfold_v) as files:
            file: os.DirEntry
            for file in files:
                if file.name.endswith('.json') and file.is_file():
                    _files.append(file)
        if len(_files) == 0:
            print(
                'No language settings was found! Generating default language file...\n - You can copy&paste, rename it'
                ' and edit them to create your own translation.')
            self.logger.warning(
                'Directory "%s" does not contain any language sets! Loading default built-in language...' % langfold_v)
            _langs[default_lang_name] = langtemplate_v
            _langs['default'] = _langs[default_lang_name]
            self.logger.info('Dumping built-in language into "%s" ...' % os.path.abspath(langfold_v))
            fl = open(langfold_v + f'/{default_lang_name}.json', 'x')
            fl.write(json.dumps(langtemplate_v, indent=True))
            fl.close()
            logger.info('Successfully created default language.')
            return _langs, missing_fields, insuf_fields
        else:
            if not conf['default_lang'] + '.json' in [x.name for x in _files]:
                print('%s: Language settings "%s" was not found!' % (__name__, conf['default_lang'] + '.json'))
                logger.warning('%s:  "%s/%s" language is not found! Using built-in default language instead...' % (
                    __name__, langfold_v, conf['default_lang'] + '.json'))
                _langs[default_lang_name] = langtemplate_v
                _langs['default'] = _langs[default_lang_name]
                self.logger.info('Dumping built-in language into "%s" ...' % os.path.abspath(langfold_v))
                fl = open(langfold_v + f'/{default_lang_name}.json', 'x')
                fl.write(json.dumps(langtemplate_v, indent=True))
                fl.close()
                logger.info('Successfully created default language.')
            # else:
            #    _langs['default'] = conf['default_lang']+'.json'
            _error_enc = False
            logger.info('Reading language content...')
            for file in _files:
                _flabel = file.name.split('.')[0]
                # fl = None
                # ld = None
                try:
                    fl = open(langfold_v + '/' + file.name, 'r')
                    ld = json.loads(fl.read())
                except json.JSONDecodeError as exc:
                    _exctext = traceback.format_exc()
                    print('Error: language file "%s" is damaged.' % file.name)
                    logger.critical('%s: language file "%s" is corrupted and unable to load.' % (_flabel, file.name))
                    print(exc)
                    fl.close()
                else:
                    # We are successfully got the language content, so we can validate them with validator pattern and
                    # by recursive function.
                    # The validation is need to keep out our program from KeyError or TypeError exceptions and notify
                    # the bot's owner about missing translation.
                    self.logger.info('Validating %s...' % _flabel)
                    _missing_fields, _insuf_fields = self.validateLang(ld, langvalid_v)
                    if len(_missing_fields) + len(_insuf_fields) > 0:
                        logger.critical(
                            '%s: Correctness test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.' % (
                                __name__, len(_missing_fields), ', '.join(_missing_fields), len(_insuf_fields),
                                ', '.join(_insuf_fields)))
                        print('%s: lang file is invalid. Please check the log.' % _flabel)
                        missing_fields[_flabel] = _missing_fields
                        insuf_fields[_flabel] = _insuf_fields
                    else:
                        logger.info('Successful correctness test! Language "%s" loaded.' % _flabel)
                    _langs[_flabel] = ld
            _langs['default'] = _langs[default_lang_name]
            return _langs, missing_fields, insuf_fields

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id

    async def start(self, *args, **kwargs):
        # --- Do something after that event loop has been started
        # invoke cog event on_eventloop_start if present
        for cog in self.cogs:
            if hasattr(self.cogs[cog], 'on_eventloop_start'):
                task = asyncio.create_task(self.cogs[cog].on_eventloop_start())

                def done_callback():
                    exc = task.exception()
                    if exc:
                        logger.error('Failed to invoke on_eventloop_start event of cog %s: %s: %s' % (
                            cog, exc.__class__.__name__, exc))

                if task.done():
                    done_callback()
                else:
                    task.add_done_callback(done_callback)
        # init authorban timers
        for _user in self.data['user_data']:
            if 'author_ban' in self.data['user_data'][_user]:
                if 'date_exp' in self.data['user_data'][_user]['author_ban']:
                    self.tasks['ab'][int(_user)] = asyncio.create_task(self.authorban_expiry_timer(int(_user)))
            # init place-authorban timers
            if 'author_ban_places' in self.data['user_data'][_user]:
                for guild in self.data['user_data'][_user]['author_ban_places']:
                    for channel in self.data['user_data'][_user]['author_ban_places'][guild]:
                        if 'date_exp' in self.data['user_data'][_user]['author_ban_places'][guild][channel]:
                            self.tasks['abh'][int(_user)] = asyncio.create_task(
                                self.authorbanplace_expiry_timer(int(_user), guild.id, channel.id))
        # init authorban guild timers
        for _guild in self.data['guild_data']:
            if 'author_ban' in self.data['guild_data'][_guild]:
                if 'date_exp' in self.data['guild_data'][_guild]['author_ban']:
                    self.tasks['abg'][int(_guild)] = asyncio.create_task(self.authorbanguild_expiry_timer(int(_guild)))
            elif 'banned_users' in self.data['guild_data'][_guild]:  # init guild admin's bans
                for _user in self.data['guild_data'][_guild]['banned_users']:
                    if 'date_exp' in self.data['guild_data'][_guild]['banned_users'][_user]:
                        if int(_guild) not in self.tasks['gab']:
                            self.tasks['gab'][int(_guild)] = {}
                        self.tasks['gab'][int(_guild)][int(_user)] = asyncio.create_task(
                            self.guildadminban_expiry_timer(int(_guild), int(_user)))
        await super().start(*args, **kwargs)

    def formatExactDuration(self, td, language, shorten=False, in_word=False, years=True, months=True, weeks=True,
                            days=True, hours=True, minutes=True, seconds=True):
        """
        This function formats the exact string of timedelta in the specified language.
        It uses the only seconds and convert it to the minutes, days, weeks, months etc.
        Example (in the default language):
             short: 1h 25min 59secs
            full: 1 hour 25 minutes 59 seconds
        """
        subtr = abs(td.total_seconds())
        strout = ''
        _lang_sc = language['contents']['formats']['duration']
        yearsc = subtr // 31557600
        if yearsc > 0 and years:
            _num_sc = str(nearList(_lang_sc['ys'].keys() if shorten else _lang_sc['years'].keys(), yearsc))
            strout += '%d%s ' % (yearsc, _lang_sc['ys'][_num_sc] if shorten else ' ' + _lang_sc['years'][_num_sc])
            subtr -= 31557600 * years
        monthsc = subtr // 2629800
        if monthsc > 0 and months:
            _num_sc = str(nearList(_lang_sc['mons'].keys() if shorten else _lang_sc['months'].keys(), monthsc))
            strout += '%d%s ' % (monthsc, _lang_sc['mons'][_num_sc] if shorten else ' ' + _lang_sc['months'][_num_sc])
            subtr -= 2629800 * monthsc
        weeksc = subtr // 604800
        if weeksc > 0 and weeks:
            _num_sc = str(nearList(_lang_sc['ws'].keys() if shorten else _lang_sc['weeks'].keys(), weeksc))
            strout += '%d%s ' % (weeksc, _lang_sc['ws'][_num_sc] if shorten else ' ' + _lang_sc['weeks'][_num_sc])
            subtr -= 604800 * weeksc
        daysc = subtr // 86400
        if daysc > 0 and days:
            _num_sc = str(nearList(_lang_sc['ds'].keys() if shorten else _lang_sc['days'].keys(), daysc))
            strout += '%d%s ' % (daysc, _lang_sc['ds'][_num_sc] if shorten else ' ' + _lang_sc['days'][_num_sc])
            if in_word and daysc == 1 and subtr % 86400 == 0:
                if td.total_seconds() < 0:
                    return language['contents']['formats']['date_relative']['yesterday']
                else:
                    return language['contents']['formats']['date_relative']['tomorrow']
            subtr -= 86400 * daysc
        hoursc = subtr // 3600
        if hoursc > 0 and hours:
            _num_sc = str(nearList(_lang_sc['hs'].keys() if shorten else _lang_sc['hours'].keys(), hoursc))
            strout += '%d%s ' % (hoursc, _lang_sc['hs'][_num_sc] if shorten else ' ' + _lang_sc['hours'][_num_sc])
            subtr -= 3600 * hoursc
        minsc = subtr // 60
        if minsc > 0 and minutes:
            _num_sc = str(nearList(_lang_sc['mins'].keys() if shorten else _lang_sc['minutes'].keys(), minsc))
            strout += '%d%s ' % (minsc, _lang_sc['mins'][_num_sc] if shorten else ' ' + _lang_sc['minutes'][_num_sc])
            subtr -= 60 * minsc
        if subtr > 0 and seconds:
            _num_sc = str(nearList(_lang_sc['secs'].keys() if shorten else _lang_sc['seconds'].keys(), subtr))
            strout += '%d%s' % (subtr, _lang_sc['secs'][_num_sc] if shorten else ' ' + _lang_sc['seconds'][_num_sc])
        return strout

    def formatAverageDuration(self, td, language, shorten=False, in_word=True):
        """
        This function formats the near of timedelta in the specified language.
        It uses the only seconds and convert it to the minutes, days, weeks, months etc.
        Example (in the default language):
             short: 2mons
            full: 2 months
        """
        subtr = abs(td.total_seconds())
        strout = language['contents']['formats']['date_relative']['in_exact_time'] + ' ' if in_word else ''
        _lang_sc = language['contents']['formats']['duration']
        yearsc = subtr // 31557600
        monthsc = subtr // 2629800
        weeksc = subtr // 604800
        daysc = subtr // 86400
        hoursc = subtr // 3600
        minsc = subtr // 60
        if yearsc > 0:
            _num_sc = str(nearList(_lang_sc['ys'].keys() if shorten else _lang_sc['years'].keys(), yearsc))
            strout += '%d%s' % (yearsc, _lang_sc['ys'][_num_sc] if shorten else ' ' + _lang_sc['years'][_num_sc])
            # subtr -= 31557600 * years
        elif monthsc > 0:
            _num_sc = str(nearList(_lang_sc['mons'].keys() if shorten else _lang_sc['months'].keys(), monthsc))
            strout += '%d%s' % (monthsc, _lang_sc['mons'][_num_sc] if shorten else ' ' + _lang_sc['months'][_num_sc])
            # subtr -= 2629800 * monthsc
        elif weeksc > 0:
            _num_sc = str(nearList(_lang_sc['ws'].keys() if shorten else _lang_sc['weeks'].keys(), weeksc))
            strout += '%d%s' % (weeksc, _lang_sc['ws'][_num_sc] if shorten else ' ' + _lang_sc['weeks'][_num_sc])
            # subtr -= 604800 * weeksc
        elif daysc > 0:
            _num_sc = str(nearList(_lang_sc['ds'].keys() if shorten else _lang_sc['days'].keys(), daysc))
            strout += '%d%s' % (daysc, _lang_sc['ds'][_num_sc] if shorten else ' ' + _lang_sc['days'][_num_sc])
            if in_word and daysc == 1:
                if td.total_seconds() < 0:
                    strout = language['contents']['formats']['date_relative']['yesterday']
                else:
                    strout = language['contents']['formats']['date_relative']['tomorrow']
            # subtr -= 86400 * daysc
        elif hoursc > 0:
            _num_sc = str(nearList(_lang_sc['hs'].keys() if shorten else _lang_sc['hours'].keys(), hoursc))
            # subtr -= 3600 * hoursc
            strout += '%d%s' % (hoursc, _lang_sc['hs'][_num_sc] if shorten else ' ' + _lang_sc['hours'][_num_sc])
        elif minsc > 0:
            _num_sc = str(nearList(_lang_sc['mins'].keys() if shorten else _lang_sc['minutes'].keys(), minsc))
            # subtr -= 60 * minsc
            strout += '%d%s' % (minsc, _lang_sc['mins'][_num_sc] if shorten else ' ' + _lang_sc['minutes'][_num_sc])
        elif subtr > 0:
            _num_sc = str(nearList(_lang_sc['secs'].keys() if shorten else _lang_sc['seconds'].keys(), subtr))
            strout += '%d%s' % (subtr, _lang_sc['secs'][_num_sc] if shorten else ' ' + _lang_sc['seconds'][_num_sc])
        else:
            strout = language['contents']['formats']['date_relative']['now']
        return strout

    def renderMessage(self, language, default_language, message_type, config, default_config=None, definition=None,
                      definition_required=False, fields=None, date_relative=False, show_direction=False,
                      duration_options: dict = None, field_inline=True, **kwargs):
        """
        Resolves a language node with defined language and parses all optional arguments with formatted strings.
        Returns a dictionary with content or Embed.
        language: dict. The language is to be used to render a message.
        default_language: dict. The fallback language that could be used if the node is missing or encountered an error.
        message_type: str. The name of the section in the messages.
        config: dict. The configuration data with message settings.
        default_config: dict. The default configuration settings in the case of error. Not used yet.
        definition: str. Optional. The alternative template. If not set or doesn't exist it couldn't be used.
        fields: list. Optional. Contains a dictionaries with 'title' and 'value' subdictionaries.
            Field formatting is separate from regular
        date_relative: bool. Show relative date and time from now.
        by_day: bool. Show only amount of days left.
            If the specified time falls to the next day, it shows "Tomorrow" instead of "1 day",
            but if the time falls on the current day, it shows "Today".
            If the specified time falls to the previous day, it shows "Yesterday".
        kwargs: map. Formatting values for template.
        """
        if duration_options is None:
            duration_options = {}
        assert bool(definition) >= definition_required, 'definition is required, but not given'
        if (message_type not in config['messages']) or (message_type not in language["contents"]["messages"]):
            self.logger.error('renderMessage: unknown message type: ' + message_type)
            return {'content': 'Error occurred, please contact to the bot\'s owner'}

        def getDateFormatter(val):
            return {
                'year': '%0.4d' % val.year,
                'month': val.month,
                'month_name': language['contents']['formats']['months'][str(val.month)],
                'month_name_capital': language['contents']['formats']['months'][str(val.month)].capitalize(),
                'month_sname': language['contents']['formats']['mons'][str(val.month)],
                'month_sname_capital': language['contents']['formats']['mons'][str(val.month)].capitalize(),
                'day': val.day,
                'dow': val.isoweekday(),
                'dow_name': language['contents']['formats']['days_of_week'][str(val.isoweekday())],
                'dow_name_capital': language['contents']['formats']['days_of_week'][str(val.isoweekday())].capitalize(),
                'dow_sname': language['contents']['formats']['dow'][str(val.isoweekday())],
                'dow_sname_capital': language['contents']['formats']['dow'][str(val.isoweekday())].capitalize(),
                'hour': '%0.2d' % val.hour,
                '12-hour': '%0.2d' % val.hour if val.hour <= 12 else '%0.2d' % (val.hour % 12),
                'minute': '%0.2d' % val.minute,
                'second': '%0.2d' % val.second,
                'meridiem': 'AM' if val.hour <= 12 else 'PM'
            }

        # reconstruct **kwargs and convert every argument but dict and others
        def convert(kws):
            _formatter = {}
            for k in kws:
                val = kws[k]
                if type(val) == str:
                    _formatter[k] = val
                elif type(val) in [int, float, complex]:
                    _formatter[k] = str(val)
                elif type(val) == bool:
                    if val:
                        _formatter[k] = language['contents']['formats']['logic']['true'].capitalize()
                    else:
                        _formatter[k] = language['contents']['formats']['logic']['false'].capitalize()
                elif type(val) == State:
                    if bool(val):
                        _formatter[k] = language['contents']['formats']['switch']['on']
                    else:
                        _formatter[k] = language['contents']['formats']['switch']['off']
                elif type(val) == Partially:
                    _formatter[k] = language['contents']['formats']['logic']['partially'].capitalize()
                elif val is None:
                    _formatter[k] = language['contents']['formats']['logic']['none'].capitalize()
                elif val == Never:
                    _formatter[k] = language['contents']['formats']['date_relative']['never'].capitalize()
                elif val == Forever:
                    _formatter[k] = language['contents']['formats']['date_relative']['forever'].capitalize()
                elif type(val) == datetime.datetime:
                    if date_relative:
                        td = val - datetime.datetime.now()
                        direction = language['contents']['formats']['duration']['direction']
                        if show_direction:
                            direction = ' ' + direction['after'] if td < datetime.timedelta(0) else ' ' + direction[
                                'before']
                        else:
                            direction = ''
                        _formatter[k] = self.formatExactDuration(td, language, **duration_options) + direction
                    else:
                        _formatter[k] = language['contents']['formats']['date_format'] % getDateFormatter(val)
                elif type(val) == datetime.timedelta:
                    if date_relative:
                        direction = language['contents']['formats']['duration']['direction']
                        if show_direction:
                            direction = ' ' + direction['after'] if val < datetime.timedelta(0) else ' ' + direction[
                                'before']
                        else:
                            direction = ''
                        _formatter[k] = self.formatExactDuration(val, language, **duration_options) + direction
                    else:
                        dt = datetime.datetime.now() + val
                        _formatter[k] = language['contents']['formats']['date_format'] % getDateFormatter(dt)
                elif type(val) == inspect.Parameter:
                    _formatter[k] = val.name
                elif type(val) in [list, tuple, set]:
                    _dict = {}
                    inc = 0
                    for el in val:
                        _dict[inc] = el
                    _conv = convert(_dict).values()
                    _formatter[k] = ', '.join(_conv)
                else:
                    _formatter[k] = repr(val)
            return _formatter

        formatter = convert(kwargs)
        # mandatory options: there is no mandatory options, you can send an empty embed if you want to.
        _lang_sc = language["contents"]['messages'][message_type]
        _conf_sc = config['messages']

        def format_if_str(item: Union[str, dict], keyitem=""):  # recursive
            try:
                if type(item) is str:
                    return item % formatter
                if type(item) is dict:
                    _origin = {}
                    for key in item:
                        _origin[key] = format_if_str(item[key], keyitem="%s:%s" % (keyitem, key))
                    return _origin
                return item
            except KeyError as exc:
                logger.error("Failed to format %s (%s:%s): %s" % (keyitem, message_type, definition, exc))
                return item

        def parse():
            # this is replacement for the above code
            self.debug_print('parse called: _lang_sc = \n%s\n_conf_sc = \n%s' % (repr(_lang_sc), repr(_conf_sc)),
                             'message_rendering')

            def decl(item) -> Union[str, dict, None]:
                self.debug_print('decl called with item %s' % (repr(item)), 'message_rendering')
                if 'definitions' in language["contents"]['messages'][message_type]:
                    self.debug_print('this language shortcut (_lang_sc) has definitions', 'message_rendering')
                    if definition and (definition in _lang_sc['definitions']) and (
                            item in _lang_sc['definitions'][definition]):
                        self.debug_print(
                            'definition is given, definition exists in definitions, item exists in this definition',
                            'message_rendering')
                        return format_if_str(_lang_sc['definitions'][definition][item], item)
                    elif definition:
                        self.debug_print('definition is given, but neither definition exists nor item is found in it.',
                                         'message_rendering')
                        if (definition not in _lang_sc['definitions']) and definition_required:
                            self.debug_print('the problem is - definition doesn\'t exists.', 'message_rendering')
                            logger.error("No definition found: %s" % definition)
                            return ''
                        elif (item not in _lang_sc['definitions'][definition]) and definition_required:
                            self.debug_print('the problem is - the item doesn\'t exist in definition.',
                                             'message_rendering')
                            logger.error("No item found in %s: %s" % (definition, item))
                            return ''
                        elif not definition_required:
                            # this is the point where we have the problem, but it's not eventually necessary to
                            self.debug_print('definition is not required, meaning that we can replace item by default',
                                             'message_rendering')
                            if definition not in _lang_sc['definitions']:
                                self.debug_print('definition not found, using default item from outside',
                                                 'message_rendering')
                                if item in _lang_sc:
                                    self.debug_print('item found in message type', 'message_rendering')
                                    return format_if_str(_lang_sc[item], item)
                                else:
                                    self.debug_print('no default item is provided, returning None', 'message_rendering')
                                    return ''
                            elif item not in _lang_sc['definitions'][definition]:
                                self.debug_print(
                                    'item is not found on this definition, falling back to the default item given on '
                                    'the root',
                                    'message_rendering')
                                if item in _lang_sc:
                                    self.debug_print('item found in message type', 'message_rendering')
                                    return format_if_str(_lang_sc[item], item)
                                else:
                                    self.debug_print('no default item is provided, returning None', 'message_rendering')
                                    return ''
                            else:
                                self.debug_print('how the heck did we get into here? ._.', 'message_rendering')
                                return ''
                        else:
                            self.debug_print(
                                'definition is required, item and definition probably exists in the dict, then how '
                                'the heck did we get into there? ',
                                'message_rendering')
                            return format_if_str(_lang_sc['definitions'][definition][item], item)
                    else:
                        self.debug_print(
                            'no definition, probably no item and also no requirement for definition. Returning '
                            'default item if it exists',
                            'message_rendering')
                        if item in _lang_sc:
                            self.debug_print('got default item in _lang_sc', 'message_rendering')
                            return format_if_str(_lang_sc[item], item)
                        else:
                            self.debug_print('no default item is given', 'message_rendering')
                            return ''
                else:
                    self.debug_print('there\'s no possible definitions for this message type: %s' % message_type,
                                     'message_rendering')
                    if item in _lang_sc:
                        self.debug_print('item is present, returning an item')
                        return format_if_str(_lang_sc[item], item)
                    else:
                        self.debug_print('no default item exist, returning None', 'message_rendering')
                        return ''

            if _conf_sc[message_type]['embed']:
                embed = discord.embeds.Embed(
                    title=decl('title'),
                    description=decl('description'),
                    color=(_conf_sc[message_type]['color'] if 'color' in _conf_sc[message_type] else None)
                )
                if _conf_sc[message_type]['use_icon']:
                    embed.set_thumbnail(url=_conf_sc[message_type]['icon_url'])
                _footer = decl('footer')
                if _footer:
                    embed.set_footer(text=_footer)
                _author = decl('author')
                if _author:
                    embed.set_author(name=_author, icon_url=(_conf_sc[message_type]['author_icon_url']
                                                             if 'author_icon_url' in _conf_sc[
                        message_type] else discord.Embed.Empty))
                if fields and ('fields' in _lang_sc or 'fields' in _lang_sc['definitions'][definition]):
                    for field in fields:
                        embed.add_field(name=decl('fields')['name'] % convert(field['name']),
                                        value=decl('fields')['value'] % convert(field['value']), inline=field_inline)
                return {'embed': embed}
            else:
                _title = decl('title')
                _description = decl('description')
                _footer = decl('footer')
                _author = decl('author')
                _fields = ''
                if fields and ('fields' in _lang_sc or 'fields' in _lang_sc['definitions'][definition]):
                    for field in fields:
                        _fields += '**%s**\n%s\n' % (
                            decl('fields')['name'] % field['name'], decl('fields')['value'] % field['value'])
                _content = \
                    ('**' + _author + '**\n' if _author else '') + \
                    ('**' + _title + '**\n' if _title else '') + \
                    (_description + '\n' if _description else '') + \
                    _fields + ('`' + _footer + '`' if _footer else '')
                return {'content': _content if _content else None}

        try:
            return parse()
        except KeyError:
            print('Failed to render %s message!' % message_type)
            self.logger.error('renderMessage: %s' % traceback.format_exc())
            _lang_sc = default_language["contents"]['messages'][message_type]
            _conf_sc = default_config['messages']
            return parse()

    def getLanguage(self, userid, guildid, languages):
        """
        Returns language code for current user or guild.
        When the user didn't set the language for the bot, the function returns a language code for the guild or the
        default language.
        If the guild has 'language_override' setting, the function returns a language code of the guild regardless of
        the user setting,
        but if the user doesn't have 'language_override' setting enabled (it couldn't be set and also deprecated).
        """
        # elangs - existing lang codes
        self.debug_print('retrieving language for userid=%s and guildid=%s' % (userid, guildid), 'bot_utility')
        if type(userid) not in (int, type(None)):
            self.debug_print('type of given userid is not integer, but %s instead' % type(userid).__name__,
                             'bot_utility')
            raise ValueError('userid: int or NoneType expected, got %s.' % type(userid).__name__)
        if type(guildid) not in (int, type(None)):
            self.debug_print('type of given userid is not integer, but %s instead' % type(guildid).__name__,
                             'bot_utility')
            raise ValueError('userid: int or NoneType expected, got %s.' % type(guildid).__name__)
        if (userid == 0 and guildid == 0) or (userid is None and guildid is None):
            self.debug_print('neither guildid nor userid is provided')
            return 'default'
        if type(languages).__name__ == 'dict':
            elangs = languages.keys()
        elif type(languages).__name__ in ['set', 'list', 'tuple', 'dict_keys']:
            elangs = list(languages)
        else:
            elangs = list(languages)
        self.debug_print('the given list of available languages is: %s' % elangs, 'bot_utility')
        # print('elangs '+str(elangs))
        try:
            if userid is not None:
                self.debug_print('userid is specified', 'message_rendering')
                user_lang = self.data['user_data'][str(userid)]['language'] \
                    if 'language' in self.data['user_data'][str(userid)] \
                    else ''
            else:
                self.debug_print('user is not specified', 'bot_utility')
                user_lang = ''
        except KeyError:
            user_lang = ''
            self.debug_print('user doesn\'t have custom language set', 'bot_utility')
        # print('user_lang '+str(user_lang))
        try:
            if guildid is not None:
                self.debug_print('guild is provided.', 'bot_utility')
                try:
                    if 'lang_override' in self.data['guild_data'][str(guildid)]:
                        self.debug_print('guild does have language override', 'bot_utility')
                        guild_override = self.data['guild_data'][str(guildid)]['lang_override']
                    else:
                        self.debug_print('guild doesn\'t have language override', 'bot_utility')
                        guild_override = False
                except KeyError:
                    self.debug_print('guild probably doesn\'t have language override', 'bot_utility')
                    guild_override = False
                self.debug_print('guild override is set to %s' % guild_override, 'bot_utility')
                # print('guild_override '+str(guild_override))
                try:
                    if 'lang_override' in self.data['user_data'][str(userid)]:
                        self.debug_print('user has language override', 'bot_utility')
                        user_override = self.data['user_data'][str(userid)]['lang_override']
                    else:
                        self.debug_print('user doesn\'t have language override', 'bot_utility')
                        user_override = False
                except KeyError:
                    self.debug_print('user probably doesn\'t have language override', 'bot_utility')
                    user_override = False
                self.debug_print('user language override is set to %s' % user_override, 'bot_utility')
                # print('user_override '+str(guild_override))
                if user_override:
                    self.debug_print('returning user\'s overrider language', 'bot_utility')
                    if user_lang not in elangs:
                        self.debug_print('user language is not in present languages, returning default instead',
                                         'bot_utility')
                        # print('user_lang not in elangs, return default')
                        return 'default'
                    return user_lang
                elif guild_override:
                    self.debug_print('user doesn\'t have language overrider, but guild does have', 'bot_utility')
                    _lang = self.data['guild_data'][str(guildid)]['language']
                    if _lang in elangs:
                        self.debug_print('language in supported langs', 'bot_utility')
                        return _lang
                    else:
                        self.debug_print('language not in supported langs', 'bot_utility')
                        return 'default'
                else:
                    try:
                        if 'language' in self.data['user_data'][str(userid)]:
                            # print('this user have a language setting')
                            return user_lang if user_lang in elangs else 'default'
                    except KeyError:
                        pass
                    try:
                        if 'language' in self.data['guild_data'][str(guildid)]:
                            # print('this guild have a language setting')
                            _lang = self.data['guild_data'][str(guildid)]['language']
                            # print('returning '+_lang if _lang in elangs else 'default')
                            return _lang if _lang in elangs else 'default'
                    except KeyError:
                        pass
                    return 'default'
            else:
                self.debug_print('guild is not given, returning user_lang', 'bot_utility')
                return user_lang if user_lang in elangs else 'default'
        except KeyError:
            # print('got keyerror exception')
            # print(traceback.format_exc())
            return 'default'

    def parseDuration(self, durations, timestr):
        _timestr = timestr.split(',')
        if len(_timestr) == 1 and timestr.isnumeric():
            return datetime.timedelta(seconds=int(timestr))
        _td = datetime.timedelta()
        durationsd = durations.copy()
        if 'direction' in durationsd:
            del durationsd['direction']
        for nd in _timestr:
            for ew in durationsd:
                for ind in durationsd[ew].keys():
                    if nd.endswith(durationsd[ew][ind]):
                        num = nd[:len(nd) - len(durationsd[ew][ind])]
                        if not num.isnumeric():
                            raise IncorrectDuration("duration node must starts with number", node=num)
                        _mul = 0
                        if ew in ['seconds', 'secs']:
                            _mul = 1
                        elif ew in ['minutes', 'mins']:
                            _mul = 60
                        elif ew in ['hours', 'hs']:
                            _mul = 3600
                        elif ew in ['days', 'ds']:
                            _mul = 86400
                        elif ew in ['weeks', 'ws']:
                            _mul = 604800
                        elif ew in ['months', 'mons']:
                            _mul = 2629800
                        elif ew in ['years', 'ys']:
                            _mul = 31557600
                        else:
                            raise IncorrectDuration("unknown duration node type", node=num)
                        _td += datetime.timedelta(seconds=int(num) * _mul)
        return _td

    def getNotifyChannel(self, guild):
        """Returns messageable TextChannel that was set manually, otherwise return most viewable available channel
        Used for directly messaging to the guild"""
        if str(guild.id) not in self.data['guild_data']:
            self.data['guild_data'][str(guild.id)] = {}

        if 'notify_channel' in self.data['guild_data'][str(guild.id)]:
            return self.get_channel(int(self.data['guild_data'][str(guild.id)]['notify_channel']))
        # get all accessible
        _channels = []
        _counts = []
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                _channels.append(channel)
                _counts.append(len(channel.members))
        _sc = _counts.copy()
        _sc.sort(reverse=True)
        return _channels[_counts.index(_sc[0])]


def main():
    logger.setLevel(logging.INFO)
    tm = time.localtime()
    if not os.path.isdir(logfold):
        os.mkdir(logfold)
    if not os.path.isdir(modfold):
        os.mkdir(modfold)
    if not os.path.isdir(langfold):
        os.mkdir(langfold)
    handler = logging.FileHandler(
        filename=logfold + '/discord-' + '%0.2d' % tm.tm_mday + '-' + '%0.2d' % tm.tm_mon + '-' + '%0.4d' % (
            tm.tm_year) + '_' + enzero(
            tm.tm_hour) + '-' + '%0.2d' % tm.tm_min + '-' + '%0.2d' % tm.tm_sec + '.log', encoding='utf-8',
        mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    # Perform configuration loading.
    global conf
    loadConf()
    loadData()
    # Exit from the program if the language load failed.
    if not loadLangs():
        exit(1)
    loop = asyncio.get_event_loop()
    intents = discord.Intents(members=True, bans=True, emojis=True, guilds=True, integrations=True, webhooks=True,
                              invites=True, voice_states=True, messages=True, guild_messages=True, dm_messages=True,
                              reactions=True, guild_reactions=True, dm_reactions=True, typing=True, guild_typing=True,
                              dm_typing=True)
    if 'owner' in conf.keys():
        bot = PtDiscordBot(logger, conf, data, lang,
                           command_prefix=discord.ext.commands.when_mentioned_or(*conf['prefix']),
                           owner_id=int(conf['owner']), intents=intents)
    else:
        bot = PtDiscordBot(logger, conf, data, lang,
                           command_prefix=discord.ext.commands.when_mentioned_or(*conf['prefix']), intents=intents)

    @bot.command()
    @commands.is_owner()
    async def shutdown(ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            msg = await ctx.channel.send('Cannot delete message')
            await asyncio.sleep(1.6)
            await msg.delete()
        await loop.pwroff()

    @bot.listen()
    async def on_command_error(ctx, exc):
        mod_exc_summary = []
        for cont in bot.mod_exc_dict.values():
            if cont is not None:
                mod_exc_summary.extend(cont)
        if type(exc) not in mod_exc_summary:
            langcode = bot.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, bot.lang.keys())
            if isinstance(exc, ProcessingIdle):
                # do nothing
                return
            if isinstance(exc, GuildAdminBlockCategory) or isinstance(exc, GuildAdminBlockChannel):
                return
            elif isinstance(exc, commands.CheckFailure):
                msgtype = 'check_failures'
                known_exceptions = bot.lang[langcode]['contents']['messages']['check_failures']['definitions'].keys()
            elif isinstance(exc, commands.CommandError):
                msgtype = 'command_errors'
                known_exceptions = bot.lang[langcode]['contents']['messages']['command_errors']['definitions'].keys()
            elif isinstance(exc, discord.DiscordException):
                msgtype = 'common_errors'
                known_exceptions = bot.lang[langcode]['contents']['messages']['common_errors']['definitions'].keys()
            else:
                msgtype = 'command_errors'
                known_exceptions = []
            if type(exc).__name__ in known_exceptions:  # v Whoops, we left an exploit
                kws = exc.__dict__
                kws['exception'] = str(exc)
                await ctx.send(**bot.renderMessage(bot.lang[langcode], langtemplate, msgtype, bot.conf, conftemplate,
                                                   definition=type(exc).__name__, **kws))
            else:
                await ctx.send(
                    **bot.renderMessage(bot.lang[langcode], langtemplate, 'command_errors', bot.conf, conftemplate,
                                        definition=None, exception=str(exc)))
                logger.error("Got an exception while performing requested command: (%s) %s\n%s" % (
                    type(exc).__name__, str(exc), traceback.format_exc()))
        else:
            # Let the cogs to handle the error by itself.
            pass

    async def logmsgdeleted(msg):
        assert not isinstance(msg.channel, discord.GroupChannel), 'How the fuck bot appears on the group channel?'
        if isinstance(msg.channel, discord.DMChannel):
            destname = 'DM UID: {0}|{1}#{2}'.format(str(msg.channel.recipient.id), msg.channel.recipient.name,
                                                    msg.channel.recipient.discriminator)
        elif isinstance(msg.channel, discord.TextChannel):
            destname = 'channel pairs:{0}={1}|{2}={3}'.format(str(msg.channel.guild.id), str(msg.channel.id),
                                                              msg.channel.guild.name, msg.channel.name)
        else:
            raise Exception('Unknown channel type')
        logger.info(str(
            msg.author.id) + '|' + msg.author.name + '#' + msg.author.discriminator + ' message deleted in ' + destname
                    + ': ' + msg.content)

    bot.add_listener(logmsgdeleted, 'on_message_delete')
    bot.loadConf = loadConf
    loop.dbot = bot
    loop.d = discord
    loop.dcmd = commands
    loop.sys = sys

    async def bot_shutdown():
        print('Bot has been stopped, saving data...')
        logger.info('Shutting down and saving data...')
        fl = open(dataf, 'w')
        fl.write(json.dumps(data, indent=True))
        fl.close()
        logger.info('Data saved, cancelling all pending tasks...')
        for _type in bot.tasks:
            # if type is 'longcmd':
            #    for usertasks in bot.tasks['longcmd'].values():
            #        for task in usertasks:
            #            if not task.cancelled():
            #                task.cancel()
            if _type != 'abh':
                for guild in bot.tasks['abh']:
                    for channel in bot.tasks['abh'][guild]:
                        for task in bot.tasks['abh'][guild][channel].values():
                            if not task.cancelled():
                                task.cancel()
            else:
                for task in bot.tasks[_type].values():
                    if not task.cancelled():
                        task.cancel()
        logger.info('Logging out...')
        await loop.dbot.close()

    loop.pwroff = bot_shutdown
    loop.run_until_complete(bot.start(conf['token']))
    # loop.run_until_complete(shutdown())
    return 0


if __name__ == '__main__':
    sys.exit(main())

print("ENd...")
