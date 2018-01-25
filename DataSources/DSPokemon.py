from geopy.distance import great_circle
import matplotlib.path as mplPath
import numpy as np

class DSPokemon:
	def __init__(self, encounter_id, pokemon_id, latitude, longitude, disappear_time, ivs, iv_attack, iv_defense, iv_stamina, move1, move2, cp, cp_multiplier, gender):
		self.encounter_id = encounter_id
		self.pokemon_id = pokemon_id
		self.latitude = latitude
		self.longitude = longitude
		self.disappear_time = disappear_time # Should be datetime
		self.ivs = ivs
		self.iv_attack = iv_attack
		self.iv_defense = iv_defense
		self.iv_stamina = iv_stamina
		self.move1 = move1
		self.move2 = move2
		self.cp = cp
		self.cp_multiplier = cp_multiplier
		self.gender = gender

	def getEncounterID(self):
		return self.encounter_id

	def getPokemonID(self):
		return self.pokemon_id

	def getLatitude(self):
		return self.latitude

	def getLongitude(self):
		return self.longitude

	def getDisappearTime(self):
		return self.disappear_time

	def getIVs(self):
		return self.ivs

	def getIVattack(self):
		return self.iv_attack

	def getIVdefense(self):
		return self.iv_defense

	def getIVstamina(self):
		return self.iv_stamina

	def getMove1(self):
		return self.move1

	def getMove2(self):
		return self.move2

	def getCP(self):
		return self.cp

	def getCPM(self):
		return self.cp_multiplier

	def getGender(self):
		return self.gender

	def filterbylocation(self,user_location):
		user_lat_lon = (user_location[0], user_location[1])
		pok_loc = (float(self.latitude), float(self.longitude))
		return great_circle(user_lat_lon, pok_loc).km <= user_location[2]
