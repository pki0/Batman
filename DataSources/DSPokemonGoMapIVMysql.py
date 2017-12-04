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

	def getPokemonByIdsAll(self, ids, ivmin, atkmin, defmin, stamin, lat_n, lat_s, lon_e, lon_w):
		pokelist = []
		ivmin = float(ivmin)/100*45

		sqlquery = ("SELECT encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time, "
			"individual_attack, individual_defense, individual_stamina, move_1, move_2, cp, cp_multiplier "
			"FROM pokemon WHERE last_modified > UTC_TIMESTAMP() - INTERVAL 10 MINUTE AND ")
		sqlquery += ' disappear_time > "' + str(datetime.utcnow()) + '"'
		sqlquery += ' AND pokemon_id in ('
		for pokemon in ids:
			sqlquery += str(pokemon) + ','
		sqlquery = sqlquery[:-1]
		sqlquery += ')'
		sqlquery += ' AND pokemon_id NOT IN (10,11,13,14,16,17,19,21,41,46,48,60,72,90,98,118,161,163,165,167,177,183,194,198,220)'
		sqlquery += ' AND latitude BETWEEN "' + str(lat_s) + '" AND "' + str(lat_n) + '" AND longitude BETWEEN "' + str(lon_w) + '" AND "' + str(lon_e) +'"'
		sqlquery += ' GROUP BY encounter_id HAVING SUM(individual_attack + individual_defense + individual_stamina) >= "' + str(ivmin) + '"'
		sqlquery += ' OR individual_attack is NULL'
		sqlquery += ' ORDER BY pokemon_id ASC'
		try:
			with self.con:
				cur = self.con.cursor()

				cur.execute(sqlquery)
				rows = cur.fetchall()
				for row in rows:
					encounter_id = str(row[0])
					spaw_point = str(row[1])
					pok_id = str(row[2])
					latitude = str(row[3])
					longitude = str(row[4])

					disappear = str(row[5])
					disappear_time = datetime.strptime(disappear[0:19], "%Y-%m-%d %H:%M:%S")

					individual_attack = row[6]
					individual_defense = row[7]
					individual_stamina = row[8]
					cp = row[11]
					cp_multiplier = row[12]

					if row[9] is not None:
						move1 = str(row[9])
						move2 = str(row[10])
					else:
						move1 = None
						move2 = None

					iv = None
					if individual_attack is not None:
						iv = str((int(individual_attack) +  int(individual_defense) + int(individual_stamina)) / 45 * 100)
						iv = iv[0:4]

					poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, iv, individual_attack, individual_defense, individual_stamina, move1, move2, cp, cp_multiplier)
					pokelist.append(poke)
		except pymysql.err.OperationalError as e:
			if e.args[0] == 2006:
				self.__reconnect()
			else:
				logger.error(e)
		except Exception as e:
			logger.error(e)

		return pokelist

	def getPokemonByIdsIV(self, ids, ivmin, atkmin, defmin, stamin,  lat_n, lat_s, lon_e, lon_w):
		pokelist = []
		ivmin = float(ivmin)/100*45

		sqlquery = ("SELECT encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time, "
			"individual_attack, individual_defense, individual_stamina, move_1, move_2, cp, cp_multiplier "
			"FROM pokemon WHERE last_modified > UTC_TIMESTAMP() - INTERVAL 10 MINUTE AND ")
		sqlquery += ' disappear_time > "' + str(datetime.utcnow()) + '"'
		sqlquery += ' AND pokemon_id in ('
		for pokemon in ids:
			sqlquery += str(pokemon) + ','
		sqlquery = sqlquery[:-1]
		sqlquery += ')'
		sqlquery += ' AND pokemon_id NOT IN (10,11,13,14,16,17,19,21,41,46,48,60,72,90,98,118,161,163,165,167,177,183,194,198,220)'
		sqlquery += ' AND latitude BETWEEN "' + str(lat_s) + '" AND "' + str(lat_n) + '" AND longitude BETWEEN "' + str(lon_w) + '" AND "' + str(lon_e) +'"'
		sqlquery += ' GROUP BY encounter_id HAVING SUM(individual_attack + individual_defense + individual_stamina) >= "' + str(ivmin) + '"'
		sqlquery += ' ORDER BY pokemon_id ASC'
		try:
			with self.con:
				cur = self.con.cursor()

				cur.execute(sqlquery)
				rows = cur.fetchall()
				for row in rows:
					encounter_id = str(row[0])
					spaw_point = str(row[1])
					pok_id = str(row[2])
					latitude = str(row[3])
					longitude = str(row[4])

					disappear = str(row[5])
					disappear_time = datetime.strptime(disappear[0:19], "%Y-%m-%d %H:%M:%S")

					individual_attack = row[6]
					individual_defense = row[7]
					individual_stamina = row[8]
					cp = row[11]
					cp_multiplier = row[12]

					if row[9] is not None:
						move1 = str(row[9])
						move2 = str(row[10])
					else:
						move1 = None
						move2 = None

					iv = None
					if individual_attack is not None:
						iv = str((int(individual_attack) +  int(individual_defense) + int(individual_stamina)) / 45 * 100)
						iv = iv[0:4]

					poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, iv, individual_attack, individual_defense, individual_stamina, move1, move2, cp, cp_multiplier)
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
