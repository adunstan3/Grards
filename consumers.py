import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . import gameManager

class GrardConsumer(WebsocketConsumer):

    def connect(self):
        self.gameCode = str(self.scope['url_route']['kwargs']['gameCode'])
        self.userName = self.scope['url_route']['kwargs']['userName']

        #check for am existing game and a unique username before returning the render
        if gameManager.getGame(self.gameCode):
            if gameManager.getGame(self.gameCode).uniqueUserName(self.userName):
                self.validConsumer=True
                # Join game group for messages to the game
                async_to_sync(self.channel_layer.group_add)(self.gameCode, self.channel_name)
                self.groups.append(self.gameCode)

                # Join private group for messages to you
                async_to_sync(self.channel_layer.group_add)(self.userName, self.channel_name)
                self.groups.append(self.userName)

                self.accept()

                gameManager.getGame(self.gameCode).addPlayer(self.userName)

                self.game = gameManager.getGame(self.gameCode)
                self.myPlayer = self.game.getPlayer(self.userName)

                return

        #if there were problems
        self.validConsumer=False
        print("ERROR: Either the game does not exist or the user name is not unique")

    def receive(self, text_data):
        data = json.loads(text_data)
        if data['toDo']=='playCard':
            print("consumer playcard called")
            self.myPlayer.playCard(data['cardToPlay'])

        elif data['toDo']=='startRound':
            self.game.changeState('cardSubmission')
        elif data['toDo']=='stopRound':
            self.game.changeState('cardJudging')
        elif data['toDo']=='endJudging':
            self.game.winningCard=data['winningCard']
            self.game.changeState('downTime')


    def disconnect(self, close_code):
        #disconection hapens automaitcaly with groups list
        if self.validConsumer:
            #return cards and delete player
            print('Num Discarded cards: '+str(len(self.game.whiteCardDiscard)))
            self.game.whiteCardDiscard = self.game.whiteCardDiscard + self.myPlayer.hand
            self.game.removePlayer(self.userName)
            print('Num Discarded cards: '+str(len(self.game.whiteCardDiscard)))

    def updatePlayers(self, event):
        print(event)
        playerData=[]

        for player in event['players']:
            tempPlayer = self.game.getPlayer(player)
            if tempPlayer:
                playerData.append({
                    'userName':tempPlayer.userName,
                    'points':tempPlayer.points,
                    'state':tempPlayer.state,
                    'toDelete':False,
                })
            else:
                playerData.append({
                    'userName':player,
                    'points':'You got no points you dead',
                    'state':'This boi dead',
                    'toDelete':True,
                })

        self.send(text_data=json.dumps({
            'type': 'updatePlayers',
            'players': playerData,
        }))

    def updateCards(self, event):
        self.send(text_data=json.dumps({
            'type': 'updateCards',
            'cards': event['cards'],
        }))

    def startRound(self, event):
        print("startRound called")
        self.send(text_data=json.dumps({
            'type': 'startRound',
            'judge': event['judge'],
            'blackCard': event['blackCard'],
        }))

    def startJudging(self, event):
        print("consumer start judging called")
        self.send(text_data=json.dumps({
            'type' : 'startJudging',
            'judge': event['judge'],
            'submitedCards': event['submitedCards'],
        }))

    def finishJudging(self, event):
        print("finished judging, round over")
        self.send(text_data=json.dumps({
            'type': 'finishJudging',
            'winningCard': event['winningCard'],
            'winningPlayer': event['winningPlayer'],
        }))
