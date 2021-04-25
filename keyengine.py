import pygame

class KeyEngine:
    currEvents = list()
    eventmap = dict()

    def __init__(self):
        return

    def run(self):
        for i in self.currEvents:
            if i in self.eventmap:
                self.eventmap[i]()

    def register(self, key: int, event):
        self.eventmap[key] = event

    def handleEvents(self, event):
        # Nothing to do
        if len(self.eventmap) < 1 or (event.type != pygame.KEYDOWN and event.type != pygame.KEYUP):
            return
        if event.type == pygame.KEYDOWN:
            if event.key in self.currEvents:
                return
            self.currEvents.append(event.key)

        if event.key in self.currEvents and event.type == pygame.KEYUP:
            self.currEvents.remove(event.key)
