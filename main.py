#!/usr/bin/env python3

import discord, asyncio, time, datetime, logging, math, json, traceback, importlib, inspect
from discord.ext import commands
from threading import Thread
import sys, os

conff = 'conf.json'
dataf = 'data.json'
langfold = 'languages'
logfold= 'logs'
modfold = 'mods'
conf = {}
data = {}
lang = {}

#Logic primitives

class Never:
    pass
class Forever:
    pass
class Partially:
    pass
class State:
    def __init__(self, state:bool):
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
# TODO:

#Default configuration.
conftemplate = {
    'token':'put your bot token here',
    'prefix':['&'],
    'default_lang':'en_US',
    'owner_permission_bypass': False,
    'messages': {
        'check_failures': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':16711680,
            'show_undefined': False
        },
        'command_errors': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':16711680,
            'show_undefined': False
        },
        'common_errors': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':16711680,
            'show_undefined': False
        },
        'custom_errors': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':16711680,
            'show_undefined': False
        },
        'notifications': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':0xFF0F00
        },
        'info': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':0x1A1AFF
        },
        'warning': {
            'embed': True,
            'use_icon': False,
            'icon_url': 'https://example.com',
            'color':0xFFFF00
        },
        'response': {
            'embed': False
        }
    }
}
#Default language (english)
langtemplate = {
    'name': 'English (US)',
    'contents': {
        'formats': {
            'date_format': '%(dow_sname_capital)s, %(month_sname_capital)s %(day)s. %(year)s. %(12-hour)s:%(minute)s %(meridiem)s',
            'duration': {
                'seconds': {
                    '1': 'second',
                    '2': 'seconds'
                },
                'secs': {
                    '1': 'sec',
                    '2': 'secs'
                },
                'minutes': {
                    '1': 'minute',
                    '2': 'minutes'
                },
                'mins': {
                    '1': 'min',
                    '2': 'mins'
                },
                'hours': {
                    '1': 'hour',
                    '2': 'hours'
                },
                'hs': {
                    '1': 'h'
                },
                'days': {
                    '1': 'day',
                    '2': 'days'
                },
                'ds': {
                    '1': 'd'
                },
                'weeks': {
                    '1': 'week',
                    '2': 'weeks'
                },
                'ws': {
                    '1': 'w'
                },
                'months': {
                    '1': 'month',
                    '2': 'months'
                },
                'mons': {
                    '1': 'mon'
                },
                'years': {
                    '1': 'year',
                    '2': 'years'
                },
                'ys': {
                    '1': 'y'
                },
                'direction': {
                    'before': 'left',
                    'after': 'ago'
                }
            },
            'days_of_week': {
                '1': 'monday',
                '2': 'tuesday',
                '3': 'wednesday',
                '4': 'thursday',
                '5': 'friday',
                '6': 'saturday',
                '7': 'sunday'
            },
            'dow': {
                '1': 'mon',
                '2': 'tue',
                '3': 'wed',
                '4': 'thu',
                '5': 'fri',
                '6': 'sat',
                '7': 'sun'
            },
            'months': {
                '1': 'january',
                '2': 'february',
                '3': 'march',
                '4': 'april',
                '5': 'may',
                '6': 'june',
                '7': 'july',
                '8': 'august',
                '9': 'september',
                '10': 'october',
                '11': 'november',
                '12': 'december'
            },
            'mons': {
                '1': 'jan',
                '2': 'feb',
                '3': 'mar',
                '4': 'apr',
                '5': 'may',
                '6': 'jun',
                '7': 'jul',
                '8': 'aug',
                '9': 'sep',
                '10': 'oct',
                '11': 'nov',
                '12': 'dec'
            },
            'logic': {
                'true': 'yes',
                'false': 'no',
                'partially': 'partially',
                'none': 'not set'
            },
            'date_relative': {
                'today': 'today',
                'tomorrow': 'tomorrow',
                'yesterday': 'yesterday',
                'never': 'never',
                'forever': 'forever',
                'now': 'now',
                'in_exact_time': 'in'
            },
            'switch': {
                'on': 'turned on',
                'off': 'turned off'
            }
        },
        'messages': {
            'check_failures': {
                'title': 'Action is forbidden.',
                'description': '--- %(exception)s',
                'definitions': {
                    'AuthorBan': {
                        'title': 'Action is forbidden.',
                        'description': 'You have been banned from this bot by author.\nReason: %(reason)s.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'AuthorAdministrationBan': {
                        'title': 'Administration of this guild is forbidden.',
                        'description': 'The bot control has been banned on this guild by author.\nReason: %(reason)s.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'AuthorBanHere': {
                        'title': 'Action is forbidden here.',
                        'description': 'You have been banned from this bot by author from here.\nReason: %(reason)s.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'AuthorBanGuild': {
                        'title': 'This guild is forbidden.',
                        'description': 'This guild has been banned from this bot by author.\nReason: %(reason)s.\nbut anyway you can use bot in DM\'s or on another guilds.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'GuildAdminBan': {
                        'title': 'Action is forbidden here.',
                        'description': 'You have been banned from this bot by guild\'s admin from this guild.\nReason: %(reason)s.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'GuildAdminBanHere': {
                        'title': 'Action is forbidden here.',
                        'description': 'You have been banned from this bot by guild\'s admin from here.\nReason: %(reason)s.',
                        'footer': 'Expiration date: %(date_exp)s'
                    },
                    'GuildAdminBlockChannel': {
                        'title': 'This channel is blocked.',
                        'description': 'You can\'t use bot commands in this channel.'
                    },
                    'GuildAdminBlockCategory': {
                        'title': 'This category is blocked.',
                        'description': 'You can\'t use bot commands in this category.'
                    },
                    'NotOwner': {
                        'title': 'Action is forbidden.',
                        'description': 'This command is allowed for bot author only.'
                    },
                    'InsufficientPoints': {
                        'title': 'Not enough points!',
                        'description': 'You need at least %(price)s points (%(insuf)s need more.) in order to perform that payment.'
                    },
                    'InsufficientGuildPoints': {
                        'title': 'Not enough guild points!',
                        'description': 'You need at least %(price)s guild points (%(insuf)s need more.) in order to perform that payment.',
                    },
                    'NoPrivateMessage': {
                        'title': 'Don\'t use it here.',
                        'description': 'You cannot use that command in DM\'s'
                    },
                    'PrivateMessageOnly': {
                        'title': 'Don\'t use it here.',
                        'description': 'You can use that command in bot DM only.'
                    },
                    'MissingPermissions': {
                        'title': 'You don\'t have enough permissions.',
                        'description': 'You need to have "%(missing_perms)s" in order to perform that command.'
                    },
                    'BotMissingPermissions': {
                        'title': 'The bot doesn\'t have enough permissions.',
                        'description': 'I need at least "%(missing_perms)s" in order to perform that command here.'
                    },
                    # DEPRECATED: Since this bot is public, we're deprecated these library-side checks.
                    'MissingRole': {
                        'title': 'Action is forbidden.',
                        'description': 'You don\'t have a %(role_mention)s role.'
                    },
                    'BotMissingRole': {
                        'title': 'The bot doesn\'t have a %(role_mention)s role.',
                        'description': 'I can\'t perform this action without this role.'
                    },
                    'MissingAnyRole': {
                        'title': 'Action is forbidden.',
                        'description': 'You do not have (at least one) these roles: %(role_mentions)s'
                    },
                    'BotMissingAnyRole': {
                        'title': 'The bot doesn\'t have at least one role to do that.',
                        'description': 'I need at least one of those roles: %(role_mentions)s'
                    },
                    # --------------------------------------------------------------------- #
                    'NSFWChannelRequired': {
                        'title': 'This is not allowed here.',
                        'description': 'This command is allowed for NSFW channel only.'
                    },
                    'NotAllowed': {
                        'title': 'Action is forbidden.',
                        'description': 'You cannot perform this action here.'
                    },
                    'NotAllowedBypass': {
                        'title': 'Action performance rejected.',
                        'description': 'Stop! You do not have permission issued by the guild owner for this action.',
                        'footer': 'If you\'re a bad guy, you can bypass this restriction, but you aren\'t?'
                    }
                }
            },
            'command_errors': {
                'title': 'An unknown error has occurred.',
                'description': 'Please, contact to the author',
                'definitions': {
                    'MissingRequiredArgument': {
                        'title': 'Missing argument.',
                        'description': 'You have missed the \"%(param)s\" parameter.'
                    },
                    'TooManyArguments': {
                        'title': 'Too many arguments.',
                        'description': 'This command does not require so much arguments.'
                    },
                    'CommandNotFound': {
                        'title': 'Unknown command.',
                        'description': 'We don\'t know that command you invoked, \nif you want to see the full list of available commands, type **help**',
                    },
                    'DisabledCommand': {
                        'title': 'Command is inavailable currently.',
                        'description': 'We\'re disabled this command due to several malfunctions and/or we\'re still working on this issue'
                    },
                    'CommandOnCooldown': {
                        'title': 'Too fast.',
                        'description': 'Please wait %(retry_after)s seconds and run this command again.'
                    },
                    'UnexpectedQuoteError': {
                        'title': 'Unexpected quote.',
                        'description': 'The symbol %(quote)s was unexpected here.'
                    },
                    'InvalidEndOfQuotedStringError': {
                        'title': 'Invalid character after quoted string.',
                        'description': 'The symbol %(char)s was unexpected after quoted string.\nDid you forgot to separate the quoted string with the space?'
                    },
                    'ExpectedClosingQuoteError': {
                        'title': 'Closing quote expected, but not found.',
                        'description': 'Did you just forgot to enclose argument with second quote?'
                    },
                    'InvalidDuration': {
                        'title': 'Error occurred while parsing duration argument.',
                        'description': 'Invalid duration node: "%(invalid_node)s"'
                    },
                    'InvalidNumber': {
                        'title': 'Error occurred while parsing number argument.',
                        'description': 'Invalid number: "%(invalid_number)s"'
                    },
                    'Busy': {
                        'title': 'Busy',
                        'description': 'There are already running task. Wait for it and then repeat the command.'
                    }
                }
            },
            'common_errors': {
                'title': 'Error',
                'description': '--- %(error)s',
                'definitions': {
                    'Forbidden': {
                        'title': 'We do not have access.',
                        'description': 'Sorry but this couldn\'t be done because we were forbidden to perform that action for some reason.'
                    },
                    'NotFound': {
                        'title': 'Not found.',
                        'description': 'Couldn\'t find "%(item)s".'
                    }
                }
            },
            'custom_errors': {
                'title': 'Error',
                'description': 'An unknown error.',
                'definitions': {
                    'no_langs': {
                        'title': 'No available languages',
                        'description': 'We didn\'t found any available languages. Please report this issue to the bot\'s author.'
                    },
                    'non_abanned': {
                        'title': 'This user isn\'t banned',
                        'description': 'The user %(user_name)s#%(user_discriminator)s isn\'t author-banned.'
                    },
                    'non_banned': {
                        'title': 'This user isn\'t banned',
                        'description': 'The user %(user_name)s#%(user_discriminator)s isn\'t banned.'
                    },
                    'non_aadminbanned': {
                        'title': 'The administration of this guild isn\'t banned',
                        'description': 'The administration of the guild %(guild_name)s isn\'t banned.'
                    },
                    'non_abanned_guild': {
                        'title': 'This guild isn\'t banned',
                        'description': 'The guild %(guild_name)s isn\'t banned.'
                    },
                    'non_banned_here': {
                        'title': 'This user isn\'t banned here',
                        'description': 'The user %(user_name)s#%(user_discriminator)s isn\'t banned at #%(channel_name)s.'
                    },
                    'no_ban_self': {
                        'title': 'Wrong user',
                        'description': 'You cannot ban yourself.'
                    },
                    'no_ban_guild_owner': {
                        'title': 'Wrong user',
                        'description': 'You cannot ban a guild owner.'
                    },
                    'no_ban_higher_lpl': {
                        'title': 'Wrong user',
                        'description': 'You cannot ban a member, who have a higher permission level.'
                    },
                    'abort_nothing': {
                        'title': 'Nothing to abort',
                        'description': 'There\'s no running task right now.'
                    },
                    'no_with_owner': {
                        'title': 'Action is forbidden',
                        'description': 'You cannot do that with guild\'s owner.'
                    },
                    'no_with_higher_lpl': {
                        'title': 'Action is forbidden',
                        'description': 'You cannot do that with the member, who have higher permission level.'
                    }
                }
            },
            'response': {
                'description': '--- %(response)s',
                'definitions': {
                    'lang': {
                        'description': 'Your current language is %(name)s (%(langcode)s).'
                    },
                    'lang_of_user': {
                        'description': '%(user_name)s#%(user_discriminator)s\'s language is %(name)s (%(langcode)s).'
                    },
                    'lang_of_guild': {
                        'description': '%(guild_name)s\'s language is %(name)s (%(langcode)s).'
                    },
                    'notify_channel': {
                        'description': '%(guild_name)s\'s notify channel is #%(channel_name)s'
                    }
                }
            },
            'info': {
                'definitions': {
                    'abort': {
                        'title': 'Successful',
                        'description': 'Current task has been aborted.'
                    },
                    'lang_list': {
                        'title': 'Language list',
                        'description': 'Currently available languages (%(count)s): \n%(list)s'
                    },
                    'lang_set': {
                        'title': 'Language changed successfully',
                        'description': 'Your current language now: %(name)s (%(langcode)s).'
                    },
                    'lang_set_user': {
                        'title': 'Language changed successfully for user %(user_name)s#%(user_discriminator)s',
                        'description': '%(user_name)s\'s current language now: %(name)s (%(langcode)s).'
                    },
                    'lang_set_guild': {
                        'title': 'Language successfully changed for the guild',
                        'description': '%(guild_name)s\'s current language now: %(name)s (%(langcode)s).'
                    },
                    'authorban_banned': {
                        'title': 'Banned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s author-banned successfully.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'authorban_unbanned': {
                        'title': 'Unbanned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s author-unbanned successfully.'
                    },
                    'authorban_banned_here': {
                        'title': 'Banned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s author-banned at #%(channel_name)s successfully.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'authorban_unbanned_here': {
                        'title': 'Unbanned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s author-unbanned at #%(channel_name)s successfully.'
                    },
                    'authorban_list': {
                        'title': 'Author Ban List (%(banned_count)s)',
                        'fields': {
                            'name': '%(user_name)s#%(user_discriminator)s (%(user_id)s):',
                            'value': 'Ban reason: %(reason)s\nExpiration date: %(date_exp)s.'
                        }
                    },
                    'authoradminban_banned': {
                        'title': 'Banned successfully',
                        'description': 'Administration of the guild %(guild_name)s has been banned successfully.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'authoradminban_unbanned': {
                        'title': 'Unbanned successfully',
                        'description': 'Administration of the guild %(guild_name)s unbanned successfully.'
                    },
                    'authoradminban_list': {
                        'title': 'Author administration banned guilds list (%(banned_count)s)',
                        'fields': {
                            'name': '%(guild_name)s (%(guild_id)s):',
                            'value': 'Ban reason: %(reason)s\nExpiration date: %(date_exp)s.'
                        }
                    },
                    'authorban_places_list': {
                        'title': 'Author Place-Ban List (%(banned_count)s)',
                        'fields': {
                            'name': '%(user_name)s#%(user_discriminator)s (%(user_id)s)\nat #%(channel_name)s of %(guild_name)s:',
                            'value': 'Ban reason: %(reason)s\nExpiration date: %(date_exp)s.'
                        }
                    },
                    'authorban_banned_guild': {
                        'title': 'Banned successfully',
                        'description': 'Guild %(guild_name)s author-banned successfully.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'authorban_unbanned_guild': {
                        'title': 'Unbanned successfully',
                        'description': 'Guild %(guild_name)s author-unbanned successfully.'
                    },
                    'authorban_guild_list': {
                        'title': 'Author Banned Guild List (%(banned_count)s)',
                        'fields': {
                            'name': '%(guild_name)s (%(guild_id)s):',
                            'value': 'Ban reason: %(reason)s\nExpiration date: %(date_exp)s.'
                        }
                    },
                    'guild_admin_ban': {
                        'title': 'Banned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s banned successfully.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'guild_admin_unban': {
                        'title': 'Unbanned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s unbanned successfully.'
                    },
                    'guild_admin_ban_here': {
                        'title': 'Banned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s banned successfully at channel #%(channel_name)s.\nWith reason: %(reason)s\nBan expires at **%(date_exp)s**.'
                    },
                    'guild_admin_unban_here': {
                        'title': 'Unbanned successfully',
                        'description': 'User %(user_name)s#%(user_discriminator)s unbanned successfully.'
                    },
                    'guild_admin_ban_list': {
                        'title': 'Banned Members (%(banned_count)s)',
                        'description': '**Note:** these members may not be banned from this guild.',
                        'fields': {
                            'name': '%(user_name)s#%(user_discriminator)s:',
                            'value': 'Ban reason: %(reason)s\nExpiration date: %(date_exp)s.'
                        }
                    },
                    'lpl_set': {
                        'title': 'Permission level successfully set',
                        'description': 'User %(user_name)s#%(user_discriminator)s\'s permission level is %(lpl_value)s now.'
                    },
                    'lpl_role_set': {
                        'title': 'Permission level successfully set',
                        'description': 'Member role %(role_name)s\'s permission level is %(lpl_value)s now.'
                    },
                    'remote_toggle': {
                        'title': 'Remote access changed successfully',
                        'description': 'Remote access to the %(guild_name)s for the user %(user_name)s#%(user_discriminator)s has been %(switch)s.'
                    },
                    'remote_list': {
                        'title': 'Remote users',
                        'description': '%(list)s'
                    },
                    'notify_channel_set': {
                        'title': 'Notify channel updated',
                        'description': 'Channel #%(channel_name)s has been set as notify channel.'
                    }
                }
            },
            'notifications': {
                'title': 'Incoming notification',
                'description': 'No description',
                'definitions': {
                    'authorban_banned': {
                        'title': 'You has been banned from this bot',
                        'description': 'You got banned by the bot\'s author.\nBecause of this, you\'re unable to use this bot anywhere from now,\nuntil it expires or the bot\'s author manually removes the ban.\nReason: %(reason)s\nExpiration date: %(date_exp)s.'
                    },
                    'authorban_unbanned': {
                        'title': 'Your ban has been removed from this bot',
                        'description': 'Now you can use this bot from now.'
                    },
                    'authorban_banned_here': {
                        'title': 'You has been banned from this bot locally',
                        'description': 'You got banned by the bot\'s author at channel #%(channel_name)s of the guild %(guild_name)s.\nBecause of this, you\'re unable to use this bot at this place from now,\nuntil it expires or the bot\'s author manually removes the ban.\nReason: %(reason)s\nExpiration date: %(date_exp)s.'
                    },
                    'authorban_unbanned_here': {
                        'title': 'Your ban has been removed from this bot locally',
                        'description': 'Now you can use this bot at channel #%(channel_name)s of the guild %(guild_name)s from now.'
                    },
                    'authoradminban_banned_ownerdm': {
                        'title': 'Your guild has been banned from administration',
                        'description': 'One of your guilds with name %(guild_name)s has been banned from administration by author.\nNeither you nor administrators couldn\'t use administration or moderation tools on that guild and also unable to change some settings from now,\nuntil it expires or the bot\'s author manually removes the ban.\nReason: %(reason)s\nExpiration date: %(date_exp)s.'
                    },
                    'authoradminban_unbanned_ownerdm': {
                        'title': 'Your guild has been unbanned from administration',
                        'description': 'Bot administration on the guild %(guild_name)s has been unlocked.'
                    },
                    'authoradminban_banned': {
                        'title': 'This guild has been banned from administration',
                        'description': 'The administration features of this bot is locked on this guild from now by the bot author.\nYou are unable to **configure** features of that guild and also use moderation or administration commands, but you still able to **use** features of that bot.'
                    },
                    'authoradminban_unbanned': {
                        'title': 'This guild has been unbanned from administration',
                        'description': 'Administration, features settings and moderation commands has been unlocked.'
                    },
                    'authorban_banned_guild_ownerdm': {
                        'title': 'Your guild has been banned from this bot',
                        'description': 'One of your guilds with name %(guild_name)s has been banned from this bot by author. The bot will no longer maintain your guild and all functions of the bot is unable on this guild from now, \nuntil it expires or the bot\'s author manually removes the ban.\nReason: %(reason)s\nExpiration date: %(date_exp)s.\nThe members of your guild is also unable to use bot on your guild, but they can use it in other places.'
                    },
                    'authorban_unbanned_guild_ownerdm': {
                        'title': 'Your guild has been unbanned from this bot',
                        'description': 'Bot usage on guild %(guild_name)s has been unlocked.'
                    },
                    'authorban_banned_guild': {
                        'title': 'This guild has been banned from this bot',
                        'description': 'The functionality of the bot is locked on this guild from now by the bot author. \nYou cannot use bot on this guild until it expires or the bot\'s author manually removes the ban.\nReason: %(reason)s\nExpiration date: %(date_exp)s.',
                        'footer': 'The bot is still available in DMs or another guilds.'
                    },
                    'authorban_unbanned_guild': {
                        'title': 'The ban has been removed from this guild',
                        'description': 'The functionality of the bot is available for this guild now.'
                    },
                    'guild_admin_ban': {
                        'title': 'You got banned from %(guild_name)s',
                        'description': 'The guild administrator has just banned you from the guild.\nReason: %(reason)s\nExpiration date: %(date_exp)s.'
                    },
                    'guild_admin_ban_here': {
                        'title': 'You got locally banned at %(guild_name)s',
                        'description': 'The guild administrator has just banned you at the channel #%(channel_name)s of the guild %(guild_name)s by it\'s administrator.\nYou cannot use bot commands and use most of the bot\'s functionality in that channel.\nReason: %(reason)s\nExpiration date: %(date_exp)s.'
                    },
                    'guild_admin_unban': {
                        "title": 'Your ban has been removed from %(guild_name)s',
                        'description': 'Now you can join to this guild.'
                    },
                    'guild_admin_unban_here': {
                        "title": 'Your ban has been removed at channel #%(channel_name)s of the guild %(guild_name)s',
                        'description': 'Now you\'re able to use bot in that channel.'
                    },
                    'moderator_warning': {
                        'title': 'Warning from %(guild_name)s',
                        'description': '%(warning)s'
                    }
                }
            }
        },

        #'help': {
        #    'langs': 'Show the list of the all available languages.',
        #    'setlang': 'Change current language.',
        #    'lang': 'Show what current language I have.'
        #},
        'permissions': {
            'create_instant_invite': 'create instant invite',
            'kick_members': 'kick members',
            'ban_members': 'ban members',
            'administrator': 'administrator',
            'manage_channels': 'manage channels',
            'manage_guild': 'manage guild',
            'add_reactions': 'react',
            'view_audit_log': 'view audit log',
            'priority_speaker': 'priority speaker',
            'stream': 'stream',
            'read_messages': 'read messages',
            'send_messages': 'send messages',
            'send_tts_messages': 'send tts messages',
            'manage_messages': 'manage messages',
            'embed_links': 'embed links',
            'attach_files': 'attach files',
            'read_message_history': 'read message history',
            'mention_everyone': 'mention everyone',
            'external_emojis': 'use external emojis',
            'connect': 'connect',
            'speak': 'speak',
            'mute_members': 'mute members',
            'deafen_members': 'deafen members',
            'use_voice_activation': 'use voice activation',
            'change_nickname': 'change nickname',
            'manage_nicknames': 'manage nicknames',
            'manage_roles': 'manage roles',
            'manage_emojis': 'manage emojis',
            'manage_webhooks': 'manage webhooks'
        },
        'audit_log_actions': {
            'guild_update': 'guild updated',
            'channel_create': 'channel created',
            'channel_update': 'channel updated',
            'channel_delete': 'channel deleted',
            'overwrite_create': 'permission overwrite set',
            'overwrite_update': 'permission overwrite changed',
            'overwrite_delete': 'permission overwrite unset',
            'kick': 'member kicked',
            'member_prune': 'member pruned',
            'ban': 'member banned',
            'unban': 'member unbanned',
            'member_update': 'member updated',
            'member_role_update': 'member role updated',
            'role_create': 'role created',
            'role_update': 'role updated',
            'role_delete': 'role deleted',
            'invite_create': 'invite link created',
            'invite_update': 'invite link updated',
            'invite_delete': 'invite link deleted',
            'webhook_create': 'webhook created',
            'webhook_update': 'webhook updated',
            'webhook_delete': 'webhook deleted',
            'emoji_create': 'emoji created',
            'emoji_update': 'emoji updated',
            'emoji_delete': 'emoji deleted',
            'message_delete': 'message deleted'
        },
        'audit_log_action_category': {
            'create': 'creation',
            'update': 'updating',
            'delete': 'deletion'
        }
    }
}
#Used to validate all keys
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
                    'MissingPermissions': dict,
                    'BotMissingPermissions': dict
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
                    'guild_admin_ban_here': dict,
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

#Exceptions
class ProcessingIdle(commands.CheckFailure):
    #This shouldn't send any error messages, it just blocks the command
    pass
class AuthorBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class AuthorBanHere(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class AuthorAdministrationBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class AuthorBanGuild(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
# --- DEPRECATED (however they have been removed from validator) --- #
class AuthorBanCategory(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class AuthorBanRole(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class AuthorBanChannel(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
# ------------------------------------------------------------------ #
class GuildAdminBan(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class GuildAdminBanHere(commands.CheckFailure):
    def __init__(self, description=None, *, reason='Not defined', date_exp=Never):
        self.reason = reason
        self.date_exp = date_exp
class GuildAdminBlockChannel(commands.CheckFailure):
    pass
class GuildAdminBlockCategory(commands.CheckFailure):
    pass
class InsufficientPoints(commands.CheckFailure):
    def __init__(self, description=None, *, insuf=0, price=0):
        self.insuf = insuf
        self.price = price
class InsufficientGuildPoints(commands.CheckFailure):
    def __init__(self, description=None, *, insuf=0, price=0):
        self.insuf = insuf
        self.price = price
class NotAllowed(commands.CheckFailure):
    pass
class NotAllowedBypass(commands.CheckFailure):
    pass

class IncorrectDuration(commands.CommandError):
    def __init__(self, description=None, *, node=""):
        self.node = node
class InvalidNumber(commands.CommandError):
    def __init__(self, description=None, *, invalid_number=0):
        self.invalid_number = invalid_number
class Busy(commands.CommandError):
    pass
#NotFound exceptions DEPRECATED
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
def enzero(num,count=2):
    snum = str(num)
    if len(snum) >= count:
        return snum
    return '0'*(count-len(snum))+snum
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
    global fl, conf
    try:
        if os.path.isfile(conff):
            fl = open(conff,'r')
            conf = json.loads(fl.read())
        else:
            fl = open(conff,'x')
            fl.write(json.dumps(conftemplate,indent=True))
            fl.close()
            print('The example configuration has been created, enter bot token in them')
            exit(0)
    except json.JSONDecodeError as exc:
        print('The configuration file is broken.')
        print(exc)
        print('Please check the validance of the configuration: '+os.path.abspath(conff))
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
            fl = open(dataf,'x')
            # TODO
            data_tmpl = {'templates':{'guilds':[],'roles':[],'channels':[]},'user_data':{},'guild_data':{}}
            fl.write(json.dumps(data_tmpl,indent=True))
            fl.close()
            data = data_tmpl
        else:
            fl = open(dataf,'r')
            data = json.loads(fl.read())
    except json.JSONDecodeError as exc:
        print('The data file is broken.')
        print(exc)
        print('Please check the validance of the configuration: '+os.path.abspath(dataf))
        fl.close()
        exit(1)
    else:
        logger.info('Successfully read the data')
        fl.close()

def validateLang(langdict, langvalid, prefix=''):
    _missing_fields = []
    _insuf_fields = []
    for entry in langvalid.keys():
        assert not type(langvalid[entry]) == 'list', 'The language validate template is damaged, it shouldn\'t contain any lists'
        if not str(entry) in langdict.keys():
            _missing_fields.append(prefix+str(entry))
        else:
            if langvalid[entry].__class__.__name__ == 'dict':
                #this is a section, perform recursion.
                if langdict[str(entry)].__class__.__name__ != 'dict':
                    _insuf_fields.append(prefix+entry+'("dict" expected, got "%s")'%langdict[entry].__class__.__name__)
                _rmf, _rif = validateLang(langdict[entry], langvalid[entry], prefix+str(entry)+'.')
                _missing_fields.extend(_rmf)
                _insuf_fields.extend(_rif)
            elif langdict[entry].__class__ != langvalid[entry]:
                #if the node is not a section, then just validate the type.
                _insuf_fields.append(prefix+str(entry)+'("%s" expected, got "%s")'%(langvalid[entry].__name__, langdict[entry].__class__.__name__))
    return (_missing_fields, _insuf_fields)
def loadLangs():
    logger.info('Loading language settings...')
    if not os.path.isdir(langfold):
        print('FATAL: %s directory not found!'%langfold)
        logger.critical('Directory "%s" was not found!'%langfold)
        return False
    else:
        if not 'default_lang' in conf:
            logger.warning('The "default_lang" option is not set in the configuration, using "en_US" as the default.')
            conf['default_lang'] = "en_US"
        _files = []
        with os.scandir(langfold) as files:
            for file in files:
                if file.name.endswith('.json') and file.is_file():
                    _files.append(file)
        if 'en_US.json' not in [x.name for x in _files]:
            print('No language settings was found! Generating default language file...\n - You can copy&paste, rename it and edit them to create your own translation.')
            logger.error('Directory "%s" does not contain any language sets! Loading default built-in language...'%langfold)
            _missing_fields, _insuf_fields = validateLang(langtemplate, langvalid)
            if _missing_fields or _insuf_fields:
                logger.critical('Validance test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.'%(len(_missing_fields),', '.join(_missing_fields),len(_insuf_fields),', '.join(_insuf_fields)))
                print('FATAL: The program is corrupted (the language template is invalid). Please check the log.')
                return False
            lang['en_US'] = langtemplate
            lang['default'] = lang['en_US']
            logger.info('Dumping built-in language into "%s" ...'%os.path.abspath(langfold))
            fl = open(langfold+'/en_US.json', 'x')
            fl.write(json.dumps(langtemplate, indent=True))
            fl.close()
            logger.info('Successfully created default language.')
            return True
            #We're allowed to start bot.
        if not conf['default_lang']+'.json' in [x.name for x in _files]:
            print('Language settings "%s" was not found! Please check your configuration!'%(conf['default_lang']+'.json'))
            logger.critical('Directory "%s" does not contain the "%s" file, check your configuration!'%(langfold,conf['default_lang']+'.json'))
            return False
        else:
            _error_enc = False
            logger.info('Reading language content...')
            for file in _files:
                #fl = None
                #ld = None
                try:
                    fl = open(langfold+'/'+file.name, 'r')
                    ld = json.loads(fl.read())
                except json.JSONDecodeError as exc:
                    _exctext = traceback.format_exc()
                    print('Error: language file "%s" is damaged.\n%s'%(file.name,_exctext))
                    logger.critical('Language file "%s" is corrupted and unable to load. Exception traceback:\n%s'%(file.name, _exctext))
                    print(exc)
                    print('It is strongly recommended to turn your bot off.')
                    fl.close()
                    _error_enc = True
                else:
                    _flabel = file.name.split('.')[0]
                    #We are successfully got the language content, so we can validate them with validator pattern and by recursive function.
                    #The validation is need to keep out our program from KeyError or TypeError exceptions and notify the bot's owner about missing translation.
                    logger.info('Validating %s...'%_flabel)
                    _missing_fields, _insuf_fields = validateLang(ld, langvalid)
                    if len(_missing_fields)+len(_insuf_fields) > 0:
                        logger.critical('Validance test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.'%(len(_missing_fields),', '.join(_missing_fields),len(_insuf_fields),', '.join(_insuf_fields)))
                        print('%s: lang file is invalid. Please check the log.'%_flabel)
                        _error_enc = True
                    else:
                        lang[_flabel] = ld
                        logger.info('Successful validance test! Language "%s" loaded.'%_flabel)
            if conf['default_lang'] not in lang:
                return False
            lang['default'] = lang[conf['default_lang']] #self-reference
            return not _error_enc
class GuildConverter(commands.Converter):
    def __init__(self, *args, **kwargs):
        commands.Converter.__init__(self, *args, **kwargs)
    async def convert(self, ctx, arg):
        if ctx.guild and (arg == "" or arg == "-"):
            return ctx.guild
        #arg = str(arg)
        if arg.isnumeric():
            #search by id
            for guild in ctx.bot.get_visible_guilds(ctx.author):
                #print(str(guild.id))
                if str(guild.id) == arg:
                    return guild
        #search by name
        for guild in ctx.bot.get_visible_guilds(ctx.author):
            #print(str(guild.name))
            if guild.name == arg:
                return guild
        #failed, raise
        raise commands.BadArgument('Guild with name "%s" not found.'%arg,arg)


class PtDiscordBot(commands.Bot):
    def __init__(self, logger, conf, data, lang, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.conf = conf
        self.data = data
        self.mods = []
        self.modfold = modfold
        self.mod_dict = {}
        self.mod_exc_dict = {}
        self.lang = lang
        self.langfold = langfold
        self.validateLang = validateLang
        self.loadLangs = loadLangs
        self.tasks = {'ab': {}, 'aab': {}, 'abh': {}, 'abg': {}, 'gab': {}, 'gabh': {}, 'sched': {}, 'longcmd': {}}
        self.local_tz: datetime.timezone = None
        self.loadMods()

        #Global checks
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
            # I'll always pass the bot author through, even if it is banned.
            if ctx.author.id == self.owner_id:
                return True
            try:
                if self.data['user_data'][str(ctx.author.id)]['author_ban']:
                    if 'date_exp' in self.data['user_data'][str(ctx.author.id)]['author_ban']:
                        date_exp = datetime.datetime(**self.data['user_data'][str(ctx.author.id)]['author_ban']['date_exp'])
                    else:
                        date_exp = Never
                    if 'reason' in self.data['user_data'][str(ctx.author.id)]['author_ban']:
                        reason = self.data['user_data'][str(ctx.author.id)]['author_ban']['reason']
                    else:
                        reason = '--'
                    raise AuthorBan('You have been banned by author. Reason: %s'%reason, reason=reason, date_exp=date_exp)
                    return False
                else:
                    return True
            except (AttributeError, KeyError):
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
            if ctx.author.id == self.owner_id or not ctx.guild:
                return True
            try:
                if self.data['user_data'][str(ctx.author.id)]['author_ban_places']:
                    #check if we have the guild.
                    place = self.data['user_data'][str(ctx.author.id)]['author_ban_places'][str(ctx.guild.id)][str(ctx.channel.id)]
                    #if we didn't got a KeyError exception, we ran on the place.
                    if 'date_exp' in place:
                        date_exp = datetime.datetime(**place['date_exp'])
                    else:
                        date_exp = Never
                    if 'reason' in place:
                        reason = place['reason']
                    else:
                        reason = '--'
                    raise AuthorBanHere('You have been banned by author in that place. Reason: %s'%reason, reason=reason, date_exp=date_exp)
                    return False
                else:
                    return True
            except (AttributeError, KeyError):
                return True
        @self.check
        def check_author_ban_guild(ctx):
            try:
                if self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                    if 'date_exp' in self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                        date_exp = datetime.datetime(**self.data['guild_data'][str(ctx.guild.id)]['author_ban']['date_exp'])
                    else:
                        date_exp = Never
                    if 'reason' in self.data['guild_data'][str(ctx.guild.id)]['author_ban']:
                        reason = self.data['guild_data'][str(ctx.guild.id)]['author_ban']['reason']
                    else:
                        reason = '--'
                    raise AuthorBanGuild('This guild has been banned by the author. Reason: %s'%reason, reason=reason, date_exp=date_exp)
                    return False
            except (AttributeError, KeyError):
                return True
        @self.check
        def check_guild_admin_ban(ctx):
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                if bool(self.conf['owner_permission_bypass']):
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    return True
                if str(ctx.author.id) in self.data['guild_data'][str(ctx.guild.id)]['banned_users']:
                    if 'date_exp' in self.data['guild_data'][str(ctx.guild.id)]['banned_users'][str(ctx.author.id)]:
                        date_exp = self.data['guild_data'][str(ctx.guild.id)]['banned_users'][str(ctx.author.id)]['date_exp']
                    else:
                        date_exp = Never
                    if 'reason' in self.data['guild_data'][str(ctx.guild.id)]['banned_users'][str(ctx.author.id)]:
                        reason = self.data['guild_data'][str(ctx.guild.id)]['banned_users'][str(ctx.author.id)]['reason']
                    else:
                        reason = '--'
                    raise GuildAdminBan('You have been banned by the guild\'s administrator from this bot on this guild. Reason: %s'%reason, reason=reason, date_exp=date_exp)
                    return False
            except (AttributeError, KeyError):
                return True
        @self.check
        def check_guild_admin_ban_here(ctx):
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                if bool(self.conf['owner_permission_bypass']):
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    return True
                if str(ctx.author.id) in self.data['guild_data'][str(ctx.guild.id)]['placebanned_users'][str(ctx.channel.id)]:
                    ban = self.data['guild_data'][str(ctx.guild.id)]['placebanned_users'][str(ctx.channel.id)][str(ctx.author.id)]
                    if 'date_exp' in ban:
                        date_exp = datetime.datetime(**ban['date_exp'])
                    else:
                        date_exp = Never
                    if 'reason' in ban:
                        reason = ban['reason']
                    else:
                        reason = '--'
                    raise GuildAdminBanHere('You have been banned by the guild\'s administrator here. Reason: %s'%reason, reason=reason, date_exp=date_exp)
                    return False
            except (AttributeError, KeyError):
                return True
        @self.check
        def check_guild_admin_block_category(ctx):
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                if bool(self.conf['owner_permission_bypass']):
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    return True
                if ctx.channel.id in self.data['guild_data'][str(ctx.guild.id)]['denied_categories']:
                    raise GuildAdminBlockCategory('You cannot use bot commands here.')
            except (AttributeError, KeyError):
                return True
        @self.check
        def check_guild_admin_block_channel(ctx):
            if ctx.author.id == self.owner_id and 'owner_permission_bypass' in self.conf:
                if bool(self.conf['owner_permission_bypass']):
                    return True
            try:
                if ctx.guild.owner_id == ctx.author.id:
                    return True
                if ctx.channel.id in self.data['guild_data'][str(ctx.guild.id)]['denied_channels']:
                    raise GuildAdminBlockChannel('You cannot use bot commands here.')
            except (AttributeError, KeyError):
                return True

        # TODO: help
        # - Commands -
        #Language
        @commands.command()
        async def abort(ctx):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if ctx.author.id in self.tasks['longcmd']:
                if not self.tasks['longcmd'][ctx.author.id].done():
                    self.tasks['longcmd'][ctx.author.id].cancel()
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'abort'))
                else:
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'abort_nothing'))
                del self.tasks['longcmd'][ctx.author.id]
            else:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'abort_nothing'))
        @self.check
        def check_processing_idle(ctx):
            if ctx.command is abort:
                return True
            if ctx.author.id in self.tasks['longcmd']:
                if self.tasks['longcmd'][ctx.author.id].done():
                    return True
                else:
                    raise ProcessingIdle()
                    return False
            else:
                return True
        #Language control
        @commands.command()
        async def langs(ctx):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            if not self.lang:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_langs'))
            else:
                _lngs = list()
                for lngcode in self.lang:
                    if lngcode != 'default':
                        _lngs.append('%s (%s)'%(self.lang[lngcode]['name'],lngcode))
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_list', count=len(_lngs), list=(', '.join(_lngs))))
        @commands.command(usage="[language code]")
        async def setlang(ctx, language, user=None):
            if user is not None and ctx.author.id != self.owner_id:
                #raise commands.NotOwner("You are not allowed to change language for another user.")
                user=None
            #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            langslc = [x.lower() for x in self.lang.keys()]
            if language.lower() not in langslc:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate, 'NotFound', item=language))
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
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_set_user', name=self.lang[langcode]['name'], langcode=langcode, user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                else:
                    if str(ctx.author.id) not in self.data['user_data']:
                        self.data['user_data'][str(ctx.author.id)] = dict()
                    self.data['user_data'][str(ctx.author.id)]['language'] = langcode
                    self.savedata()
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_set', name=self.lang[langcode]['name'], langcode=langcode))
        @commands.command()
        async def lang(ctx, user=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if user is not None and ctx.author.id != self.owner_id:
                #raise commands.NotOwner("You are not allowed to get current language for another user.")
                user=None
            if user is not None:
                targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
                if not targetuser:
                    return None
                if str(targetuser.id) not in self.data['user_data']:
                    langcode = 'default'
                else:
                    langcode = self.data['user_data'][str(targetuser.id)]['language']
                #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate, 'lang_of_user', name=self.lang[langcode]['name'], langcode=langcode, user_id=targetuser.id, user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            else:
                #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                langcode = _lang
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate, 'lang', name=self.lang[langcode]['name'], langcode=langcode))
        @commands.command(usage="[language code]")
        async def setguildlang(ctx, language, guild=None):
            if guild is not None and ctx.author.id != self.owner_id:
                guild=None
            #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
            langslc = [x.lower() for x in self.lang.keys()]
            if language.lower() not in langslc:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate, 'NotFound', item=language))
            else:
                langcode = list(self.lang.keys())[langslc.index(language.lower())]
                if guild is not None:
                    targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                    if not targetguild:
                        return None
                    #if not ctx.author.id in [m.id for m in targetguild.members] and ctx.author.id != self.owner_id:
                    #    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate, 'NotFound', item=guild))
                    #    return None
                    if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                        self.runtime_check_guild_lpl(targetguild, ctx.author, 3)
                        self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                    if str(targetguild.id) not in self.data['guild_data']:
                        self.data['guild_data'][str(targetguild.id)] = {}
                    self.data['guild_data'][str(targetguild.id)]['language'] = langcode
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_set_guild', name=self.lang[langcode]['name'], langcode=langcode, guild_name=targetguild.name))
                else:
                    if not ctx.guild:
                        await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                        return None
                    self.runtime_check_guild_lpl(ctx.guild, ctx.author, 3)
                    if str(ctx.guild.id) not in self.data['guild_data']:
                        self.data['guild_data'][str(ctx.guild.id)] = dict()
                    self.data['guild_data'][str(ctx.guild.id)]['language'] = langcode
                    self.savedata()
                    _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang.keys())
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lang_set_guild', name=self.lang[langcode]['name'], langcode=langcode, guild_name=ctx.guild.name))
        @commands.command()
        async def guildlang(ctx, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return None
                if not ctx.author.id in [m.id for m in targetguild.members] and ctx.author.id != self.owner_id:
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate, 'NotFound', item=guild))
                    return None
                if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                    self.runtime_check_guild_admin_ban(targetguild, ctx.author)
                if str(targetguild.id) not in self.data['guild_data']:
                    langcode = 'default'
                else:
                    langcode = self.data['guild_data'][str(targetguild.id)]['language'] if 'language' in self.data['guild_data'][str(targetguild.id)] else 'default'
                #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate, 'lang_of_guild', name=self.lang[langcode]['name'], langcode=langcode, guild_name=targetguild.name))
            else:
                #_lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                if not ctx.guild:
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                    return None
                self.runtime_check_guild_admin_ban(ctx.guild, ctx.author)
                try:
                    langcode = self.data['guild_data'][str(ctx.guild.id)]['language'] if 'language' in self.data['guild_data'][str(ctx.guild.id)] else 'default'
                except (AttributeError, KeyError):
                    langcode = 'default'
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'response', self.conf, conftemplate, 'lang_of_guild', name=self.lang[langcode]['name'], langcode=langcode, guild_name=ctx.guild.name))
        #Local permission level
        @commands.command()
        async def setpermlevel(ctx, user, value, guild=None):
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #...
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_guild_ownership(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild)
            if not str(targetguild.id) in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if not 'user_permission_levels' in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['user_permission_levels'] = {}
            try:
                self.data['guild_data'][str(targetguild.id)]['user_permission_levels'][str(targetuser.id)] = int(value)
                self.savedata()
            except ValueError:
                raise InvalidNumber('Invalid number: %s'%value, invalid_number=value)
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lpl_set', user_id=targetuser.id, user_name=targetuser.name, user_discriminator=targetuser.discriminator, guild_name=targetguild.name, guild_id=targetguild.id, lpl_value=int(value)))
        #Local permission level, but for role
        @commands.command()
        async def setrolelevel(ctx, role, value, guild=None):
            print(1)
            if guild is not None:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    print(2)
                    return
            elif not ctx.guild:
                print(3)
                _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
                print(4)
            #...
            ctx.guild = targetguild
            #
            print(5)
            targetrole = await self.wrapped_convert(ctx, commands.RoleConverter, commands.RoleConverter, role)
            if not targetrole:
                print(6)
                return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                print(ctx.author.id)
                print(self.owner_id)
                self.runtime_check_guild_ownership(targetguild,ctx.author)
                self.runtime_check_guild_authoradminban(targetguild)
            if not str(targetguild.id) in self.data['guild_data']:
                print(8)
                self.data['guild_data'][str(targetguild.id)] = {}
            if not 'role_settings' in self.data['guild_data'][str(targetguild.id)]:
                print(9)
                self.data['guild_data'][str(targetguild.id)]['role_settings'] = {}
            if not str(targetrole.id) in self.data['guild_data'][str(targetguild.id)]['role_settings']:
                print(10)
                self.data['guild_data'][str(targetguild.id)]['role_settings'][str(targetrole.id)] = {}
            try:
                print(11)
                self.data['guild_data'][str(targetguild.id)]['role_settings'][str(targetrole.id)]['local_permission_level'] = int(value)
                self.savedata()
                print(12)
            except ValueError:
                raise InvalidNumber('Invalid number: %s'%value, invalid_number=value)
                print(13)
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            print(14)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'lpl_role_set', role_id=targetrole.id, role_name=targetrole.name, guild_name=targetguild.name, guild_id=targetguild.id, lpl_value=int(value)))
            print(15)
        #Remote access
        @commands.command()
        async def setremote(ctx, logic, user=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
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
            await self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'remote_toggle', user_id=targetuser.id, user_name=targetuser.name, user_discriminator=targetuser.discriminator, switch=State(bool(logic)))
        #Guild settings
        @commands.command()
        async def setnotifychannel(ctx, channel=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
                targetchannel = self.findchannel(targetguild, channel)
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='channel'))
                return
            else:
                targetguild = ctx.guild
                if channel:
                    targetchannel = self.findchannel(targetguild, channel)
                else:
                    targetchannel = ctx.channel
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 3)
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['notify_channel'] = targetchannel.id
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'notify_channel_set', guild_id=targetguild.id, guild_name=targetguild.name, channel_id=targetchannel.id, channel_name=targetchannel.name))
        #Ban
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
            if date.lower() != '' or date.lower() != _lang['contents']['formats']['date_relative']['never'].lower() or date.lower() != self.lang[_lang]['contents']['formats']['date_relative']['never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
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
            #BANNED
            self.savedata()
            if targetuser.id in self.tasks['longcmd']:
                self.tasks['longcmd'][targetuser.id].cancel()
                del self.tasks['longcmd'][targetuser.id]
            if targetuser.id in self.tasks['ab']:
                self.tasks['ab'][targetuser.id].cancel()
            self.tasks['ab'][targetuser.id] = asyncio.create_task(self.authorban_expiry_timer(str(targetuser.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authorban_banned', reason=reason, date_exp=date_exp, user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            #notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_banned', reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass
        #Unban
        @commands.command(hidden=True)
        @commands.is_owner()
        async def unaban(ctx, user):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if str(targetuser.id) not in self.data['user_data']:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator))
                return None
            elif 'author_ban' not in self.data['user_data'][str(targetuser.id)]:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator))
                return None
            del self.data['user_data'][str(targetuser.id)]['author_ban']
            self.savedata()
            if targetuser.id in self.tasks['ab']:
                self.tasks['ab'][targetuser.id].cancel()
                del self.tasks['ab'][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authorban_unbanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned'))
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
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter, commands.TextChannelConverter, channel)
                if not targetchannel:
                    return None
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='channel'))
                return None
            else:
                targetchannel = ctx.channel
            if str(targetuser.id) not in self.data['user_data']:
                self.data['user_data'][str(targetuser.id)] = {}
            if 'author_ban_places' not in self.data['user_data'][str(targetuser.id)]:
                self.data['user_data'][str(targetuser.id)]['author_ban_places'] = {}
            if str(targetchannel.guild.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places']:
                self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)] = {}
            #if str(targetchannel.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)]:
            #    self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][str(targetchannel.id)] = {}
            #[str(targetchannel.guild.id)][str(targetchannel.id)]
            self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][str(targetchannel.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != _lang['contents']['formats']['date_relative']['never'].lower() or date.lower() != self.lang[_lang]['contents']['formats']['date_relative']['never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
                self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][str(targetchannel.id)]['date_exp'] = {
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
            #BANNED
            self.savedata()
            if targetchannel.guild.id not in self.tasks['abh']:
                self.tasks['abh'][targetchannel.guild.id] = {}
            if targetchannel.id not in self.tasks['abh'][targetchannel.guild.id]:
                self.tasks['abh'][targetchannel.guild.id][targetchannel.id] = {}
            if targetuser.id in self.tasks['abh'][targetchannel.guild.id][targetchannel.id]:
                self.tasks['abh'][targetchannel.guild.id][targetchannel.id][targetuser.id].cancel()
            self.tasks['abh'][targetchannel.guild.id][targetchannel.id][targetuser.id] = asyncio.create_task(self.authorbanplace_expiry_timer(str(targetuser.id), targetchannel.guild.id, targetchannel.id))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authorban_banned_here', reason=reason, date_exp=date_exp, user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id, guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name, channel_id=targetchannel.id, channel_name=targetchannel.name))
            #notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_banned_here', reason=reason, date_exp=date_exp, guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name, channel_id=targetchannel.id, channel_name=targetchannel.name))
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
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter, commands.TextChannelConverter)
                if not targetchannel:
                    return None
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='channel'))
                return None
            else:
                targetchannel = ctx.channel
            if str(targetuser.id) not in self.data['user_data']:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if 'author_ban_places' not in self.data['user_data'][str(targetuser.id)]:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if str(targetchannel.guild.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places']:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            if str(targetchannel.id) not in self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)]:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id))
                return None
            del self.data['user_data'][str(targetuser.id)]['author_ban_places'][str(targetchannel.guild.id)][str(targetchannel)]
            try:
                self.tasks['abh'][targetuser.id][targetchannel.guild.id][targetchannel.id].cancel()
                del self.tasks['abh'][targetuser.id][targetchannel.guild.id][targetchannel.id]
            except (KeyError, AttributeError):
                pass
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authorban_unbanned_here', user_name=targetuser.name, user_discriminator=targetuser.discriminator, user_id=targetuser.id, guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name, channel_id=targetchannel.id, channel_name=targetchannel.name))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_here', guild_id=targetchannel.guild.id, guild_name=targetchannel.guild.name, channel_id=targetchannel.id, channel_name=targetchannel.name))
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
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['author_administration_ban'] = {'reason': reason}
            if date.lower() != '' or date.lower() != _lang['contents']['formats']['date_relative']['never'].lower() or date.lower() is not self.lang[_lang]['contents']['formats']['date_relative']['never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
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
                date = Never
            #BANNED
            self.savedata()
            if targetguild.id in self.tasks['aab']:
                self.tasks['aab'][targetguild.id].cancel()
            self.tasks['aab'][targetguild.id] = asyncio.create_task(self.authorbanguild_expiry_timer(str(targetguild.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authoradminban_banned', guild_id=targetguild.id, guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_banned', guild_id=targetguild.id, guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_banned_ownerdm', reason=reason, date_exp=date_exp, guild_id=targetguild.id, guild_name=targetguild.name))
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
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'author_administration_ban' not in self.data['guild_data'][str(targetguild.id)]:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_aadminbanned', guild_id=targetguild.id, guild_name=targetguild.name))
            if not self.tasks['aab'][targetguild.id].done():
                self.tasks['aab'][targetguild.id].cancel()
            del self.tasks['aab'][targetguild.id]
            del self.data['guild_data'][str(targetguild.id)]['author_administration_ban']
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_unbanned', guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_unbanned_ownerdm', guild_id=targetguild.id, guild_name=targetguild.name))
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
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['author_ban'] = {'reason': reason}
            if date.lower() != '' or date.lower() != _lang['contents']['formats']['date_relative']['never'].lower() or date.lower() is not self.lang[_lang]['contents']['formats']['date_relative']['never']:
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
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
                date = Never
            #BANNED
            self.savedata()
            if targetguild.id in self.tasks['abg']:
                self.tasks['abg'][targetguild.id].cancel()
            self.tasks['abg'][targetguild.id] = asyncio.create_task(self.authorbanguild_expiry_timer(str(targetguild.id)))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'authorban_banned_guild', guild_id=targetguild.id, guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_banned_guild', guild_id=targetguild.id, guild_name=targetguild.name, reason=reason, date_exp=date_exp))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_banned_guild_ownerdm', reason=reason, date_exp=date_exp, guild_id=targetguild.id, guild_name=targetguild.name))
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
                    await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                else:
                    targetguild = ctx.guild
            if str(targetguild.id) not in self.data['guild_data']:
                self.data['guild_data'][str(targetguild.id)] = {}
            if 'author_ban' not in self.data['guild_data'][str(targetguild.id)]:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_abanned_guild', guild_id=targetguild.id, guild_name=targetguild.name))
            if not self.tasks['abg'][targetguild.id].done():
                self.tasks['abg'][targetguild.id].cancel()
            del self.tasks['abg'][targetguild.id]
            del self.data['guild_data'][str(targetguild.id)]['author_ban']
            try:
                _lang = self.getLanguage(targetguild.id, None, self.lang)
                await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_guild', guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass
            try:
                _lang = self.getLanguage(targetguild.owner.id, None, self.lang)
                await targetguild.owner.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_guild_ownerdm', guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass
        @commands.command()
        async def ban(ctx, user, date='', guild=None, *, reason=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            #hmm...
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if targetuser.id == ctx.author.id:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_self'))
                return
            if targetuser.id == targetguild.owner.id:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_guild_owner'))
                return
            if not self.runtime_check_guild_higher_lpl(targetguild, targetuser, ctx.author):
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_higher_lpl'))
                return
            if 'banned_users' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['banned_users'] = {}
            self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != _lang['contents']['formats']['date_relative']['never'].lower():
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
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
            #BANNED
            self.savedata()
            await targetguild.ban(targetuser, reason=reason)
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
            self.tasks['gab'][targetguild.id][targetuser.id] = asyncio.create_task(self.guildadminban_expiry_timer(targetguild.id, targetuser.id))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_ban', user_id=targetuser.id, user_name=targetuser.name, user_discriminator=targetuser.discriminator, guild_name=targetguild.name, guild_id=targetguild.id, reason=reason, date_exp=date_exp))
            #notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_ban', guild_id=targetguild.id, guild_name=targetguild.name, reason=reason, date_exp=date_exp))
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
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            if channel:
                targetchannel = self.findchannel(targetguild, channel)
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='channel'))
                return
            else:
                targetchannel = ctx.channel
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author)
                self.runtime_check_guild_lpl(targetguild, ctx.author, 2)
            #wait... this is illegal
            ctx.guild = targetguild
            #
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return
            if targetuser.id == ctx.author.id:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_self'))
                return
            if targetuser.id == targetguild.owner.id:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_guild_owner'))
                return
            if not self.runtime_check_guild_higher_lpl(targetguild, targetuser, ctx.author):
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'no_ban_higher_lpl'))
                return
            if 'placebanned_users' not in self.data['guild_data'][str(targetguild.id)]:
                self.data['guild_data'][str(targetguild.id)]['banned_users'] = {}
            if str(targetchannel.id) not in self.data['guild_data'][str(targetguild.id)]['placebanned_users']:
                self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)] = {}
            self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)][str(targetuser.id)] = {'reason': reason}
            if date.lower() != '' or date.lower() != self.lang[_lang]['contents']['formats']['date_relative']['never'].lower():
                date_exp = datetime.datetime.now() + self.parseDuration(langtemplate['contents']['formats']['duration'], date.lower())
                self.data['guild_data'][str(targetguild.id)]['placebanned_users'][str(targetchannel.id)][str(targetuser.id)] = {
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
            #BANNED
            self.savedata()
            if targetuser.id in self.tasks['gabh'][targetguild.id][targetchannel.id]:
                self.tasks['gabh'][targetguild.id][targetchannel.id][targetuser.id].cancel()
            self.tasks['gabh'][targetguild.id][targetchannel.id][targetuser.id] = asyncio.create_task(self.guildadminbanhere_expiry_timer(targetguild.id, targetchannel.id, targetuser.id))
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_ban_here', user_id=targetuser.id, user_name=targetuser.name, user_discriminator=targetuser.discriminator, guild_name=targetguild.name, guild_id=targetguild.id, reason=reason, date_exp=date_exp))
            #notifiation
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_ban_here', guild_id=targetguild.id, guild_name=targetguild.name, channel_id=targetchannel.id, channel_name=targetchannel.name, reason=reason, date_exp=date_exp))
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
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #NOW this is really bad
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author.id)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author.id)
                self.runtime_check_guild_lpl(targetguild, ctx.author.id, 2)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            try:
                del self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)]
            except KeyError:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_banned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, guild_id=targetguild.id, guild_name=targetguild.name))
                return None
            self.savedata()
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
                del self.tasks['ab'][targetguild.id][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_unban', user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_unban'))
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
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #NOW this is really bad
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author.id)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author.id)
                self.runtime_check_guild_lpl(targetguild, ctx.author.id, 2)
            targetuser = await self.wrapped_convert(ctx, commands.MemberConverter, commands.UserConverter, user)
            if not targetuser:
                return None
            if channel:
                targetchannel = await self.findchannel(targetguild, channel)
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='channel'))
                return
            else:
                targetchannel = ctx.channel
            try:
                del self.data['guild_data'][str(targetguild.id)]['banned_users'][str(targetuser.id)]
            except KeyError:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'custom_errors', self.conf, conftemplate, 'non_banned', user_name=targetuser.name, user_discriminator=targetuser.discriminator, guild_id=targetguild.id, guild_name=targetguild.name))
                return None
            self.savedata()
            if targetuser.id in self.tasks['gab'][targetguild.id]:
                self.tasks['gab'][targetguild.id][targetuser.id].cancel()
                del self.tasks['ab'][targetguild.id][targetuser.id]
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_unban', user_name=targetuser.name, user_discriminator=targetuser.discriminator))
            try:
                _lang = self.getLanguage(targetuser.id, None, self.lang)
                await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_unban'))
            except discord.Forbidden:
                pass
        @commands.command()
        @commands.is_owner()
        async def abans(ctx, channel=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            fields = []
            for userid in self.data['user_data']:
                if 'author_ban' in self.data['user_data'][userid]:
                    ban = self.data['user_data'][userid]['author_ban']
                    banned = self.get_user(int(userid))
                    if banned: #if user actually exists
                        try:
                            date_exp = datetime.datetime(**ban['date_exp'])
                        except (KeyError, AttributeError):
                            date_exp = Never
                        fields.append({'name': {'user_name': banned.name, 'user_discriminator': banned.discriminator, 'user_id': banned.id}, 'value': {'reason': ban['reason'], 'date_exp': date_exp}})
                    else:
                        try:
                            date_exp = datetime.datetime(**ban['date_exp'])
                        except (KeyError, AttributeError):
                            date_exp = Never
                        fields.append({'name': {'user_name': ('Unknown User (%s)'%userid), 'user_discriminator': '0000', 'user_id': userid}, 'value': {'reason': ban['reason'], 'date_exp': date_exp}})
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'author_ban_list', fields=fields, banned_count=len(fields)))
        @commands.command()
        async def bans(ctx, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #
            ctx.guild = targetguild
            #
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author.id)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author.id)
                self.runtime_check_guild_lpl(targetguild, ctx.author.id, 2)
            fields = []
            for userid in self.data['guild_data'][str(targetguild.id)]['banned_users']:
                ban = self.data['guild_data'][str(targetguild.id)]['banned_users'][userid]
                banned = self.get_user(int(userid))
                if banned: #if user actually exists
                    try:
                        date_exp = datetime.datetime(**ban['date_exp'])
                    except (KeyError, AttributeError):
                        date_exp = Never
                    fields.append({'name': {'user_name': banned.name, 'user_discriminator': banned.discriminator, 'user_id': banned.id}, 'value': {'reason': ban['reason'], 'date_exp': date_exp}})
                else:
                    try:
                        date_exp = datetime.datetime(**ban['date_exp'])
                    except (KeyError, AttributeError):
                        date_exp = Never
                    fields.append({'name': {'user_name': ('Unknown User (%s)'%userid), 'user_discriminator': '0000', 'user_id': userid}, 'value': {'reason': ban['reason'], 'date_exp': date_exp}})
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'info', self.conf, conftemplate, 'guild_admin_ban_list', fields=fields, banned_count=len(fields)))
        #Load internal commands
        async def bansin(ctx, channel=None, guild=None):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            if guild:
                targetguild = await self.wrapped_convert(ctx, GuildConverter, GuildConverter, guild)
                if not targetguild:
                    return
            elif not ctx.guild:
                await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'command_errors', self.conf, conftemplate, 'MissingRequiredArgument', param='guild'))
                return
            else:
                targetguild = ctx.guild
            #
            ctx.guild = targetguild
            #
            if channel:
                targetchannel = await self.wrapped_convert(ctx, commands.TextChannelConverter, commands.TextChannelConverter, channel)
                if not targetchannel:
                    return
            if not (ctx.author.id == self.owner_id and self.conf['owner_permission_bypass']):
                self.runtime_check_authorban_guild(targetguild, ctx.author.id)
                self.runtime_check_guild_authoradminban(targetguild, ctx.author.id)
                self.runtime_check_guild_lpl(targetguild, ctx.author.id, 2)
            fields = []
        self.add_command(langs)
        self.add_command(setlang)
        self.add_command(lang)
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
        self.add_command(banhere)
        self.add_command(unbanhere)
        self.add_command(setpermlevel)
        self.add_command(setrolelevel)
        self.add_command(setnotifychannel)
        #Command groups
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
    async def wrapped_convert(self, ctx, converter1, converter2, arg):
        try:
            if ctx.guild:
                target = await converter1().convert(ctx, arg)
            else:
                target = await converter2().convert(ctx, arg)
            return target
        except (commands.ConversionError, commands.BadArgument):
            _lang = self.getLanguage(ctx.author.id, ctx.guild.id if ctx.guild else None, self.lang)
            await ctx.send(**self.renderMessage(self.lang[_lang], langtemplate, 'common_errors', self.conf, conftemplate, 'NotFound', item=arg))
            return None
    def savedata(self):
        fl = open(dataf, 'w')
        fl.write(json.dumps(self.data,indent=True))
        fl.close()
    def findchannel(self, guild, channel):
        if str(channel).isnumeric():
            targetchannel = discord.utils.get(guild.text_channels, id=int(channel))
            if not targetchannel:
                raise discord.NotFound('Channel with ID %s not found'%channel, item=channel)
                return None
        else:
            targetchannel = discord.utils.get(guild.text_channels, name=channel)
            if not targetchannel:
                raise discord.NotFound('Channel with name %s not found'%channel, item=channel)
                return None
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
    async def authorban_expiry_timer(self, id):
        async def notify():
            try:
                targetuser = self.get_user(int(id))
                if targetuser:
                    _lang = self.getLanguage(int(id), None, self.lang)
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned'))
            except discord.Forbidden:
                pass
        if 'date_exp' not in self.data['user_data'][str(id)]['author_ban']:
            return False
        trg = datetime.datetime(**self.data['user_data'][str(id)]['author_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['user_data'][str(id)]['author_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_ban' in self.data['user_data'][str(id)]:
            del self.data['user_data'][str(id)]['author_ban']
            self.savedata()
            await notify()
        return True
    async def authorbanplace_expiry_timer(self, id, guildid, channelid):
        async def notify():
            try:
                targetuser = self.get_user(int(id))
                targetguild = self.get_guild(int(guildid))
                targetchannel = self.get_channel(int(channelid))
                if targetuser and targetguild and targetchannel:
                    _lang = self.getLanguage(int(id), None, self.lang)
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_here', guild_name=targetguild.name, guild_id=guildid, channel_name=targetchannel.name, channel_id=channelid))
            except discord.Forbidden:
                pass
        if 'date_exp' not in self.data['user_data'][str(id)]['author_ban_places'][str(guildid)][str(channelid)]:
            return False
        trg = datetime.datetime(**self.data['user_data'][str(id)]['author_ban_places'][str(guildid)][str(channelid)]['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['user_data'][str(id)]['author_ban_places'][str(guildid)][str(channelid)]
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if str(channelid) in self.data['user_data'][str(id)]['author_ban_places'][str(guildid)]:
            del self.data['user_data'][str(id)]['author_ban_places'][str(guildid)][str(channelid)]
            self.savedata()
            await notify()
        return True
    async def authoradminban_expiry_timer(self, id):
        async def notify():
            try:
                targetguild = self.get_guild(int(id))
                targetuser = targetguild.owner
                if targetguild:
                    _lang = self.getLanguage(None, int(id), self.lang)
                    await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_unbanned'))
                if targetuser:
                    _lang = self.getLanguage(int(id), None, self.lang)
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authoradminban_unbanned_ownerdm', guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass
        if 'date_exp' not in self.data['guild_data'][str(id)]['author_administration_ban']:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(id)]['author_administration_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(id)]['author_administration_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_administration_ban' in self.data['guild_data'][str(id)]:
            del self.data['guild_data'][str(id)]['author_administration_ban']
            self.savedata()
            await notify()
        return True
    async def authorbanguild_expiry_timer(self, id):
        async def notify():
            try:
                targetguild = self.get_guild(int(id))
                targetuser = targetguild.owner
                if targetguild:
                    _lang = self.getLanguage(None, int(id), self.lang)
                    await self.getNotifyChannel(targetguild).send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_guild'))
                if targetuser:
                    _lang = self.getLanguage(int(id), None, self.lang)
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'authorban_unbanned_guild_ownerdm', guild_id=targetguild.id, guild_name=targetguild.name))
            except discord.Forbidden:
                pass
        if 'date_exp' not in self.data['guild_data'][str(id)]['author_ban']:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(id)]['author_ban']['date_exp'])
        if datetime.datetime.now() >= trg:
            del self.data['guild_data'][str(id)]['author_ban']
            self.savedata()
            await notify()
            return True
        td = trg - datetime.datetime.now()
        await asyncio.sleep(td.total_seconds())
        if 'author_ban' in self.data['guild_data'][str(id)]:
            del self.data['guild_data'][str(id)]['author_ban']
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
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_unban', guild_id=guildid, guild_name=targetguild.name))
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
                    await targetuser.send(**self.renderMessage(self.lang[_lang], langtemplate, 'notifications', self.conf, conftemplate, 'guild_admin_unban_here', guild_id=guildid, guild_name=targetguild.name, channel_id=channelid, channel_name=targetchannel.name))
            except discord.Forbidden:
                pass
        if 'date_exp' not in self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)][str(userid)]:
            return False
        trg = datetime.datetime(**self.data['guild_data'][str(guildid)]['placebanned_users'][str(channelid)]['date_exp'])
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
    #Runtime checks shouldn't be used as decorators: it should be used as regular functions and they MAY also require context
    #Runtime checks allows the commands to perform checks by using custom arguments.
    #When runtime check has passed successfully, it just returns True, otherwise raises an exception.
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
                return False
            else:
                if withdraw:
                    self.data['user_data'][str(ctx.author.id)]['points'] -= cost
                return True
        except (AttributeError, KeyError):
            self.logger.error('The user %s may not been intialized, exception traceback:%s\n'%(ctx.author.id, traceback.format_exc()))
            raise InsufficientPoints('Not enough points.',insuf=cost, price=cost)
            return False
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
                raise InsufficientGuildPoints('Not enough points on this guild.', insuf=(cost - _user_points), price=cost)
                return False
            else:
                if withdraw:
                    self.data['guild_data'][str(guild.id)]['points'][str(ctx.author.id)] -= cost
                return True
        except (AttributeError, KeyError):
            self.logger.error('The user %s may not been intialized, exception traceback:%s\n'%(ctx.author.id, traceback.format_exc()))
            raise InsufficientGuildPoints('Not enough points on this guild.',insuf=cost, price=cost)
            return False
    #Checks the local permission level of the user in a certain guild.
    #Current default of the lplvalue levels:
    # -1 (Unverified member: if the guild have a private mode and this member is unverified: unable to write messages and view some channels)
    #  0 (Regular member: default permissions)
    #  1 (Message moderator: able to mute someone and manage messages, manage warnings, but not permitted to ban or kick someone.)
    #  2 (Member moderator: able to change nicknames, ban, kick, voice mute/deafen)
    #  3 (Guild controller: exclusive, able to modify some basic bot-side guild settings, but not permitted to manage channels/guild/roles etc.)
    #  4 (Channel editor: able to change the channels/categories name and description, excluding their overwrites)
    #  5 (Channel manager: same as above, but also allows to create/delete channels or categories and manage overwrites, refers to Manage Channels permission)
    #  6 (Guild editor: refers to Manage Guild permission)
    #  7 (Guild manager: refers to Manage Guild, Manage Roles, Manage Emojis, Manage Webhooks permissions)
    #  8 or more (Guild administrator: all possible permissions is granted, including Administrator, View Audit Log permissions)
    def runtime_check_guild_lpl(self, guild, user, lplvalue, raisee=True):
        if user.id == self.owner_id and 'owner_permission_bypass' in self.conf:
            if bool(self.conf['owner_permission_bypass']):
                return True
        #shortcut
        def fail():
            if user.id == self.owner_id:
                raise NotAllowedBypass('Regardless of the authority, you still don\'t have the permission to perform this action on that guild.')
                return False
            else:
                raise NotAllowed('You don\'t have the permission to perform this action on that guild.')
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
                    if self.data['guild_data'][str(guild.id)]['role_settings'][str(_role.id)]['local_permission_level'] >= lplvalue:
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
                    raise AuthorBan('You have been banned by author. Reason: %s'%reason, reason=reason, date_exp=date_exp)
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
                #check if we have the guild.
                place = self.data['user_data'][str(user.id)]['author_ban_places'][str(guild.id)][str(channel.id)]
                #if we didn't got a KeyError exception, we ran on the place.
                if 'date_exp' in place:
                    date_exp = datetime.datetime(**place['date_exp'])
                else:
                    date_exp = Never
                if 'reason' in place:
                    reason = place['reason']
                else:
                    reason = '--'
                if raisee:
                    raise AuthorBanHere('You have been banned by author in that place. Reason: %s'%reason, reason=reason, date_exp=(datetime.datetime(**place['date_exp']) if 'date_exp' in place else Never))
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
                    raise AuthorAdministrationBan('Administration of this guild has been forbidden. Reason: %s.'%_ban['reason'], reason=_ban['reason'], date_exp=(datetime.datetime(**_ban['date_exp']) if 'date_exp' in _ban else Never))
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
                    raise AuthorBanGuild('This guild has been banned by the author. Reason: %s.'%_ban['reason'], reason=_ban['reason'], date_exp=(datetime.datetime(**_ban['date_exp']) if 'date_exp' in _ban else Never))
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
                    raise GuildAdminBan('You has been banned from this guild by guild\'s owner. Reason: %s.'%_ban['reason'], reason=_ban['reason'], date_exp=datetime.datetime(**_ban['date_exp']))
                return False
            else:
                return True
        except (AttributeError, KeyError):
            return True
    def runtime_check_guild_ownership(self, guild, user, raisee=True):
        fail = False
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
                    raise NotAllowedBypass('Regardless of the authority, you still don\'t have the permission to perform this action on that guild.')
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
                lpl1_ = int(self.data['guild_data'][str(guild.id)]['role_settings'][str(user1.top_role.id)]['local_permission_level'])
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
                lpl2_ = int(self.data['guild_data'][str(guild.id)]['role_settings'][str(user2.top_role.id)]['local_permission_level'])
                if lpl2_ > lpl2:
                    lpl2 = lpl2_
        except (KeyError, ValueError, AttributeError):
            pass
        if lpl1 < lpl2:
            return True
        else:
            if user1.id == self.owner_id:
                raise NotAllowedBypass('Regardless of the authority, you still don\'t have the permission to perform this action on that guild.')
                return False
            else:
                raise NotAllowed('You don\'t have the permission to perform this action on that guild.')
                return False
    def loadMods(self):
        if not os.path.isdir(self.modfold):
            os.mkdir(self.modfold)
        self.logger.info('Loading modules from %s...' % os.path.abspath(self.modfold))
        #this is a modules.
        #I have discovered that this library (discord.py) is already have a modding solution (but it's too late), it is called "extensions".
        #But instead of using this, I've made my own solution (oh why?)
        # TODO: depends and softdepends sort mechanism
        try:
            files = list()
            with os.scandir(self.modfold) as it:
                for entry in it:
                    if entry.is_file() and entry.name.endswith('.py'):
                        files.append(entry.name)
            if len(files) == 0:
                self.logger.warning('No mods has been loaded.')
                print('Warning! No mods has been loaded.')
            else:
                self.logger.info('{0} mods in order to load: {1}'.format(len(files),', '.join(files)))
                for name in files:
                    self.loadMod(name)
        except (ImportError, IOError) as exc:
            tr = traceback.format_exc(exc)
            self.logger.critical('Failed to load mods: '+str(exc)+'\n'+tr)
            print('Failed to load : '+str(exc)+'\n'+tr)
            return False
        else:
            self.logger.info('Successfully loaded modules.')
            return True
    def loadMod(self, name):
        _flabel = name.split('.')[0]
        self.logger.info('Attempting to load \"%s\"...'%_flabel)
        _cspec = importlib.util.spec_from_file_location(_flabel,os.path.abspath('mods')+'/'+name)
        _mod = importlib.util.module_from_spec(_cspec)
        try:
            _cspec.loader.exec_module(_mod)
        except Exception as exc:
            print('Failed to load module \"'+_flabel+'\": '+str(exc))
            _exception = traceback.format_exc()
            self.logger.error('Module "'+_flabel+'" was failed to load. Exception traceback: '+_exception)
            return False
        else:
            print('Module \"%s\" loaded successfully.'%_flabel)
            self.mods.append(_mod)
            self.mod_dict[_mod] = []
            print('Loading cogs in module %s...'%_mod.__name__)
            self.logger.info('Loading cogs in module %s...'%_mod.__name__)
            try:
                _cogs = _mod.getCogs()
                for cog in _cogs:
                    print('Loading cog %s...'%cog.__name__)
                    self.logger.info('Loading cog %s...'%cog.__name__)
                    try:
                        _cog = cog(self)
                        self.add_cog(_cog)
                        self.mod_dict[_mod].append(_cog)
                    except Exception as exc:
                        print('Failed to load cog {0}:\n{1}'.format(cog.__name__,traceback.format_exc()))
                        self.logger.error('Failed to load cog {0}:\n{1}'.format(cog.__name__,traceback.format_exc()))
                        return False
            except AttributeError:
                print('Error: This module does not have getCogs function.')
                self.logger.error('Module "%s" does not have getCogs function.'%_mod.__name__+'\n'+traceback.format_exc())
                return False
            else:
                print('Cogs loaded!')
                self.logger.info('Cogs for module "%s" loaded.'%_mod.__name__)
            try:
                _exceptions = _mod.getExceptions()
                self.mod_exc_dict[_mod] = _exceptions
                self.logger.info('Got %d exceptions to the ignorelist from module %s' % (len(_exceptions), _mod.__name__))
            except Exception:
                pass
            return True
    def unloadMod(self, modName):
        if not modName in [x.__name__ for x in self.mods]:
            self.logger.error('unloadMod: Module with name %s not found!'%modName)
            print('Module with name %s not found!'%modName)
            return False
        else:
            # current module
            _mod = self.mods[[x.__name__ for x in self.mods].index(modName)]
            self.logger.info('Preparing to unload module "%s"...'%_mod.__name__)
            # remove matching cogs from the bot
            _mod_classes = _mod.getCogs()
            _loaded_classes = [x.__class__ for x in self.cogs.values()]
            # perform the intersection between module cogs classes and loaded cogs
            # and then convert them into the module qualified names.
            _intersection = list([set(_mod_classes) & set(_loaded_classes)])
            for cog in _intersection:
                _qualif_name = list(self.cogs.keys())[ list(_loaded_classes).index(list(cog)[0]) ]
                self.logger.info('Unloading cog {0} (class {1})'.format(_qualif_name, list(cog)[0].__name__))
                self.remove_cog(_qualif_name)
            del self.mods[self.mods.index(_mod)]
            del self.mod_dict[_mod]
            try:
                del self.mod_exc_dict[_mod]
            except KeyError:
                pass
            return True
    def reloadMod(self, modName):
        _file = str(modName)+'.py'
        if not modName in [x.__name__ for x in self.mods]:
            self.logger.error('unloadMod: Module with name %s not found!'%modName)
            print('Module with name %s not found!'%modName)
            return False
        elif not os.path.isfile('mods/'+_file):
            print('The file of the module %s has been moved or deleted, reload failed.'%modName)
            self.logger.warning('reloadMod: The file of the module %s is not found, reload failed.'%modName)
            return False
        else:
            self.logger.info('Reloading module %s'%modName)
            if not self.unloadMod(modName):
                self.logger.error('reloadMod: Module %s didn\'t unloaded. Reload failed.'%modName)
                return False
            if not self.loadMod(_file):
                self.logger.error('reloadMod: Module %s refused to load after unloading. Reload failed.'%modName)
                return False
            self.logger.info('Module %s reloaded successfully.'%modName)
            return True
    def loadModLangs(self, langfold, langvalid, langtemplate, default_lang_name='en_US'):
        """
        Loads and validates language files for modules. Returns a tuple (dict, dict, dict)
        First is a language dictionary, second is a dict of lists of missing fields, third is a dict of lists of insufficient (with wrong type) fields.
        """
        _langs = {}
        self.logger.info('Loading language settings for this cog...')
        if not os.path.isdir(langfold):
            os.mkdir(langfold)
        if not 'default_lang' in self.conf:
            self.logger.warning('%s: The "default_lang" option is not set in the configuration, using "en_US" as the default.')
            self.conf['default_lang'] = "en_US"
        _files = []
        missing_fields = {}
        insuf_fields = {}
        with os.scandir(langfold) as files:
            for file in files:
                if file.name.endswith('.json') and file.is_file():
                    _files.append(file)
        if len(_files) == 0:
            print('No language settings was found! Generating default language file...\n - You can copy&paste, rename it and edit them to create your own translation.')
            self.logger.warning('Directory "%s" does not contain any language sets! Loading default built-in language...'%langfold)
            _langs[default_lang_name] = langtemplate
            _langs['default'] = _langs[default_lang_name]
            self.logger.info('Dumping built-in language into "%s" ...'%os.path.abspath(langfold))
            fl = open(langfold+f'/{default_lang_name}.json', 'x')
            fl.write(json.dumps(langtemplate, indent=True))
            fl.close()
            logger.info('Successfully created default language.')
            return _langs, missing_fields, insuf_fields
        else:
            if not conf['default_lang']+'.json' in [x.name for x in _files]:
                print('%s: Language settings "%s" was not found!'%(__name__, conf['default_lang']+'.json'))
                logger.warning('%s:  "%s/%s" language is not found! Using built-in default language instead...'%(__name__,langfold,conf['default_lang']+'.json'))
                _langs[default_lang_name] = langtemplate
                _langs['default'] = _langs[default_lang_name]
                self.logger.info('Dumping built-in language into "%s" ...'%os.path.abspath(langfold))
                fl = open(langfold+f'/{default_lang_name}.json', 'x')
                fl.write(json.dumps(langtemplate, indent=True))
                fl.close()
                logger.info('Successfully created default language.')
            #else:
            #    _langs['default'] = conf['default_lang']+'.json'
            _error_enc = False
            logger.info('Reading language content...')
            for file in _files:
                _flabel = file.name.split('.')[0]
                #fl = None
                #ld = None
                try:
                    fl = open(langfold+'/'+file.name, 'r')
                    ld = json.loads(fl.read())
                except json.JSONDecodeError as exc:
                    _exctext = traceback.format_exc()
                    print('Error: language file "%s" is damaged.'%file.name)
                    logger.critical('%s: language file "%s" is corrupted and unable to load.'%(_flabel,file.name))
                    print(exc)
                    fl.close()
                else:
                    #We are successfully got the language content, so we can validate them with validator pattern and by recursive function.
                    #The validation is need to keep out our program from KeyError or TypeError exceptions and notify the bot's owner about missing translation.
                    self.logger.info('Validating %s...'%_flabel)
                    _missing_fields, _insuf_fields = self.validateLang(ld, langvalid)
                    if len(_missing_fields)+len(_insuf_fields) > 0:
                        logger.critical('%s: Validance test failed. Missing nodes (%d): %s | Insufficient nodes (%d): %s.'%(__name__, len(_missing_fields),', '.join(_missing_fields),len(_insuf_fields),', '.join(_insuf_fields)))
                        print('%s: lang file is invalid. Please check the log.'%_flabel)
                        missing_fields[_flabel] = _missing_fields
                        insuf_fields[_flabel] = _insuf_fields
                    else:
                        logger.info('Successful validance test! Language "%s" loaded.'%_flabel)
                    _langs[_flabel] = ld
            _langs['default'] = _langs[default_lang_name]
            return _langs, missing_fields, insuf_fields
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id
    async def start(self, *args, **kwargs):
        # --- Do something after that event loop has been started
        #init authorban timers
        for _user in self.data['user_data']:
            if 'author_ban' in self.data['user_data'][_user]:
                if 'date_exp' in self.data['user_data'][_user]['author_ban']:
                    self.tasks['ab'][int(_user)] = asyncio.create_task(self.authorban_expiry_timer(int(_user)))
            #init place-authorban timers
            if 'author_ban_places' in self.data['user_data'][_user]:
                for guild in self.data['user_data'][_user]['author_ban_places']:
                    for channel in self.data['user_data'][_user]['author_ban_places'][guild]:
                        if 'date_exp' in self.data['user_data'][_user]['author_ban_places'][guild][channel]:
                            self.tasks['abh'][int(_user)]
        #init authorban guild timers
        for _guild in self.data['guild_data']:
            if 'author_ban' in self.data['guild_data'][_guild]:
                if 'date_exp' in self.data['guild_data'][_guild]['author_ban']:
                    self.tasks['abg'][int(_guild)] = asyncio.create_task(self.authorbanguild_expiry_timer(int(_guild)))
            elif 'banned_users' in self.data['guild_data'][_guild]: #init guild admin's bans
                for _user in self.data['guild_data'][_guild]['banned_users']:
                    if 'date_exp' in self.data['guild_data'][_guild]['banned_users'][_user]:
                        if int(_guild) not in self.tasks['gab']:
                            self.tasks['gab'][int(_guild)] = {}
                        self.tasks['gab'][int(_guild)][int(_user)] = asyncio.create_task(self.guildadminban_expiry_timer(int(_guild), int(_user)))
        await super().start(*args)
    def formatExactDuration(self, td, language, shorten=False, in_word=False, years=True, months=True, weeks=True, days=True, hours=True, minutes=True, seconds=True):
        '''
        This function formats the exact string of timedelta in the specified language.
        It uses the only seconds and convert it to the minutes, days, weeks, months etc.
        Example (in the default language):
             short: 1h 25min 59secs
            full: 1 hour 25 minutes 59 seconds
        '''
        subtr = abs(td.total_seconds())
        strout = ''
        _lang_sc = language['contents']['formats']['duration']
        yearsc = subtr//31557600
        if yearsc > 0 and years:
            _num_sc = str(nearList(_lang_sc['ys'].keys() if shorten else _lang_sc['years'].keys(), yearsc))
            strout += '%d%s ' % (yearsc, _lang_sc['ys'][_num_sc] if shorten else ' '+_lang_sc['years'][_num_sc] )
            subtr -= 31557600 * years
        monthsc = subtr//2629800
        if monthsc > 0 and months:
            _num_sc = str(nearList(_lang_sc['mons'].keys() if shorten else _lang_sc['months'].keys(), monthsc))
            strout += '%d%s ' % (monthsc, _lang_sc['mons'][_num_sc] if shorten else ' '+_lang_sc['months'][_num_sc])
            subtr -= 2629800 * monthsc
        weeksc = subtr//604800
        if weeksc > 0 and weeks:
            _num_sc = str(nearList(_lang_sc['ws'].keys() if shorten else _lang_sc['weeks'].keys(), weeksc))
            strout += '%d%s ' % (weeksc, _lang_sc['ws'][_num_sc] if shorten else ' '+_lang_sc['weeks'][_num_sc])
            subtr -= 604800 * weeksc
        daysc = subtr//86400
        if daysc > 0 and days:
            _num_sc = str(nearList(_lang_sc['ds'].keys() if shorten else _lang_sc['days'].keys(), daysc))
            strout += '%d%s ' % (daysc, _lang_sc['ds'][_num_sc] if shorten else ' '+_lang_sc['days'][_num_sc])
            if in_word and daysc == 1 and subtr%86400 == 0:
                if td.total_seconds() < 0:
                    return language['contents']['formats']['date_relative']['yesterday']
                else:
                    return language['contents']['formats']['date_relative']['tomorrow']
            subtr -= 86400 * daysc
        hoursc = subtr//3600
        if hoursc > 0 and hours:
            _num_sc = str(nearList(_lang_sc['hs'].keys() if shorten else _lang_sc['hours'].keys(), hoursc))
            strout += '%d%s ' % (hoursc, _lang_sc['hs'][_num_sc] if shorten else ' '+_lang_sc['hours'][_num_sc])
            subtr -= 3600 * hoursc
        minsc = subtr//60
        if minsc > 0 and minutes:
            _num_sc = str(nearList(_lang_sc['mins'].keys() if shorten else _lang_sc['minutes'].keys(), minsc))
            strout += '%d%s ' % (minsc, _lang_sc['mins'][_num_sc] if shorten else ' '+_lang_sc['minutes'][_num_sc])
            subtr -= 60 * minsc
        if subtr > 0 and seconds:
            _num_sc = str(nearList(_lang_sc['secs'].keys() if shorten else _lang_sc['seconds'].keys(), subtr))
            strout += '%d%s' % (subtr, _lang_sc['secs'][_num_sc] if shorten else ' '+_lang_sc['seconds'][_num_sc])
        return strout
    def formatAverageDuration(self, td, language, shorten=False, in_word=True):
        '''
        This function formats the near of timedelta in the specified language.
        It uses the only seconds and convert it to the minutes, days, weeks, months etc.
        Example (in the default language):
             short: 2mons
            full: 2 months
        '''
        subtr = abs(td.total_seconds())
        strout = language['contents']['formats']['date_relative']['in_exact_time']+' ' if in_word else ''
        _lang_sc = language['contents']['formats']['duration']
        yearsc = subtr//31557600
        monthsc = subtr//2629800
        weeksc = subtr//604800
        daysc = subtr//86400
        hoursc = subtr//3600
        minsc = subtr//60
        if yearsc > 0:
            _num_sc = str(nearList(_lang_sc['ys'].keys() if shorten else _lang_sc['years'].keys(), yearsc))
            strout += '%d%s' % (yearsc, _lang_sc['ys'][_num_sc] if shorten else ' '+_lang_sc['years'][_num_sc] )
            #subtr -= 31557600 * years
        elif monthsc > 0:
            _num_sc = str(nearList(_lang_sc['mons'].keys() if shorten else _lang_sc['months'].keys(), monthsc))
            strout += '%d%s' % (monthsc, _lang_sc['mons'][_num_sc] if shorten else ' '+_lang_sc['months'][_num_sc])
            #subtr -= 2629800 * monthsc
        elif weeksc > 0:
            _num_sc = str(nearList(_lang_sc['ws'].keys() if shorten else _lang_sc['weeks'].keys(), weeksc))
            strout += '%d%s' % (weeksc, _lang_sc['ws'][_num_sc] if shorten else ' '+_lang_sc['weeks'][_num_sc])
            #subtr -= 604800 * weeksc
        elif daysc > 0:
            _num_sc = str(nearList(_lang_sc['ds'].keys() if shorten else _lang_sc['days'].keys(), daysc))
            strout += '%d%s' % (daysc, _lang_sc['ds'][_num_sc] if shorten else ' '+_lang_sc['days'][_num_sc])
            if in_word and daysc == 1:
                if td.total_seconds() < 0:
                    strout = language['contents']['formats']['date_relative']['yesterday']
                else:
                    strout = language['contents']['formats']['date_relative']['tomorrow']
            #subtr -= 86400 * daysc
        elif hoursc > 0:
            _num_sc = str(nearList(_lang_sc['hs'].keys() if shorten else _lang_sc['hours'].keys(), hoursc))
            #subtr -= 3600 * hoursc
            strout += '%d%s' % (hoursc, _lang_sc['hs'][_num_sc] if shorten else ' '+_lang_sc['hours'][_num_sc])
        elif minsc > 0:
            _num_sc = str(nearList(_lang_sc['mins'].keys() if shorten else _lang_sc['minutes'].keys(), minsc))
            #subtr -= 60 * minsc
            strout += '%d%s' % (minsc, _lang_sc['mins'][_num_sc] if shorten else ' '+_lang_sc['minutes'][_num_sc])
        elif subtr > 0:
            _num_sc = str(nearList(_lang_sc['secs'].keys() if shorten else _lang_sc['seconds'].keys(), subtr))
            strout += '%d%s' % (subtr, _lang_sc['secs'][_num_sc] if shorten else ' '+_lang_sc['seconds'][_num_sc])
        else:
            strout = language['contents']['formats']['date_relative']['now']
        return strout
    def renderMessage(self, language, default_language, message_type, config, default_config=None, definition=None, fields=None, date_relative=False, show_direction=False, duration_options={}, **kwargs):
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
        if (message_type not in config['messages']) or (message_type not in language["contents"]["messages"]):
            self.logger.error('renderMessage: unknown message type: '+message_type)
            return {'content': 'Error occurred, please contact to the bot\'s owner'}
        def getDateFormatter(val):
            return {
                'year': val.year,
                'month': val.month,
                'month_name': language['contents']['formats']['months'][str(val.month)],
                'month_name_capital': language['contents']['formats']['months'][str(val.month)].capitalize(),
                'month_sname': language['contents']['formats']['mons'][str(val.month)],
                'month_sname_capital': language['contents']['formats']['mons'][str(val.month)].capitalize(),
                'day': val.day,
                'dow': val.weekday(),
                'dow_name': language['contents']['formats']['days_of_week'][str(val.weekday())],
                'dow_name_capital': language['contents']['formats']['days_of_week'][str(val.weekday())].capitalize(),
                'dow_sname': language['contents']['formats']['dow'][str(val.weekday())],
                'dow_sname_capital': language['contents']['formats']['dow'][str(val.weekday())].capitalize(),
                'hour': enzero(val.hour),
                '12-hour': enzero(val.hour) if val.hour <= 12 else enzero(val.hour%12),
                'minute': enzero(val.minute),
                'second': enzero(val.second),
                'meridiem': 'AM' if val.hour <= 12 else 'PM'
            }

        #reconstruct **kwargs and convert every argument but dict and others
        def convert(kws):
            formatter = {}
            for k in kws:
                val = kws[k]
                if type(val) == str:
                    formatter[k] = val
                elif type(val) in [int, float, complex]:
                    formatter[k] = str(val)
                elif type(val) == bool:
                    if val:
                        formatter[k] = language['contents']['formats']['logic']['true'].capitalize()
                    else:
                        formatter[k] = language['contents']['formats']['logic']['false'].capitalize()
                elif type(val) == State:
                    if bool(val):
                        formatter[k] = language['contents']['formats']['switch']['on']
                    else:
                        formatter[k] = language['contents']['formats']['switch']['off']
                elif type(val) == Partially:
                    formatter[k] = language['contents']['formats']['logic']['partially'].capitalize()
                elif type(val) == type(None):
                    formatter[k] = language['contents']['formats']['logic']['none'].capitalize()
                elif val == Never:
                    formatter[k] = language['contents']['formats']['date_relative']['never'].capitalize()
                elif val == Forever:
                    formatter[k] = language['contents']['formats']['date_relative']['forever'].capitalize()
                elif type(val) == datetime.datetime:
                    if date_relative:
                        td = val - datetime.datetime.now()
                        direction = language['contents']['formats']['duration']['direction']
                        if show_direction:
                            direction = ' '+direction['after'] if td < datetime.timedelta(0) else ' '+direction['before']
                        else:
                            direction = ''
                        formatter[k] = self.formatExactDuration(td, language, **duration_options)+direction
                    else:
                        formatter[k] = language['contents']['formats']['date_format'] % getDateFormatter(val)
                elif type(val) == datetime.timedelta:
                    if date_relative:
                        direction = language['contents']['formats']['duration']['direction']
                        if show_direction:
                            direction = ' '+direction['after'] if val < datetime.timedelta(0) else ' '+direction['before']
                        else:
                            direction = ''
                        formatter[k] = self.formatExactDuration(val, language, **duration_options)+direction
                    else:
                        dt = datetime.datetime.now() + val
                        formatter[k] = language['contents']['formats']['date_format'] % getDateFormatter(dt)
                elif type(val) == inspect.Parameter:
                    formatter[k] = val.name
                elif type(val) in [list, tuple, set]:
                    _dict = {}
                    inc=0
                    for el in val:
                        _dict[inc] = el
                    _conv = convert(_dict).values()
                    formatter[k] = ', '.join(_conv)
                else:
                    formatter[k] = repr(val)
            return formatter
        formatter = convert(kwargs)
        #mandatory options: there is no mandatory options, you can send an empty embed if you want to.
        _lang_sc = language["contents"]['messages'][message_type]
        _conf_sc = config['messages']
        def parse():
            if 'definitions' in language["contents"]['messages'][message_type]:
                #Avoiding KeyError exception by using nested conditions
                if definition and definition in _lang_sc['definitions']:
                    decl = lambda item: _lang_sc['definitions'][definition][item] % formatter \
                        if item in _lang_sc['definitions'][definition] \
                        else (_lang_sc[item] if item in _lang_sc else None)
                else:
                    decl = lambda item: _lang_sc[item] if item in _lang_sc else None
            else:
                #This is unnecessary, because the module shouldn't ask for definition unless it is defined in the language
                decl = lambda item: _lang_sc[item] if item in _lang_sc else None
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
                    embed.set_author(name=_author,icon_url=(_conf_sc[message_type]['author_icon_url'] \
                        if 'author_icon_url' in _conf_sc[message_type] else discord.Embed.Empty ))
                if fields and ('fields' in _lang_sc or 'fields' in _lang_sc['definitions'][definition]):
                    for field in fields:
                        embed.add_field( name=decl('fields')['name'] % convert(field['name']), value=decl('fields')['value'] % convert(field['value']) )
                return {'embed': embed}
            else:
                _title = decl('title')
                _description = decl('description')
                _footer = decl('footer')
                _author = decl('author')
                _fields = ''
                if fields and ('fields' in _lang_sc or 'fields' in _lang_sc['definitions'][definition]):
                    for field in fields:
                        _fields += '**%s**\n%s\n'%(decl('fields')['name'] % field['name'], decl('fields')['value'] % field['value'] )
                _content = \
                    ('**'+_author+'**\n' if _author else '')+ \
                    ('**'+_title+'**\n' if _title else '')+ \
                    (_description+'\n' if _description else '')+ \
                    _fields + ('`'+_footer+'`' if _footer else '')
                return {'content': _content if _content else None}
        try:
            return parse()
        except KeyError:
                print('Failed to render %s message!'%message_type)
                self.logger.error('renderMessage: %s'%traceback.format_exc())
                _lang_sc = default_language["contents"]['messages'][message_type]
                _conf_sc = default_config['messages']
                return parse()
    def getLanguage(self, userid, guildid, languages):
        """
        Returns language code for current user or guild.
        When the user didn't set the language for the bot, the function returns a language code for the guild or the default language.
        If the guild has 'language_override' setting, the function returns a language code of the guild regardless of the user setting,
        but if the user doesn't have 'language_override' setting enabled (it couldn't be set and also deprecated).
        """
        #elangs - existing lang codes
        if type(languages).__name__ == 'dict':
            elangs = languages.keys()
        elif type(languages).__name__ in ['set', 'list', 'tuple', 'dict_keys']:
            elangs = list(languages)
        else:
            elangs = list(languages)
        #print('elangs '+str(elangs))
        try:
            user_lang = self.data['user_data'][str(userid)]['language'] \
                if 'language' in self.data['user_data'][str(userid)] \
                else ''
        except KeyError:
            user_lang = ''
        #print('user_lang '+str(user_lang))
        try:
            if guildid is not None:
                try:
                    guild_override = self.data['guild_data'][str(guildid)]['lang_override'] \
                        if 'lang_override' in self.data['guild_data'][str(guildid)] else False
                except KeyError:
                    guild_override = False
                #print('guild_override '+str(guild_override))
                try:
                    user_override = self.data['user_data'][str(userid)]['lang_override'] \
                        if 'lang_override' in self.data['user_data'][str(userid)] else False
                except KeyError:
                    user_override = False
                #print('user_override '+str(guild_override))
                if user_override:
                    if user_lang not in elangs:
                        #print('user_lang not in elangs, return default')
                        return 'default'
                    return user_lang
                elif guild_override:
                    _lang = self.data['guild_data'][str(guildid)]['language']
                    return _lang if _lang in elangs else 'default'
                else:
                    try:
                        if 'language' in self.data['user_data'][str(userid)]:
                            #print('this user have a language setting')
                            return user_lang if user_lang in elangs else 'default'
                    except KeyError:
                        pass
                    try:
                        if 'language' in self.data['guild_data'][str(guildid)]:
                            #print('this guild have a language setting')
                            _lang = self.data['guild_data'][str(guildid)]['language']
                            #print('returning '+_lang if _lang in elangs else 'default')
                            return _lang if _lang in elangs else 'default'
                    except KeyError:
                        pass
                    return 'default'
            else:
                return user_lang if user_lang in elangs else 'default'
        except KeyError:
            #print('got keyerror exception')
            #print(traceback.format_exc())
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
                        num = nd[:len(nd)-len(durationsd[ew][ind])]
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
                        _td += datetime.timedelta(seconds=int(num)*_mul)
        return _td
    def getNotifyChannel(self, guild):
        """Returns messageable TextChannel that was set manually, otherwise return most viewable available channel
        Used for directly messaging to the guild"""
        if 'notify_channel' in self.data['guild_data'][str(guild.id)]:
            return self.get_channel(int(self.data['guild_data'][str(guild.id)]['notify_channel']))
        #get all accessible
        _channels = []
        _counts = []
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                _channels.append(channel)
                _counts.append(len(channel.members))
        _sc = _counts.copy()
        _sc.sort(reverse=True)
        return _channels[_counts.index(_sc[0])]
def main(args):

    logger.setLevel(logging.INFO)
    tm = time.localtime()
    if not os.path.isdir(logfold):
        os.mkdir(logfold)
    if not os.path.isdir(modfold):
        os.mkdir(modfold)
    if not os.path.isdir(langfold):
        os.mkdir(langfold)
    handler = logging.FileHandler(filename=logfold+'/discord-'+enzero(tm.tm_mday)+'-'+enzero(tm.tm_mon)+'-'+enzero(tm.tm_year,4)+'_'+enzero(tm.tm_hour)+'-'+enzero(tm.tm_min)+'-'+enzero(tm.tm_sec)+'.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    #Perform configuration loading.
    global conf
    loadConf()
    loadData()
    #Exit from the program if the language load failed.
    if not loadLangs():
        exit(1)
    loop = asyncio.get_event_loop()
    intents = discord.Intents(members=True, bans=True, emojis=True, guilds=True, integrations=True, webhooks=True, invites=True, voice_states=True, messages=True, guild_messages=True, dm_messages=True, reactions=True, guild_reactions=True, dm_reactions=True, typing=True, guild_typing=True, dm_typing=True)
    if 'owner' in conf.keys():
        bot = PtDiscordBot(logger, conf, data, lang, command_prefix=tuple(conf['prefix']), owner_id=int(conf['owner']), intents=intents)
    else:
        bot = PtDiscordBot(logger, conf, data, lang, command_prefix=tuple(conf['prefix']), intents=intents)
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
                #do nothing
                return
            elif isinstance(exc, commands.CheckFailure):
                msgtype = 'check_failures'
                known_exceptions = bot.lang[langcode]['contents']['messages']['check_failures']['definitions'].keys()
            elif isinstance(exc, commands.CommandError):
                msgtype = 'command_errors'
                known_exceptions = bot.lang[langcode]['contents']['messages']['command_errors']['definitions'].keys()
            if type(exc).__name__ in known_exceptions: #                                                                                  v Whoops, we left an exploit
                await ctx.send(**bot.renderMessage(bot.lang[langcode], langtemplate, msgtype, bot.conf, conftemplate, type(exc).__name__, **exc.__dict__))
            else:
                await ctx.send(**bot.renderMessage(bot.lang[langcode], langtemplate, msgtype, bot.conf, conftemplate, None, exception=str(exc)))
                logger.error("Got an exception while performing requested command: (%s) %s\n%s"%(type(exc).__name__,str(exc), traceback.format_exc()))
        else:
            #Let the cogs to handle the error by itself.
            #logger.critical('There was an error while executing command: '+str(type(exc).__name__)+' | '+str(exc)+'\n'+traceback.format_exc())
            pass
    async def logmsgdeleted(msg):
        assert not isinstance(msg.channel, discord.GroupChannel), 'How the fuck bot appears on the group channel?'
        if isinstance(msg.channel, discord.DMChannel):
            destname = 'DM UID: {0}|{1}#{2}'.format(str(msg.channel.recipient.id),msg.channel.recipient.name,msg.channel.recipient.discriminator)
        elif isinstance(msg.channel, discord.TextChannel):
            destname = 'channel pairs:{0}={1}|{2}={3}'.format(str(msg.channel.guild.id),str(msg.channel.id),msg.channel.guild.name,msg.channel.name)
        else:
            raise Exception('Unknown channel type')
        logger.info(str(msg.author.id)+'|'+msg.author.name+'#'+msg.author.discriminator+' message deleted in '+destname+': '+msg.content)

    bot.add_listener(logmsgdeleted, 'on_message_delete')
    bot.loadConf = loadConf
    loop.dbot = bot
    loop.d = discord
    loop.dcmd = commands
    #loop.cf = conf
    #loop.dt = data
    loop.sys = sys
    #loop.mods = bot.mods
    #loop.mod_dict = bot.mod_dict
    async def shutdown():
        print('Bot has been stopped, saving data...')
        logger.info('Shutting down and saving data...')
        fl = open(dataf, 'w')
        fl.write(json.dumps(data,indent=True))
        fl.close()
        logger.info('Data saved, cancelling all pending tasks...')
        for type in bot.tasks:
            #if type is 'longcmd':
            #    for usertasks in bot.tasks['longcmd'].values():
            #        for task in usertasks:
            #            if not task.cancelled():
            #                task.cancel()
            if type != 'abh':
                for guild in bot.tasks['abh']:
                    for channel in bot.tasks['abh'][guild]:
                        for task in bot.tasks['abh'][guild][channel].values():
                            if not task.cancelled():
                                task.cancel()
            else:
                for task in bot.tasks[type].values():
                    if not task.cancelled():
                        task.cancel()
        logger.info('Logging out...')
        await loop.dbot.close()
    loop.pwroff = shutdown
    loop.run_until_complete(bot.start(conf['token']))
    #loop.run_until_complete(shutdown())
    return 0
if __name__ == '__main__':
    sys.exit(main(sys.argv))

print("ENd...")
