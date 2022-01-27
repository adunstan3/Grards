from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from . import gameManager
from .models import Grard, CahCard
import json
import os

def landing (request):
    if request.method == 'POST':
        gameCode = gameManager.makeGame('grards','test')
        game = gameManager.getGame(gameCode)
        return render(request, 'grards/testGame.html')

    return render(request, 'grards/home.html')

def join (request):
    if request.method == 'POST': #the form has been submitted check the data
        userName = request.POST.get('user-name')
        gameCode = request.POST.get('game-code')
        posibleGame = gameManager.getGame(gameCode)

        # throw error for blank user name
        if userName.isspace() or userName == "":
            return render(request, 'grards/join.html', {
                'gameCode':gameCode,
                'userName':userName,
                'error':'blankUser',
            })

        if posibleGame:
            if posibleGame.uniqueUserName(userName):
                if posibleGame.gameState == 'downTime':
                    #everything checks out send them to the game
                    return HttpResponseRedirect(reverse("grards-game", args=(gameCode, userName)))
                else:
                    #users cant join in the middle of a round throw error
                    return render(request, 'grards/join.html', {
                        'gameCode':gameCode,
                        'userName':userName,
                        'error':'roundInProgress',
                    })
            else:
                #not a unique user name render error screen
                return render(request, 'grards/join.html', {
                    'gameCode':gameCode,
                    'userName':userName,
                    'error':'badUserName',
                })
        else:
            #not a valid game code render error screen
            return render(request, 'grards/join.html', {
                'gameCode':gameCode,
                'userName':userName,
                'error':'badGameCode',
            })

    # no form submission yet render the regular page
    return render(request, 'grards/join.html', {
        'gameCode':'',
        'userName':'',
        'error':'none',
    })

def create(request):
    if request.method == 'POST':
        userName = request.POST.get('userNameInput')
        cardType = request.POST.get('card-type')
        gameCode = gameManager.makeGame(cardType)

        # no blank usernames, throw error
        if userName.isspace() or userName == "":
            return render(request, 'grards/create.html', {
                'error':'blankUser',
            })

        return HttpResponseRedirect(reverse("grards-game", args=(gameCode, userName)))

    return render(request, 'grards/create.html', {})

def game(request, gameCode, userName):
    #check for am existing game and a unique username before returning the render
    if gameManager.getGame(gameCode):
        if gameManager.getGame(gameCode).uniqueUserName(userName):
            return render(request, 'grards/game.html', {
                'gameCode':gameCode,
                'userName':userName,
            })
    #if not a good url redirect them to the join page
    return HttpResponseRedirect(reverse('grards-join'))



def password(request):
    if request.method == 'POST':
        passwordAtempt= request.POST.get('password-text')
        password = os.environ.get('GRARDS_PASSWORD')
        print("Password Atempt: {}, Password: {}".format(passwordAtempt,password))
        if passwordAtempt == password:
            print("right password")
            return HttpResponseRedirect(reverse("grards-edit"))
        else:
            print("wrong password")
            return render(request, 'grards/password.html', {'bad_password_atempt': True})
    print("no post recorded")

    return render(request, 'grards/password.html', {'bad_password_atempt': False})

def edit(request):
    if request.method == 'POST':
        if 'createSubmitButton' in request.POST:
            print("GrardSubmission!!!!!!!")
            grardType = request.POST.get('grard-type')
            if grardType=='white':
                grardText= request.POST.get('white-textarea')
            else:
                grardText= request.POST.get('first_text')
                last_text=request.POST.get('last_text')
                if not last_text == "":
                    grardText+= " ___ "
                    grardText+= last_text

            #check for making a duplicate grard
            if not Grard.objects.filter(card_text=grardText).exists():
                yourGrard = Grard(type=grardType, card_text=grardText)
                yourGrard.save()

        else: #a delete button was clicked
            cardToDelete= request.POST.get('cardToDelete')
            Grard.objects.filter(card_text=cardToDelete).delete()

    whiteCards = list(Grard.objects.filter(type='white').values_list('card_text', flat=True))
    blackCards = list(Grard.objects.filter(type='black').values_list('card_text', flat=True))

    whiteCards.reverse()
    blackCards.reverse()


    return render(request, 'grards/edit.html', {
        'whiteCards':whiteCards,
        'blackCards':blackCards
    })
