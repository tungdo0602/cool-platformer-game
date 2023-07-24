import pygame, json, time
import gameTools
from tkinter import messagebox, simpledialog

pygame.init()

w, h = [800, 500]
screen = pygame.display.set_mode((w, h), vsync=1)
pygame.display.set_caption("Cool Platformer :O")
pygame.display.set_icon(pygame.image.load("./assets/icon.png"))
ts = 10

class Box(pygame.Surface):
    def __init__(self, wh=(50, 50), type=1):
        global ts
        super().__init__(size=wh)
        self.types = {1: (0, 0, 0), 2: (255, 0, 0), 3: (0, 0, 255), 4: (0, 255, 0), 5: (255, 255, 0)}
        self.type = 1 if type > len(self.types) else len(self.types) if type < 1 else type
        self.fill(self.types[self.type])
        self.rect = self.get_rect()

class Sound():
    def __init__(self, path, volume=1):
        self.volume = volume
        self.s = pygame.mixer.Sound(path)
        self.s.set_volume(volume)
        
    def play(self):
        self.s.play()
        

class World():
    def __init__(self):
        global ts
        self.data = {}
        self.tl = []
        self.debug = False
        self.nextLvl = ""
        self.respawnPos = []
    
    def load(self, path):
        global w, h, ts
        try:
            self.data = json.loads(open(path).read())
        except FileNotFoundError:
            self.data = {"respawnPos": [0, 0], "blockSize": 50, "nextLvl": "", "data": [[0]*int(w/ts) for _ in range(int(h/ts))]}
        ts = self.data["blockSize"]
        self.respawnPos = self.data["respawnPos"]
        self.nextLvl = self.data["nextLvl"]
        row = 0
        for i in self.data["data"]:
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
    
    def placeBox(self, newSpawnPoint=False):
        global ts, w, h, player
        x, y = map((lambda i: (i//ts)*ts), pygame.mouse.get_pos())
        if type(self.containBox(x, y)) != int and x <= w and y <= h:
            if newSpawnPoint:
                player.setRespawnPos(x, y)
            else:
                box = Box((ts, ts))
                box.rect.x = x
                box.rect.y = y
                self.tl.append(box)
        return (x, y)
            
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
        global ts, w, h, player
        data = [[0]*int(w/ts) for _ in range(int(h/ts))]
        for i in self.tl:
            x, y = map((lambda i: int(i)-1), [i.rect.x / ts, i.rect.y / ts])
            data[y][x] = i.type
        return {
            "respawnPos": player.respawnPos,
            "blockSize": ts,
            "nextLvl": "",
            "data": data
        }
    
    def exportToFile(self, filename):
        with open(filename + ".json", "w") as f:
            f.write(json.dumps(world.convertToData()))

    def clear(self):
        global player
        self.tl = []
        self.nextLvl = ""
        player.setRespawnPos(0, 0)
    
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
        self.playerts = ts / 100 * 80 # 80% #
        self.image = pygame.Surface((self.playerts, self.playerts))
        self.image.fill((255, 255, 150))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = [x, y]
        self.vely = 0
        self.speed = 5
        self.onGround = False
        self.inWater = False
        self.respawnPos = [x, y]
        self.now = time.time()
        self.die = False
    
    def update(self):
        global screen, w, h, world, ts
        keys = pygame.key.get_pressed()
        
        dx = dy = 0
        
        currentSpeed = self.speed / 2 if self.inWater else self.speed
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            if time.time() - self.now > 0.35 and self.onGround:
                Sound("./assets/Sounds/walk.wav", 0.3).play()
                self.now = time.time()
            dx += currentSpeed if keys[pygame.K_RIGHT] else -currentSpeed
            
        if keys[pygame.K_UP] and self.onGround:
            if self.inWater:
                self.vely = -5
            else:
                Sound("./assets/Sounds/jump.wav").play()
                self.vely = -15
        self.rect.x = 0 if self.rect.x < 0 else screen.get_width() if self.rect.x > screen.get_width() else self.rect.x
        if self.rect.y > screen.get_height() or self.rect.y == -40:
            self.die = True
            self.respawn()
        elif -40 < self.rect.y < 0:
            dy = screen.get_rect().bottom - self.rect.top
            self.vely = 0
        else:
            self.die = False
        
        self.vely += 0.25 if self.inWater else 1
        if self.vely > 10:
            self.vely = 10
        dy += self.vely
        self.coolStuffsChecker()
        for i in world.tl:
            
            if i.type == 1:
                if i.rect.colliderect(self.rect.x + dx, self.rect.y, self.image.get_width(), self.image.get_height()):
                    dx = 0
            
                if i.rect.colliderect(self.rect.x, self.rect.y + self.vely, self.image.get_width(), self.image.get_height()):
                    if self.vely < 0:
                        dy = i.rect.bottom - self.rect.top
                        self.vely = 0
                    elif self.vely >= 0:
                        dy = i.rect.top - self.rect.bottom
                        self.vely = 0
            elif pygame.sprite.collide_rect(i, self):
                if i.type == 2:
                    self.die = True
                    self.respawn()
                elif i.type == 4 and world.nextLvl:
                    Sound("./assets/Sounds/nextLvl.wav", 0.25).play()
                    newWorld = World()
                    newWorld.load(world.nextLvl)
                    world = newWorld
                    self.setRespawnPos(*world.respawnPos)
                    self.respawn()
                elif i.type == 5:
                    Sound("./assets/Sounds/jumpPad.wav", 0.5).play()
                    self.vely = -20
                else:
                    self.die = False
        
        self.rect.move_ip([dx, dy])
        screen.blit(self.image, self.rect)
        
    def coolStuffsChecker(self): # Bro Dupelicate :skull: #
        global world
        for i in world.tl:
            if i.type == 1:
                
                if i.rect.colliderect(self.rect.x, self.rect.y + self.vely, self.image.get_width(), self.image.get_height()):
                    if self.vely >= 0:
                        self.onGround = True
                        break
                else:
                    self.onGround = False
            if self.rect.colliderect(i.rect):
                if i.type == 3:
                    self.inWater = self.onGround = True
                    break
            else:
                self.inWater = False
    
    def respawn(self):
        if self.die:
            Sound("./assets/Sounds/crash.wav", 0.25).play()
        self.rect.x, self.rect.y = self.respawnPos
        self.onGround = self.inWater = False # Reset state #
        
    def setRespawnPos(self, x, y):
        self.respawnPos = [x, y]
            
    
isRunning = True
clock = pygame.time.Clock()
world = World()
world.load("./levels/lvl_1.json")
player = Player(*world.respawnPos)
pygame.mixer.music.load("./assets/sounds/bg.wav")
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(1)
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                if messagebox.askyesno("Confirm", "Are you sure to update the level from the cloud?"):
                    gameTools.updateLevels()
                    messagebox.showinfo("Done!", "Levels are up-to-date!")
            if event.key == pygame.K_F2:
                pygame.mixer.music.set_volume(float(not pygame.mixer.music.get_volume()))
            if event.key == pygame.K_F5:
                world.debug = not world.debug
            if world.debug:
                if event.key == pygame.K_F7:
                    filename = simpledialog.askstring("Save as...", "File Name:", initialvalue="custom_level")
                    world.exportToFile(filename)
                    messagebox.showinfo("Saved", "Saved! Check {}.json".format(filename))
                if event.key == pygame.K_F9:
                    if messagebox.askyesno("Confirm", "Are you sure to clear the level?"):
                        world.clear()
                if event.key == pygame.K_e:
                    world.editBoxState()
            if event.key == pygame.K_r:
                player.respawn()
        if world.debug:
            if event.type == pygame.MOUSEWHEEL:
                world.editBoxState(-1 if event.y < 0 else 1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2: # Middle click #
                    x, y = world.placeBox(True)
                    print("Set new spawn point to:", x, y)

    mousePressed = pygame.mouse.get_pressed()
    keyPressed = pygame.key.get_pressed()
    if world.debug:
        if mousePressed[0]:
            world.placeBox()
        elif mousePressed[2]:
            world.deleteBox()
    
    #BG Handler
    screen.fill((255, 255, 255)) #Fill first or it will replace the obj
    
    # Updater #
    world.update()
    player.update()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
