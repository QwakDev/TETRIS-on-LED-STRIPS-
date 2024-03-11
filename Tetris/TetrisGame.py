import libs.Pixel.example.opc
import time
import random
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START constants (17)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#list of block colours: 0-GREEN 1-RED 2-YELLOW 3=PURPLE 
col_ListBlocks = [(0,255,0),(255,0,0),(255,255,0),(0,255,255)]
#list of animation colours: 0-LightBlue 1-Blue 2-DarkBlue
col_ListAnimations = [(255,0,255),(0,0,255),(0,0,125)]
#DefColour (black)
col_def = (0 ,0, 0)
col_lightGrey = (200,200,200)
col_darkGrey = (150,150,150)
col_loseWall= (60,60,60)
col_warrning = (255,135,75)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END Constants
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START Enviroment(Game Grid, Menu, Controls)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------


#GLOBAL DATA
#TetrisGame
gameOn = False
isLost = False
#MenuEnviroment
programOn = True




#list of static blocks
staticBlocks = [False]*360
staticElements = []

#GAME GRID


#setting "background", all LEDS turn white
led_colour = [col_def] *360

#strip ranges
#strip1 0-59
#strip1 60-119
#strip1 120-179
#strip1 180-239
#strip1 240-299
#strip6 300-359

#GAME MENU
def ShowHelp():
    print("MenuCommands:")
    print("Write 'START' to start the game")
    print("Write 'EXIT' to close the application")
    print("Write 'HELP' to see all commands")
    
    print("GameCommands:")
    print("Write 'W' to move up")
    print("Write 'S' to move down")
    print("Write 'A' to rotate")
    print("Write 'D' to get new block of blocks")
    print("Write 'EXIT' to get back to Menu")
    print("Write 'RESTART' to Restart the game")
    print("Write 'HELP' to see all commands")

def ShowMenu():
    print("MENU")
    print("'START' - PLAY")
    print("'EXIT' - CLOSE")
    print("'HELP' - HELP")
    

def GetInput():
    if gameOn:
        print("GameInput: ")
    else:
        print("MenuInput: ")
    #setting input to uppercase so user can ignore using uppercase
    usrInput = input().upper()
    if usrInput == "HELP":
        ShowHelp()
    else:
        #if user plays the game
        if gameOn:
            GameInput(usrInput)
        else:
            MenuInput(usrInput)

#GAME CONTROLS
# W-up S-down A-rotate D-"approval" RESTART-restart EXIT-exit HELP-help
def GameInput(usrInput):
    if usrInput == 'W':
        MoveUpBlock()
    elif usrInput == 'S':
        MoveDownBlock()
        #down
    elif usrInput =='A':
        RotateBlock()
        #rotate
    elif usrInput == 'D':
        ApproveBlock()
        #approved
    elif usrInput == "RESTART":
        NewGame()
        #restart
    elif usrInput == "EXIT":
        CloseGame()
        #close
        CloseGame()
    elif usrInput == "HELP":
        ShowHelp()
    else:
        print("!Unrecognisied input in the GAME!")
        ShowHelp()

#MENU CONTROLS START-start game EXIT-close application HELP-show help
def MenuInput(usrInput):
    if usrInput == "START":
        NewGame()
    elif usrInput == "EXIT":
        global programOn
        CloseAppAnimation()
        programOn = False
    elif usrInput == "HELP":
        ShowHelp()
    else:
        print("!Unrecognisied input in the MENU!")
        ShowHelp()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END Enviroment(Game Grid, Menu, Controls)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START GAME LOGIC
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#array of "walls" for each strip, When block's next location is a "wall", block ==> Static block, change of BlockWall value
LoseWall = [7,67,127,187,247,307]

class StaticElement():
    RGB = (255,255,255)
    globalLocation = 0
    positionX = 0
    positionY = 0
    Freeze = 0
    def SetElement(self, x, y, RGB):
        self.positionX = x
        self.positionY = y
        self.globalLocation = TransformGamePosToLedPosition(x,y)
        self.RGB = RGB
        #debug print(self.globalLocation)
        staticBlocks[self.globalLocation] = True
        led_colour[self.globalLocation] = self.RGB
    #checks if its there is another element with the same location and is it within the grid led locations of 0-359
    def isUniqueAndPossible(self, x,y):
        global staticElements
        position = TransformGamePosToLedPosition(x,y)
        if position > 359 or position < 0:
            return False
        for el in staticElements:
            if el.globalLocation == position:
                return False
        return True
    #def isUniqueAndPossible(self, point):
    #    global staticElements
    #    if TransformGamePosToLedPosition(point.x,point.y) > 359 or TransformGamePosToLedPosition(point.x,point.y) < 0:
    #        return False
    #    for el in staticElements:
    #        if point.x == el.positionX and point.y == el.positionY:
    #            return False
    #   return True
    def MoveRight(self):
        if self.Freeze == 0:
            global led_colour
            global staticElements
            self.SetElement(self.positionX + 1, self.positionY, self.RGB)
            #check if other is not assigned to old location
            setDef = True
            for el in staticElements:
                if self.positionX - 1 == el.positionX and self.positionY == el.positionY:
                    setDef = False
            if setDef:
                led_colour[TransformGamePosToLedPosition(self.positionX -1, self.positionY)] = col_def
                staticBlocks[TransformGamePosToLedPosition(self.positionX -1, self.positionY)] = False
        else:
            self.Freeze = self.Freeze - 1

#grid is inverted around X axis for example point[2times to the right, 2times down] is (2,2) 
class Block:
    localX = 0
    localY = 0
    previousLocalX = 0
    previousLocalY = 0

    RGB = col_def

    def SetLocalPosition(self, x, y):
        self.previousLocalX = self.localX
        self.previousLocalY = self.localY
        #DEBUG 
        #print("prevX: ", self.previousLocalX, " prevY: ", self.previousLocalY, " newX: ", x, " newY: ", y)
        self.localX = x
        self.localY = y
    def SetRandomRGB(self):
        #creates new random so every time is gonna be new random number 
        ran = random.SystemRandom()
        a = ran.randint(0, 3)
        global col_ListBlocks
        self.RGB = col_ListBlocks[a]
    #Updates local position when not rotating
    def UpdateLocalPosition(self):
        self.SetLocalPosition(self.localX, self.localY)
    #Rotates 90* around point (0,0) $mainBlock
    def Rotate90(self):
        newX = self.localY
        newY = self.localX * (-1)
        self.SetLocalPosition(newX, newY)
#Class of block object which consists other blocks with (local location)
class BlockOfBlocks:
    positionX = 0
    positionY = 0
    previousPositionX = 0
    previousPositionY = 0
    BlockZero = Block()
    #list of blocks exluding block zero
    Blocks = []
    def SetPosition(self, x, y):
        self.previousPositionX = self.positionX
        self.previousPositionY = self.positionY
        self.positionX = x
        self.positionY = y
        #DEBUG print("PrevX: " , self.previousPositionX, " newX: ", self.positionX, " prevY: ", self.previousPositionY, " newY: ", self.positionY )

    def GenerateBlocks(self):
        self.BlockZero.SetRandomRGB()
        self.Blocks = []
        previousBlock = self.BlockZero
        #if X bigger than 2 stop the loop so the block of blocks will be always 3x length and max 2x height
        while True:
            y = random.randint(-1,1)
            newLocalY = previousBlock.localY + y
            newLocalX = previousBlock.localX

            if newLocalY == previousBlock.localY or newLocalY > 1 or newLocalY < 0:
                newLocalX = newLocalX + 1

            if newLocalX > 2:
                break
            else:
                if newLocalY > 1 :
                    newLocalY = 1
                if newLocalY < 0:
                    newLocalY = 0

                blockToBeAdded = Block()
                blockToBeAdded.SetLocalPosition(newLocalX, newLocalY)
                blockToBeAdded.previousLocalX = newLocalX
                blockToBeAdded.previousLocalY = newLocalY
                blockToBeAdded.SetRandomRGB()
                self.Blocks.append(blockToBeAdded)
                previousBlock = blockToBeAdded

    def GetMaxY(self):
        output = 0
        output = self.positionY
        for block in self.Blocks:
            if output< (block.localY + self.positionY):
                output = (block.localY + self.positionY)
        
        #DEBUG 
        #print("MAX ",output)
        return output

    def GetMinY(self):
        output = 5
        output = self.positionY
        for block in self.Blocks:
            if output> (block.localY + self.positionY):
                output = (block.localY + self.positionY)
        
        #DEBUG 
        #print("MIN ",output)
        return output

    def MoveUp(self):
        if self.GetMinY() > 0:
            self.SetPosition(self.positionX, (self.positionY - 1))
            #updating localPosition
            for block in self.Blocks:
                block.UpdateLocalPosition()
            self.Update()
            self.SetPosition(self.positionX, self.positionY)
        else:
            self.OutOfBorderNotification()

    def MoveDown(self):
        if self.GetMaxY() < 5:
            self.SetPosition(self.positionX, (self.positionY + 1))
            #updating localPosition
            for block in self.Blocks:
                block.UpdateLocalPosition()
            self.Update()
            self.SetPosition(self.positionX, self.positionY)
        else:
            self.OutOfBorderNotification()

    def RotateBlock(self):
        for block in self.Blocks:
            block.Rotate90()
        #if out of the border go to the previous state
        if self.GetMinY() > -1 and self.GetMaxY() < 6:
            self.Update()
        else:
            count = 0
            #called 3 times to rotateIt 270* so with 90* before it will give 360*(previous stage)
            while count < 3:
                count = count + 1
                for block in self.Blocks:
                    block.Rotate90() 
            self.OutOfBorderNotification()
            self.Update()
        for block in self.Blocks:
            block.SetLocalPosition(block.localX,block.localY)

    def ApproveThis(self):
        oldPositionX = self.positionX
        newPositionX = oldPositionX
        while self.MoveRight():
            newPositionX = newPositionX + 1
            continue

        self.MovementAnimation(oldPositionX, newPositionX)
        #self.ToListOfStaticElement()
        self.Update()
        global LoseWall
        
        #checking if any of the blocks are on the loseWall
        blocksPositions = []
        #adding blockZero
        blocksPositions.append(TransformGamePosToLedPosition(self.positionX, self.positionY))
        #Adding rest of the blocks
        for block in self.Blocks:
            blocksPositions.append(TransformGamePosToLedPosition(block.localX + self.positionX, block.localY + self.positionY))
        for loc in LoseWall:
            for blockLoc in blocksPositions:
                if loc == blockLoc:
                    global isLost
                    isLost = True
        

    def MoveRight(self):
        possible = True
        global staticElements
        self.positionX = self.positionX + 1
        
        #check if movmentPossible if hits staticElement notPossible
        #checkBlockZero
        for el in staticElements:
            if el.globalLocation == TransformGamePosToLedPosition(self.positionX, self.positionY):
                possible = False
        #checkLocalBlocks
        for block in self.Blocks:
            globalBlockPos = TransformGamePosToLedPosition(block.localX + self.positionX, block.localY + self.positionY)
            for el in staticElements:
                if el.globalLocation == globalBlockPos:
                    possible = False
        #Back the position    
        if possible == False:
            self.positionX = self.positionX - 1
        return possible
    
    def ToListOfStaticElement(self):
        output = []
        newStatic = StaticElement()
        newStatic.SetElement(self.positionX, self.positionY, self.BlockZero.RGB)
        output.append(newStatic)

        for block in self.Blocks:
            newStatic = StaticElement()
            newStatic.SetElement(self.positionX + block.localX, self.positionY + block.localY, block.RGB)
            output.append(newStatic)

        return output

    def OutOfBorderNotification(self):
        WrongInputAnimation()
        #debug 
        #print("OutOFBorders")
    #Updates the LEDs 
    def Update(self):
        global led_colour
        #sets LEDs to def for previous position of the block
        led_colour[TransformGamePosToLedPosition(self.previousPositionX, self.previousPositionY)] = col_def
        for block in self.Blocks:
            #sets LEDs to def for previous position of the block
            led_colour[TransformGamePosToLedPosition(self.previousPositionX + block.previousLocalX, self.previousPositionY + block.previousLocalY)] = col_def
            #debug
            #print("OLD LED: ",TransformGamePosToLedPosition(self.previousPositionX + block.previousLocalX, self.previousPositionY + block.previousLocalY), " NEW LED: ",TransformGamePosToLedPosition(self.positionX + block.localX, self.positionY + block.localY))
        #glows new position
        led_colour[TransformGamePosToLedPosition(self.positionX, self.positionY)] = self.BlockZero.RGB 
        for block in self.Blocks:
            #glows new position
            led_colour[TransformGamePosToLedPosition(self.positionX + block.localX, self.positionY + block.localY)] = block.RGB
    
    def MovementAnimation(self, oldX, toX):
        #number of movments
        count = oldX
        self.SetPosition(oldX, self.positionY)

        while not count == toX:
            count = count + 1 
            self.SetPosition(count, self.positionY)
            #animation execution
            #Basic Movment
            self.Update()
            #adding tail ( works only after lose wall)

            #CHECKING IF THE PREVIOUS LOC OF THE BLOCK IS A LOSE WALL if yes set it to darkGrey so the loseWall stays 
            global led_colour
            global LoseWall
            prevPos = TransformGamePosToLedPosition(self.previousPositionX, self.previousPositionY)
            match = False
            for el in LoseWall:
                if el == prevPos:
                    match = True
            if match:
                led_colour[prevPos] = col_darkGrey
            #checking for every local block
            for block in self.Blocks:
                block.SetLocalPosition(block.localX,block.localY)
                prevPos = TransformGamePosToLedPosition(self.previousPositionX + block.previousLocalX, self.previousPositionY + block.localY)
                match = False
                for el in LoseWall:
                    if el == prevPos:
                        match = True
                if match:
                    led_colour[prevPos] = col_darkGrey

            Refresh()
            time.sleep(0.075)
        

newBlock = BlockOfBlocks()
def NewGame():
    global gameOn
    global staticBlocks
    global staticElements
    global isLost
    NewGameAnimation()
    time.sleep(5)
    GameResetAnimation()
    gameOn = True
    isLost = False
    ResetAllLeds()
    staticBlocks = [False]*360
    #[60,120,180,240,360]
    #Setting Up the staticBlockWall
    count = 0
    staticElements = []
    while count < 6:
        newElement = StaticElement()
        newElement.SetElement(59,count,col_darkGrey)
        count = count + 1
        staticElements.append(newElement)
    global led_colour
    #settingUp the LoseWall
    for el in LoseWall:
        led_colour[el] = col_darkGrey
    
    CreateNewBlock()
    Refresh()
    
    #debug print(staticBlocks)
    #game Menu
    
    print("TETRIS GAME")
    print("WRITE 'HELP' TO SEE CONTROLS AND OTHER COMMANDS")

def GameLost():
    print("U lose")

def CloseGame():
    global gameOn
    NewGame()
    gameOn = False
    ShowMenu()
    ResetAllLeds()
    print("callled")

def CreateNewBlock():
    global newBlock
    newBlock = BlockOfBlocks()
    newBlock.SetPosition(3,2)
    newBlock.previousPositionX = 3
    newBlock.previousPositionY = 2
    newBlock.GenerateBlocks()
    newBlock.Update()

def RotateBlock():
    global newBlock
    newBlock.RotateBlock()

def MoveUpBlock():
    global newBlock
    newBlock.MoveUp()

def MoveDownBlock():
    global newBlock
    newBlock.MoveDown()

def ApproveBlock():
    global newBlock
    global staticElements
    global isLost
    newBlock.ApproveThis()
    sta = newBlock.ToListOfStaticElement()
    for el in sta:
        alreadyExists = False
        #checks if static element already exists
        for sEl in staticElements:
            if el.positionY == sEl.positionY and el.positionX == sEl.positionX:
                alreadyExists = True
        #if it doesnt exists add to the list of static elements
        if not alreadyExists:
            staticElements.append(el)
    #debug
    #for el in staticElements:
    #    if not el.positionX == 59:
    #        print("static: ", el.positionX, " ", el.positionY)
    FullColumnCheck()
    if not isLost:
        CreateNewBlock()
    else:
        GameLost()

def FullColumnCheck():
    global staticElements
    for el in staticElements:
        #check if rest of the elements are in the collumn
        elementsInTheCollumn = 1
        if el.positionY == 0 and not el.positionX == 59:
            for resEl in staticElements:
                if resEl.positionX == el.positionX and not resEl.positionY == el.positionY:
                    elementsInTheCollumn = elementsInTheCollumn + 1
        if elementsInTheCollumn > 5:
            DeleteCollumn(el.positionX)

def DeleteCollumn(x):
    #find all static elements in collumn x
    global staticElements
    elementsToBeDel = []

    for el in staticElements:
        if el.positionX == x:
            elementsToBeDel.append(el)
    for el in elementsToBeDel:
        listOfOneEl = []
        listOfOneEl.append(el.globalLocation)
        FadeOut(listOfOneEl, el.RGB)
        staticElements.remove(el)
    for el in staticElements:
        if el.positionX < x:
            el.MoveRight()
    #check new matches
    FullColumnCheck()

            


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END  GAME LOGIC
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START ANIMATIONS
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# LightUp Orange collumn of LEDs
def WrongInputAnimation():
    #global led_colour
    strip = [0,60,120,180,240,300]
    FadeOut(strip, col_warrning)
    #OLD CODE
    #for loc in strip:
    #   led_colour[loc] = orange
    #Refresh()
    #time.sleep(0.5)
    #for loc in strip:
     #   led_colour[loc] = defColour
    #Refresh()
#FADE OUT ANIMATION
def FadeOut(listOfLeds, fromColour):
    global led_colour
    #DEBUG
    #print(fromColour)
    #set Leds to entry colour
    for loc in listOfLeds:
        led_colour[loc] = fromColour
    
    nextColour = list(fromColour)

    while not nextColour == [0,0,0]:
        if nextColour[0] > 0:
            nextColour[0] = nextColour[0] - 1
        if nextColour[1] > 0:
            nextColour[1] = nextColour[1] - 1
        if nextColour[2] > 0:
            nextColour[2] = nextColour[2] - 1  
        nextColTuple = (nextColour[0],nextColour[1],nextColour[2])
        for loc in listOfLeds:
            led_colour[loc] = nextColTuple
        
        #DEBUG print(nextColTuple)
        Refresh()
        time.sleep(0.006)


def NewGameAnimation():
    global staticElements
    global LoseWall
    global led_colour
    staticElements = []
    #create 6 static objects with random sizes 2-4 and random deleys 0-5
    count = 0 
    while count<6:
        size = random.randint(3,6)
        deley = random.randint(0,15)
        inter = 0
        while size > inter:
            element = StaticElement()
            element.SetElement(size,count,col_ListAnimations[2])
            element.Freeze = deley
            staticElements.append(element)
            size = size - 1
        count = count + 1
    Refresh()
    while len(staticElements) > 0:
        time.sleep(0.1)

        for el in staticElements:
            point = Point()
            point.x = el.positionX + 1
            point.y = el.positionY
            
            if point.IsInBorders():
                el.MoveRight()
            else:
                led_colour[el.globalLocation] = col_darkGrey
                staticElements.remove(el)
            for loseWallEl in LoseWall:
                if TransformGamePosToLedPosition(point.x - 1, point.y) == loseWallEl:
                    led_colour[loseWallEl] = col_darkGrey
        Refresh()
    #move them


def GameResetAnimation():
    global staticElements
    
    staticElements = []
    #if moveLeft outOf border destroy element
    def CreateLine(long):
        count = 0
        while count<long:

            element = StaticElement()
            element.SetElement(0,5-count, col_ListAnimations[1])
            count = count + 1
            staticElements.append(element)
           #debug print("ok")
    #move right static element
    #create a line(11)
    count = 1
    numberOfElements = 0
    while count<12:
        
        #move all existing elements right

        for el in staticElements:
            point = Point()
            point.x = el.positionX + 1
            point.y = el.positionY
            if point.IsInBorders:
                el.MoveRight()
            else:
                staticElements.remove(el)
                #debug print("WWW")
        if count < 7:
            numberOfElements = numberOfElements + 1
            CreateLine(numberOfElements)
            #increasing 
        if count > 6:
            numberOfElements = numberOfElements - 1
            CreateLine(numberOfElements)
            #decresing
            
        count = count + 1
        
        Refresh()
        time.sleep(0.1)
    #debug print(len(staticElements))
    #move Wave to right and destroy 
    while len(staticElements) > 0:
        time.sleep(0.1)

        for el in staticElements:
            point = Point()
            point.x = el.positionX + 1
            point.y = el.positionY
            if point.IsInBorders():
                el.MoveRight()
            else:
                global led_colour
                led_colour[el.globalLocation] = col_def
                staticElements.remove(el)
        Refresh()
        
                #debug print("WWW")
         

        
class Point:
        x = 0
        y = 0
        def Up(self):
            self.y = self.y - 1
        def Down(self):
            self.y = self.y + 1
        def Right(self):
            self.x = self.x + 1
        def Left(self):
            self.x = self.x - 1
        def IsInBorders(self):
            pos = TransformGamePosToLedPosition(self.x, self.y)
            #debug print(pos)
            if pos<0 or pos>359 or pos == 60 or pos == 120 or pos == 180 or pos == 240 or pos == 300:
                return False
            else:
                return True

def CloseAppAnimation():
    global led_colour
    global staticElements
    # Middle 0-59
    staticElements = []
    count = 0

    #starting points
    
    
    #SETTING UP POINTS
    #left
    pLeft = Point()
    pLeft.x = 29
    pLeft.y = -1
    #right
    pRight = Point()
    pRight.x = 30
    pRight.y = -1
    while count < 300:
        element = StaticElement()

        #moving down both points
        pLeft.Down()
        pRight.Down()
        #generating new element right side
        # DOWN RIGHT UP LEFT
        if element.isUniqueAndPossible(pRight.x, pRight.y):
            element.SetElement(pRight.x, pRight.y, col_ListAnimations[0])
            staticElements.append(element)
        else:
            #back ToThePreviousPossition and LEFT
            pRight.Up()
            pRight.Right()
            if element.isUniqueAndPossible(pRight.x, pRight.y):
                element.SetElement(pRight.x, pRight.y, col_ListAnimations[0])
                staticElements.append(element)
            else:
                pRight.Left()
                pRight.Up()
                if element.isUniqueAndPossible(pRight.x, pRight.y):
                    element.SetElement(pRight.x, pRight.y, col_ListAnimations[0])
                    staticElements.append(element)
                else:
                    pRight.Down()
                    pRight.Left()
                    if element.isUniqueAndPossible(pRight.x, pRight.y):
                        element.SetElement(pRight.x, pRight.y, col_ListAnimations[0])
                        staticElements.append(element)
                    else:
                        pRight.Right()

        element = StaticElement()
        #generating new element left side
        #DOWN LEFT UP RIGHT
        if element.isUniqueAndPossible(pLeft.x, pLeft.y):
            element.SetElement(pLeft.x, pLeft.y, col_ListAnimations[1])
            staticElements.append(element)
        else:
            #back ToThePreviousPossition and LEFT
            pLeft.Up()
            pLeft.Left()
            if element.isUniqueAndPossible(pLeft.x, pLeft.y):
                element.SetElement(pLeft.x, pLeft.y, col_ListAnimations[1])
                staticElements.append(element)
            else:
                pLeft.Right()
                pLeft.Up()
                if element.isUniqueAndPossible(pLeft.x, pLeft.y):
                    element.SetElement(pLeft.x, pLeft.y, col_ListAnimations[1])
                    staticElements.append(element)
                else:
                    pLeft.Down()
                    pLeft.Right()
                    if element.isUniqueAndPossible(pLeft.x, pLeft.y):
                        element.SetElement(pLeft.x, pLeft.y, col_ListAnimations[1])
                        staticElements.append(element)
                    else:
                        pLeft.Left()
                        #outOfLEDS
                        break

        Refresh()
        time.sleep(0.04)
        count = count + 1
    def sixtyRanLocations():
        output = []
        count = 0
        while count<60:
            ran = random.randint(0,len(staticElements) - 1)
            toBeAdded = True
            for el in output:
                if staticElements[ran].globalLocation == el:
                    toBeAdded = False
                
            if toBeAdded:
                count = count + 1
                output.append(staticElements[ran].globalLocation)
                staticElements.remove(staticElements[ran])
        #debug print(len(staticElements))
        return output
    #FADING OUT ALL STATIC ELEMENTS (random 60 per time)
    while len(staticElements) > 59:
        FadeOut(sixtyRanLocations(), col_warrning)
    
    #debug print (len(staticElements))
    pass
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END ANIMATIONS
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START LEDs Control
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#transforms grid position x,y to LEDs position 
def TransformGamePosToLedPosition(x,y):
    output = 0
    output = output + x + (y*60)
    return output 

#SET ALL LEDS TO WHITE
def ResetAllLeds():
    global led_colour
    led_colour=[col_def]*360
    global client
    client.put_pixels(led_colour)

def Refresh():
    global led_colour
    global client
    client.put_pixels(led_colour)




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END  LEDs Control
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START MAIN
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------


#to use simulator
client = libs.Pixel.example.opc.Client('localhost:7890')
ResetAllLeds()
ShowMenu()
#as long as programOn is true
while programOn:
    #taking input from the user
    GetInput()
    #Refreshes LEDs once after the user's input 
    Refresh()


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END MAIN
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------


### TEMPLATE ###
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#START 
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------


#CODE


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#END 
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------