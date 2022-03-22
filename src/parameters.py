import json

PATHDB = 'db/'
ENVS = None
RANKING = None

class ManagerDB:
	def __init__(self):
		self.loadEnvConfig()
		self.loadHistoryOfGames()

	@property
	def username(self):
		return ENVS['user']['name']

	@property
	def level(self):
		return ENVS['game']['level']

	@property
	def resume(self):
		return ENVS['resume']
	
	@property	
	def rankingList(self):
		return RANKING

	def getColorsFromTheme(self, theme):
		return ENVS['themes'][theme]
	
	def addToRanking(self, data):
		if data.name in rankinglist:
			rankinglist[data.name][wins] += 1
			rankinglist[data.name][time] += data.time
			rankinglist[data.name][timeslist] += [data.time]

		else:
			newinranking = {
				data.name: {
					'wins': 1,
					'timeslist': [data.time],
				},
			}

			rankinglist.update(newinranking)

	def loadEnvConfig(self):
		global ENVS
		with open(PATHDB + 'configs.json', 'r') as configs:
			ENVS = json.load(configs)

	def loadHistoryOfGames(self):
		global RANKING
		with open(PATHDB + 'history.json', 'r') as history:
			RANKING = json.load(history)

	def updateHistory(self, data={}):
		self.addToRanking(data)
		with open(PATHDB + 'history.json', 'w') as history:
			json.dump(RANKING, history, indent=4)

	def updateEnvs(self, data={}):
		ENVS.update(data)
		with open(PATHDB + 'configs.json', 'w') as configs:
			json.dump(ENVS, configs, indent=4)
