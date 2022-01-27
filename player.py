from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()

from . import gameManager

class player:
    def __init__(self, userName, gameCode):
        self.userName = userName
        self.gameCode = gameCode
        self.game = gameManager.getGame(gameCode)
        self.points=0
        self.state='grardDefault' #can be needToPlay or grardJudge
        self.toDelete=False

        self.hand=[]
        for x in range(self.game.numCardsPerHand):
            self.hand.append(self.game.dealCard('white'))

        async_to_sync(channel_layer.group_send)(self.userName, {"type": "updateCards", "cards": self.hand})

    def drawCard(self):
        newCard=self.game.dealCard('white')
        self.hand.append(newCard)
        async_to_sync(channel_layer.group_send)(self.userName, {"type": "updateCards", "cards": [newCard]})

    def playCard(self, cardToPlay):
        #move the card from your hand to the played pile
        try:
            self.hand.remove(cardToPlay)
        except:
            print("You tried to play a card not in your hand. Im still not sure how that happened.")
        self.game.submitWhiteCard(cardToPlay, self.userName)

        #change your state and tell everyone
        self.state='grardDefault'
        async_to_sync(channel_layer.group_send)(self.gameCode, {"type": "updatePlayers", "players": [self.userName]})

        self.drawCard()
