import pygame
import random
import math 
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
# This generates a random dungeon.

class DungeonGen:
    def __init__(self,game,level=1):

        self.game = game
        self.level = level
        self.level = 1
        self.cells = []
        self.cells_moved = []
        self.rooms = []
        self.roomsCentroids = []
        self.CompleteConnections = []
        self.ValidConnections = []
        self.allConnections = []
        self.corridor = []

        


    def generate(self,level,mean,std,origin,radius,res):
        noRooms = 90
        seed = int(random.random()*100000000)
        random.seed(seed)
        np.random.seed(seed)
        print(seed)
        # ,toplength,width
        for room in range(0,noRooms):
            #print('room',room)
            inCircle = 0
            #get point in a circle
            while inCircle == 0:
                point = [random.random()*res[0],random.random()*res[1]]
                dx = abs(point[0]-origin[0])
                dy = abs(point[1]-origin[1])
                dist = math.sqrt(dx**2+dy**2)
                #If in circle:
                if dist < radius:
                    inCircle = 1

            #END OF CIRCLE POINT 

            #Create Rect List
            WLRatio = 0
            while WLRatio == 0:
                width = np.random.normal(mean,std)
                length = np.random.normal(mean,std)
                aspectR = width/length
                if aspectR < 5 and aspectR > 0.2:
                    WLRatio = 1
            rect = pygame.Rect(point[0],point[1],width,length)
            if rect.height > 0 and rect.width > 0:
                self.cells.append(rect)
        
        return self.cells

        #END OF OVERLAPPING ROOM GEN



    def move_cells(self):
        max_move = 1
        while max_move > 0:
            max_move = -1
            #Separate rooms
            aIndex = -1
            for room1 in self.cells:
                aIndex += 1
                r1Cent = room1.center
                #THis is a list of the INDEXES not the rects directly.
                colliding = room1.collidelistall(self.cells)

                for cIndex in colliding:
                    room2 = self.cells[cIndex]
                    r2Cent = room2.center
                    #If centres match
                    if r2Cent == r1Cent:
                        room1.move(1,1)
                    else:
                    #Find vector 
                        vec = [r2Cent[0]-r1Cent[0],r2Cent[1]-r1Cent[1]]
                        vecMag = math.sqrt(vec[0]**2+vec[1]**2)
                        vec_norm = [math.ceil(vec[0]/vecMag),math.ceil(vec[1]/vecMag)]
                        room1 = room1.move(vec_norm[0]*-1,vec_norm[1]*-1)
                        room2 = room2.move(vec_norm[0],vec_norm[1])
                        #check if there is still movement.
                        max_move = max(vecMag,max_move)
                    
                    self.cells[aIndex] = room1
                    self.cells[cIndex] = room2
            #print(max_move)
                    

                #move squares in the opposite direction of the vector between them.
                #square 1:



        return self.cells

    def room_select(self):
        for cell in self.cells:
            #Criteria for cells.
            cWidth = cell.width
            cLength = cell.height
            cSize = cWidth*cLength
            aspectR = cWidth/cLength
            if cSize >= 400:
                if aspectR > 0.2 and aspectR < 5:
                    self.rooms.append(cell)                   
                    self.roomsCentroids.append(cell.center)

        return self.rooms, self.roomsCentroids
    

    def DelaunayTri(self):
        tri = Delaunay(self.roomsCentroids)
        
        return tri











    def MinSpanTree(self,tri):
        
        k=0
        #Min Edge Spanning.
        #random start point. (point w/ index 0)
        noRooms = len(self.roomsCentroids)

        #0. Vertex index, 1. connections, 3. weight (distance)
        
        #self.connectedPoints.append(self.pointIndex)


        triangles =tri.simplices

        


        #step 1: look at points connected to pointIndex0 and create an array of initial valid connections
        self.ValidConnections = self.find_connecting_points(0,triangles,self.CompleteConnections)
        self.allConnections.extend(self.ValidConnections)
        #Sort so the top is the lowest weight.
        self.ValidConnections.sort(key=lambda x:x[2])


#LOOP FROM HERE
        while len(self.ValidConnections) > 0:
            #step 2. look at ValidConnections and select lowest weight path that DOES NOT for a closed loop
            #Lowest weight connection:

            #we update updatedValidConnections so the for loop doesn't mess up.
            updatedValidConnections = self.ValidConnections.copy()

            for connection in self.ValidConnections:
                testConnection = connection
                #Test for closed loop:
                #a. start from testconnection[0] and see if you can get to testconnection[1] via complete connections.


                completeConnectionIndexList = []
                for finConnection in self.CompleteConnections:
                    #create a list of all self.CompleteConnection indexes
                    completeConnectionIndexList.append(finConnection[0])
                    completeConnectionIndexList.append(finConnection[1])
                

                #if testConnection[1] is in that list then it is NOT valid
                if testConnection[1] not in completeConnectionIndexList:
                    #step 3. add lowest weight path to self.Complete connections
                    X = updatedValidConnections[0]
                    self.CompleteConnections.append(X)
                    break
                else:
                    #remove connection
                    #print('Invalid connection!')
                    updatedValidConnections.pop(0)
                    a=1


            self.ValidConnections = updatedValidConnections.copy()
            
            


            #If no more connections then exit the while loop
            if len(self.ValidConnections) == 0:
                break

            #step 4. remove lowest weight path from self.ValidConnections.
            self.ValidConnections.pop(0)
            
            #step 5. find all connections to the point just added.
            index = self.CompleteConnections[-1][1]
            newValidConnections = self.find_connecting_points(index,triangles,self.CompleteConnections)
            self.allConnections.extend(newValidConnections)
            #step 6. add the connections to ValidConnections - miht need to remove some old possibilities but not sure yet. - I think I need something here to remove more
            #Backwards is not remove I think? (for example: [1 2] might be removed but [2 1] is not! They are identical so should be removed)
            self.ValidConnections.extend(newValidConnections)
            self.ValidConnections.sort(key=lambda x:x[2])
            #Finally sort 
            #repeat from step 2

            a=1



        #debug bit
            debug = 0
            if debug == 1:
                for i in range(len(self.CompleteConnections)):
                    ind = self.CompleteConnections[i]
                    pygame.draw.line(self.game.display,(0,255,0),(self.roomsCentroids[ind[0]][0],self.roomsCentroids[ind[0]][1]),(self.roomsCentroids[ind[1]][0],self.roomsCentroids[ind[1]][1]))



                self.game.screen.blit(pygame.transform.scale(self.game.display, self.game.screen.get_size()),(0,0))

                pygame.display.update()
                self.game.clock.tick(1)







        return self.CompleteConnections,self.roomsCentroids


    
    
    def find_connecting_points(self,refPoint,triangles,InvalidPoints):
        #input is the indexPoint
        #output is a list as follows:
        # [[refP,COnnecting point,weight],[...]]
        weightTable = []
        dist = []
        InvalidPointList = []

         #Go through every point and find the points connected.
        connectingTriangles = []
        connectingTrianglesIndex = []
        k=0
        for triang in triangles:
            exists = refPoint in triang                
            if exists:              
                connectingTrianglesIndex.append(k)
                connectingTriangles.append(triang)
            k+=1
    
        iterator = 0 
        for point in InvalidPoints:
            InvalidPointList.append(point[0])
            InvalidPointList.append(point[1])
            iterator += 2


        #Weight calcuation
        p1Coords = self.roomsCentroids[refPoint]
        indexList = []
        for triang in connectingTriangles:
            for pointIndex in triang:
                if pointIndex == refPoint or pointIndex in indexList or pointIndex in InvalidPointList:
                    continue
                else:
                    indexList.append(pointIndex)
                    p2Coords = self.roomsCentroids[pointIndex]
                    dist = math.sqrt((p1Coords[0]-p2Coords[0])**2+(p1Coords[1]-p2Coords[1])**2)
                    weightTable.append([refPoint,pointIndex,dist])
                   



        return weightTable
    
    # adds a desired amount of paths back to create some variation
    def addExtraPaths(self,CurrentPaths,percent):
        for connection in self.allConnections:
            if connection not in CurrentPaths:
                if random.random() <= percent:
                    CurrentPaths.append(connection)

        return CurrentPaths
    

    def rightAnglefication(self,Paths):
        CorridorWidth = 2
        for path in Paths:
            startInd = path[0]
            endInd = path[1]
            startCoords = self.roomsCentroids[startInd]
            EndCoords = self.roomsCentroids[endInd]
            dx = EndCoords[0]-startCoords[0]
            dy = EndCoords[1]-startCoords[1]

            #X direction
            if dx >= 0:
                #Make rects in x and y direction
                rectx = pygame.Rect(startCoords[0],startCoords[1],abs(dx),CorridorWidth)
                ystart = [startCoords[0] + dx,startCoords[1]]
                
                
            else:
                rectx = pygame.Rect(startCoords[0]+dx,startCoords[1],abs(dx),CorridorWidth)
                ystart = [startCoords[0]+dx,startCoords[1]]
            

            #Y direrction
            if dy >= 0:
                recty = pygame.Rect(ystart[0],ystart[1],CorridorWidth,abs(dy))
            else:
                recty = pygame.Rect(ystart[0],ystart[1]+dy,CorridorWidth,abs(dy))

            self.corridor.append([rectx,recty])
        return self.corridor

