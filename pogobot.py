#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3.")

from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters
from telegram import Bot
import logging
from datetime import datetime, timezone, timedelta
import datetime as dt
import time
import os
import errno
import json
import threading
import fnmatch
import DataSources
import Preferences
import copy
from time import sleep
from geopy.geocoders import Nominatim
import geopy
from geopy.distance import VincentyDistance

from instructions import help_text_1, help_text_2, start_text

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
prefs = Preferences.UserPreferences()
jobs = dict()
geolocator = Nominatim()

# Variables - Empty dicts
sent = dict()
locks = dict()
search_ids = dict()
pokemon_name = dict()
move_name = dict()

location_radius = 1
# Mysql data
thismodule = sys.modules[__name__]


# Command-functions
def cmd_help(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    logger.info('[%s@%s] Sending help text.' % (userName, chat_id))

    bot.sendMessage(chat_id, help_text_1, parse_mode='Markdown')
    bot.sendMessage(chat_id, help_text_2, parse_mode='Markdown')


def cmd_start(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.first_name

    logger.info('[%s@%s] Starting.' % (userName, chat_id))

    bot.sendMessage(chat_id, start_text % (userName), parse_mode='Markdown')

    # Setze default Werte und den Standort auf Kiel
    pref = prefs.get(chat_id)
    checkAndSetUserDefaults(pref)


def cmd_add(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    lan = pref.get('language')
    pokemon_ids = list()
    usage_message = 'Nutzung:\n/pokemon #Nummer oder /pokemon #Nummer1 #Nummer2\n' + \
    '/pokemon #Name oder /pokemon #Name1 #Name2 ... (Ohne #)'

    # Check Args to prevent wrong input
    if args[0].find(',') >= 0:
        args = args[0].split(',')
    else:
        for x in args:
            if x.find(',') >= 0:
                bot.sendMessage(chat_id, text=usage_message)
                return

    if args != []:
        if len(args) <= 0:
            bot.sendMessage(chat_id, text=usage_message)
            return

        if not args[0].isdigit():
            if len(args) == 1 and args[0].upper() in ('GEN1', 'GEN2', 'GEN3', 'GEN4', 'ALLE', 'ALL'):
                    if args[0].upper() == 'GEN1':
                        args = list(range(1, 152))
                    elif args[0].upper() == 'GEN2':
                        args = list(range(152, 252))
                    elif args[0].upper() == 'GEN3':
                        args = list(range(252, 387))
                    elif args[0].upper() == 'GEN4':
                        args = list(range(387, 493))
                    elif args[0].upper() in ['ALLE', 'ALL']:
                        args = list(range(1, 493))

            else:
                for x in args:
                    for poke_id, name in pokemon_name[lan].items():
                        if x.upper() in name.upper():
                            pokemon_ids.append(str(poke_id))
                if len(pokemon_ids) < 1:
                    bot.sendMessage(chat_id, text='*Ich habe nicht alle Pokémon gefunden! Bitte versuche es erneut.*', parse_mode='Markdown')
                    return

                args = pokemon_ids

    for x in args:
        if int(x) > 721 or int(x) <= 0:
            bot.sendMessage(chat_id, text='Bitte keine Pokemonnummer über 721 eingeben!')
            return

    addJob(bot, update, job_queue)
    logger.info('[%s@%s] Add pokemon.' % (userName, chat_id))

    # Wenn nicht geladen oder mit /start gestartet wurde, dann setze ggf. auch default Werte und setze Standort auf Kiel
    loc = pref.get('location')
    if loc[0] is None or loc[1] is None:
        bot.sendMessage(chat_id, text='*Du hast keinen Standort gewählt! Du wirst nun nach Kiel gesetzt!*', parse_mode='Markdown')

    checkAndSetUserDefaults(pref)

    try:
        search = pref.get('search_ids')
        tmp = 'Du hast folgende Pokémon hinzugefügt:\n'

        for x in args:
            if int(x) not in search:
                search.append(int(x))
                tmp += "%s %s\n" % (x, pokemon_name[lan][str(x)])
            else:
                tmp += "Du willst *%s %s* hinzufügen. Es existiert aber bereits in deiner Liste.\n" % (x, pokemon_name[lan][str(x)])

        search.sort()
        pref.set('search_ids',search)

        # Stringlänge berechnen und schneiden:
        cut_position = 1
        while cut_position > 0:
            cut_position = tmp.rfind('\n', 3800, 4096)
            if cut_position > 0:
                bot.sendMessage(chat_id, text = tmp[:cut_position], parse_mode='Markdown')
                tmp = tmp[cut_position+1:]
            else:
                bot.sendMessage(chat_id, text = tmp, parse_mode='Markdown')

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=usage_message)


def cmd_remove(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    lan = pref.get('language')
    pokemon_ids = list()
    usage_message = 'Nutzung:\n/entferne #Nummer oder /entferne #Nummer1 #Nummer2\n' + \
    '/entferne #Name oder /entferne #Name1 #Name2 ... (Ohne #)'
    logger.info('[%s@%s] Remove pokemon.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='Du willst Pokémon entfernen, aber du hast keinen aktiven Scanner!\n' + \
        'Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...')
        return

    # Check Args to prevent wrong input
    if args[0].find(',') >= 0:
        args = args[0].split(',')
    else:
        for x in args:
            if x.find(',') >= 0:
                bot.sendMessage(chat_id, text=usage_message)
                return

    if args != []:
        if len(args) <= 0:
            bot.sendMessage(chat_id, text=usage_message)
            return

        if not args[0].isdigit():
            if len(args) == 1 and args[0].upper() in ('GEN1', 'GEN2', 'GEN3', 'GEN4', 'ALLE', 'ALL'):
                    if args[0].upper() == 'GEN1':
                        args = list(range(1, 152))
                    elif args[0].upper() == 'GEN2':
                        args = list(range(152, 252))
                    elif args[0].upper() == 'GEN3':
                        args = list(range(252, 387))
                    elif args[0].upper() == 'GEN4':
                        args = list(range(387, 493))
                    elif args[0].upper() in ['ALLE', 'ALL']:
                        args = list(range(1, 493))

            else:
                for x in args:
                    for poke_id, name in pokemon_name[lan].items():
                        if x.upper() in name.upper():
                            pokemon_ids.append(str(poke_id))
                if len(pokemon_ids) < 1:
                    bot.sendMessage(chat_id, text='*Ich habe nicht alle Pokémon gefunden! Bitte versuche es erneut.*', parse_mode='Markdown')
                    return

                args = pokemon_ids

    try:
        search = pref.get('search_ids')
        tmp = 'Du hast folgende Pokémon entfernt:\n'

        for x in args:
            if int(x) in search:
                search.remove(int(x))
                tmp += "%s %s\n" % (x, pokemon_name[lan][str(x)])
            else:
                tmp += "Du willst *%s %s* entfernen. Es existiert aber nicht in deiner Liste.\n" % (x, pokemon_name[lan][str(x)])
        pref.set('search_ids',search)

        # Stringlänge berechnen und schneiden:
        cut_position = 1
        while cut_position > 0:
            cut_position = tmp.rfind('\n', 3800, 4096)
            if cut_position > 0:
                bot.sendMessage(chat_id, text = tmp[:cut_position], parse_mode='Markdown')
                tmp = tmp[cut_position+1:]
            else:
                bot.sendMessage(chat_id, text = tmp, parse_mode='Markdown')

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=usage_message)


def cmd_IV(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/iv #minimum oder /iv #minimum #maximum" (Ohne # und nicht über 100 / unter 0!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> minIV = Eingabe, maxIV = 100.
    if len(args) == 1:
        IVmin = float(args[0])
        IVmax = float(100)
    else:
        IVmin = float(args[0])
        IVmax = float(args[1])

    # Fange Werte unter 0 und über 100 ab
    if IVmin > 100 or IVmax > 100 or IVmin < 0 or IVmax < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze minIV und maxIV
    pref.set('user_miniv', IVmin)
    pref.set('user_maxiv', IVmax)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set minIV to %s and maxIV to %s' % (userName, chat_id, IVmin, IVmax))
    bot.sendMessage(chat_id, text='Setze Minimum IV auf: %s und Maximum IV auf: %s' % (IVmin, IVmax))


def cmd_CP(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/cp #minimum oder /cp #minimum #maximum" (Ohne #!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> minCP = Eingabe, maxCP = 5000.
    if len(args) == 1:
        CPmin = int(args[0])
        CPmax = int(5000)
    else:
        CPmin = int(args[0])
        CPmax = int(args[1])

    # Fange Werte unter 0 ab
    if CPmin < 0 or CPmax < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze minCP und maxCP
    pref.set('user_mincp', CPmin)
    pref.set('user_maxcp', CPmax)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set minCP to %s and maxCP to %s' % (userName, chat_id, CPmin, CPmax))
    bot.sendMessage(chat_id, text='Setze Minimum WP auf: %s und Maximum WP auf: %s' % (CPmin, CPmax))


def cmd_LVL(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/lvl #minimum oder /lvl #minimum #maximum" (Ohne #! und nicht über 40 / unter 0!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> minLVL = Eingabe, maxLVL = 40.
    if len(args) == 1:
        LVLmin = int(args[0])
        LVLmax = int(40)
    else:
        LVLmin = int(args[0])
        LVLmax = int(args[1])

    # Fange Werte unter 0 ab
    if LVLmin < 0 or LVLmax < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return
    if LVLmin > 40 or LVLmax > 40:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze minLVL und maxLVL
    pref.set('user_minlvl', LVLmin)
    pref.set('user_maxlvl', LVLmax)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set minLVL to %s and maxLVL to %s' % (userName, chat_id, LVLmin, LVLmax))
    bot.sendMessage(chat_id, text='Setze Minimum Level auf: %s und Maximum Level auf: %s' % (LVLmin, LVLmax))


def cmd_attack_filter(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/angriff #minimum oder /agriff #minimum #maximum" (Ohne # und nicht über 15 / unter 0!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> attack_min = Eingabe, attack_max = 15.
    if len(args) == 1:
        attack_min = int(args[0])
        attack_max = int(15)
    else:
        attack_min = int(args[0])
        attack_max = int(args[1])

    # Fange Werte unter 0 ab
    if attack_min < 0 or attack_max < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return
    # Und über 15
    if attack_min > 15 or attack_max > 15:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze attack_min und attack_max
    pref.set('user_attack_min', attack_min)
    pref.set('user_attack_max', attack_max)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set attack_min to %s and attack_max to %s' % (userName, chat_id, attack_min, attack_max))
    bot.sendMessage(chat_id, text='Setze Minimum Anriff auf: %s und Maximum Angriff auf: %s' % (attack_min, attack_max))


def cmd_defense_filter(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/verteidigung #minimum oder /verteidigung #minimum #maximum" (Ohne # und nicht über 15 / unter 0!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> defense_min = Eingabe, defense_max = 15.
    if len(args) == 1:
        defense_min = int(args[0])
        defense_max = int(15)
    else:
        defense_min = int(args[0])
        defense_max = int(args[1])

    # Fange Werte unter 0 ab
    if defense_min < 0 or defense_max < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return
    # Und über 15
    if defense_min > 15 or defense_max > 15:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze defense_min und defense_max
    pref.set('user_defense_min', defense_min)
    pref.set('user_defense_max', defense_max)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set defense_min to %s and defense_max to %s' % (userName, chat_id, defense_min, defense_max))
    bot.sendMessage(chat_id, text='Setze Minimum Verteidigung auf: %s und Maximum Verteidigung auf: %s' % (defense_min, defense_max))


def cmd_stamina_filter(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/ausdauer #minimum oder /ausdauer #minimum #maximum" (Ohne # und nicht über 15 / unter 0!)'

    # Fange keine Eingabe oder mehr als 2 Eingaben ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 2:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Wenn nur ein Wert eingegeben wird -> stamina_min = Eingabe, stamina_max = 15.
    if len(args) == 1:
        stamina_min = int(args[0])
        stamina_max = int(15)
    else:
        stamina_min = int(args[0])
        stamina_max = int(args[1])

    # Fange Werte unter 0 ab
    if stamina_min < 0 or stamina_max < 0:
        bot.sendMessage(chat_id, text=usage_message)
        return
    # Und über 15
    if stamina_min > 15 or stamina_max > 15:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Setze stamina_min und stamina_max
    pref.set('user_stamina_min', stamina_min)
    pref.set('user_stamina_max', stamina_max)

    # Sende Bestaetigung
    logger.info('[%s@%s] Set stamina_min to %s and stamina_max to %s' % (userName, chat_id, stamina_min, stamina_max))
    bot.sendMessage(chat_id, text='Setze Minimum Ausdauer auf: %s und Maximum Ausdauer auf: %s' % (stamina_min, stamina_max))


# Funktion: Modus = 0 -> Nur Pokemon mit IV . Modus = 1 -> Auch Pokemon ohne IV
def cmd_Mode(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/modus 0" oder "/modus 1" (Einen Wert: 0 oder 1!)'

    # Fange keine Eingabe ab
    if args != []:
        if args[0].isdigit():
            if len(args) < 1 or len(args) > 1:
                bot.sendMessage(chat_id, text=usage_message)
                return
            else:
                if len(args[0]) > 1:
                    bot.sendMessage(chat_id, text=usage_message)
                    return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    if int(args[0]) == 1 or int(args[0]) == 0:
        # Setze Modus
        pref.set('user_mode', int(args[0]))

        # Sende Bestaetigung
        logger.info('[%s@%s] Set mode to %s' % (userName, chat_id, args[0]))

        if int(args[0]) == 0:
            bot.sendMessage(chat_id, text='Modus ist 0: Nur Pokémon mit IV werden gesendet!')
        else:
            bot.sendMessage(chat_id, text='Modus ist 1: Auch Pokémon ohne IV werden gesendet!')
    else:
        bot.sendMessage(chat_id, text=usage_message)


def cmd_SwitchVenue(bot, update):

    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)

    if pref['user_send_venue'] == 0:
        pref.set('user_send_venue', 1)
        bot.sendMessage(chat_id, text='Pokémon werden nun in einer Nachricht gesendet')
    else:
        pref.set('user_send_venue', 0)
        bot.sendMessage(chat_id, text='Pokémon werden nun in zwei Nachrichten gesendet')

    logger.info('[%s@%s] Switched message style' % (userName, chat_id))


def cmd_status(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    # Lade User Einstellungen
    pref = prefs.get(chat_id)

    miniv = int(pref.get('user_miniv'))
    maxiv = int(pref.get('user_maxiv'))
    mincp = int(pref.get('user_mincp'))
    maxcp = int(pref.get('user_maxcp'))
    minlvl = int(pref.get('user_minlvl'))
    maxlvl = int(pref.get('user_maxlvl'))
    minatk = int(pref.get('user_attack_min'))
    maxatk = int(pref.get('user_attack_max'))
    mindef = int(pref.get('user_defense_min'))
    maxdef = int(pref.get('user_defense_max'))
    minsta = int(pref.get('user_stamina_min'))
    maxsta = int(pref.get('user_stamina_max'))
    mode = int(pref.get('user_mode'))
    loc = pref.get('location')
    lat = loc[0]
    lon = loc[1]
    radius = "Kein Radius"

    if lat is not None and loc[2] is not None:
        radius = float(loc[2])*1000

    prefmessage = "*Einstellungen:*\n" + \
    "Minimum IV: *%s*, Maximum IV: *%s*\nMinimum Angriff: *%s*, " % (miniv, maxiv, minatk) + \
    "Maximum Angriff: *%s*\n Minimum Verteidigung: *%s*, Maximum Verteidigung: *%s*\n" % (maxatk, mindef, maxdef) + \
    "Minimum Ausdauer: *%s*, Maximum Ausdauer: *%s*\nMinimum WP: *%s*, Maximum WP: *%s*\n" % (minsta, maxsta, mincp, maxcp) + \
    "Minimum Level: *%s*, Maximum Level: *%s*\nModus: *%s*\n" % (minlvl, maxlvl, mode)
    "Standort: %s,%s\nRadius: %s m" % (lat, lon, radius)

    commandmessage = "*Die Einstellungen entsprechen folgenden Befehlen:*\n\n" + \
    "/iv %s %s\n/angriff %s %s\n/verteidigung %s %s\n/ausdauer %s %s\n" % (miniv, maxiv, minatk, maxatk, mindef, maxdef, minsta, maxsta) + \
    "/wp %s %s\n/lvl %s %s\n/modus %s\n" % (mincp, maxcp, minlvl, maxlvl, mode) + \
    "/standort %s,%s\n/radius %s" % (lat, lon, radius)

    try:
        lan = pref.get('language')
        tmpcmdPoke = '\n/pokemon '

        for x in pref.get('search_ids'):
            tmpcmdPoke += "%i " % x

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text='Liste leider Fehlerhaft. Bitte /ende eingeben und erneut beginnen')

    commandmessage += tmpcmdPoke

    cmd_list(bot, update)
    bot.sendMessage(chat_id, text='%s' % (prefmessage), parse_mode='Markdown')
    bot.sendMessage(chat_id, text='%s' % (commandmessage), parse_mode='Markdown')


def cmd_clear(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)

    #Removes the job if the user changed their mind
    logger.info('[%s@%s] Clear list.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...')
        return

    # Remove from jobs
    job = jobs[chat_id]
    job.schedule_removal()
    #job.stop()
    del jobs[chat_id]

    # Remove from sent
    del sent[chat_id]
    # Remove from locks
    del locks[chat_id]

    pref.reset_user()

    bot.sendMessage(chat_id, text='Benachrichtigungen erfolgreich entfernt!')


def cmd_list(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] List.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...')
        return

    try:
        lan = pref.get('language')
        tmp = 'Liste der Benachrichtigungen:\n'

        for x in pref.get('search_ids'):
            tmp += "%i %s\n" % (x, pokemon_name[lan][str(x)])

        # Stringlänge berechnen und schneiden:
        cut_position = 1
        while cut_position > 0:
            cut_position = tmp.rfind('\n', 3800, 4096)
            if cut_position > 0:
                bot.sendMessage(chat_id, text = tmp[:cut_position], parse_mode='Markdown')
                tmp = tmp[cut_position+1:]
            else:
                bot.sendMessage(chat_id, text = tmp, parse_mode='Markdown')

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage('Liste leider Fehlerhaft. Bitte /ende eingeben und erneut beginnen')

def cmd_save(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    usage_message = 'Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...'
    logger.info('[%s@%s] Save.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=usage_message)
        return
    pref.set_preferences()
    bot.sendMessage(chat_id, text='Speichern erfolgreich!')

def cmd_saveSilent(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    usage_message = 'Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...'
    logger.info('[%s@%s] Save.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=usage_message)
        return
    pref.set_preferences()

def cmd_load(bot, update, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    usage_message = 'Du hast keine gespeicherten Einstellungen!'
    logger.info('[%s@%s] Attempting to load.' % (userName, chat_id))

    r = pref.load()
    if r is None:
        bot.sendMessage(chat_id, text=usage_message)
        return

    if not r:
        bot.sendMessage(chat_id, text='Bereits aktuell')
        return
    else:
        bot.sendMessage(chat_id, text='Laden erfolgreich!')

    # We might be the first user and above failed....
    if len(pref.get('search_ids')) > 0:
        addJob(bot, update, job_queue)
        miniv = pref.get('user_miniv')
        maxiv = pref.get('user_maxiv')
        mincp = pref.get('user_mincp')
        maxcp = pref.get('user_maxcp')
        minlvl = pref.get('user_minlvl')
        maxlvl = pref.get('user_maxlvl')
        mode = pref.get('user_mode')
        send_venue = pref.get('user_send_venue')
        loc = pref.get('location')
        lat = loc[0]
        lon = loc[1]

        # Korrigiere Einstellungen, wenn jemand "null" oder "strings" hat
        if lat is None or lon is None:
            bot.sendMessage(chat_id, text='*Du hast keinen Standort gewählt! Du wirst nun nach Kiel gesetzt!*', parse_mode='Markdown')

        # Send Settings to user and save to json file
        checkAndSetUserDefaults(pref)
        cmd_saveSilent(bot, update)
        cmd_status(bot, update)

    else:
        if chat_id not in jobs:
            job = jobs[chat_id]
            job.schedule_removal()
            #job.stop()
            del jobs[chat_id]


def cmd_load_silent(bot, chat_id, job_queue):
    userName = ''

    pref = prefs.get(chat_id)

    #logger.info('[%s@%s] Automatic load.' % (userName, chat_id))
    r = pref.load()
    if r is None:
        return

    if not r:
        return

    # We might be the first user and above failed....
    if len(pref.get('search_ids')) > 0:
        addJob_silent(bot, chat_id, job_queue)
        miniv = pref.get('user_miniv')
        maxiv = pref.get('user_maxiv')
        mincp = pref.get('user_mincp')
        maxcp = pref.get('user_maxcp')
        minlvl = pref.get('user_minlvl')
        maxlvl = pref.get('user_maxlvl')
        mode = pref.get('user_mode')
        send_venue = pref.get('user_send_venue')
        loc = pref.get('location')
        lat = loc[0]
        lon = loc[1]

        checkAndSetUserDefaults(pref)

    else:
        if chat_id not in jobs:
            job = jobs[chat_id]
            job.schedule_removal()
            #job.stop()
            del jobs[chat_id]


def cmd_location(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    if update.message.chat.type != 'private':
        return

    pref = prefs.get(chat_id)
    usage_message = 'Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...'

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=usage_message)
        return

    user_location = update.message.location
    location_radius = pref['location'][2]

    # We set the location from the users sent location.
    pref.set('location', [user_location.latitude, user_location.longitude, location_radius])

    logger.info('[%s@%s] Setting scan location to Lat %s, Lon %s, R %s' % (userName, chat_id,
        pref['location'][0], pref['location'][1], pref['location'][2]))

    # Send confirmation nessage
    location_url = ('https://www.freemaptools.com/radius-around-point.htm?clat=%f&clng=%f&r=%f&lc=FFFFFF&lw=1&fc=00FF00&mt=r&fs=true&nomoreradius=true'
        % (pref['location'][0], pref['location'][1], pref['location'][2]))
    bot.sendMessage(chat_id, text="Setze Standort auf: %f / %f mit Radius %.2f m" %
        (pref['location'][0], pref['location'][1], 1000*pref['location'][2]))
    bot.sendMessage(chat_id, text="Deinen Radius kannst du hier sehen:\n\n" + location_url, disable_web_page_preview="True")


def cmd_location_str(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    location_radius = pref['location'][2]
    usage_message = 'Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...'

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=usage_message)
        return

    if len(args) <= 0:
        bot.sendMessage(chat_id, text='You have not supplied a location')
        return

    try:
        user_location = geolocator.geocode(' '.join(args), timeout=10)
    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text='Standort nicht gefunden oder Openstreetmap ist down! Bitte versuche es erneut damit der Bot startet!')
        return

    # We set the location from the users sent location.
    pref.set('location', [user_location.latitude, user_location.longitude, location_radius])

    logger.info('[%s@%s] Setting scan location to Lat %s, Lon %s, R %s' % (userName, chat_id,
        pref['location'][0], pref.preferences['location'][1], pref.preferences['location'][2]))

    # Send confirmation nessage
    location_url = ('https://www.freemaptools.com/radius-around-point.htm?clat=%f&clng=%f&r=%f&lc=FFFFFF&lw=1&fc=00FF00&mt=r&fs=true&nomoreradius=true'
        % (pref['location'][0], pref['location'][1], pref['location'][2]))
    bot.sendMessage(chat_id, text="Setze Standort auf: %f / %f mit Radius %.2f m" %
        (pref['location'][0], pref['location'][1], 1000*pref['location'][2]))
    bot.sendMessage(chat_id, text="Deinen Radius kannst du hier sehen:\n\n" + location_url, disable_web_page_preview="True")

def cmd_radius(bot, update, args):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    usage_message = 'Du hast keinen aktiven Scanner! Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...'

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=usage_message)
        return

    # Check if user has set a location
    user_location = pref.get('location')

    if user_location[0] is None:
        bot.sendMessage(chat_id, text="Du hast keinen Standort eingestellt. Bitte mache dies zuerst!")
        return

    # Get the users location
    logger.info('[%s@%s] Retrieved Location as Lat %s, Lon %s, R %s (Km)' % (
    userName, chat_id, user_location[0], user_location[1], user_location[2]))

    if args != []:
        if args[0].isdigit():
            if len(args) < 1:
                bot.sendMessage(chat_id, text="Aktueller Standort ist: %f / %f mit Radius %.2f m"
                    % (user_location[0], user_location[1], user_location[2]))
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    # Change the radius
    if float(args[0]) > 5000:
        args[0] = 5000
        bot.sendMessage(chat_id, text='Dein Radius ist größer als 5000m! Er wird auf 5000m gestellt.')
    try:
        radius = float(args[0])
        pref.set('location', [user_location[0], user_location[1], radius/1000])

        logger.info('[%s@%s] Set Location as Lat %s, Lon %s, R %s (Km)' % (userName, chat_id, pref['location'][0],
            pref['location'][1], pref['location'][2]))

        # Send confirmation
        location_url = ('https://www.freemaptools.com/radius-around-point.htm?clat=%f&clng=%f&r=%f&lc=FFFFFF&lw=1&fc=00FF00&mt=r&fs=true&nomoreradius=true' % (pref['location'][0], pref['location'][1], pref['location'][2]))
        bot.sendMessage(chat_id, text="Setze Standort auf: %f / %f mit Radius %.2f m" % (pref['location'][0],
            pref['location'][1], 1000*pref['location'][2]))
        bot.sendMessage(chat_id, text="Deinen Radius kannst du hier sehen:\n\n" + location_url, disable_web_page_preview="True")

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text='Radius nicht zulässig! Bitte Zahl eingeben!')
        return


def cmd_unknown(bot, update):
    chat_id = update.message.chat_id
    if update.message.text and update.message.chat.type == 'private':
        bot.send_message(chat_id, text="Falsche Eingabe. Ich habe dich nicht verstanden!\nSchaue am besten in der Hilfe nach: /help")


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def checkAndSetUserDefaults(pref):
    if pref.get('user_miniv') is None:
        pref.set('user_miniv', 0)
    if pref.get('user_maxiv') is None:
        pref.set('user_maxiv', 100)
    if pref.get('user_mincp') is None:
        pref.set('user_mincp', 0)
    if pref.get('user_maxcp') is None:
        pref.set('user_maxcp', 5000)
    if pref.get('user_minlvl') is None:
        pref.set('user_minlvl', 1)
    if pref.get('user_maxlvl') is None:
        pref.set('user_maxlvl', 40)
    if pref.get('user_mode') is None:
        pref.set('user_mode', 1)

    loc = pref.get('location')
    if loc[0] is None or loc[1] is None:
        pref.set('location', [54.321362, 10.134511, 0.1])
    if loc[2] is None:
        pref.set('location', [loc[0], loc[1], 0.1])
    if loc[2] is not None and float(loc[2]) > 5:
        pref.set('location', [loc[0], loc[1], 5])


def getMysqlData(bot, job):
    logger.info('Getting MySQLdata...')
    thismodule.pokemon_db_data = dataSource.getPokemonData()
    return thismodule.pokemon_db_data


def addJobMysql(bot, job_queue):
    chat_id = ''
    logger.info('MySQL job added.')
    try:
        if chat_id not in jobs:
            #job = Job(getMysqlData, 30, repeat=True, context=(chat_id, "Other"))
            job = job_queue.run_repeating(getMysqlData, interval=30, first=5, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            #job_queue.put(job)

    except Exception as e:
        logger.error('MySQL job failed.')


def alarm(bot, job):
    chat_id = job.context[0]
    #logger.info('[%s] Checking alarm.' % (chat_id))

    checkAndSend(bot, chat_id, prefs.get(chat_id).get('search_ids'), thismodule.pokemon_db_data)


def addJob(bot, update, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username
    #logger.info('[%s@%s] Adding job.' % (userName, chat_id))

    try:
        if chat_id not in jobs:
            #job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            job = job_queue.run_repeating(alarm, interval=30, first=0, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            #job_queue.put(job)

            # User dependant
            if chat_id not in sent:
                sent[chat_id] = dict()
            if chat_id not in locks:
                locks[chat_id] = threading.Lock()
            text = "Scanner gestartet."
            bot.sendMessage(chat_id, text)
    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))


def addJob_silent(bot, chat_id, job_queue):
    userName = ''
    #logger.info('[%s@%s] Adding job.' % (userName, chat_id))

    try:
        if chat_id not in jobs:
            #job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            job = job_queue.run_repeating(alarm, interval=30, first=0, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            #job_queue.put(job)

            # User dependant
            if chat_id not in sent:
                sent[chat_id] = dict()
            if chat_id not in locks:
                locks[chat_id] = threading.Lock()

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))


def checkAndSend(bot, chat_id, pokemons, pokemon_db_data):
    pref = prefs.get(chat_id)
    lock = locks[chat_id]

    message_counter = 0
    #blacklisted_pokemon_0_100 = [10,11,13,14,16,17,19,21,29,32,41,43,46,48,54,
        #60,69,72,90,96,98,116,118,161,163,165,167,170,177,183,187,190,194,209,
        #216,220,261,263,265,273,276,293,300,316]
    #blacklisted_pokemon_0_90 = [129,133,198,296,309,315,320,333,351,363]
    blacklisted_pokemon_0_100 = []
    blacklisted_pokemon_0_90 = []

    #weather_icons = ['', '\xE2\x98\x80', '\xE2\x98\x94', '\xE2\x9B\x85', '\xE2\x98\x81', '\xF0\x9F\x92\xA8', '\xE2\x9B\x84', '\xF0\x9F\x8C\x81']
    weather_icons = ['', '☀️', '☔️', '⛅', '☁️', '💨', '⛄️', '🌁']
    #logger.info('[%s] Checking pokemon and sending notifications.' % (chat_id))
    pokemon_forms = {30:"Sonne", 31:"Regen", 32:"Schnee", 46:"Alola", 48:"Alola", 50:"Alola", 52:"Alola", 54:"Alola", 56:"Alola", 58:"Alola", 60:"Alola", 62:"Alola", 64:"Alola", 66:"Alola", 68:"Alola", 70:"Alola", 72:"Alola", 74:"Alola", 76:"Alola", 78:"Alola", 80:"Alola", 81:"Normal", 82:"Frost", 83:"Wirbel", 84:"Schneid", 85:"Wasch", 86:"Hitze", 87:"Pflanze", 88:"Sand", 89:"Lumpen", 92:"Zenit", 93:"Land", 94:"Wolke", 95:"Sonne", 96:"West", 97:"Ost", 98:"West", 99:"Ost", 118:"Pflanze", 119:"Sand", 120:"Lumpen"}

    if len(pokemons) == 0:
        return

    try:
        checkAndSetUserDefaults(pref)
        moveNames = move_name["de"]

        lan = pref['language']
        mySent = sent[chat_id]
        location_data = pref['location']
        user_iv_min = int(pref['user_miniv'])
        user_iv_max = int(pref['user_maxiv'])
        user_cp_min = int(pref['user_mincp'])
        user_cp_max = int(pref['user_maxcp'])
        user_lvl_min = int(pref['user_minlvl'])
        user_lvl_max = int(pref['user_maxlvl'])
        user_attack_min = int(pref['user_attack_min'])
        user_attack_max = int(pref['user_attack_max'])
        user_defense_min = int(pref['user_defense_min'])
        user_defense_max = int(pref['user_defense_max'])
        user_stamina_min = int(pref['user_stamina_min'])
        user_stamina_max = int(pref['user_stamina_max'])
        user_mode = int(pref['user_mode'])
        user_send_venue = int(pref['user_send_venue'])

        lock.acquire()

        for pokemon in pokemon_db_data:
            # Get pokemon_id and check if it's in users list
            pok_id = pokemon.getPokemonID()
            if int(pok_id) not in pokemons:
                continue
            # Get encounter_id and check if already sent
            encounter_id = pokemon.getEncounterID()
            if encounter_id in mySent:
                continue
            # Check if Pokemon inside radius
            if not pokemon.filterbylocation(location_data):
                continue

            # Get general Pokémon infos
            iv = pokemon.getIVs()
            iv_attack = pokemon.getIVattack()
            iv_defense = pokemon.getIVdefense()
            iv_stamina = pokemon.getIVstamina()
            cp = pokemon.getCP()
            cpm = pokemon.getCPM()
            gender = pokemon.getGender()
            weather = pokemon.getWeather()
            form = pokemon.getForm()
            move1 = pokemon.getMove1()
            move2 = pokemon.getMove2()
            latitude = pokemon.getLatitude()
            longitude = pokemon.getLongitude()
            disappear_time = pokemon.getDisappearTime()
            delta = disappear_time - datetime.utcnow()
            deltaStr = '%02dm:%02ds' % (int(delta.seconds / 60), int(delta.seconds % 60))
            disappear_time_str = disappear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S")

            if weather is None:
                weather = 0

            if gender == 1:
                gender = '\u2642'
            elif gender == 2:
                gender = '\u2640'
            elif gender == 3:
                gender = '\u26B2'
            else:
                gender = ''

            pok_form = ''
            if int(form) != 0:
                if int(form) in pokemon_forms:
                    pok_form = ' (' + pokemon_forms[int(form)] + ')'

            # If IV is known
            if iv is not None:
                # First: Filter blacklisted Pokémon
                if int(pok_id) in blacklisted_pokemon_0_100:
                    if float(iv) < 100:
                        if float(iv) != 0:
                            continue
                if int(pok_id) in blacklisted_pokemon_0_90:
                    if float(iv) < 90:
                        if float(iv) != 0:
                            continue

                # Second: Calculate Pokémon level
                pkmnlvl = getPokemonLevel(cpm)

                # Third: Filter IV/CP/LVL with user_settings
                if float(iv) < user_iv_min or float(iv) > user_iv_max:
                    continue
                if int(cp) < user_cp_min or int(cp) > user_cp_max:
                    continue
                if int(pkmnlvl) < user_lvl_min or int(pkmnlvl) > user_lvl_max:
                    continue
                if int(iv_attack) < user_attack_min or int(iv_attack) > user_attack_max:
                    continue
                if int(iv_defense) < user_defense_min or int(iv_defense) > user_defense_max:
                    continue
                if int(iv_stamina) < user_stamina_min or int(iv_stamina) > user_stamina_max:
                    continue


                # Fourth: Build message
                pkmname =  pokemon_name[lan][pok_id]
                if user_send_venue == 1:
                    pkmname = "%s%s%s: %s WP %s" % (pokemon_name[lan][pok_id], pok_form, gender, cp, weather_icons[int(weather)])
                    address = "%s - %s%%(%s/%s/%s)/L%s" % (disappear_time_str, iv, iv_attack, iv_defense, iv_stamina, pkmnlvl)
                else:
                    pkmname = "%s%s%s %s" % (pokemon_name[lan][pok_id], pok_form, gender, weather_icons[int(weather)])
                    address = "%s (%s)." % (disappear_time_str, deltaStr)
                    title = "*IV*:%s (%s/%s/%s) - *WP*:%s - *Level*:%s\n" % (iv, iv_attack, iv_defense, iv_stamina, cp, pkmnlvl)
                    move1Name = moveNames[move1]
                    move2Name = moveNames[move2]
                    title += "*Moves*: %s/%s" % (move1Name, move2Name)


            # If IV is unknown
            else:
                if user_mode == 0:
                    continue
                if int(pok_id) in blacklisted_pokemon_0_100:
                    continue
                if int(pok_id) in blacklisted_pokemon_0_90:
                    continue

                if user_mode == 1:
                    if user_send_venue == 1:
                        pkmname =  '%s%s%s %s' % (pokemon_name[lan][pok_id], pok_form, gender, weather_icons[int(weather)])
                        address = "%s (%s). Leider keine IV/WP." % (disappear_time_str, deltaStr)
                        title = ""
                    else:
                        pkmname =  '%s%s%s %s' % (pokemon_name[lan][pok_id], pok_form, gender, weather_icons[int(weather)])
                        address = "%s (%s)." % (disappear_time_str, deltaStr)
                        title = "Leider keine IV/WP"

            # Add encounter_id to mySent after filter
            mySent[encounter_id] = disappear_time
            notDisappeared = delta.seconds > 0

            if message_counter > 10:
                bot.sendMessage(chat_id, text = 'Zu viele Pokemon eingestellt! '
                    'Erhöhe die Minimum IV, verwende /modus 1 oder Entferne Pokemon.')
                logger.info('Too many sent')
                break

            if notDisappeared and message_counter <= 10:
                try:
                    if user_send_venue == 0:
                        bot.sendLocation(chat_id, latitude, longitude)
                        bot.sendMessage(chat_id, text = '*%s* Bis %s \n%s'
                            % (pkmname, address, title), parse_mode='Markdown')
                    else:
                        bot.sendVenue(chat_id, latitude, longitude, pkmname, address)

                    message_counter += 1

                except Exception as e:
                    logger.error('[%s] %s' % (chat_id, repr(e)))

    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
    lock.release()

    # Clean already disappeared pokemon
    current_time = datetime.utcnow() - dt.timedelta(minutes=10)
    try:

        lock.acquire()
        toDel = []
        for encounter_id in mySent:
            time = mySent[encounter_id]
            if time < current_time:
                toDel.append(encounter_id)
        for encounter_id in toDel:
            del mySent[encounter_id]
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
    lock.release()
    #logger.info('Done.')

def read_config():
    config_path = os.path.join(
        os.path.dirname(sys.argv[0]), "config-bot.json")
    logger.info('Reading config: <%s>' % config_path)
    global config

    try:
        with open(config_path, "r", encoding='utf-8') as f:
            config = json.loads(f.read())
    except Exception as e:
        logger.error('%s' % (repr(e)))
        config = {}
    report_config()

def report_config():

    logger.info('TELEGRAM_TOKEN: <%s>' % (config.get('TELEGRAM_TOKEN', None)))
    logger.info('DB_CONNECT: <%s>' % (config.get('DB_CONNECT', None)))

def read_pokemon_names(loc):
    logger.info('Reading pokemon names. <%s>' % loc)
    config_path = "locales/pokemon." + loc + ".json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            pokemon_name[loc] = json.loads(f.read())
    except Exception as e:
        logger.error('%s' % (repr(e)))
        # Pass to ignore if some files missing.
        pass

def read_move_names(loc):
    logger.info('Reading move names. <%s>' % loc)
    config_path = "locales/moves." + loc + ".json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            move_name[loc] = json.loads(f.read())
    except Exception as e:
        logger.error('%s' % (repr(e)))
        # Pass to ignore if some files missing.
        pass


def getPokemonLevel(cpMultiplier):
    if (cpMultiplier < 0.734):
        pokemonLevel = (58.35178527 * cpMultiplier * cpMultiplier - 2.838007664 * cpMultiplier + 0.8539209906)
    else:
        pokemonLevel = 171.0112688 * cpMultiplier - 95.20425243

    pokemonLevel = (round(pokemonLevel) * 2) / 2

    return int(pokemonLevel)


def ReadIncomingCommand(bot, update, args, job_queue):
    Authenticated = 0

    ChatId = update.message.chat_id
    IncomingCommand = update.message.text.upper().split()[0]
    ChatType = update.message.chat.type
    UserID = update.effective_user.id

    if ChatType == 'private':
        Authenticated = 1
    else:
        GroupAdmins = bot.get_chat_administrators(chat_id = ChatId)
        for Admin in GroupAdmins:
            if Admin.user.id == UserID:
                Authenticated = 1
                break

    if Authenticated == 0:
        return

    # Commands
    # Without args:
    if IncomingCommand in ['/START']:
        cmd_start(bot, update)
    elif IncomingCommand in ['/STATUS']:
        cmd_status(bot, update)
    elif IncomingCommand in ['/NACHRICHT', '/MESSAGE']:
        cmd_SwitchVenue(bot, update)
    elif IncomingCommand in ['/HILFE', '/HELP']:
        cmd_help(bot, update)
    elif IncomingCommand in ['/LISTE', '/LIST']:
        cmd_list(bot, update)
    elif IncomingCommand in ['/SPEICHERN', '/SAVE']:
        cmd_save(bot, update)
    elif IncomingCommand in ['/ENDE', '/CLEAR']:
        cmd_clear(bot, update)

    # With args:
    elif IncomingCommand in ['/MODUS', '/MODE']:
        cmd_Mode(bot, update, args)
    elif IncomingCommand in ['/RADIUS']:
        cmd_radius(bot, update, args)
    elif IncomingCommand in ['/IV']:
        cmd_IV(bot, update, args)
    elif IncomingCommand in ['/WP', '/CP']:
        cmd_CP(bot, update, args)
    elif IncomingCommand in ['/LEVEL', '/LVL']:
         cmd_LVL(bot, update, args)
    elif IncomingCommand in ['/ANGRIFF', '/ATTACK', '/ATK']:
         cmd_attack_filter(bot, update, args)
    elif IncomingCommand in ['/VERTEIDIGUNG', '/DEFENSE', '/DEF']:
         cmd_defense_filter(bot, update, args)
    elif IncomingCommand in ['/AUSDAUER', '/STAMINA', '/STA']:
         cmd_stamina_filter(bot, update, args)

    # With job_queue
    elif IncomingCommand in ['/LADEN', '/LOAD']:
        cmd_load(bot, update, job_queue)
    elif IncomingCommand in ['/ADD', '/POKEMON']:
        cmd_add(bot, update, args, job_queue)
    elif IncomingCommand in ['/ENTFERNE', '/REM']:
        cmd_remove(bot, update, args, job_queue)
    elif IncomingCommand in ['/STANDORT', '/LOCATION']:
        cmd_location_str(bot, update, args, job_queue)

    else:
        cmd_unknown(bot, update)

def main():
    logger.info('Starting...')
    read_config()

    # Read lang files
    path_to_local = "locales/"
    for file in os.listdir(path_to_local):
        if fnmatch.fnmatch(file, 'pokemon.*.json'):
            read_pokemon_names(file.split('.')[1])
        if fnmatch.fnmatch(file, 'moves.*.json'):
            read_move_names(file.split('.')[1])

    global dataSource
    dataSource = None

    dataSource = DataSources.DSPokemonGoMapIVMysql(config.get('DB_CONNECT', None))

    if not dataSource:
        raise Exception("Error in MySQL connection")


    #ask it to the bot father in telegram
    token = config.get('TELEGRAM_TOKEN', None)
    updater = Updater(token)
    b = Bot(token)
    logger.info("BotName: <%s>" % (b.name))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    AvailableCommands = ['Add','Pokemon',
        'Nachricht',
        'Start',
        'Status',
        'Modus',
        'Help','Hilfe',
        'Ende','Clear',
        'Entferne','Rem',
        'Speichern','Save',
        'Laden','Load',
        'Liste','List',
        'Radius',
        'Standort','Location',
        'Iv',
        'Wp','Cp',
        'Level','Lvl',
        'Angriff','Attack','Atk',
        'Verteidigung','Defense','Def',
        'Ausdauer','Stamina','Sta']

    dp.add_handler(CommandHandler(AvailableCommands, ReadIncomingCommand, pass_args = True, pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.location, cmd_location))
    dp.add_handler(MessageHandler((Filters.text | Filters.command), cmd_unknown))

    # log all errors
    dp.add_error_handler(error)

    # add the configuration to the preferences
    prefs.add_config(config)

    # Start the Bot
    bot = b;
    updater.start_polling()
    j = updater.job_queue
    addJobMysql(b,j)
    thismodule.pokemon_db_data = getMysqlData(b,j)

    # Check if directory exists
    if not os.path.exists("userdata/"):
        os.makedirs("userdata/")

    else:
        allids = os.listdir("userdata/")
        newids = []

        for x in allids:
            newids = x.replace(".json", "")
            chat_id = int(newids)
            j = updater.job_queue
            #logger.info('%s' % (chat_id))

            try:
                cmd_load_silent(b, chat_id, j)
            except Exception as e:
                logger.error('%s' % (chat_id))
                logger.info("FEHLER!!!!")

    logger.info('Started!')

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
