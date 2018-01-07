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
#search_ids = dict()
#language = dict()
#location_ids = dict()
location_radius = 1
#pokemon:
pokemon_name = dict()
#move:
move_name = dict()

#pokemon rarity
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
    "/hilfe Um Hilfe zu bekommen und dieses Menü anzuzeigen \n\n" + \
    "*Pokémon:*\n\n" + \
    "/pokemon 1 \n" + \
    "Nummer des Pokémon eingeben um über dieses Benachrichtigungen zu erhalten \n" + \
    "/pokemon 1 2 3 ... \n" + \
    "Mehrfache Nummern der Pokémon können so eingegeben werden \n\n" + \
    "/seltenheit 1 \n" + \
    "Fügt eine Gruppe von Pokémon hinzu. Dabei steht die 1 für gewöhnliche Pokémon und die 5 für ultra-seltene Pokémon." + \
    "6 für Gen1, 7 für Gen2, 8 für Gen3, 9 für alle Pokémon \n\n" + \
    "/iv 50 \n" + \
    "Setze die Minimum IV für die Pokémon, über die du benachrichtigt werden willst \n" + \
    "/iv 0 100 \n" + \
    "Setze die Minimum IV und Maximum IV für die Pokémon, über die du benachrichtigt werden willst \n\n" + \
    "/wp 1500 \n" + \
    "Setze die Minimum WP für die Pokémon, über die du benachrichtigt werden willst \n" + \
    "/wp 0 5000 \n" + \
    "Setze die Minimum WP und Maximum WP für die Pokémon, über die du benachrichtigt werden willst \n\n" + \
    "/lvl 15 \n" + \
    "Setze die Minimum Level für die Pokémon, über die du benachrichtigt werden willst \n" + \
    "/lvl 0 30 \n" + \
    "Setze die Minimum Level und Maximum Level für die Pokémon, über die du benachrichtigt werden willst \n\n" + \
    "/modus 0 \n" + \
    "Stellt den Modus um: /modus 0 = Du erhälst nur Benachrichtigungen für Pokemon mit IV und WP \n" + \
    "/modus 1 = Du erhälst auch Benachrichtigungen für Pokémon ohne IV und WP (zum Beispiel, wenn die IV/WP" +\
    "nicht ermittelt werden konnte. Somit bekommst du z.B. auch ein Relaxo ohne IV/WP angezeigt) \n\n"
    text2 = "/entferne 1 \n" + \
    "Nummer des Pokémon löschen, wenn du über dieses nicht mehr benachrichtigt werden willst \n" + \
    "/entferne 1 2 3 ... \n" + \
    "Mehrfache Nummern der Pokémon löschen, wenn du über diese nicht mehr benachrichtigt werden willst \n\n" + \
    "*Standort:*\n\n" + \
    "Sende deinen Standort über Telegram \n" + \
    "Dies fügt einen Umkreis um deinen Standort hinzu und du erhälst Benachrichtigungen für deine Umgebung. " + \
    "Hinweis: Das senden des Standorts funktioniert nicht in Gruppen \n" +\
    "/standort xx.xx, yy.yy \n" + \
    "Sende Koordinaten als Text in der Angezeigten Form um in dem Umkreis benachrichtigt zu werden. Es kann auch" + \
    "eine Adresse eingegeben werden zum Beispiel: /standort Holstenstraße 1, 24103 Kiel oder auch /standort Kiel, DE \n" + \
    "/radius 1000 \n" + \
    "Stellt deinen Such-Radius in m (Metern) um deinen Standort herum ein \n" + \
    "/entfernestandort \n" + \
    "Lösche deinen Standort und deinen Radius. Vorsicht: Du bekommst nun Meldungen aus ganz Schleswig-Holstein! \n\n" + \
    "*Sonstiges:*\n\n" + \
    "/liste \n" + \
    "Alle Pokemon auflisten, über die du aktuell benachrichtigt wirst \n" + \
    "/speichern \n" + \
    "Speichert deine Einstellungen. *Dies ist wichtig*, damit du nach einem Neustart des Bots deine Einstellungen behälst! \n" + \
    "/laden \n" + \
    "Lade deine gespeicherten Einstellungen \n" + \
    "/status \n" + \
    "Liste deine aktuellen Einstellungen auf \n" + \
    "/ende \n" + \
    "Damit kannst du alle deine Einstellungen löschen und den Bot ausschalten. Du kannst ihn danach mit /laden " + \
    "wieder einschalten und deine Einstellungen werden geladen \n"
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
    "(In Gruppen funktioniert das Senden des Standortes leider nicht)\n\nEs gibt noch weitere Einstellungen " + \
    "zu *IV*, *WP* und *Level*.\nBitte denk daran deine Einstellungen immer zu *speichern* mit /speichern\n" + \
    "*Fahre fort mit* /hilfe *um die möglichen Befehle aufzulisten*\n"
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
    "Minimum IV: *%s*, Maximum IV: *%s*\nMinimum Angriff: *%s*," % (miniv, maxiv, minatk) + \
    "Maximum Angriff: *%s*\nMinimum Verteidigung: *%s*, Maximum Verteidigung: *%s*\n" % (maxatk, mindef, maxdef) + \
    "Minimum Ausdauer: *%s*, Maximum Ausdauer: *%s*\nMinimum WP: *%s*, Maximum WP: *%s*\n" % (minsta, maxsta, mincp, maxcp) + \
    "Minimum Level: *%s*, Maximum Level: *%s*\nModus: *%s*\n" % (minlvl, maxlvl, mode)
    "Standort: %s,%s\nRadius: %s m" % (lat, lon, radius)

    commandmessage = "*Die Einstellungen entsprechen folgenden Befehlen:*\n\n" + \
    "/iv %s %s\n/angriff %s %s\n/verteidigung %s %s\n/ausdauer %s %s\n" % (miniv, maxiv, minatk, maxatk, mindef, maxdef, minsta, maxsta) + \
    "/wp %s %s\n/lvl %s %s\n/modus %s\n" % (mincp, maxcp, minlvl, maxlvl, mode) + \
    "/standort %s,%s\n/radius %s" % (lat, lon, radius)

    try:
        lan = pref.get('language')
        tmppref = '\n\n*Pokémon:*\n'
        tmpcmdPoke = '\n/pokemon '

        for x in pref.get('search_ids'):
            tmppref += "%i %s\n" % (x, pokemon_name[lan][str(x)])
            tmpcmdPoke += "%i " % x

    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))
        bot.sendMessage(chat_id, text='Liste leider Fehlerhaft. Bitte /ende eingeben und erneut beginnen')

    prefmessage += tmppref
    commandmessage += tmpcmdPoke

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
        cmd_list(bot, update)
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

    #addJob(bot, update, job_queue)

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
        addJob(bot, update, job_queue)
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


def cmd_clearlocation(bot, update):
    chat_id = update.message.chat_id
    userName = update.message.from_user.username

    pref = prefs.get(chat_id)
    pref.set('location', [None, None, None])
    bot.sendMessage(chat_id, text='Dein Standort wurde entfernt!')
    logger.info('[%s@%s] Location has been unset' % (userName, chat_id))


def cmd_unknown(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id, text="Falsche Eingabe. Ich habe dich nicht verstanden!\nSchaue am besten in der Hilfe nach: /help")


## Functions
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

def alarm(bot, job):
    chat_id = job.context[0]
    logger.info('[%s] Checking alarm.' % (chat_id))
    checkAndSend(bot, chat_id, prefs.get(chat_id).get('search_ids'))

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
            #text = "Scanner gestartet."
            #bot.sendMessage(chat_id, text)
    except Exception as e:
        logger.error('[%s@%s] %s' % (userName, chat_id, repr(e)))


def checkAndSend(bot, chat_id, pokemons):
    pref = prefs.get(chat_id)
    lock = locks[chat_id]
    logger.info('[%s] Checking pokemon and sending notifications.' % (chat_id))
    if len(pokemons) == 0:
        return

    try:

        lan = pref['language']
        mySent = sent[chat_id]
        location_data = pref['location']
        user_miniv = pref['user_miniv']
        user_maxiv = pref['user_maxiv']
        user_mincp = pref['user_mincp']
        user_maxcp = pref['user_maxcp']
        user_minlvl = pref['user_minlvl']
        user_maxlvl = pref['user_maxlvl']
        user_mode = pref['user_mode']
        user_send_venue = pref['user_send_venue']
        user_attack_min = pref['user_attack_min']
        user_attack_max = pref['user_attack_max']
        user_defense_min = pref['user_defense_min']
        user_defense_max = pref['user_defense_max']
        user_stamina_min = pref['user_stamina_min']
        user_stamina_max = pref['user_stamina_max']
        #user_ivfilter = pref['user_ivfilter']
        #user_lvlfilter = pref['user_lvlfilter']

        pokeMinIV = user_miniv
        pokeMaxIV = user_maxiv
        pokeMinCP = user_mincp
        pokeMaxCP = user_maxcp
        pokeMinLVL = user_minlvl
        pokeMaxLVL = user_maxlvl
        pokeMinATK = user_attack_min
        pokeMaxATK = user_attack_max
        pokeMinDEF = user_defense_min
        pokeMaxDEF = user_defense_max
        pokeMinSTA = user_stamina_min
        pokeMaxSTA = user_stamina_max
        mode = user_mode
        send_venue = user_send_venue

        counter = 0

        #logger.info('%s' % max(user_ivfilter))

        # Setze default Werte, falls keine vorhanden sind
        if pokeMinIV is None:
            pokeMinIV = 0
        if pokeMaxIV is None:
            pokeMaxIV = 100
        if pokeMinCP is None:
            pokeMinCP = 0
        if pokeMaxCP is None:
            pokeMaxCP = 5000
        if pokeMinLVL is None:
            pokeMinLVL = 1
        if pokeMaxLVL is None:
            pokeMaxLVL = 40
        if pokeMinATK is None:
            pokeMinATK = 0
        if pokeMaxATK is None:
            pokeMaxATK = 15
        if pokeMinDEF is None:
            pokeMinDEF = 0
        if pokeMaxDEF is None:
            pokeMaxDEF = 15
        if pokeMinSTA is None:
            pokeMinSTA = 0
        if pokeMaxSTA is None:
            pokeMaxSTA = 15
        if mode is None:
            mode = 1

        # Standort setzen wenn keiner eingegeben wurde:
        if location_data[0] is not None and location_data[2] is None:
            location_data[2] = 0.1
        if location_data[0] is None:
            location_data[0] = 54.321362
            location_data[1] = 10.134511
            location_data[2] = 0.1
        if float(location_data[2]) > 30:
            location_data[2] = 30

        # Vorfilter 1.0
        pokeMinIV = float(pokeMinIV)
        # Radius + 500m für Ungenauigkeit
        radius = location_data[2] + 0.5

        # Berechne Koordinaten vorher
        origin = geopy.Point(location_data[0], location_data[1])
        destination_north = VincentyDistance(radius).destination(origin, 0)
        destination_east = VincentyDistance(radius).destination(origin, 90)
        destination_south = VincentyDistance(radius).destination(origin, 180)
        destination_west = VincentyDistance(radius).destination(origin, 270)

        lat_n = destination_north.latitude
        lon_e = destination_east.longitude
        lat_s = destination_south.latitude
        lon_w = destination_west.longitude

        # Hole nur noch die richtigen Pokemon aus der DB... ABER dann ist der IVFilter hinüber
        if int(mode) == 0:
            allpokes = dataSource.getPokemonByIdsIV(pokemons, pokeMinIV, pokeMinATK, pokeMinDEF, pokeMinSTA, lat_n, lat_s, lon_e, lon_w)
        if int(mode) == 1:
            allpokes = dataSource.getPokemonByIdsAll(pokemons, pokeMinIV, pokeMinATK, pokeMinDEF, pokeMinSTA, lat_n, lat_s, lon_e, lon_w)

        moveNames = move_name["de"]

        lock.acquire()

        for pokemon in allpokes:
            # Prüfe ob Pokemon im Radius
            if not pokemon.filterbylocation(location_data):
                continue

            #logger.info('%s' % len(allpokes))


            encounter_id = pokemon.getEncounterID()
            spaw_point = pokemon.getSpawnpointID()
            pok_id = pokemon.getPokemonID()
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



            # Wenn IV vorhanden
            if iv_attack is not None:
                # Calculate Pokemon level
                pkmnlvl = getPokemonLevel(cpm)
                # Überspringe in for-Loop, wenn nicht in IV/WP/LVL Range
                if float(iv) < float(pokeMinIV) or float(iv) > float(pokeMaxIV):
                    continue
                if int(cp) < int(pokeMinCP) or int(cp) > int(pokeMaxCP):
                    continue
                if int(pkmnlvl) < int(pokeMinLVL) or int(pkmnlvl) > int(pokeMaxLVL):
                    continue
                if int(iv_attack) < int(pokeMinATK) or int(iv_attack) > int(pokeMaxATK):
                    continue
                if int(iv_defense) < int(pokeMinDEF) or int(iv_defense) > int(pokeMaxDEF):
                    continue
                if int(iv_stamina) < int(pokeMinSTA) or int(iv_stamina) > int(pokeMaxSTA):
                    continue

                #Build message
                pkmname =  pokemon_name[lan][pok_id]
                if int(send_venue) == 1:
                    pkmname = "%s: %s WP" % (pokemon_name[lan][pok_id], cp)
                    address = "%s - %s%%(%s/%s/%s)/L%s" % (disappear_time_str, iv, iv_attack, iv_defense, iv_stamina, pkmnlvl)
                else:
                    address = "%s (%s)." % (disappear_time_str, deltaStr)
                    title = "*IV*:%s (%s/%s/%s) - *WP*:%s - *Level*:%s\n" % (iv, iv_attack, iv_defense, iv_stamina, cp, pkmnlvl)
                    move1Name = moveNames[move1]
                    move2Name = moveNames[move2]
                    title += "*Moves*: %s/%s" % (move1Name, move2Name)



            # Pokemon without IV
            else:
                if int(mode) == 1:
                    if send_venue == 1:
                        pkmname =  pokemon_name[lan][pok_id]
                        address = "%s" % (disappear_time_str)
                        title = ""
                    else:
                        pkmname =  pokemon_name[lan][pok_id]
                        address = "%s (%s)." % (disappear_time_str, deltaStr)
                        title = "Leider keine IV/WP"




            # TO-DO:
            #
            #
            # Mehrere location: /loc1 = location 1 ... /locn = location n + /useloc 1 2 3 4 zum aktivieren von loc1, loc2, loc3, loc4 ?
            # /listloc ? DSpokemon.py = Radius Berechnung. if not pokemon.filterbylocation(location_data):
            # Abfrage ob pokemon im Bereich liegt.
            # Ist das quatsch? Wieviele SQL abfragen macht der Bot? Für jeden Chat eine oder eine für alle?
            # (1. Fall -> location schon in mysql als Rechteck filtern und dann als Kreis? + Er macht diese Schleife für alle 1000 pokemon
            # (die pro Minute spawnen) -> Falls SQL Abfrage pro Person, dann aufjedenfall schon dort filtern)


            if encounter_id not in mySent:
                mySent[encounter_id] = disappear_time

                notDisappeared = delta.seconds > 0

                if counter > 20:
                    bot.sendMessage(chat_id, text = 'Zu viele Pokemon eingestellt! Erhöhe die Minimum IV oder Entferne Pokemon.')
                    logger.info('Too many sent')
                    break
                if notDisappeared and counter <= 20:
                    try:
                        if send_venue == 0:
                            bot.sendLocation(chat_id, latitude, longitude)
                            bot.sendMessage(chat_id, text = '*%s* Bis %s \n%s' % (pkmname, address, title), parse_mode='Markdown')
                        else:
                            bot.sendVenue(chat_id, latitude, longitude, pkmname, address)
                        counter += 1
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
    dp.add_handler(CommandHandler("Start", cmd_start))

    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("Help", cmd_help))
    dp.add_handler(CommandHandler("hilfe", cmd_help))
    dp.add_handler(CommandHandler("Hilfe", cmd_help))

    dp.add_handler(CommandHandler("add", cmd_add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Add", cmd_add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("pokemon", cmd_add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Pokemon", cmd_add, pass_args = True, pass_job_queue=True))

    dp.add_handler(CommandHandler("addbyrarity", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Addbyrarity", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("seltenheit", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Seltenheit", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("rare", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Rare", cmd_addByRarity, pass_args = True, pass_job_queue=True))


    dp.add_handler(CommandHandler("clear", cmd_clear))
    dp.add_handler(CommandHandler("Clear", cmd_clear))

    dp.add_handler(CommandHandler("ende", cmd_clear))
    dp.add_handler(CommandHandler("Ende", cmd_clear))

    dp.add_handler(CommandHandler("rem", cmd_remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Rem", cmd_remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("entferne", cmd_remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Entferne", cmd_remove, pass_args = True, pass_job_queue=True))

    dp.add_handler(CommandHandler("save", cmd_save))
    dp.add_handler(CommandHandler("Save", cmd_save))
    dp.add_handler(CommandHandler("speichern", cmd_save))
    dp.add_handler(CommandHandler("Speichern", cmd_save))

    dp.add_handler(CommandHandler("load", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("Load", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("laden", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("Laden", cmd_load, pass_job_queue=True))

    dp.add_handler(CommandHandler("list", cmd_list))
    dp.add_handler(CommandHandler("List", cmd_list))
    dp.add_handler(CommandHandler("liste", cmd_list))
    dp.add_handler(CommandHandler("Liste", cmd_list))


    dp.add_handler(CommandHandler("radius", cmd_radius, pass_args=True))
    dp.add_handler(CommandHandler("Radius", cmd_radius, pass_args=True))

    dp.add_handler(CommandHandler("location", cmd_location_str, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Location", cmd_location_str, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("standort", cmd_location_str, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("Standort", cmd_location_str, pass_args=True, pass_job_queue=True))

    dp.add_handler(MessageHandler([Filters.location],cmd_location))

    dp.add_handler(CommandHandler("iv", cmd_IV, pass_args = True))
    dp.add_handler(CommandHandler("Iv", cmd_IV, pass_args = True))
    dp.add_handler(CommandHandler("IV", cmd_IV, pass_args = True))

    dp.add_handler(CommandHandler("wp", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("Wp", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("WP", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("cp", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("Cp", cmd_CP, pass_args = True))
    dp.add_handler(CommandHandler("CP", cmd_CP, pass_args = True))

    dp.add_handler(CommandHandler("lvl", cmd_LVL, pass_args = True))
    dp.add_handler(CommandHandler("Lvl", cmd_LVL, pass_args = True))
    dp.add_handler(CommandHandler("LVL", cmd_LVL, pass_args = True))

    dp.add_handler(CommandHandler("angriff", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("Angriff", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("attack", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("Attack", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("atk", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("Atk", cmd_attack_filter, pass_args = True))
    dp.add_handler(CommandHandler("ATK", cmd_attack_filter, pass_args = True))

    dp.add_handler(CommandHandler("verteidigung", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("Verteidigung", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("defense", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("Defense", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("def", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("Def", cmd_defense_filter, pass_args = True))
    dp.add_handler(CommandHandler("DEF", cmd_defense_filter, pass_args = True))

    dp.add_handler(CommandHandler("ausdauer", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("Ausdauer", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("stamina", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("Stamina", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("sta", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("Sta", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("STA", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("kp", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("Kp", cmd_stamina_filter, pass_args = True))
    dp.add_handler(CommandHandler("KP", cmd_stamina_filter, pass_args = True))

    dp.add_handler(CommandHandler("modus", cmd_Mode, pass_args = True))
    dp.add_handler(CommandHandler("Modus", cmd_Mode, pass_args = True))

    dp.add_handler(CommandHandler("status", cmd_status))
    dp.add_handler(CommandHandler("Status", cmd_status))

    dp.add_handler(CommandHandler("nachricht", cmd_SwitchVenue))
    dp.add_handler(CommandHandler("Nachricht", cmd_SwitchVenue))

    #dp.add_handler(CommandHandler("lang", cmd_lang, pass_args = True))
    #dp.add_handler(CommandHandler("wladd", cmd_addToWhitelist, pass_args=True))
    #dp.add_handler(CommandHandler("wlrem", cmd_remFromWhitelist, pass_args=True))
    #dp.add_handler(CommandHandler("remloc", cmd_clearlocation))
    #dp.add_handler(CommandHandler("entfernestandort", cmd_clearlocation))
    #dp.add_handler(CommandHandler("Enfernestandort", cmd_clearlocation))

    dp.add_handler(MessageHandler([Filters.command], cmd_unknown))

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


    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
