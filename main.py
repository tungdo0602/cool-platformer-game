import pygame, json, time

pygame.init()

w, h = [800, 500]
screen = pygame.display.set_mode((w, h), vsync=1)
pygame.display.set_caption("Bro FR")
ts = 50

class Box(pygame.Surface):
    def __init__(self, wh=(50, 50), type=1):
        global ts
        super().__init__(size=wh)
        self.types = {1: (0, 0, 0), 2: (255, 0, 0), 3: (0, 0, 255), 4: (0, 255, 0)}
        self.type = 0 if type >= len(self.types) else len(self.types) if type < 1 else type
        self.fill(self.types[type])
        self.rect = self.get_rect()

class World():
    def __init__(self):
        global ts
        self.data = {}
        self.tl = []
        self.debug = False
    
    def load(self, path):
        self.data = json.loads(open(path).read())["data"]
        row = 0
        for i in self.data:
            col = 0
            for j in i:
                if j != 0:
                    box = Box((ts, ts), j)
                    box.rect.x = col * ts
                    box.rect.y = row * ts
                    self.tl.append(box)
                col += 1
            row += 1
        self.data = {} # Clear
    
    def drawGrid(self):
        global ts, w, h, screen
        for x in range(0, w, ts):
            for y in range(0, h, ts):
                pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(x, y, ts, ts), 1)
    
    def containBox(self, x, y):
        for i in range(len(self.tl)):
            if self.tl[i].rect.x == x and self.tl[i].rect.y == y:
                return i
        return False
    
    def placeBox(self):
        global ts, w, h
        x, y = map((lambda i: (i//ts)*ts), pygame.mouse.get_pos())
        if type(self.containBox(x, y)) != int and x <= w and y <= h:
            box = Box((ts, ts))
            box.rect.x = x
            box.rect.y = y
            self.tl.append(box)
            
    def deleteBox(self):
        global ts
        x, y = map((lambda i: (i//ts)*ts), pygame.mouse.get_pos())
        boxPos = self.containBox(x, y)
        if type(self.containBox(x, y)) == int:
            del self.tl[boxPos]
        
    def editBoxState(self, step=1):
        global ts
        x, y = map((lambda i: (i//ts)*ts), pygame.mouse.get_pos())
        boxPos = self.containBox(x, y)
        if type(boxPos) == int:
            box = Box((ts, ts), self.tl[boxPos].type + step)
            box.rect = self.tl[boxPos].rect
            self.tl[boxPos] = box
            
    def convertToData(self):
        global ts, w, h
        data = [[0]*int(w/ts) for _ in range(int(h/ts))]
        for i in self.tl:
            x, y = map((lambda i: int(i)-1), [i.rect.x / ts, i.rect.y / ts])
            data[y][x] = i.type
        return {"data": data}
    
    def exportToFile(self):
        with open("custom_level.json", "w") as f:
            f.write(json.dumps(world.convertToData()))

    def clear(self):
        self.tl = []
    
    def update(self):
        global screen
        for i in self.tl:
            screen.blit(i, i.rect)
        if self.debug:
            self.drawGrid()

class Player():
    def __init__(self, x, y):
        global ts
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 255, 150))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = [x, y]
        self.vely = 0
        self.speed = 5
        self.jumped = False
        self.onGround = False
    
    def update(self):
        global screen, w, h, world, ts
        dy = dx = 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            dx += self.speed if keys[pygame.K_RIGHT] else -self.speed
            
        if keys[pygame.K_UP] and self.onGround:
            self.vely = -15
        
        self.vely += 1
        if self.vely > 10:
            self.vely = 10
        dy += self.vely
        self.onGroundCheck()
        for i in world.tl:
            if i.rect.colliderect(self.rect.x + dx, self.rect.y, self.image.get_width(), self.image.get_height()):
                dx = 0
            
            if i.rect.colliderect(self.rect.x, self.rect.y + self.vely, self.image.get_width(), self.image.get_height()):
                if self.vely < 0:
                    dy = i.rect.bottom - self.rect.top
                    self.vely = 0
                elif self.vely >= 0:
                    dy = i.rect.top - self.rect.bottom
                    self.vely = 0
        
        self.rect.move_ip([dx, dy])
        screen.blit(self.image, self.rect)
        
    def onGroundCheck(self): # Bro Dupelicate :skull: #
        global world
        for i in world.tl:
            if i.rect.colliderect(self.rect.x, self.rect.y + self.vely, self.image.get_width(), self.image.get_height()):
                if self.vely >= 0:
                    self.onGround = True
                    break
            else:
                self.onGround = False
            
    
isRunning = True
clock = pygame.time.Clock()
world = World()
#world.load()
player = Player(100, 100)
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                world.debug = not world.debug
            if world.debug:
                if event.key == pygame.K_F7:
                    world.exportToFile()
                if event.key == pygame.K_F9:
                    world.clear()
                if event.key == pygame.K_e:
                    world.editBoxState()
                if event.key == pygame.K_r:
                    player.rect.x = player.rect.y = 100
        # if event.type == pygame.MOUSEWHEEL and world.debug:
        #     world.editBoxState(-1 if event.y < 0 else 1)

    mouse = pygame.mouse.get_pressed()
    if world.debug:
        if mouse[0]:
            world.placeBox()
        elif mouse[2]:
            world.deleteBox()
    
    #BG Handler
    screen.fill((255, 255, 255)) #Fill first or it will replace the obj
    
    # Updater #
    world.update()
    player.update()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
