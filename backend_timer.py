from time import sleep

class Timer:
    def __init__(self, minute, second):
        self.time = [minute, second]
        self.state = [minute, second]
        self.paused = False

    def set_time(self, minute, second):
        self.time = [minute, second]
        self.state = [minute, second]

    def get_actual_time(self):
        return self.state
    
    def pause(self):
        self.paused = True

    def play(self):
        self.paused = False

        if self.state[1] >= 60:
            self.state[1] = 59

        while self.state[0] >= 0 and not self.paused:
            sleep(1)
            self.state[1] -= 1
            if self.state[1] == -1:
                self.state[1] = 59
                self.state[0] -= 1
            elif self.state[0] == 0 and self.state[1] == 0:
                break

    def restart(self):
        self.state = self.time