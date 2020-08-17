from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_keyboard_pvp(pvp_settings):
    keyboard_pvp = [
                    [InlineKeyboardButton("1500er Liga %s" % pvp_settings['1500_sign'], callback_data='button_pvp_1500_league'),
                     InlineKeyboardButton("2500er Liga %s" % pvp_settings['2500_sign'], callback_data='button_pvp_2500_league')],

                    [InlineKeyboardButton("Maximaler Rang: %s" % pvp_settings['user_pvp_max_rank'], callback_data='button_pvp_max_rank'),
                     InlineKeyboardButton("Buddy: %s" % pvp_settings['buddy_sign'], callback_data='button_pvp_buddy')],

                    #[InlineKeyboardButton("Zurück 🔙", callback_data='button_config_back_to_main')]
                    [InlineKeyboardButton("Fertig", callback_data='button_pvp_finished')]
                   ]

    return keyboard_pvp


def get_keyboard_config_main():
    keyboard_config_main = [
                            [InlineKeyboardButton("Pokémon hinzufügen ➕", callback_data='button_config_main_pokemon_add')],

                            [InlineKeyboardButton("Pokémon entfernen ➖", callback_data='button_config_main_pokemon_remove')],

                            [InlineKeyboardButton("Pokémon Einstellungen (IV) ⚙", callback_data='button_config_main_pokemon_settings')],

                            [InlineKeyboardButton("Standort Einstellungen 📌", callback_data='button_config_main_location_settings')],

                            [InlineKeyboardButton("Nachrichten Einstellungen ✉️", callback_data='button_config_main_message_settings')],

                            [InlineKeyboardButton("PVP Einstellungen ⚔️", callback_data='button_config_main_pvp')],

                            [InlineKeyboardButton("Fertig ✅", callback_data='button_config_main_finished')]
                           ]

    return keyboard_config_main

def get_keyboard_config_pokemon_settings(config_settings):
    # Preconditions
    if config_settings['user_mode'] == 1:
        config_user_mode_on = "Nur Pokémon mit IV senden ✅"
    else:
        config_user_mode_on = "Nur Pokémon mit IV senden ❌"



    keyboard_config_pokemon_settings = [
                       [InlineKeyboardButton("%s" % config_user_mode_on, callback_data='button_config_pokemon_user_mode')],
                       [InlineKeyboardButton("Min IV: %s" % config_settings['user_miniv'], callback_data='button_config_pokemon_min_iv'),
                        InlineKeyboardButton("Max IV: %s" % config_settings['user_maxiv'], callback_data='button_config_pokemon_max_iv')],

                       [InlineKeyboardButton("Min Angriff: %s" % config_settings['user_attack_min'], callback_data='button_config_pokemon_min_attack'),
                        InlineKeyboardButton("Max Angriff: %s" % config_settings['user_attack_max'], callback_data='button_config_pokemon_max_attack')],

                       [InlineKeyboardButton("Min Verteidigung: %s" % config_settings['user_defense_min'], callback_data='button_config_pokemon_min_defense'),
                        InlineKeyboardButton("Max Verteidigung: %s" % config_settings['user_defense_max'], callback_data='button_config_pokemon_max_defense'),],

                       [InlineKeyboardButton("Min Ausdauer: %s" % config_settings['user_stamina_min'], callback_data='button_config_pokemon_min_stamina'),
                        InlineKeyboardButton("Max Ausdauer: %s" % config_settings['user_stamina_max'], callback_data='button_config_pokemon_max_stamina')],

                       [InlineKeyboardButton("Min WP: %s" % config_settings['user_mincp'], callback_data='button_config_pokemon_min_cp'),
                        InlineKeyboardButton("Max WP: %s" % config_settings['user_maxcp'], callback_data='button_config_pokemon_max_cp')],

                       [InlineKeyboardButton("Min Level: %s" % config_settings['user_minlvl'], callback_data='button_config_pokemon_min_level'),
                        InlineKeyboardButton("Max Level: %s" % config_settings['user_maxlvl'], callback_data='button_config_pokemon_max_level')],

                       [InlineKeyboardButton("Zurück 🔙", callback_data='button_config_back_to_main')]
                      ]

    return keyboard_config_pokemon_settings


def get_keyboard_config_location_settings(config_settings):
    if config_settings['location'][2] is None:
        radius = 0
    else:
        radius = config_settings['location'][2]

    keyboard_config_location_settings = [
                       [InlineKeyboardButton("Neuer Standort", callback_data='button_config_location')],
                       [InlineKeyboardButton("Radius: %s m" % radius, callback_data='button_config_radius')],

                       [InlineKeyboardButton("Zurück 🔙", callback_data='button_config_back_to_main')]
                      ]
    return keyboard_config_location_settings


def get_keyboard_config_message_settings(config_settings):
    if config_settings['user_send_venue'] == 1:
        config_user_send_venue_on = "1-Nachrichten-Modus ✅"
        config_user_send_venue_off = "2-Nachrichten-Modus ❌"
    else:
        config_user_send_venue_on = "1-Nachrichten-Modus ❌"
        config_user_send_venue_off = "2-Nachrichten-Modus ✅"

    keyboard_config_message_settings = [
                       [InlineKeyboardButton("%s" % config_user_send_venue_on, callback_data='button_config_message_venue_on')],
                       [InlineKeyboardButton("%s" % config_user_send_venue_off, callback_data='button_config_message_venue_off')],

                       [InlineKeyboardButton("Zurück 🔙", callback_data='button_config_back_to_main')]
                      ]
    return keyboard_config_message_settings
