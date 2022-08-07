#imports
from random import choice
import pygame, pygame.font, pygame.event, pygame.draw
from pygame.locals import *
from pygame import mixer
import webbrowser
pygame.init()  # initialize pygame and mixer
mixer.init()
# ---------------------------------------#
# initialize global variables/constants  #
# ---------------------------------------#
# setting colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (102, 255, 255)
DARK_GREEN = (8, 166, 25)

# initializing the fonts
defaultFont = pygame.font.SysFont('arial', 30)
defaultFontBold = pygame.font.SysFont('arial', 50, bold=True)

# variables for input box
VALID_KEYS = '0123456789'
capsOn = False

mixer.music.load('CasinoMusic.mp3') # set background music

# inits win/loss sound and sets their volume
winSound = mixer.Sound('tada.wav')
mixer.Sound.set_volume(winSound, 0.8)
lossSound = mixer.Sound('loss.wav')
mixer.Sound.set_volume(lossSound, 0.4)


# ---------------------------------------------------------#
# function that gets the values of the cards being played  #
# ---------------------------------------------------------#
def cardValues(playerDecksList, hitCount, cp, scores):
    global ACountUser, ACountDealer, counter # global statments
    if len(playerDecksList) == 4: #card values for the start
        r1 = 0
        r2 = 2
        cp = 0
        while True:
            for card in range(r1, r2):
                if playerDecksList[card][0].isdigit():
                    if int(playerDecksList[card][0]) > 1:
                        scores[cp] += int(playerDecksList[card][0])
                    else:
                        scores[cp] += 10
                else:
                    if playerDecksList[card][0] == 'J' or playerDecksList[card][0] == 'Q' or playerDecksList[card][0] == 'K':
                        scores[cp] += 10
                    elif playerDecksList[card][0] == 'A' and cp == 0:
                        scores[cp] += 11
                        ACountDealer += 1
                    elif playerDecksList[card][0] == 'A' and cp == 1:
                        scores[cp] += 11
                        ACountUser += 1
            r1 += 2
            r2 += 2
            cp += 1
            if cp >= 2:
                break
    else: # card values for the rest if the game
        if cp == 0: # dealer
            if playerDecksList[hitCount + counter][0].isdigit():
                if int(playerDecksList[hitCount + counter][0]) > 1:
                    scores[0] += int(playerDecksList[hitCount + counter][0])
                else:
                    scores[0] += 10
            else:
                if playerDecksList[hitCount + counter][0] == 'J' or playerDecksList[hitCount + counter][0] == 'Q' or playerDecksList[hitCount + counter][0] == 'K':
                    scores[0] += 10
                elif playerDecksList[hitCount + counter][0] == 'A' and scores[cp] >= 11:
                    scores[cp] += 1
                elif playerDecksList[hitCount + counter][0] == 'A' and scores[cp] < 11:
                    scores[cp] += 11
                    ACountDealer += 1
            counter += 1
        else: # user
            if playerDecksList[hitCount + 3][0].isdigit():
                if int(playerDecksList[hitCount + 3][0]) > 1:
                    scores[1] += int(playerDecksList[hitCount + 3][0])
                else:
                    scores[1] += 10
            else:
                if playerDecksList[hitCount + 3][0] == 'J' or playerDecksList[hitCount + 3][0] == 'Q' or playerDecksList[hitCount + 3][0] == 'K':
                    scores[1] += 10
                elif playerDecksList[hitCount + 3][0] == 'A' and scores[cp] >= 11:
                    scores[cp] += 1
                elif playerDecksList[hitCount + 3][0] == 'A' and scores[cp] < 11:
                    scores[cp] += 11
                    ACountUser += 1


# ----------------------------------------------------#
# function that gives the players their initial hand  #
# ----------------------------------------------------#
def playerDecks(playerDecksList, cardDeck):
    for deck in range(4): # 4 cards(2 for each player)
        card = choice(cardDeck) #picks random card from deck
        playerDecksList.append(card)
        cardDeck.remove(card)


# --------------------------------------------------------------------------------#
# function that makes a list of the users cards and a list for the dealers cards  #
# --------------------------------------------------------------------------------#
def deckPrint(playerDecksList, playerMove):
    global userCards, dealerCards # global statments
    if len(playerDecksList) == 4 and turnCount == 0 and playerMove != 's': # first 4 cards
        dealerCards.append(playerDecksList[0])
        dealerCards.append(playerDecksList[1])
        userCards.append(playerDecksList[2])
        userCards.append(playerDecksList[3])
    elif playerMove == 's': # if player stands
        for i in range(len(playerDecksList)):
            if playerDecksList[i] not in userCards and playerDecksList[i] not in dealerCards:
                dealerCards.append(playerDecksList[i])
    elif playerMove == 'h': # if player hits
        for i in range(len(playerDecksList)):
            if playerDecksList[i] not in userCards and playerDecksList[i] not in dealerCards:
                userCards.append(playerDecksList[i])


# -------------------------------------------------------------------------------------------#
# function that chooses what to do/where to go for each situation (hit, stand, double down)  #
# -------------------------------------------------------------------------------------------#
def playerTurn():
    global turnCount, playerMove, hitCount, NotEnoughDD, gameOver, money, bet # global statments
    if playerMove == 'h': # if you clicked hit
        turnCount += 1
        hitCount += 1
        hitStand(playerDecksList, cardDeck, hitCount, scores, cp=1)
        deckPrint(playerDecksList, playerMove) # refresh what cards each player has
    elif playerMove == 's': # if you clicked stand
        hitStand(playerDecksList, cardDeck, hitCount, scores, cp=0)
        while scores[0] < 17: # dealer hits until he has 17+
            hitStand(playerDecksList, cardDeck, hitCount, scores, cp=0)
        gameOver = True
    elif playerMove == 'd': # if you clicked double down
        if money >= bet: # check if you can afford double down
            turnCount += 1
            hitCount += 1
            money -= bet # half money
            bet *= 2 # double bet
            playerMove = 'h' # hit one card
            hitStand(playerDecksList, cardDeck, hitCount, scores, cp=1)
            if scores[1] <= 21:
                playerMove = 's' # stand after one hit
                while scores[0] < 17:
                    hitStand(playerDecksList, cardDeck, hitCount, scores, cp=0)
            gameOver = True
        else:
            NotEnoughDD = True # cannot afford to double down


# ---------------------------------------------------------------------#
# function that does the actions for a hit or a stand or a double down #
# ---------------------------------------------------------------------#
def hitStand(playerDecksList, cardDeck, hitCount, scores, cp):
    global ACountUser, ACountDealer, HS, gameOver # global statments
    if scores[0] <= 16 and playerMove == 's' or playerMove == 'h': #checking if game isn't done to add a card
        card = choice(cardDeck)
        playerDecksList.append(card)
        cardDeck.remove(card)
        cardValues(playerDecksList, hitCount, cp, scores) # adding the value to the correct player
    HS = True
    if playerMove == 's': # if you clicked stand
        if 17 <= scores[0] and ACountDealer == 0: # dealer must stand on 17+
            gameOver = True
        elif scores[0] > 21 and ACountDealer >= 1: # dealer goes over 21 with a ace(11), so the value of his ace goes from 11 to 1
            scores[0] -= 10
            ACountDealer -= 1
    elif scores[1] > 21 and ACountUser == 0: # user busted (over 21)
        gameOver = True
    elif scores[1] > 21 and ACountUser >= 1: # user goes over 21 with a ace(11), so the value of his ace goes from 11 to 1
        scores[1] -= 10
        ACountUser -= 1
    deckPrint(playerDecksList, playerMove) # refreshes each players cards


#---------------------------------------#
# function that redraws all objects     #
#---------------------------------------#
def redraw_game_window(currentScreen):
    global money, moneyCounter, startMoney, bet, insure, insFail, gameOver, insAmount, insureOver, t, t2, end, soundCounter, rebet, inPlay # global statments
    if currentScreen == GAME_SCREEN:
        win.blit(images[53], (0, 0)) # blits background image
        if float(money).is_integer(): # makes sure money is in correct form
            money = int(money)
        blitText('Your current money is: ' + str(money), 30, 5, 5, center=False)
        blitText('Your current bet is: ' + str(bet), 30, 5, 50, center=False)
        if NotEnoughDD and t2 < 100 and not gameOver: # if clicked on double down and cannot afford
            blitText("You cannot afford to Double Down,", 20, 690, 370, center=False)
            blitText('Choose another action.', 20, 693, 400, center=False)
            t2 += 1
        if insFail and t < 100 and not gameOver: # if clicked on insurance and lost/cannot afford
            blitText("Your Insurance failed, or you don't", 20, 690, 370, center=False)
            blitText('have enough money for insurance.', 20, 693, 400, center=False)
            t += 1
        if insAmount > 0:
            if float(insAmount).is_integer(): # makes sure insurance amount is in correct form
                insAmount = int(insAmount)
            blitText('Your current insurance is: ' + str(insAmount), 30, 5, 95, center=False)
        if gameOver: # if the game is over, all possible outcomes are in this if statment
            drawCards(userCards, dealerCards, cardDeckUnedited, used)
            blitText('There are no more actions', 50, 0, 550, center=True)
            if insureOver: # if the final outcome comes right after the insurance
                if scores[1] == 21 and scores[0] == 21: # if both players have blackjack, and you insured
                    blitText('Push! Both the player and the dealer', 20, 670, 340, center=False)
                    blitText('have blackjack, you gain back your bet,', 20, 670, 370, center=False)
                    blitText('but your insurance wins!', 20, 670, 400, center=False)
                    if moneyCounter == 0: # adds money
                        money += bet
                        money += insAmount * 3
                        moneyCounter += 1
                elif scores[0] == 21: # if dealer has blackjack but you insured
                    blitText('You lose your bet, but win the insurance!', 20, 650, 380, center=False)
                    if moneyCounter == 0:
                        money += insAmount * 3
                        moneyCounter += 1
                elif scores[1] == 21: # if you have blackjack and lost insurance
                    blitText('BlackJack! You gain 3 to 2 of what', 20, 670, 340, center=False)
                    blitText('you bet, but you lost your insurance.', 20, 670, 370, center=False)
                    if moneyCounter == 0:
                        money += bet * 2.5
                        moneyCounter += 1
                if soundCounter == 0 and SEToggle == 'yes': # plays win sound
                    winSound.play()
                    soundCounter += 1
                blitText('Play again?', 40, 63, 230, center=False) # asks to play again
                drawMultipleButtons(win, buttonsEnd, yornList)
            elif not insureOver and len(playerDecksList) == 4 and not HS: # instant outcomes with no insurance
                if t >= 100 and insFail or t == 0 and not insFail:
                    if scores[1] == 21 and scores[0] == 21: # both players hack blackjack
                        blitText('Push! Both the player and the dealer', 20, 670, 340, center=False)
                        blitText('have Blackjack, you gain back your bet.', 20, 670, 370, center=False)
                        if moneyCounter == 0:
                            money += bet
                            moneyCounter += 1
                    elif scores[1] == 21: # user has blackjack
                        blitText('BlackJack! you gain 3 to 2 of what you bet!', 20, 640, 365, center=False)
                        if soundCounter == 0 and SEToggle == 'yes':
                            winSound.play()
                            soundCounter += 1
                        if moneyCounter == 0:
                            money += bet * 2.5
                            moneyCounter += 1
                    elif scores[0] == 21: # dealer has blackjack (with the ace as the hidden card so there is no insurance)
                        blitText('Dealer has BlackJack! You lose. :(', 20, 670, 340, center=False)
                        if soundCounter == 0 and SEToggle == 'yes': # plays loss sound
                            lossSound.play()
                            soundCounter += 1
                    blitText('Play again?', 40, 63, 230, center=False)
                    drawMultipleButtons(win, buttonsEnd, yornList)
            elif HS:
                if scores[0] > 21 and ACountDealer == 0: # if dealer busted
                    blitText('Dealer busted! You win!', 20, 640, 365, center=False)
                    if soundCounter == 0 and SEToggle == 'yes':
                        winSound.play()
                        soundCounter += 1
                    if moneyCounter == 0:
                        money += bet * 2
                        moneyCounter += 1
                elif scores[1] > 21 and ACountUser == 0: # if user busted
                    blitText('Bust! You got over 21,', 20, 710, 365, center=False)
                    blitText('you lose your bet!', 20, 710, 395, center=False)
                    if soundCounter == 0 and SEToggle == 'yes':
                        lossSound.play()
                        soundCounter += 1
                elif scores[1] > scores[0]: # if neither player busted but user has higher
                    blitText('You have a higher score than the dealer,', 20, 640, 365, center=False)
                    blitText('You win!', 20, 640, 395, center=False)
                    if soundCounter == 0 and SEToggle == 'yes':
                        winSound.play()
                        soundCounter += 1
                    if moneyCounter == 0:
                        money += bet * 2
                        moneyCounter += 1
                elif scores[0] > scores[1]: # if neither player busted but dealer has higher
                    blitText('The dealer has a higher score than you,', 20, 640, 365, center=False)
                    blitText('you lose. :(', 20, 640, 395, center=False)
                    if soundCounter == 0 and SEToggle == 'yes':
                        lossSound.play()
                        soundCounter += 1
                elif scores[0] == scores[1]: # if both players have equal scores
                    blitText('Push! You and the dealer have the', 20, 640, 365, center=False)
                    blitText('same score, you get your bet back.', 20, 640, 395, center=False)
                    if moneyCounter == 0:
                        money += bet
                        moneyCounter += 1
                blitText('Play again?', 40, 63, 230, center=False)
                drawMultipleButtons(win, buttonsEnd, yornList)
        if insure: # if statment to deal with insurance (dealers shown card is a ace)
            drawCards(userCards, dealerCards, cardDeckUnedited, used)
            blitText('Would you like to', 30, 785, 230, center=False)
            blitText('take insurance?', 30, 795, 260, center=False)
            drawMultipleButtons(win, buttonsIns, yornList)
            if insIndex == 0: # if yes to insurance
                if money >= bet * 0.5: # checks if you can afford
                    money = money - bet * 0.5 # adjusts money
                    insAmount = bet * 0.5
                    if scores[1] == 21 or scores[0] == 21: # checks if anyone won
                        gameOver = True
                        insure = False
                        insureOver = True
                    else:
                        insAmount = 0
                        insure = False
                        insFail = True
                else:
                    insAmount = 0
                    insure = False
                    insFail = True
            elif insIndex == 1: # if no to insurance
                insure = False
        elif not insure and insAmount == 0: # checks if anyone won normally (after insurance or instal win/loss)
            drawCards(userCards, dealerCards, cardDeckUnedited, used)
            if scores[0] == 21 or scores[1] == 21 and playerMove == 's' or scores[1] == 21 and len(playerDecksList) == 4:
                gameOver = True
            else:
                if not gameOver: # if game is still going, lbit the hit, stand and sometimes the Double down button (if first turn).
                    if turnCount > 0 or NotEnoughDD:
                        drawMultipleButtons(win, buttonsHS, HSList)
                    elif turnCount == 0:
                        drawMultipleButtons(win, buttonsHSD, HSDList)
    elif currentScreen == START_SCREEN:
        win.blit(images[52], (0, 0)) # blit background image
        welcomeSurface = defaultFontBold.render('Welcome to Blackjack!', True, BLACK)
        win.blit(welcomeSurface, (win.get_width() // 2 - welcomeSurface.get_width() // 2, 80))
        blitText('Made by Nick Jano', 30, 0, 140, center=True)
        win.blit(images[55], (win.get_width() // 2 - images[55].get_width() // 2, 485))
        drawMultipleButtons(win, buttonsStart, startList) # blit buttons on start screen
    elif currentScreen == INST_SCREEN:
        win.blit(images[52], (0, 0)) # blit background image
        blitText('Instructions:', 50, 0, 80, center=True)
        h = 155
        for i in range(len(instr)): # for loop to blit the instructions
            blitText(instr[i], 20, 0, h, center=True)
            h += 35
        drawMultipleButtons(win, buttonsInstr, instrList)
    elif currentScreen == MONEY_SCREEN:
        win.blit(images[52], (0, 0)) # blit background image
        drawButton(win, 'Back', (800, 32, 175, 85), buttonColour, BLACK, defaultFont)
        blitText('How much money would you like to start with?', 40, 0, 140, center=True)
        blitText('Please input a int number greater than 0 for your money to start with.', 30, 0, 460, center=True)
        blitText('Press enter to submit the typed number.', 30, 0, 510, center=True)
        if startMoney == 0 and money != 'back':
            money = inputBox('Money', DARK_GREEN) # makes a input box
            while True:
                if money.isdigit(): # checks for valid input
                    money = int(money)
                    if 1 <= money <= 99999999999999999999: # checks for valid input
                        startMoney = money
                        break
                    else:
                        money = inputBox('Money', RED) # turns box red on invalid input
                elif money == 'back': # back to start page
                    break
                elif money == 'exit': # closes program
                    inPlay = False
                    break
                else:
                    money = inputBox('Money', RED) # turns box red on invalid input
    elif currentScreen == BET_SCREEN:
        win.blit(images[52], (0, 0)) # blit background image
        drawButton(win, 'Instructions', (800, 32, 175, 85), buttonColour, BLACK, defaultFont)
        drawButton(win, 'Rebet', (win.get_width()//2 - 60, 363, 120, 75), buttonColour, BLACK, defaultFont)
        blitText('Your current money is: ' + str(money), 40, 5, 5, center=False)
        blitText('How much would you like to bet?', 40, 0, 140, center=True)
        blitText('Your bet must be a int number greater than 0,', 30, 0, 460, center=True)
        blitText('and less or equal too your current money.', 30, 0, 510, center=True)
        blitText('Press enter to submit the typed number.', 30, 0, 560, center=True)
        if bet == 0:
            bet = inputBox('Bet', DARK_GREEN) # makes a input box
            while True:
                if bet.isdigit(): # checks for valid input
                    bet = int(bet)
                    if 1 <= bet <= money: # checks for valid input
                        money -= bet
                        rebet = bet
                        break
                    else:
                        bet = inputBox('Bet', RED) # turns box red on invalid input
                elif bet == 'back': # goes to instrusctions page
                    break
                elif bet == 'exit': # closes program
                    inPlay = False
                    break
                else:
                    bet = inputBox('Bet', RED) # turns box red on invalid input
    elif currentScreen == GG_SCREEN:
        win.blit(images[52], (0, 0))
        if money < 1: # checks if you are on this page becuase you ran out of money
            blitText('You ran out of money!', 40, 0, 140, center=True)
            if PAIndex == 0: # if you want to play again
                drawMultipleButtons(win, buttonsExit, exitList)
            elif PAIndex == 1: # if you dont want to play again
                drawButton(win, 'EXIT', (win.get_width() // 2 - 150, win.get_height() // 2 - 75, 300, 150),buttonColour, BLACK, defaultFont)
                end = True
        else:
            blitText('Thank you for playing!', 40, 0, 140, center=True)
            drawButton(win, 'EXIT', (win.get_width() // 2 - 150, win.get_height() // 2 - 75, 300, 150), buttonColour, BLACK, defaultFont)
            end = True
        if startMoney > money: # blits money started with and ended with, in red because you lost money
            redSurface = defaultFont.render(('You started with ' + str(startMoney) + ' money and finished with ' + str(money) + ' money. :('), True, RED)
            win.blit(redSurface, (win.get_width() // 2 - redSurface.get_width() // 2, 455))
        if money > startMoney: # blits money started with and ended with, in green becuase you gained money
            greenSurface = defaultFont.render(('You started with ' + str(startMoney) + ' money and finished with ' + str(money) + ' money. :)'), True, GREEN)
            win.blit(greenSurface, (win.get_width() // 2 - greenSurface.get_width() // 2, 455))
        if money == startMoney: # blits money started with and ended with, in black becuase you finished with equal amount that you started with
            blitText('You started with ' + str(startMoney) + ' money and finished with ' + str(money) + ' money, you broke even!', 30, 0, 455, center=True)
    elif currentScreen == BUTTONS_SCREEN:
        win.blit(images[52], (0, 0))
        blitText("Pick the color of button you'd like:", 40, 0, 120, center=True)
        # blits buttons in their respective colours
        drawButton(win, 'RED', (30, win.get_height() // 2 - 75, 250, 150), RED, BLACK, defaultFont)
        drawButton(win, 'GREEN', (392, win.get_height() // 2 - 75, 250, 150), DARK_GREEN, BLACK, defaultFont)
        drawButton(win, 'BLUE', (754, win.get_height() // 2 - 75, 250, 150), BLUE, BLACK, defaultFont)
        drawButton(win, 'Back', (55, 108, 120, 70), WHITE, BLACK, defaultFont)
    elif currentScreen == SE_SCREEN:
        win.blit(images[52], (0, 0))
        blitText('Would you like sound effects on or off?', 40, 0, 120, center=True)
        drawMultipleButtons(win, buttonsSE, SEList) # blits buttons for on and off for sound effects (win/loss, not music)
    pygame.display.update()


#--------------------------------------------#
# function that blits text on the screen     #
#--------------------------------------------#
def blitText(message, fontSize, x, y, center=True):
    defaultFont = pygame.font.SysFont('arial', fontSize)
    textSurface = defaultFont.render(message, True, BLACK)
    if center:
        x = win.get_width() // 2 - textSurface.get_width() // 2 # centers text on the x axis
    win.blit(textSurface, (x, y))


#----------------------------------------------------------#
# function that blits(draws) the cards onto the screen     #
#----------------------------------------------------------#
def drawCards(userCards, dealerCards, cardDeckUnedited, used):
    global Xu, Yu, Xd, Yd # global statments
    X = 478
    Y = 391
    X2 = 478
    Y2 = 95
    if gameOver: # if game is over, blit all their cards in correct position
        for c in userCards:
            win.blit(images[cardDeckUnedited.index(c)], (X, Y))
            X += 15
            Y -= 8
        for c in dealerCards:
            win.blit(images[cardDeckUnedited.index(c)], (X2, Y2))
            X2 += 15
            Y2 -= 8
    else:
        for c in userCards: # for loop for all of users cards
            if c not in used: # checks if card is already blited or not
                win.blit(images[cardDeckUnedited.index(c)], (Xu, Yu))
                Xu += 15
                Yu -= 8
                used.append(c)
            else:
                win.blit(images[cardDeckUnedited.index(c)], (X, Y))
                X += 15
                Y -= 8
        for c in dealerCards: # for loop for all of dealers cards
            if c not in used: # checks if card is already blited or not
                if len(playerDecksList) != 4 and playerMove == 's':
                    win.blit(images[cardDeckUnedited.index(c)], (Xd, Yd))
                Xd += 15
                Yd -= 8
                used.append(c)
            else:
                if playerMove != 's': # blits one card and a card back as a hidden card
                    win.blit(images[cardDeckUnedited.index(dealerCards[0])], (X2, Y2))
                    X2 += 15
                    Y2 -= 8
                    win.blit(images[54], (X2, Y2))
                    break
                else: # blits normally if user stands
                    win.blit(images[cardDeckUnedited.index(c)], (X2, Y2))
                    X2 += 15
                    Y2 -= 8


#------------------------------------------------------#
# function that puts all needed images into a list     #
#------------------------------------------------------#
def loadImages():
    images = []
    for card in range(len(cardDeck)): # for loop get put all the card images into the list
        fileName = cardDeck[card] + '.png'
        images.append(pygame.image.load(fileName))
    # adding other images to the list
    images.append(pygame.image.load('feltStart.jpg'))  # i 52
    images.append(pygame.image.load('feltGame.png'))   # i 53
    images.append(pygame.image.load('gray_back.png'))  # i 54
    images.append(pygame.image.load('acessmall.png'))  # i 55
    images.append(pygame.image.load('spade.png'))      # 1 56
    return images


#-------------------------------------------#
# function that draws rectangle buttons     #
#-------------------------------------------#
def drawButton(win, text, r, bColor, fColor, font):
    pygame.draw.rect(win, bColor, r)
    pygame.draw.rect(win, fColor, r, 3)
    txtSurface = font.render(text, True, fColor)
    win.blit(txtSurface, (r[0] + (r[2] - txtSurface.get_width()) // 2, r[1] + (r[3] - txtSurface.get_height()) // 2))


#--------------------------------------------------#
# function that draws the multiple buttons at once #
#--------------------------------------------------#
def drawMultipleButtons(win, buttons, textList):
    for i, r in enumerate(buttons):
        drawButton(win, textList[i], r, buttonColour, BLACK, defaultFont)


#-----------------------------------------------------------------#
# function that checks what button you clicked on (rect buttons)  #
#-----------------------------------------------------------------#
def getButtonIndex(bList, mp):
    for i, r in enumerate(bList):
        if pygame.Rect(r).collidepoint(mp):
            return i
    return -1


#------------------------------------#
# function that reads a txt file     #
#------------------------------------#
def readFiles(fileName):
    file = []
    fi = open(fileName + '.txt', 'r')
    for line in fi:
        file.append(line.strip())
    return file


#------------------------------------#
# function that edits a txt file     #
#------------------------------------#
def editFiles(fileName, edit):
    open(fileName + '.txt', 'w').close()
    open(fileName + '.txt', "a").write(str(edit))


#------------------------------------------------------#
# function that puts a display box onto the screen     #
#------------------------------------------------------#
def display_box(screen, message, box_color):
    'Print a message in a box in the middle of the screen'
    if len(message) != 0:
        fontobject = pygame.font.Font(None, 18)
        message_surface = fontobject.render(message, 1, BLACK)
        recWidth = message_surface.get_width() + 10
        if recWidth < 200:
            recWidth = 200
    else:
        recWidth = 200
    pygame.draw.rect(screen, box_color,
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 15,
                      recWidth, 30), 0)
    pygame.draw.rect(screen, BLACK,
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 15,
                      recWidth, 30), 1)
    if len(message) != 0:
        screen.blit(message_surface,
                    ((screen.get_width() / 2) - 95, (screen.get_height() / 2) - 8))
    pygame.display.flip()


#--------------------------------------------------------------------------------#
# function where you can type into the display box and return what was typed     #
#--------------------------------------------------------------------------------#
def ask(win, question, box_color):
    global capsOn, VALID_KEYS, vol, money, bet #global statments
    'ask(screen, question) -> answer'
    pygame.font.init() # init pygame font
    current_string = []
    display_box(win, question + ": " + ''.join(current_string), box_color)
    enteringText = True
    while enteringText: #while youre typing into box
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if currentScreen == MONEY_SCREEN: #make money = exit, so the program can exit properly
                        money = 'exit'
                        return money
                    elif currentScreen == BET_SCREEN: #make bet = exit, so the program can exit properly
                        bet = 'exit'
                        return bet
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT: # changes volume of music while typing in display box, and saving it
                    if event.key == pygame.K_UP:
                        vol += 0.1
                        if vol > 0.5:
                            vol = 0.5
                        mixer.music.set_volume(0.5 + vol)
                    if event.key == pygame.K_DOWN:
                        vol -= 0.1
                        if vol < -0.5:
                            vol = -0.5
                        mixer.music.set_volume(0.5 + vol)
                    if event.key == pygame.K_RIGHT:
                        mixer.music.pause()
                    if event.key == pygame.K_LEFT:
                        mixer.music.unpause()
                    editFiles('Volume', vol)
                if event.key == K_LSHIFT or event.key == K_RSHIFT:
                    capsOn = True
                if event.key == K_BACKSPACE:
                    current_string = current_string[0:-1]
                if event.key == K_RETURN:
                    enteringText = False
                if chr(event.key) in VALID_KEYS:
                    inkeyLtr = chr(event.key)
                    if capsOn:
                        inkeyLtr = inkeyLtr.upper()
                    current_string.append(inkeyLtr)
            if len(current_string) > 20: #checks if string is too long and blocks from it growing
                current_string = current_string[0:-1]
            if event.type == pygame.KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT:
                    capsOn = False
            if event.type == pygame.MOUSEBUTTONDOWN: # checks if button is clicked and does proper outputs
                clickPos = pygame.mouse.get_pos()
                if pygame.Rect((800, 32, 175, 85)).collidepoint(clickPos): #checks for back button clicked
                    if currentScreen == MONEY_SCREEN:
                        money = 'back'
                        return money
                    elif currentScreen == BET_SCREEN:
                        bet = 'back'
                        return bet
                elif pygame.Rect((win.get_width()//2 - 60, 363, 120, 75)).collidepoint(clickPos) and currentScreen == BET_SCREEN: # checks rebet button clicked
                    if rebet == 0:
                        blitText('You cannot rebet', 40, 650, 273, center=False)
                        blitText('on your first turn.', 40, 650, 323, center=False)
                    if rebet > money:
                        blitText('You cannot afford', 40, 650, 273, center=False)
                        blitText('to rebet.', 40, 650, 323, center=False)
                    else:
                        return str(rebet)
        display_box(win, question + ''.join(current_string), box_color)
    return ''.join(current_string)


#-------------------------------------------------------------------#
# function that uses ask and display box to get the value inputted  #
#-------------------------------------------------------------------#
def inputBox(question, box_color):
    input = (ask(win, question + ': ', box_color))
    return input


win = pygame.display.set_mode((1024, 640)) # sets window
cardDeck = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', 'JS', 'QS', 'KS', # sets card deck used for game
            'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '10C', 'JC', 'QC', 'KC',
            'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '10H', 'JH', 'QH', 'KH',
            'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', 'JD', 'QD', 'KD']
cardDeckUnedited = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', 'JS', 'QS', 'KS', # sets card deck used for indexes (like for blitting images), this is static and wont be changed
                    'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '10C', 'JC', 'QC', 'KC',
                    'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '10H', 'JH', 'QH', 'KH',
                    'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', 'JD', 'QD', 'KD']
vol = readFiles('Volume')[0] # gets the volume file for the volume variable
vol = float(vol) # formats variable in proper form (float)
mixer.music.set_volume(0.5 + vol) # sets music volume
mixer.music.play(loops=-1) # plays music in loop
buttonColour = readFiles('buttonColours')[0] # gets the button colour file for the colour of all the buttons on the game
buttonColour = eval(buttonColour) # formats variable in proper form
SEToggle = readFiles('se')[0] # reads file if sound effects are on or off
images = loadImages()
pygame.display.set_caption('Blackjack')
pygame.display.set_icon(images[56])
#initializing all variables in the game
money = 0
bet = 0
rebet = 0
startMoney = 0
Xu = 478
Yu = 391
Xd = 478
Yd = 95
turnCount = 0
ACountUser = 0
ACountDealer = 0
hitCount = 0
moneyCounter = 0
insAmount = 0
insIndex = -1
cp = 0
scores = [0, 0]
playedCards = []
playerDecksList = []
userCards = []
dealerCards = []
used = []
playerMove = ''
counter = 4
t = 0 #timer1
t2 = 0 # timer2
soundCounter = 0
insure = False
insureOver = False
insFail = False
NotEnoughDD = False
HS = False
playerDecks(playerDecksList, cardDeck)
cardValues(playerDecksList, hitCount, cp, scores)
deckPrint(playerDecksList, playerMove)
#checking for insurance
if playerDecksList[0][0] == 'A':
    insure = True
#checking for double aces and fixing the scores
if playerDecksList[0][0] == 'A' and playerDecksList[1][0] == 'A':
    scores[0] -= 10
    ACountDealer -= 1
if playerDecksList[2][0] == 'A' and playerDecksList[3][0] == 'A':
    scores[1] -= 10
    ACountUser -= 1
instr = readFiles('rules') #list of instructions from txt file
# text on buttons
startList = ['Play', 'Instructions', 'Button Colours', 'Sound Effects']
instrList = ['Back', 'More Info']
HSDList = ['Hit', 'Stand', 'Double Down']
HSList = ['Hit', 'Stand']
yornList = ['Yes', 'No']
exitList = ['Exit', 'Play Again']
SEList = ['ON', 'OFF', 'Back']
# button locations/sizes
buttonsStart = ((win.get_width() // 4 - 120, 285, 240, 100), (win.get_width() // 2 + win.get_width() // 4 - 120, 285, 240, 100),(760, 485, 220, 70), (44, 485, 220, 70))
buttonsInstr = ((50, 50, 175, 115), (799, 50, 175, 115))
buttonsIns = ((786, 315, 90, 60), (886, 315, 90, 60))
buttonsEnd = ((52, 315, 90, 60), (152, 315, 90, 60))
buttonsHSD = ((50, 540, 200, 75), (412, 540, 200, 75), (774, 540, 200, 75))
buttonsHS = (((win.get_width() // 2) - 200 - 140, 540, 200, 75), ((win.get_width() // 2) + 140, 540, 200, 75))
buttonsExit = ((win.get_width() // 2 - 400, win.get_height() // 2 - 75, 300, 150),(win.get_width() // 2 + 100, win.get_height() // 2 - 75, 300, 150))
buttonsChangeColour = ((30, win.get_height() // 2 - 75, 250, 150), (392, win.get_height() // 2 - 75, 250, 150),(754, win.get_height() // 2 - 75, 250, 150), (55, 108, 120, 70))
buttonsSE = ((win.get_width()//2-350, win.get_height() // 2 - 75, 250, 150), (win.get_width()//2 + 100, win.get_height() // 2 - 75, 250, 150), (30, 108, 120, 70))
# screens
START_SCREEN = 1
INST_SCREEN = 2
GAME_SCREEN = 3
MONEY_SCREEN = 4
BET_SCREEN = 5
GG_SCREEN = 6
BUTTONS_SCREEN = 7
SE_SCREEN = 8
currentScreen = START_SCREEN
end = False
gameOver = False
inPlay = True
while inPlay:
    redraw_game_window(currentScreen)
    pygame.time.delay(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            inPlay = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                inPlay = False
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                if event.key == pygame.K_UP: #turn volume up
                    vol += 0.1
                    if vol > 0.5:
                        vol = 0.5
                    mixer.music.set_volume(0.5 + vol)
                if event.key == pygame.K_DOWN: #turn volume down
                    vol -= 0.1
                    if vol < -0.5:
                        vol = -0.5
                    mixer.music.set_volume(0.5 + vol)
                if event.key == pygame.K_RIGHT: #pause music
                    mixer.music.pause()
                if event.key == pygame.K_LEFT: #unpause music
                    mixer.music.unpause()
                editFiles('Volume', vol) #edit the file holding the volume to the new value
        if event.type == pygame.MOUSEBUTTONDOWN:
            clickPos = pygame.mouse.get_pos()
            if currentScreen == START_SCREEN:
                bIndex = getButtonIndex(buttonsStart, clickPos)
                #buttons on start screen to take to the following screens:
                if bIndex == 0:
                    currentScreen = MONEY_SCREEN
                elif bIndex == 1:
                    currentScreen = INST_SCREEN
                elif bIndex == 2:
                    currentScreen = BUTTONS_SCREEN
                elif bIndex == 3:
                    currentScreen = SE_SCREEN
            elif currentScreen == INST_SCREEN:
                bIndex = getButtonIndex(buttonsInstr, clickPos)
                if bIndex == 0:
                    if bet == 'back':
                        currentScreen = BET_SCREEN
                        bet = 0
                    else:
                        currentScreen = START_SCREEN
                elif bIndex == 1:
                    webbrowser.open('https://www.888casino.com/blog/blackjack-strategy-guide/how-to-play-blackjack') #opens a website for more info
            elif currentScreen == GAME_SCREEN:
                if gameOver:
                    PAIndex = getButtonIndex(buttonsEnd, clickPos)
                    if PAIndex == 0:
                        if money < 1:
                            currentScreen = GG_SCREEN
                        else:
                            currentScreen = BET_SCREEN
                            #resets variables for each round
                            cardDeck = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', 'JS', 'QS', 'KS',
                                        'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '10C', 'JC', 'QC', 'KC',
                                        'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '10H', 'JH', 'QH', 'KH',
                                        'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', 'JD', 'QD', 'KD']
                            bet = 0
                            Xu = 478
                            Yu = 391
                            Xd = 478
                            Yd = 95
                            turnCount = 0
                            ACountUser = 0
                            ACountDealer = 0
                            hitCount = 0
                            moneyCounter = 0
                            insAmount = 0
                            insIndex = -1
                            cp = 0
                            scores = [0, 0]
                            playedCards = []
                            playerDecksList = []
                            userCards = []
                            dealerCards = []
                            used = []
                            playerMove = ''
                            counter = 4
                            t = 0
                            t2 = 0
                            soundCounter = 0
                            insureOver = False
                            insFail = False
                            NotEnoughDD = False
                            HS = False
                            end = False
                            gameOver = False
                            playerDecks(playerDecksList, cardDeck)
                            cardValues(playerDecksList, hitCount, cp, scores)
                            deckPrint(playerDecksList, playerMove)
                            if playerDecksList[0][0] == 'A':
                                insure = True
                            if playerDecksList[0][0] == 'A' and playerDecksList[1][0] == 'A':
                                scores[0] -= 10
                                ACountDealer -= 1
                            if playerDecksList[2][0] == 'A' and playerDecksList[3][0] == 'A':
                                scores[1] -= 10
                                ACountUser -= 1
                    elif PAIndex == 1:
                        currentScreen = GG_SCREEN
                elif insure:
                    insIndex = getButtonIndex(buttonsIns, clickPos)
                elif not insure and insAmount == 0 and max(scores) != 21 and turnCount == 0 and not NotEnoughDD:
                    HSDIndex = getButtonIndex(buttonsHSD, clickPos)
                    if HSDIndex == 0:
                        playerMove = 'h'
                        playerTurn()
                    if HSDIndex == 1:
                        playerMove = 's'
                        playerTurn()
                    if HSDIndex == 2:
                        playerMove = 'd'
                        playerTurn()
                elif not insure and insAmount == 0 or turnCount > 0 or NotEnoughDD:
                    HSIndex = getButtonIndex(buttonsHS, clickPos)
                    if HSIndex == 0:
                        playerMove = 'h'
                        playerTurn()
                    if HSIndex == 1:
                        playerMove = 's'
                        playerTurn()
            elif currentScreen == GG_SCREEN:
                if end and pygame.Rect((win.get_width() // 2 - 150, win.get_height() // 2 - 75, 300, 150)).collidepoint(clickPos):
                    inPlay = False
                elif not end:
                    GGIndex = getButtonIndex(buttonsExit, clickPos)
                    if GGIndex == 0:
                        inPlay = False
                    elif GGIndex == 1:
                        currentScreen = START_SCREEN
                        #resets ALL variables
                        cardDeck = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', 'JS', 'QS', 'KS',
                                    'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '10C', 'JC', 'QC', 'KC',
                                    'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '10H', 'JH', 'QH', 'KH',
                                    'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', 'JD', 'QD', 'KD']
                        money = 0
                        bet = 0
                        rebet = 0
                        startMoney = 0
                        Xu = 478
                        Yu = 391
                        Xd = 478
                        Yd = 95
                        turnCount = 0
                        ACountUser = 0
                        ACountDealer = 0
                        hitCount = 0
                        moneyCounter = 0
                        insAmount = 0
                        insIndex = -1
                        cp = 0
                        scores = [0, 0]
                        playedCards = []
                        playerDecksList = []
                        userCards = []
                        dealerCards = []
                        used = []
                        playerMove = ''
                        counter = 4
                        t = 0
                        t2 = 0
                        soundCounter = 0
                        insure = False
                        insureOver = False
                        insFail = False
                        NotEnoughDD = False
                        HS = False
                        end = False
                        gameOver = False
                        playerDecks(playerDecksList, cardDeck)
                        cardValues(playerDecksList, hitCount, cp, scores)
                        deckPrint(playerDecksList, playerMove)
                        if playerDecksList[0][0] == 'A':
                            insure = True
                        if playerDecksList[0][0] == 'A' and playerDecksList[1][0] == 'A':
                            scores[0] -= 10
                            ACountDealer -= 1
                        if playerDecksList[2][0] == 'A' and playerDecksList[3][0] == 'A':
                            scores[1] -= 10
                            ACountUser -= 1
            elif currentScreen == BUTTONS_SCREEN:
                bIndex = getButtonIndex(buttonsChangeColour, clickPos)
                #check what colour button was pressed
                if bIndex != -1:
                    if bIndex == 0:
                        buttonColour = RED
                    elif bIndex == 1:
                        buttonColour = DARK_GREEN
                    elif bIndex == 2:
                        buttonColour = BLUE
                    editFiles('buttonColours', buttonColour) #replace the button colour file with the new colour
                    currentScreen = START_SCREEN
            elif currentScreen == SE_SCREEN:
                bIndex = getButtonIndex(buttonsSE, clickPos)
                #check if the sound effect toggle is on or off from a button press
                if bIndex != -1:
                    if bIndex == 0:
                        SEToggle = 'yes'
                    elif bIndex == 1:
                        SEToggle = 'no'
                    editFiles('se', SEToggle) #edit the se file with the new value
                    currentScreen = START_SCREEN
        elif currentScreen == MONEY_SCREEN:
            if money == 'back':
                currentScreen = START_SCREEN
                money = 0
            elif startMoney > 0:
                currentScreen = BET_SCREEN
        elif currentScreen == BET_SCREEN:
            if bet == 'back':
                currentScreen = INST_SCREEN
            elif bet > 0:
                currentScreen = GAME_SCREEN

pygame.quit() #always quit when done
