#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4
# ------------------------------
# changelog:
# 08.01.2018
# - Added job for MySQL query
# - Only ask MySQL once in 30s
# - Removed unused code
# - Rewrite of checkAndSend
# - Filter common Pokemon
# 07.01.2018
# - Add Gen3 to addbyrarity
# 06.01.2018
# - New function getPokemonLevel
# - Fix forgotten L30 stuff
# 01.01.2017
# - Use cmd_status for cmd_load message
# - Change max_level to 40
# - Remove old Functions
# - Minor text fixes
# 12.12.2017
# - Add and remove Pokemon by their names
# 04.12.2017
# - Add Attack, Defense, Stamina Filters
# ------------------------------

'''please READ FIRST the README.md'''


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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
prefs = Preferences.UserPreferences()
jobs = dict()
geolocator = Nominatim()

# User dependant - dont add
sent = dict()
locks = dict()

# User dependant - Add to clear, addJob, loadUserConfig, saveUserConfig
search_ids = dict()
location_radius = 1
# Pokemon:
pokemon_name = dict()
# Moves:
move_name = dict()
# Mysql data
thismodule = sys.modules[__name__]
# Pokemon rarity
pokemon_rarity = [[],
	["7","16","19","41","133","161","163","165","167","170","177","183","187","194","198","216","220"],
	["1","7","10","17","21","23","25","29","32","35","43","46","48","58","60","69","84","92","96","98",\
	"120","127","129","147","152","155","158","162","164","166","168","171","178","184","185","188","190",\
	"191","200","206","209","211","215","223","228"],
	["2","4","8","11","14","15","18","20","22","27","37","39","42","47","49","50","52","54","56","61","63",\
	"66","70","72","74","77","79","81","86","90","93","95","97","100","102","104","107","108","109","111",\
	"114","116","118","123","124","125","126","128","138","140","143","153","156","159","169","185","193",\
	"195","202","203","204","207","213","218","221","231","234"],
	["3","5","6","9","12","24","30","31","33","34","36","44","53","55","57","59","64","67","73","75","78",\
	"80","85","88","99","103","105","106","110","112","113","117","119","121","122","131","134","135","137",\
	"142","148","149","179","180","189","205","210","217","219","224","226","227","246","247"],
	["26","28","38","40","45","51","62","65","68","71","76","82","83","87","89","91","94","101","115","130",\
	"132","136","139","141","144","145","146","149","150","151","154","157","160","172","173","174","175",\
	"176","181","182","186","192","196","197","199","201","208","210","212","214","222","225","229","230",\
	"232","233","235","236","237","238","239","240","241","242","243","244","245","248","249","250","251"],
	["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22",\
	"23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43",\
	"44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64",\
	"65","66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85",\
	"86","87","88","89","90","91","92","93","94","95","96","97","98","99","100","101","102","103","104","105",\
	"106","107","108","109","110","111","112","113","114","115","116","117","118","119","120","121","122","123",\
	"124","125","126","127","128","129","130","131","132","133","134","135","136","137","138","139","140","141",\
	"142","143","144","145","146","147","148","149","150","151"],
	["152","153","154","155","156","157","158","159","160","161","162","163","164","165","166","167","168","169",\
	"170","171","172","173","174","175","176","177","178","179","180","181","182","183","184","185","186","187",\
	"188","189","190","191","192","193","194","195","196","197","198","199","200","201","202","203","204","205",\
	"206","207","208","209","210","211","212","213","214","215","216","217","218","219","220","221","222","223",\
	"224","225","226","227","228","229","230","231","232","233","234","235","236","237","238","239","240","241",\
	"242","243","244","245","246","247","248","249","250","251"],
    ["252","253","254","255","256","257","258","259","260","261","262","263","264","265","266","267","268",\
    "269","270","271","272","273","274","275","276","277","278","279","280","281","282","283","284","285","286",\
    "287","288","289","290","291","292","293","294","295","296","297","298","299","300","301","302","303","304",\
    "305","306","307","308","309","310","311","312","313","314","315","316","317","318","319","320","321","322",\
    "323","324","325","326","327","328","329","330","331","332","333","334","335","336","337","338","339","340",\
    "341","342","343","344","345","346","347","348","349","350","351","352","353","354","355","356","357","358",\
    "359","360","361","362","363","364","365","366","367","368","369","370","371","372","373","374","375","376",\
    "377","378","379","380","381","382","383","384","385","386"],
	["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23",\
    "24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44",\
    "45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64","65",\
    "66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86",\
    "87","88","89","90","91","92","93","94","95","96","97","98","99","100","101","102","103","104","105","106",\
    "107","108","109","110","111","112","113","114","115","116","117","118","119","120","121","122","123","124",\
    "125","126","127","128","129","130","131","132","133","134","135","136","137","138","139","140","141","142",\
    "143","144","145","146","147","148","149","150","151","152","153","154","155","156","157","158","159","160",\
    "161","162","163","164","165","166","167","168","169","170","171","172","173","174","175","176","177","178",\
    "179","180","181","182","183","184","185","186","187","188","189","190","191","192","193","194","195","196",\
    "197","198","199","200","201","202","203","204","205","206","207","208","209","210","211","212","213","214",\
    "215","216","217","218","219","220","221","222","223","224","225","226","227","228","229","230","231","232",\
    "233","234","235","236","237","238","239","240","241","242","243","244","245","246","247","248","249","250",\
    "251","252","253","254","255","256","257","258","259","260","261","262","263","264","265","266","267","268",\
    "269","270","271","272","273","274","275","276","277","278","279","280","281","282","283","284","285","286",\
    "287","288","289","290","291","292","293","294","295","296","297","298","299","300","301","302","303","304",\
    "305","306","307","308","309","310","311","312","313","314","315","316","317","318","319","320","321","322",\
    "323","324","325","326","327","328","329","330","331","332","333","334","335","336","337","338","339","340",\
    "341","342","343","344","345","346","347","348","349","350","351","352","353","354","355","356","357","358",\
    "359","360","361","362","363","364","365","366","367","368","369","370","371","372","373","374","375","376",\
    "377","378","379","380","381","382","383","384","385","386"],
];

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def cmd_help(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    logger.info('[%s@%s] Sending help text.' % (userName, chat_id))
    text = "*Folgende Befehle kennt der Bot:* \n\n" + \
    "/hilfe Um Hilfe zu bekommen und dieses Menü anzuzeigen. \n\n" + \
    "*Pokémon:*\n\n" + \
    "/pokemon 1 \n" + \
    "Nummer des Pokémon eingeben um über dieses Benachrichtigungen zu erhalten. \n" + \
    "/pokemon 1 2 3 ... \n" + \
    "Mehrfache Nummern der Pokémon können so eingegeben werden. \n" + \
    "/pokemon gen1 \nFügt alle Pokémon der 1. Generation hinzu. Mögliche Optionen " + \
    "sind: gen1, gen2, gen3, alle\n\n" + \
    "/seltenheit 1 \n" + \
    "Fügt eine Gruppe von Pokémon hinzu. Dabei steht die 1 für gewöhnliche Pokémon " + \
    "und die 5 für ultra-seltene Pokémon.\n\n" + \
    "/iv 50 \n" + \
    "Setze die Minimum IV z.B. auf 50 für die Pokémon, über die du benachrichtigt werden willst. \n" + \
    "/iv 0 100 \n" + \
    "Setze die Minimum IV z.B. auf 0 und Maximum IV z.B. auf 100 für die Pokémon, über die du benachrichtigt werden willst. \n\n" + \
    "/wp 1500 \n" + \
    "Setze die Minimum WP z.B. auf 1500 für die Pokémon, über die du benachrichtigt werden willst. \n" + \
    "/wp 0 5000 \n" + \
    "Setze die Minimum WP z.B. auf 0 und Maximum WP z.B. auf 5000 für die Pokémon, über die du benachrichtigt werden willst. \n\n" + \
    "/lvl 20 \n" + \
    "Setze die Minimum Level z.B. auf 20 für die Pokémon, über die du benachrichtigt werden willst. \n" + \
    "/lvl 0 40 \n" + \
    "Setze die Minimum Level z.B. auf 0 und Maximum Level z.B. auf 40 für die Pokémon, über die du benachrichtigt werden willst. \n\n" + \
    "/modus \n" + \
    "Stellt den Modus um:\n/modus 0 = Du erhälst nur Benachrichtigungen für Pokemon mit IV und WP. \n" + \
    "/modus 1 = Du erhälst auch Benachrichtigungen für Pokémon ohne IV und WP (zum Beispiel, wenn die IV/WP " +\
    "nicht ermittelt werden konnten. Somit bekommst du z.B. auch ein Relaxo ohne IV/WP angezeigt.) \n\n"
    text2 = "/entferne 1 \n" + \
    "Nummer des Pokémon löschen, wenn du über dieses nicht mehr benachrichtigt werden willst. \n" + \
    "/entferne 1 2 3 ... \n" + \
    "Mehrfache Nummern der Pokémon löschen, wenn du über diese nicht mehr benachrichtigt werden willst. \n\n" + \
    "*Standort:*\n\n" + \
    "Sende deinen Standort über Telegram. \n" + \
    "Dies fügt einen Umkreis um deinen Standort hinzu und du erhälst Benachrichtigungen für deine Umgebung. " + \
    "Hinweis: Das senden des Standorts funktioniert nicht in Gruppen. \n" +\
    "/standort xx.xx, yy.yy \n" + \
    "Sende Koordinaten als Text in der Angezeigten Form um in dem Umkreis benachrichtigt zu werden. Es kann auch" + \
    "eine Adresse eingegeben werden zum Beispiel: /standort Holstenstraße 1, 24103 Kiel oder auch /standort Kiel, DE. \n" + \
    "/radius 1000 \n" + \
    "Stellt deinen Such-Radius in m (Metern) um deinen Standort herum ein. Hierbei ist 5000m das Maximum. \n" + \
    "*Sonstiges:*\n\n" + \
    "/liste \n" + \
    "Alle Pokemon auflisten, über die du aktuell benachrichtigt wirst. \n" + \
    "/speichern \n" + \
    "Speichert deine Einstellungen. *Dies ist wichtig*, damit du nach einem Neustart des Bots deine Einstellungen behälst! \n" + \
    "/laden \n" + \
    "Lade deine gespeicherten Einstellungen. \n" + \
    "/status \n" + \
    "Liste deine aktuellen Einstellungen auf. \n" + \
    "/nachricht \n" + \
    "Stellt die Art der Nachrichten um zwischen: Nur Standort oder Standort und Pokémon-Details.\n" + \
    "/ende \n" + \
    "Damit kannst du alle deine Einstellungen löschen und den Bot ausschalten. Du kannst ihn danach mit /laden " + \
    "wieder einschalten und deine Einstellungen werden geladen. \n"
    bot.sendMessage(chat_id, text, parse_mode='Markdown')
    bot.sendMessage(chat_id, text2, parse_mode='Markdown')

def cmd_start(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.first_name

    logger.info('[%s@%s] Starting.' % (userName, chat_id))
    message = "Hallo *%s*.\nDein Bot ist nun im Einstellungsmodus. *Weitere Schritte:* \n\nFalls du den Bot " + \
    "schon genutzt hast wähle /laden um deine *gespeicherten Einstellungen* zu laden.\n\nBenutzt du diesen Bot " + \
    "zum *ersten Mal*, dann füge bitte deine gewünschten *Pokémon* hinzu z.B. mit: \n*/pokemon 1* für Bisasam " + \
    "oder */pokemon 1 2 3 ...* für mehrere Pokemon über die du informiert werden willst.\n\n*Sende* anschließend " + \
    "deinen *Standort* einfach über Telegram oder nutze */standort xx.xx, yy.yy*, */standort Kiel, DE* oder " + \
    "*/standort Holstenstraße 1, 24103 Kiel* um deine Koordinaten zu senden und den Bot somit zu starten. " + \
    "(In Gruppen funktioniert das Senden des Standortes leider nicht.)\n\nEs gibt noch weitere Einstellungen " + \
    "zu *IV*, *WP* und *Level*.\nBitte denk daran deine Einstellungen immer zu *speichern* mit /speichern.\n\n" + \
    "*Fahre fort mit* /hilfe *um die möglichen Befehle aufzulisten.*\n"
    bot.sendMessage(chat_id, message % (userName), parse_mode='Markdown')

    # Setze default Werte und den Standort auf Kiel
    pref = prefs.get(chat_id)
    checkAndSetUserDefaults(pref)

def cmd_add(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    lan = pref.get('language')
    names = list()
    usage_message = 'Nutzung:\n/pokemon #Nummer oder /pokemon #Nummer1 #Nummer2\n' + \
    '/pokemon #Name oder /pokemon #Name1 #Name2 ... (Ohne #)'

    if args != []:
        if args[0].isdigit():
            if len(args) <= 0:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            if len(args) == 1:
                if args[0].upper() == 'GEN1':
                    cmd_addByRarity(bot, update, str(6), job_queue)
                    return
                if args[0].upper() == 'GEN2':
                    cmd_addByRarity(bot, update, str(7), job_queue)
                    return
                if args[0].upper() == 'GEN3':
                    cmd_addByRarity(bot, update, str(8), job_queue)
                    return
                if args[0].upper() == 'ALL':
                    cmd_addByRarity(bot, update, str(9), job_queue)
                    return
                if args[0].upper() == 'ALLE':
                    cmd_addByRarity(bot, update, str(9), job_queue)
                    return

            for x in args:
                for poke_id, name in pokemon_name[lan].items():
                    if name.upper() == x.upper():
                        names.append(str(poke_id))
            if len(names) != len(args):
                bot.sendMessage(chat_id, text='*Ich habe nicht alle Pokémon gefunden! Bitte versuche es erneut.*', parse_mode='Markdown')

            args = names
    else:
        bot.sendMessage(chat_id, text=usage_message)
        return

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



def cmd_addByRarity(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    usage_message = 'Nutzung: "/seltenheit #Nummer" mit 1 gewöhnlich bis 5 ultra-selten, 6:Gen1, 7:Gen2, 8:Gen3, 9:Alle'

    if args != []:
        if args[0].isdigit():
            if len(args) <= 0:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
            return
    else:
        bot.sendMessage(chat_id, text='Bitte nur Zahlenwerte eingeben!')
        return

    addJob(bot, update, job_queue)
    logger.info('[%s@%s] Add pokemon by rarity.' % (userName, chat_id))

    try:
        rarity = int(args[0])
        search = pref.get('search_ids')
        for x in pokemon_rarity[rarity]:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        pref.set('search_ids', search)
        cmd_list(bot, update)
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
    bot.sendMessage(chat_id, text='Setze Minimum Anriffswert auf: %s und Maximum Angriffswert auf: %s' % (attack_min, attack_max))


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
    bot.sendMessage(chat_id, text='Setze Minimum Anriffswert auf: %s und Maximum Angriffswert auf: %s' % (defense_min, defense_max))


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
    bot.sendMessage(chat_id, text='Setze Minimum Anriffswert auf: %s und Maximum Angriffswert auf: %s' % (stamina_min, stamina_max))


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
    del jobs[chat_id]

    # Remove from sent
    del sent[chat_id]
    # Remove from locks
    del locks[chat_id]

    pref.reset_user()

    bot.sendMessage(chat_id, text='Benachrichtigungen erfolgreich entfernt!')


def cmd_remove(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    lan = pref.get('language')
    names = list()
    usage_message = 'Nutzung:\n/entferne #Nummer oder /entferne #Nummer1 #Nummer2\n' + \
    '/entferne #Name oder /entferne #Name1 #Name2 ... (Ohne #)'
    logger.info('[%s@%s] Remove pokemon.' % (userName, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='Du willst Pokémon entfernen, aber du hast keinen aktiven Scanner!\n' + \
        'Bitte füge erst Pokémon zu deiner Liste hinzu mit /pokemon 1 2 3 ...')
        return

    if args != []:
        if args[0].isdigit():
            if len(args) < 1:
                bot.sendMessage(chat_id, text=usage_message)
                return
        else:
            for x in args:
                for poke_id, name in pokemon_name[lan].items():
                    if name.upper() == x.upper():
                        names.append(str(poke_id))
            if len(names) != len(args):
                bot.sendMessage(chat_id, text='*Ich habe nicht alle Pokémon gefunden! Bitte versuche es erneut.*', parse_mode='Markdown')

            args = names
    else:
        bot.sendMessage(chat_id, text=usage_message)
        return

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
            del jobs[chat_id]


def cmd_load_silent(bot, chat_id, job_queue):
    userName = ''

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] Automatic load.' % (userName, chat_id))
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
            del jobs[chat_id]


def cmd_location(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

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
            job = Job(getMysqlData, 30, repeat=True, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            job_queue.put(job)

    except Exception as e:
        logger.error('MySQL job failed.')


def alarm(bot, job):
    chat_id = job.context[0]
    logger.info('[%s] Checking alarm.' % (chat_id))

    checkAndSend(bot, chat_id, prefs.get(chat_id).get('search_ids'), thismodule.pokemon_db_data)


def addJob(bot, update, job_queue):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username
    logger.info('[%s@%s] Adding job.' % (userName, chat_id))

    try:
        if chat_id not in jobs:
            job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            job_queue.put(job)

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
    logger.info('[%s@%s] Adding job.' % (userName, chat_id))

    try:
        if chat_id not in jobs:
            job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            job_queue.put(job)

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
    logger.info('[%s] Checking pokemon and sending notifications.' % (chat_id))
    message_counter = 0
    blacklisted_pokemon_0_100 = [10,11,13,14,16,17,19,21,29,32,41,43,46,48,54,
        60,69,72,90,96,98,116,118,161,163,165,167,170,177,183,187,190,194,209,
        216,220,261,263,265,273,300,316]
    blacklisted_pokemon_0_90 = [129,133,198,296,309,363]

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
            # Get pokemon_id
            pok_id = pokemon.getPokemonID()
            if int(pok_id) not in pokemons:
                continue
            # Get encounter_id
            encounter_id = pokemon.getEncounterID()
            if encounter_id in mySent:
                continue
            # Check if Pokemon inside radius
            if not pokemon.filterbylocation(location_data):
                continue

            latitude = pokemon.getLatitude()
            longitude = pokemon.getLongitude()
            disappear_time = pokemon.getDisappearTime()
            iv = pokemon.getIVs()
            iv_attack = pokemon.getIVattack()
            iv_defense = pokemon.getIVdefense()
            iv_stamina = pokemon.getIVstamina()
            move1 = pokemon.getMove1()
            move2 = pokemon.getMove2()
            cp = pokemon.getCP()
            cpm = pokemon.getCPM()
            delta = disappear_time - datetime.utcnow()
            deltaStr = '%02dm:%02ds' % (int(delta.seconds / 60), int(delta.seconds % 60))
            disappear_time_str = disappear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S")

            # If IV is known
            if iv_attack is not None:

                # First: Filter blacklisted Pokémon
                if int(pok_id) in blacklisted_pokemon_0_100:
                    if int(iv) < 100:
                        if int(iv) != 0:
                            continue
                if int(pok_id) in blacklisted_pokemon_0_90:
                    if int(iv) < 90:
                        if int(iv) != 0:
                            continue

                # Second: Calculate Pokemon level
                pkmnlvl = getPokemonLevel(cpm)

                # Third: Filter IV/CP/LVL settings
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
                    pkmname = "%s: %s WP" % (pokemon_name[lan][pok_id], cp)
                    address = "%s - %s%%(%s/%s/%s)/L%s" % (disappear_time_str, iv, iv_attack, iv_defense, iv_stamina, pkmnlvl)
                else:
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
                        pkmname =  pokemon_name[lan][pok_id]
                        address = "%s" % (disappear_time_str)
                        title = ""
                    else:
                        pkmname =  pokemon_name[lan][pok_id]
                        address = "%s (%s)." % (disappear_time_str, deltaStr)
                        title = "Leider keine IV/WP"


            mySent[encounter_id] = disappear_time
            notDisappeared = delta.seconds > 0

            if message_counter > 10:
                bot.sendMessage(chat_id, text = 'Zu viele Pokemon eingestellt! Erhöhe die Minimum IV oder Entferne Pokemon.')
                logger.info('Too many sent')
                break

            if notDisappeared and message_counter <= 10:
                try:
                    if user_send_venue == 0:
                        bot.sendLocation(chat_id, latitude, longitude)
                        bot.sendMessage(chat_id, text = '*%s* Bis %s \n%s' % (pkmname, address, title), parse_mode='Markdown')
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
    logger.info('Done.')

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
    admins_list = config.get('LIST_OF_ADMINS', [])
    tmp = ''
    for admin in admins_list:
        tmp = '%s, %s' % (tmp, admin)
    tmp = tmp[2:]
    logger.info('LIST_OF_ADMINS: <%s>' % (tmp))

    logger.info('TELEGRAM_TOKEN: <%s>' % (config.get('TELEGRAM_TOKEN', None)))
    logger.info('SCANNER_NAME: <%s>' % (config.get('SCANNER_NAME', None)))
    logger.info('DB_TYPE: <%s>' % (config.get('DB_TYPE', None)))
    logger.info('DB_CONNECT: <%s>' % (config.get('DB_CONNECT', None)))
    logger.info('DEFAULT_LANG: <%s>' % (config.get('DEFAULT_LANG', None)))
    logger.info('SEND_MAP_ONLY: <%s>' % (config.get('SEND_MAP_ONLY', None)))
    logger.info('SEND_POKEMON_WITHOUT_IV: <%s>' % (config.get('SEND_POKEMON_WITHOUT_IV', None)))

    poke_ivfilter_list = config.get('POKEMON_MIN_IV_FILTER_LIST', dict())
    tmp = ''
    for poke_id in poke_ivfilter_list:
        tmp = '%s %s:%s' % (tmp, poke_id, poke_ivfilter_list[poke_id])
    tmp = tmp[1:]
    logger.info('POKEMON_MIN_IV_FILTER_LIST: <%s>' % (tmp))

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

    dbType = config.get('DB_TYPE', None)
    scannerName = config.get('SCANNER_NAME', None)

    global dataSource
    dataSource = None

    global ivAvailable

    ivAvailable = True
    dataSource = DataSources.DSPokemonGoMapIVMysql(config.get('DB_CONNECT', None))

    global pokemon_db_data

    if not dataSource:
        raise Exception("The combination SCANNER_NAME, DB_TYPE is not available: %s,%s" % (scannerName, dbType))


    #ask it to the bot father in telegram
    token = config.get('TELEGRAM_TOKEN', None)
    updater = Updater(token)
    b = Bot(token)
    logger.info("BotName: <%s>" % (b.name))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", cmd_start))

    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("hilfe", cmd_help))

    dp.add_handler(CommandHandler("add", cmd_add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("pokemon", cmd_add, pass_args = True, pass_job_queue=True))

    dp.add_handler(CommandHandler("addbyrarity", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("seltenheit", cmd_addByRarity, pass_args = True, pass_job_queue=True))

    dp.add_handler(CommandHandler("ende", cmd_clear))
    dp.add_handler(CommandHandler("clear", cmd_clear))

    dp.add_handler(CommandHandler("rem", cmd_remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("entferne", cmd_remove, pass_args = True, pass_job_queue=True))

    dp.add_handler(CommandHandler("save", cmd_save))
    dp.add_handler(CommandHandler("speichern", cmd_save))

    dp.add_handler(CommandHandler("load", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("laden", cmd_load, pass_job_queue=True))

    dp.add_handler(CommandHandler("list", cmd_list))
    dp.add_handler(CommandHandler("liste", cmd_list))

    dp.add_handler(CommandHandler("radius", cmd_radius, pass_args=True))

    dp.add_handler(CommandHandler("location", cmd_location_str, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("standort", cmd_location_str, pass_args=True, pass_job_queue=True))

    dp.add_handler(MessageHandler([Filters.location], cmd_location))

    dp.add_handler(CommandHandler("iv", cmd_IV, pass_args = True))

    dp.add_handler(CommandHandler("wp", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("cp", cmd_CP, pass_args = True))

    dp.add_handler(CommandHandler("lvl", cmd_LVL, pass_args = True))
    dp.add_handler(CommandHandler("level", cmd_LVL, pass_args = True))

    dp.add_handler(CommandHandler("angriff", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("attack", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("atk", cmd_attack_filter, pass_args = True))

    dp.add_handler(CommandHandler("verteidigung", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("defense", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("def", cmd_defense_filter, pass_args = True))

    dp.add_handler(CommandHandler("ausdauer", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("stamina", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("sta", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("kp", cmd_stamina_filter, pass_args = True))

    dp.add_handler(CommandHandler("modus", cmd_Mode, pass_args = True))

    dp.add_handler(CommandHandler("status", cmd_status))

    dp.add_handler(CommandHandler("nachricht", cmd_SwitchVenue))

    dp.add_handler(MessageHandler([Filters.all], cmd_unknown))

    # log all errors
    dp.add_error_handler(error)

    # add the configuration to the preferences
    prefs.add_config(config)

    # Start the Bot
    bot = b;
    updater.start_polling()
    allids = os.listdir("userdata/")
    newids = []
    for x in allids:
        newids = x.replace(".json", "")
        chat_id = int(newids)
        j = updater.job_queue
        logger.info('%s' % (chat_id))
        try:
            cmd_load_silent(b, chat_id, j)
            #bot.sendMessage(chat_id, text = 'Hinweis: Der Bot wurde neugestartet! Bitte /laden zum laden deiner Einstellungen!')

        except Exception as e:
            logger.error('%s' % (chat_id))

    logger.info('Started!')
    addJobMysql(b,j)
    thismodule.pokemon_db_data = getMysqlData(b,j)

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
