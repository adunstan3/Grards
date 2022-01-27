from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from . import player
from .models import Grard, CahCard
import random

channel_layer = get_channel_layer()

#_____________________________________________________________________________________________
# Dealing with games

games=[]
gameCodes = [
    'startingCode',
]

def makeGame(cardType, gameCodeDefault='startingCode'):
    gameCode=gameCodeDefault
    if gameCode=='startingCode':
        while gameCode in gameCodes:
            gameCode= str(random.randrange(1,9999))

    newGame = game(gameCode, cardType)

    gameCodes.append(gameCode)
    games.append(newGame)

    return gameCode

def getGame(gameCode):
    for game in games:
        if game.gameCode == gameCode:
            return game

def deleteGame(gameCode):
    gameToDelete = getGame(gameCode)
    if gameToDelete:
        games.remove(gameToDelete)
        gameCodes.remove(gameCode)

#_____________________________________________________________________________________________
# Game Class

class game:
    def __init__(self, gameCode, cardType):
        self.gameCode = gameCode
        self.players = []
        self.playerNames = []
        self.currentJudge = None

        #set up the decks
        if cardType=='grards':
            self.whiteCards = list(Grard.objects.filter(type='white').values_list('card_text', flat=True))
            self.blackCards = list(Grard.objects.filter(type='black').values_list('card_text', flat=True))
        elif cardType == 'cahCards':
            self.whiteCards = list(CahCard.objects.filter(type='white').values_list('card_text', flat=True))
            self.blackCards = list(CahCard.objects.filter(type='black').values_list('card_text', flat=True))

        random.shuffle(self.whiteCards)
        random.shuffle(self.blackCards)
        self.whiteCardDiscard=[]
        self.blackCardDiscard=[]

        self.whiteCardsPlayed=[]
        self.playedCardsOwners={}
        self.winningCard=None
        self.currentBlackCard=None

        #Game atributes
        self.numCardsPerHand=5
        #GameState atribute: cardSubmission, cardJudging, downTime
        self.gameState='downTime'
    #_____________________________________________________________________________________________
    # Dealing with players

    def addPlayer(self, userName):
        newPlayer = player.player(userName, self.gameCode)
        self.players.append(newPlayer)

        self.playerNames.append(userName)
        #let the group know a player joined
        async_to_sync(channel_layer.group_send)(self.gameCode, {"type": "updatePlayers", "players": [userName]})
        #send the new player all the groop members
        async_to_sync(channel_layer.group_send)(userName, {"type": "updatePlayers", "players": self.playerNames})

    def removePlayer(self, userName):
        playerToRemove=self.getPlayer(userName)
        judgeLeft= (playerToRemove.state == 'grardJudge')

        self.players.remove(playerToRemove)
        self.playerNames.remove(userName)

        if len(self.playerNames) == 0:
            deleteGame(self.gameCode)
            print("deleteGame called")
        else:
            async_to_sync(channel_layer.group_send)(self.gameCode, {"type": "updatePlayers", "players": [userName]})

        if judgeLeft: # if the judge leaves end the round and go back to down time
            self.winningCard='The judge left the game before the round was over'
            self.changeState("downTime")

    #true if it is a uniqueUserName false if it is not
    def uniqueUserName(self, userName):
        return not userName in self.playerNames

    def getPlayer(self, userName):
        for player in self.players:
            if player.userName == userName:
                return player

    #_____________________________________________________________________________________________
    # Dealing with cards

    #return the requested card color
    def dealCard(self, colorToDeal):
        if colorToDeal=='white':
            if len(self.whiteCards) == 0:
                self.restoreDeck('white')
            print("Num white cards: "+str(len(self.whiteCards)))
            cardToDeal=self.whiteCards[-1] #-1 is last element in list
            del self.whiteCards[-1]
            return cardToDeal
        else:
            if len(self.blackCards) == 0:
                self.restoreDeck('black')
            cardToDeal=self.blackCards[-1] #-1 is last element in list
            del self.blackCards[-1]
            return cardToDeal

    #suffle and add the discard to the botom of the deck
    def restoreDeck(self, colorToRestore):
        if colorToRestore=='white':
            random.shuffle(self.whiteCardDiscard)
            self.whiteCards = self.whiteCardDiscard+self.whiteCards
            self.whiteCardDiscard.clear()
        if colorToRestore=='black':
            random.shuffle(self.blackCardDiscard)
            self.blackCards = self.blackCardDiscard+self.blackCards
            self.blackCardDiscard.clear()

    def submitWhiteCard(self, cardToSubmit, cardOwner):
        self.playedCardsOwners.update({cardToSubmit:cardOwner})
        self.whiteCardsPlayed.append(cardToSubmit)

        if (len(self.whiteCardsPlayed))>=((len(self.players))-1):
            #all the cards have been submitted
            print("all cards submitted")
            random.shuffle(self.whiteCardsPlayed)
            self.changeState('cardJudging')

    #_____________________________________________________________________________________________
    # Game Flow

    def changeState(self, targetState):
        self.gameState = targetState

        if targetState=='downTime':
            #Give the winning player points and update the player roles
            if self.winningCard=='The judge left the game before the round was over':
                winningPlayerName='The judge left the game before the round was over'
            elif self.winningCard=='The judge stoped the round with no submissions':
                winningPlayerName='The judge stoped the round with no submissions'
            else:
                winningPlayerName = self.playedCardsOwners[self.winningCard]
                winningPlayer = self.getPlayer(winningPlayerName)
                winningPlayer.points +=1

            for player in self.players:
                player.state='grardDefault'

            #discard white cards and reset the submit card stuff
            self.whiteCardDiscard = self.whiteCardDiscard+self.whiteCardsPlayed
            self.whiteCardsPlayed.clear()
            self.playedCardsOwners.clear()

            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type': 'updatePlayers', 'players': self.playerNames}
            )

            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type': 'finishJudging',
                'winningCard': self.winningCard,
                'winningPlayer': winningPlayerName,
                }
            )

            #TODO: Display the winning card and the black card it fills in

        if targetState=='cardSubmission':
            #select a judge and set player states for the round
            newJudge=random.choice(self.players)
            for player in self.players:
                player.state='needToPlay'

            newJudge.state='grardJudge'

            self.currentJudge=newJudge

            print(newJudge.userName+" Is this round's judge")

            self.currentBlackCard=self.dealCard('black')
            #hide all the startRound buttons and enable all card submissions
            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type': 'startRound', 'judge': self.currentJudge.userName, 'blackCard': self.currentBlackCard}
            )

            #update player states
            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type': 'updatePlayers', 'players': self.playerNames}
            )

            #Draw a black card and display it
            #

        if targetState=='cardJudging':
            print("changing state to card judging")

            #Set all player states to default incase the round was stoped early
            for player in self.players:
                if player.state == 'needToPlay':
                    player.state='grardDefault'

            #if the judge stoped the round with no submissions go back to downTime
            if len(self.whiteCardsPlayed) == 0:
                self.winningCard='The judge stoped the round with no submissions'
                self.changeState("downTime")
                return

            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type': 'updatePlayers', 'players': self.playerNames}
            )

            #start judging
            async_to_sync(channel_layer.group_send)(
                self.gameCode,
                {'type' : 'startJudging',
                'judge': self.currentJudge.userName,
                'submitedCards': self.whiteCardsPlayed, }
            )
