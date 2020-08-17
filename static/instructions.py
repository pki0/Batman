help_text_1 = "*Folgende Befehle kennt der Bot:*\n\n" + \
    "/hilfe Um Hilfe zu bekommen und dieses Menü anzuzeigen.\n\n" + \
    "*Pokémon:*\n\n" + \
    "/pokemon 1\n" + \
    "Nummer des Pokémon (z.B. 1 für Bisasam) eingeben um über dieses Benachrichtigungen zu erhalten.\n" + \
    "/pokemon 1 2 3 ...\n" + \
    "Mehrfache Nummern der Pokémon eingeben um über diese Benachrichtigungen zu erhalten.\n" + \
    "/pokemon Bisasam\n" + \
    "Name des Pokémon (z.B. Bisasam) eingeben um über dieses Benachrichtigungen zu erhalten.\n" + \
    "/pokemon Bisasam Glumanda Shiggy\n" + \
    "Mehrfache Namen der Pokémon eingeben um über diese Benachrichtigungen zu erhalten.\n" + \
    "/pokemon gen1\n" + \
    "Fügt alle Pokémon der 1. Generation hinzu. Mögliche Optionen sind: gen1, gen2, gen3, alle\n\n" + \
    "/iv 50\n" + \
    "Setze die Minimum IV (z.B. auf 50) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/iv 0 100\n" + \
    "Setze die Minimum IV (z.B. auf 0) und Maximum IV (z.B. auf 100) für die Pokémon, " + \
    "über die du benachrichtigt werden willst.\n\n" + \
    "/wp 1500\n" + \
    "Setze die Minimum WP (z.B. auf 1500) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/wp 0 5000\n" + \
    "Setze die Minimum WP (z.B. auf 0) und Maximum WP (z.B. auf 5000) für die Pokémon, " + \
    "über die du benachrichtigt werden willst.\n\n" + \
    "/lvl 20\n" + \
    "Setze die Minimum Level (z.B. auf 20) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/lvl 0 40\n" + \
    "Setze die Minimum Level (z.B. auf 0) und Maximum Level (z.B. auf 40) für die Pokémon, " + \
    "über die du benachrichtigt werden willst.\n" + \
    "/angriff 15 oder /atk 15\n" + \
    "Setze den Minimum Angriffswert (z.B. auf 15) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/atk 10 15\n" + \
    "Setze den Minimum Angriffswert (z.B. auf 10) und den Maximum Angriffswert (z.B. auf 15) " + \
    "für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/verteidigung 15 oder /def 15\n" + \
    "Setze den Minimum Verteidigungswert (z.B. auf 15) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/def 10 15\n" + \
    "Setze den Minimum Verteidigungswert (z.B. auf 10) und den Maximum Verteidigungswert (z.B. auf 15) " + \
    "für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/ausdauer 15 oder /kp 15\n" + \
    "Setze den Minimum Ausdauerwert (z.B. auf 15) für die Pokémon, über die du benachrichtigt werden willst.\n" + \
    "/kp 10 15\n" + \
    "Setze den Minimum Ausdauerwert (z.B. auf 10) und den Maximum Ausdauerwert (z.B. auf 15) " + \
    "für die Pokémon, über die du benachrichtigt werden willst.\n\n" + \
    "/modus\n" + \
    "Stellt den Modus um:\n" + \
    "/modus 0 = Du erhälst nur Benachrichtigungen für Pokemon mit IV und WP.\n" + \
    "/modus 1 = Du erhälst auch Benachrichtigungen für Pokémon ohne IV und WP (z.B. wenn die IV/WP " + \
    "nicht ermittelt werden konnten. Somit bekommst du z.B. auch ein Relaxo ohne IV/WP angezeigt, " + \
    "allerdings auch ein Kleinstein ohne IV/WP.\n\n"

help_text_2 = "/entferne 1\n" + \
    "Nummer des Pokémon (z.B. 1 für Bisasam) löschen, wenn du über dieses nicht mehr benachrichtigt werden willst.\n" + \
    "/entferne 1 2 3 ... \n" + \
    "Mehrfache Nummern der Pokémon löschen, wenn du über diese nicht mehr benachrichtigt werden willst.\n" + \
    "/entferne Bisasam\n" + \
    "Name des Pokémon (z.B. Bisasam) löschen, wenn du über dieses nicht mehr benachrichtigt werden willst.\n" + \
    "/entferne Bisasam Glumanda Shiggy\n" + \
    "Mehrfache Namen der Pokémon löschen, wenn du über diese nicht mehr benachrichtigt werden willst\n\n" + \
    "*Standort:*\n\n" + \
    "Sende einfach deinen Standort über Telegram.\n" + \
    "Dies fügt einen Umkreis um deinen Standort hinzu und du erhälst Benachrichtigungen für deine Umgebung. " + \
    "*Hinweis: Das senden des Standorts funktioniert in Gruppen nur, wenn der Bot auch Admin ist!*\n" +\
    "/standort xx.xx, yy.yy\n" + \
    "Sende Koordinaten als Text in der Angezeigten Form um in dem Umkreis benachrichtigt zu werden. " + \
    "Es kann auch eine Adresse eingegeben werden zum Beispiel: " + \
    "/standort Holstenstraße 1, 24103 Kiel oder auch /standort Kiel, DE.\n" + \
    "/radius 1000\n" + \
    "Stellt deinen Such-Radius in m (Metern) um deinen Standort herum ein. Hierbei ist 5000m das Maximum.\n\n" + \
    "*Sonstiges:*\n\n" + \
    "/liste\n" + \
    "Alle Pokemon auflisten, über die du aktuell benachrichtigt wirst.\n" + \
    "/speichern\n" + \
    "Speichert deine Einstellungen. *Dies ist wichtig*, damit du nach einem Neustart des Bots deine Einstellungen behälst!\n" + \
    "/laden\n" + \
    "Lade deine gespeicherten Einstellungen.\n" + \
    "/status\n" + \
    "Liste deine aktuellen Einstellungen auf.\n" + \
    "/nachricht\n" + \
    "Stellt die Art der Nachrichten um. Du hast die Wahl zwischen: Nur Standort oder Standort und Pokémon-Details.\n" + \
    "/ende\n" + \
    "Damit kannst du alle deine Einstellungen löschen und den Bot ausschalten. Du kannst ihn danach mit /laden " + \
    "wieder einschalten und deine Einstellungen werden geladen.\n" + \
    "Um den Bot komplett abzuschalten drücke im Chat oben auf 'Batman' und dann auf die drei Punkte. " + \
    "Wähle 'Bot anhalten' um ihn komplett auszuschalten." + \
    "\n\n*NEU: /pvp*\nPVP-Modus. Wähle 1500er oder 2500er Liga (nur eine zur Zeit möglich)."

start_text = "Hallo *%s*.\nDein Bot ist nun im Einstellungsmodus. " + \
    "*Weitere Schritte:* \n\n" + \
    "Falls du den Bot schon mal genutzt hast wähle /laden um deine *gespeicherten Einstellungen* zu laden.\n\n" + \
    "Benutzt du diesen Bot zum *ersten Mal*, dann füge bitte deine gewünschten *Pokémon* hinzu z.B. mit:\n" + \
    "*/pokemon 1* oder */pokemon Bisasam* für Bisasam " + \
    "oder */pokemon 1 2 3 ...* für mehrere Pokemon über die du informiert werden willst.\n\n*Sende* anschließend " + \
    "deinen *Standort* einfach über Telegram oder nutze */standort xx.xx, yy.yy*, */standort Kiel, DE* oder " + \
    "*/standort Holstenstraße 1, 24103 Kiel* um deine Koordinaten zu senden und den Bot somit zu starten. " + \
    "(In Gruppen funktioniert das Senden des Standortes nur, wenn der Bot Admin ist!)\n\n" + \
    "Es gibt noch weitere Einstellungen zu *IV*, *WP* und *Level*.\n\n" + \
    "Bitte denk daran deine Einstellungen immer zu *speichern* mit /speichern.\n\n" + \
    "*Fahre fort mit* /hilfe *um die möglichen Befehle aufzulisten.*\n"

config_main_text = "*Einstellungen*\n\n" + \
    "*Pokémon hinzugüfen:* Füge Pokémon anhand ihre Nummer oder ihres Namens hinzu. Du kannst auch Alle " + \
    "Pokémon hinzufügen indem du einfach __alle__ schreibst oder z.B. __Gen1__ für Generation 1.\n\n" + \
    "*Pokémon entfernen:* Lösche Pokémon aus deiner Liste, indem du die Nummer oder den Namen eingibst. " + \
    "Analog zur der Hinzufügen-Funktion kannst du auch __alle__ oder Generationen wählen.\n\n" + \
    "*Pokémon Einstellungen:* Hier kannst du deine IV, WP und Level Einstellungen vornehmen. Zudem gibt es " + \
    "eine Einstellung, ob nur Pokémon mit IV oder gernerell Alle versendet werden sollen.\n\n" + \
    "*Standort Einstellungen:* Lege einen neuen Standort fest oder verändere deinen Radius.\n\n" + \
    "*Nachrichten Einstellungen:* Wähle zwischen dem 1-Nachrichten und 2-Nachrichten-Modus.\n\n" + \
    "*PVP Einstellungen:* Lege fest ob du Batman im PVP-Modus betreiben willst. Wähle zwischen " + \
    "den unterschiedlichen Ligen und lege fest, wie gut die Pokémon sein sollen.\n\n" + \
    "Falls du Hilfe benötigst, schreibe einfach /hilfe ."

config_pokemon_text = "*Pokémon-Einstellungen*\n\n" + \
    "Lege einfach fest, welche minimalen und maximalen Werte deine Pokémon haben dürfen.\n" + \
    "Um z.B. eine 100er Gruppe zu machen, wähle *Min IV* und *Max IV* jeweils *100*."

config_location_text = "*Standort-Einstellungen*\n\n" + \
    "Zum ändern deines Standorts, klicke auf *Standort* und sende danach über die Büroklammer einen neuen Standort.\n" + \
    "Um den Suchradius zu verändern, klicke auf *Radius*."

config_message_text = "*Nachrichten-Einstellungen*\n\n" + \
    "Wähle den Modus, der für dich der richtige ist.\n" + \
    "Im *1-Nachrichten-Modus* wird ein Standort mit wenig Text versendet.\n" + \
    "Im *2-Nachrichten-Modus* wird ein Standort und eine detaillierte Nachricht über das Pokémon versendet."

pvp_text = "*PVP-Einstellung*\n\n" + \
    "Im PVP Modus kannst du deine gewünschte Liga und ein maximales Ranking festlegen. " + \
    "Die Berechnung der Ränge wird nach dem bekannten Muster durchgeführt, den Internetseiten, wie " + \
    "PokeBattler, GoStaduim oder PogoStat benutzen.\n\n" + \
    "Beachte, dass Batman dir hierfür jedesmal eine zusätzliche Nachricht senden wird, wenn du den Ein-Zeilen Modus verwendest.\n\n" + \
    "Hinweis: Formen, wie ALOLA oder Formeo-Sonne werden noch nicht unterstützt!"
