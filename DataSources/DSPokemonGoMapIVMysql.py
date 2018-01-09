from .DSPokemon import DSPokemon

import os
from datetime import datetime
import logging

import pymysql
import re

logger = logging.getLogger(__name__)

class DSPokemonGoMapIVMysql():
	def __init__(self, connectString):
		# open the database
		sql_pattern = 'mysql://(.*?):(.*?)@(.*?):(\d*)/(\S+)'
		(user, passw, host, port, db) = re.compile(sql_pattern).findall(connectString)[0]
		self.__user = user
		self.__passw = passw
		self.__host = host
		self.__port = int(port)
		self.__db = db
		logger.info('Connecting to remote database')
		self.__connect()

	def getPokemonData(self):
		pokelist = []

		sqlquery = ("SELECT encounter_id, pokemon_id, latitude, "
			"longitude, disappear_time, individual_attack, individual_defense, "
			"individual_stamina, move_1, move_2, cp, cp_multiplier ")
		sqlquery += ' FROM pokemon'
		sqlquery += ' WHERE last_modified > UTC_TIMESTAMP() - INTERVAL 5 MINUTE'
		sqlquery += ' AND disappear_time > UTC_TIMESTAMP()'
		sqlquery += ' ORDER BY pokemon_id ASC'
		try:
			with self.con:
				cur = self.con.cursor()

				cur.execute(sqlquery)
				rows = cur.fetchall()
				for row in rows:
					encounter_id = str(row[0])
					pok_id = str(row[1])
					latitude = str(row[2])
					longitude = str(row[3])

					disappear = str(row[4])
					disappear_time = datetime.strptime(disappear[0:19], "%Y-%m-%d %H:%M:%S")

					individual_attack = row[5]
					individual_defense = row[6]
					individual_stamina = row[7]
					cp = row[10]
					cp_multiplier = row[11]

					if row[8] is not None:
						move1 = str(row[8])
						move2 = str(row[9])
					else:
						move1 = None
						move2 = None

					iv = None
					if individual_attack is not None:
						iv = str((int(individual_attack) +  int(individual_defense) + int(individual_stamina)) / 45 * 100)
						iv = iv[0:4]

					poke = DSPokemon(encounter_id, pok_id, latitude, longitude, disappear_time, iv, individual_attack, individual_defense, individual_stamina, move1, move2, cp, cp_multiplier)
					pokelist.append(poke)
		except pymysql.err.OperationalError as e:
			if e.args[0] == 2006:
				self.__reconnect()
			else:
				logger.error(e)
		except Exception as e:
			logger.error(e)

		return pokelist


	def __connect(self):
		self.con = pymysql.connect(user=self.__user,password=self.__passw,host=self.__host,port=self.__port,database=self.__db)

	def __reconnect(self):
		logger.info('Reconnecting to remote database')
		self.__connect()
