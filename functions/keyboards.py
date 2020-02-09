from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_keyboard_pvp(pvp_settings):

    pvp_keyboard = [
                     [InlineKeyboardButton("1500er Liga %s" % pvp_settings['1500_sign'], callback_data='button_pvp_1500_league'),
                      InlineKeyboardButton("2500er Liga %s" % pvp_settings['2500_sign'], callback_data='button_pvp_2500_league')],

                     [InlineKeyboardButton("Maximaler Rang: %s" % pvp_settings['user_pvp_max_rank'], callback_data='button_pvp_max_rank'),
                      InlineKeyboardButton("Buddy: %s" % pvp_settings['buddy_sign'], callback_data='button_pvp_buddy')],
                
                     [InlineKeyboardButton("Fertig", callback_data='button_pvp_finished')]
                   ]
                
    return pvp_keyboard