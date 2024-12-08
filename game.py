import sys
import pygame
import random
import math 

from scripts.DungeonGen import DungeonGen

class Game:
    # This function allows us to call screen and clock in any future functions containing (self) as an initialisation
    def __init__(self):
        pygame.init()

        #Create screen
        #Set windows name
        pygame.display.set_caption("TDDG")
        self.resolution = [1440,1080]
        resScale = 1

        self.screen = pygame.display.set_mode((self.resolution[0],self.resolution[1]))

        # To scale up the screen we render at a smaller size then scale it up.
        #Create a black box with 320,240 size.
        self.display = pygame.Surface((self.resolution[0]*resScale,self.resolution[1]*resScale))


        #set max FPS
        self.clock = pygame.time.Clock()

        self.dungeon_controls(self.resolution)
        
        self.RoomsSpawned = 0
        self.Dungeon_generated = 0
        self.showMinSpanFlag = 0
        self.showDTriFlag = 0

    def run(self):
        while True:
            self.display.fill((0,0,0))

            #Generate dungeon:
            if self.RoomsSpawned == 0:
                self.DungeonGen = DungeonGen(self)
                #Generate overlapping cells
                self.DungeonGen.generate(1,self.mean,self.std,self.origin,self.radius,self.resolution)
                #Move cells to get rid of overalp
                cells = self.DungeonGen.move_cells()
                #Choose which cells are rooms:
                rooms,centroids = self.DungeonGen.room_select()
                #Delaunay Triangulation
                paths = self.DungeonGen.DelaunayTri()
                triang = paths.simplices
                self.roomConnections,self.roomCentroids = self.DungeonGen.MinSpanTree(paths)
                # Add 15% of the unused paths back in.
                self.roomConnections = self.DungeonGen.addExtraPaths(self.roomConnections,self.extraPaths)

                #Make passages right angles.
                self.corridors = self.DungeonGen.rightAnglefication(self.roomConnections)

                self.RoomsSpawned = 1
                print('Dungeon Generated')
            #print(rooms)
            

            #

           

            #pygame.draw.circle(self.display,(255,255,255),self.origin,self.radius,width = 1)
            for cell in cells:
                pass
                #self.rect = pygame.Rect(room[0],room[1],10,10)
                #pygame.draw.rect(self.display,(255,0,0),cell,width=1)
            k = 0
            for room in rooms:
                pygame.draw.rect(self.display,(0,140,255),room)
                cent = pygame.Rect(centroids[k][0]-2,centroids[k][1]-2,4,4)
                pygame.draw.rect(self.display,(255,0,0),cent)

                k+=1


            #Delaunay Triangulation display
            if self.showDTriFlag == 1:
                for i in range(len(triang)):
                    tri = triang[i]
                    points = []
                    for j in range(0,3):
                        points.append([centroids[tri[j]][0],centroids[tri[j]][1]])
                    pygame.draw.lines(self.display,(255,0,0),True,points,width=4)
                #pygame.draw.lines(self.display,(255,0,0),False,rooms)



            # min spanning tree display
            if self.showMinSpanFlag == 1:
                for i in range(len(self.roomConnections)):
                    ind = self.roomConnections[i]
                    pygame.draw.line(self.display,(0,255,0),(self.roomCentroids[ind[0]][0],self.roomCentroids[ind[0]][1]),(self.roomCentroids[ind[1]][0],self.roomCentroids[ind[1]][1]))




            #corridors
            for corridor in self.corridors:
                pygame.draw.rect(self.display,(0,0,255),corridor[0])
                pygame.draw.rect(self.display,(0,0,255),corridor[1])






            for event in pygame.event.get():
                #event is an input of some description
                


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.RoomsSpawned = 0
                    if event.key == pygame.K_m:
                        self.showMinSpanFlag = 1
                        print('MST OFF')
                    if event.key == pygame.K_t:
                        self.showDTriFlag = 1
                        print('triangulation ON')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_m:
                        self.showMinSpanFlag = 0
                        print('MST OFF')
                    if event.key == pygame.K_t:
                        self.showDTriFlag = 0
                        print('triangulation OFF')

                #Close window event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



                    
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0))

            pygame.display.update()
            #Force game to run at 60 FPS
            self.clock.tick(60)





    def dungeon_controls(self,res):
        #Dungeon controls:
        self.mean = 20
        self.std = 20
        #Circle:
        self.origin = [res[0]/2,res[1]/2]
        self.radius = 150
        self.extraPaths = 0.15




Game().run()

    