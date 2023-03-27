import copy
import math
import random
from importlib.resources import path
from itertools import permutations
from typing import List

import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        identifies = []
        path = [i for i in range(1, len(coin_distance))]

        # path = [2, 1, 3, 4]
        row = self.x
        col = self.y
        visited = [False for i in range(0, len(coin_distance))]
        visitedPom = []
        visited[0] = True
        flag = True
        cnt = 0
        i = len(path)
        while i:
            path.pop()
            i = i - 1;

        while flag:
            counter = 0
            br = max(coin_distance[cnt])
            visitedPom.clear()
            cntif = 0
            i = len(visited) - 1

            while i >= 0:
                if visited[i]:
                    cntif = cntif + 1
                if cntif == len(visited):
                    flag = False
                i = i - 1

            if len(identifies) == len(coin_distance) - 1:
                break

            while counter < len(coin_distance):
                if coin_distance[cnt][counter] <= br:

                    if not visited[counter]:
                        if coin_distance[cnt][counter] != 0:
                            br = coin_distance[cnt][counter]
                            visitedPom.append((br, counter))

                counter = counter + 1

            visitedPom = sorted(visitedPom, key=lambda x: x[0])
            print(visitedPom)
            while len(visitedPom) > 1:
                visitedPom.pop()
            pom = visitedPom[0][0]
            visitedInt = visitedPom[0][1]

            visited[visitedInt] = True
            path.append(visitedInt)

            identifies.append(pom)
            cnt = visitedInt
        print(path)
        print(identifies)

        return [0] + path + [0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        p = permutations(path)
        minsum = 5000
        path2 = []
        for i in list(p):
            sum = 0
            for j in range(len(i)):
                if j == 0:
                    sum += coin_distance[0][i[j]]
                else:
                    sum += coin_distance[i[j - 1]][i[j]]
            sum += coin_distance[i[j]][0]
            if sum < minsum:
                minsum = sum
                path2.clear()
                for k in range(len(i)):
                    path2.append(i[k])
        print(path2)

        return [0] + path2 + [0]


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]

        listaPP = []
        path2 = []

        i = 1
        while i <= 4:
            price = coin_distance[0][i]
            listPom = [0, i, price]
            listaPP.append(listPom)
            i = i + 1

        print(listaPP)

        flag = True
        while flag:
            listaPP = sorted(listaPP, key=lambda x: x[-1], reverse=True)
            pomLista = listaPP.pop()
            cnt = len(pomLista)
            if cnt <= len(coin_distance):  # npr [0,3,2,22]
                suma = pomLista.pop()  # [0,3,2]
                posl = pomLista.pop()  # [0,3]
                # fali mi 1, 4
                l = [i for i in range(1, len(coin_distance))]
                for j in l:
                    if j not in pomLista and j != posl:
                        listPom2 = copy.deepcopy(pomLista)
                        novaSuma = suma + coin_distance[posl][j]
                        listPom2.append(posl)
                        listPom2.append(j)
                        listPom2.append(novaSuma)
                        listaPP.append(listPom2)

            if cnt == len(coin_distance) + 1:
                suma = pomLista.pop()
                posl = pomLista.pop()
                suma = suma + coin_distance[posl][0]
                pomLista.append(posl)
                pomLista.append(0)
                pomLista.append(suma)
                listaPP.append(pomLista)

            if cnt > len(coin_distance) + 1:
                # sortedlist = sorted([x for x in listaPP if len(x) == len(coin_distance) + 1], key=lambda s: s[-1])
                path2 = pomLista
                path2.pop()
                print(path2)
                flag = False

        return path2

class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def minimumst(self, coin_distance, lista):
        procena = 0

        INF = 9999999
        # number of vertices in graph
        N = len(coin_distance)
        # creating graph by adjacency matrix method
        selected_node = [0]*N
        listaOdbacenih = []
        i = len(coin_distance) - 1
        #lista mi je [0,2,3]
        #hocu da napravim stablo od ta 3 cvora
        #treba da odbacim 1 i 4
        #ja sam ovde odbacila samo 1

        while i >= 0:
            if i not in lista:
                listaOdbacenih.append(i)
            i = i - 1

        no_edge = 0

        selected_node[0] = True

        # printing for edge and weight
        print("Edge : Weight\n")
        while no_edge < N - 1:

            minimum = INF
            a = 0
            b = 0
            for m in range(N):
                if selected_node[m] and m not in listaOdbacenih:
                    for n in range(N):
                        if (not selected_node[n]) and coin_distance[m][n] and n not in listaOdbacenih:
                            # not in selected and there is an edge
                            if minimum > coin_distance[m][n]:
                                minimum = coin_distance[m][n]
                                a = m
                                b = n
            print(str(a) + "-" + str(b) + ":" + str(coin_distance[a][b]))
            selected_node[b] = True
            no_edge += 1
            procena = procena + coin_distance[a][b]
        # print(selected_node)
        # print(procena)

        return procena

    def get_agent_path(self, coin_distance):
        path = [i for i in range(0, len(coin_distance))]

        listaPP = []
        path2 = []

        sumica = self.minimumst(coin_distance, path)
        #sumica = 27
        print(sumica)
        i = 1
        while i <= 4:
            price = coin_distance[0][i] + sumica
            listPom = [0, i, coin_distance[0][i], price]
            listaPP.append(listPom)
            i = i + 1
        # print(listaPP)
        flag = True
        while flag:
            listaPP = sorted(listaPP, key=lambda x: x[-1], reverse=True)
            print(listaPP)
            pomLista = listaPP.pop()
            print(pomLista)
            cnt = len(pomLista)
            if cnt <= len(coin_distance)+1:  # npr [0,3,2,22]

                suma = pomLista.pop()  # [0,3,2]
                sumaPreth = pomLista.pop()
                posl = pomLista.pop()  # [0,3]
                # fali mi 1, 4
                l = [i for i in range(1, len(coin_distance))]
                brc = [0]
                for m in l:
                    if m not in pomLista and m != posl:
                        brc.append(m)
                brcsum = self.minimumst(coin_distance, brc)
                print(brcsum)
                print(brc)

                for j in l:
                    if j not in pomLista and j != posl:
                        listPom2 = copy.deepcopy(pomLista)
                        novaSuma = sumaPreth + coin_distance[posl][j] + brcsum
                        sumaStara = sumaPreth + coin_distance[posl][j]
                        listPom2.append(posl)
                        listPom2.append(j)
                        listPom2.append(sumaStara)
                        listPom2.append(novaSuma)
                        print(listPom2)
                        listaPP.append(listPom2)

            if cnt == len(coin_distance) + 2:
                suma = pomLista.pop()
                novaSuma = pomLista.pop()
                posl = pomLista.pop()
                suma = novaSuma + coin_distance[posl][0] + 0
                novaSuma = novaSuma + coin_distance[posl][0]
                pomLista.append(posl)
                pomLista.append(0)
                pomLista.append(novaSuma)
                pomLista.append(suma)
                listaPP.append(pomLista)

            if cnt > len(coin_distance) + 2:
                # sortedlist = sorted([x for x in listaPP if len(x) == len(coin_distance) + 1], key=lambda s: s[-1])
                path2 = pomLista
                path2.pop()
                path2.pop()
                print(path2)
                flag = False


                #FALI MI JOS IZRACUNATIH MST-OVA!!!

        return path2
