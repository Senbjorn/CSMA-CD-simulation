import random
import sys
import datetime as dt


class Frame():
    def __init__(self, src, dst, payload):
        self.src = src
        self.dst = dst
        self.payload = payload


class Station():
    def __init__(self, address):
        self.address = address
        self.sent = []
        self.in_progress = None
        self.accepted = []
        self.wait = 0

    def get_address(self):
        return self.address
    
    def get_accepted(self):
        return self.accepted

    def get_sent(self):
        return self.sent

    def read(self, channel):
        frame = channel.get(self.get_address())
        if frame is not None:
            self.accepted.append(frame)
        return frame

    def send(self, channel, dst, payload):
        frame = None
        if self.wait == 0 and channel.check() and len(self.sent) == 0:
            frame = Frame(self.address, dst, payload)
            self.in_progress = frame
            channel.send(frame)
        return frame
    
    def verify(self, collision_set):
        status = 0
        if self.in_progress is not None and self.get_address() not in collision_set:
            self.sent.append(self.in_progress)
            status = 1
        else:
            self.wait = random.randint(0, 15) + 1
            status = 0
        self.in_progress = None
        return status

    def step(self):
        if self.wait > 0:
            self.wait -= 1
        

class Channel():
    def __init__(self):
        self.busy = 0
        self.data = []

    def check(self):
        return self.busy == 0

    def send(self, frame):
        if self.check():
            self.data.append(frame)

    def step(self):
        if self.busy > 0:
            self.busy -= 1
    
    def get(self, address):
        frame = None
        if len(self.data) == 1 and self.busy == 0:
            frame = self.data[0]
            if frame.dst != address:
                frame = None
        return frame

    def process_collisions(self):
        collision_set = set()
        if len(self.data) == 1 and self.busy == 0:
            self.busy = 1530 // 64 + 1
        if len(self.data) > 1 and self.busy == 0:
            collision_set = {f.src for f in self.data}
        return collision_set

    def release_data(self):
        if len(self.data) >= 1 and self.busy == 0:
            self.data = []


def main_loop(n, t_max, output='extended'):
    time_step = 0
    tau = 51.2e-6
    channel = Channel()
    stations = [Station(i) for i in range(n)]
    while True:
        sim_time = dt.timedelta(seconds=time_step * tau)
        # read when the frame is ready
        for s in stations:
            frame = s.read(channel)
            if frame is not None:
                if output == 'extended':
                    src = frame.src
                    dst = frame.dst
                    payload = frame.payload
                    print(f'{time_step}; time: {sim_time}; successful read from {src} to {dst}; data: {payload}')
        channel.release_data()
        
        # try to write something if the channel is not busy and a station is ready
        for s in stations:
            frame = s.send(
                channel,
                (s.get_address() + 1) % n,
                random.randint(s.get_address() * 100, (s.get_address() + 1) * 100 - 1)
            )

        # successful write (only 1 write and the channnel is free)
        # collision (channel is free, but more than 1 write)
        collision_set = channel.process_collisions()

        sent = False
        for s in stations:
            status = s.verify(collision_set)
            if status == 1:
                sent = True
        
        if sent:
            frame = channel.data[0]
            src = frame.src
            dst = frame.dst
            if output == 'extended':
                print(f'{time_step}; time: {sim_time}; successful write from {src} to {dst}')
            if output == 'simple':
                print(time_step, sim_time)
        if len(collision_set) > 0:
            if output == 'extended':
                print(f'{time_step}; time: {sim_time}; collision')
                print('collision set: ', end='')
                for addr in sorted(list(collision_set)):
                    print(addr, end=', ')
                print()
        
        channel.release_data()
        
        # updata counters
        channel.step()
        for s in stations:
            s.step()
        time_step += 1
        if time_step > t_max:
            print('number of steps has exceeded')
            break
        ready = True
        for s in stations:
            a = len(s.get_accepted()) == 1
            b = len(s.get_sent()) == 1
            c = a and b
            ready = ready and c
        if ready:
            print('done')
            break



if __name__ == '__main__':
    n = int(sys.argv[1])
    t_max = int(sys.argv[2])
    mode_num = int(sys.argv[3])
    modes = ['simple', 'extended']
    mode = modes[mode_num]
    main_loop(n, t_max, output=mode)