import aiwolfpy
import aiwolfpy.contentbuilder as cb
import villager_5
import seer_5
import werewolf_5
import possessed_5
import villager_15
import bodyguard_15
import medium_15
import seer_15
import werewolf_15
import possessed_15

from util import RoleType

class MyAgent:
    def __init__(self, agent_name: str):
        self.myname = agent_name
        self.behavior = None
        self.agent_list = [
            1, 
            0, 
            [0] * 15,
            set([i for i in range(1, 16)]),
            set(),
            set(),
            set(),
            set()
        ]

    def getName(self) -> str:
        return self.myname

    def initialize(self, base_info, diff_data, game_setting):
        self.base_info = base_info
        if not self.agent_list[1]:
            self.agent_list[2][0] = int(self.base_info['agentIdx'])
        self.agent_list[1] += 1
        self.game_setting = game_setting
        self.remaining = len(base_info["remainTalkMap"])
        
        ## initialize behavior
        role = base_info["myRole"]
        if self.game_setting["playerNum"] == 5:
            # 5 people game
            if role == RoleType.VILLAGER.value:
                self.behavior = villager_5.VillagerBehavior(self.myname)
            elif role == RoleType.SEER.value:
                self.behavior = seer_5.SeerBehavior(self.myname)
            elif role == RoleType.POSSESSED.value:
                self.behavior = possessed_5.PossessedBehavior(self.myname)
            elif role == RoleType.WEREWOLF.value:
                self.behavior = werewolf_5.WerewolfBehavior(self.myname)
            else:
                # if not specified, then villager
                self.behavior = villager_5.VillagerBehavior(self.myname)
        elif self.game_setting["playerNum"] == 15:
            # 15 people game
            if role == RoleType.VILLAGER.value:
                self.behavior = villager_15.VillagerBehavior(self.myname, self.agent_list)
            elif role == RoleType.MEDIUM.value:
                self.behavior = medium_15.MediumBehavior(self.myname, self.agent_list)
            elif role == RoleType.BODYGUARD.value:
                self.behavior = bodyguard_15.BodyguardBehavior(self.myname, self.agent_list)
            elif role == RoleType.SEER.value:
                self.behavior = seer_15.SeerBehavior(self.myname, self.agent_list)
            elif role == RoleType.POSSESSED.value:
                self.behavior = possessed_15.PossessedBehavior(self.myname, self.agent_list)
            elif role == RoleType.WEREWOLF.value:
                self.behavior = werewolf_15.WerewolfBehavior(self.myname, self.agent_list)
            else:
                # if not specified, then villager
                self.behavior = villager_15.VillagerBehavior(self.myname, self.agent_list)
        else:
            raise ValueError("Invalid Player Number: should be 5 or 15.")
        self.behavior.initialize(base_info, diff_data, game_setting)

    def update(self, base_info, diff_data, request):
        try:
            self.behavior.update(base_info, diff_data, request)
        except Exception:
            pass

    def dayStart(self):
        try:
            self.behavior.dayStart()
        except Exception:
            pass

    def talk(self):
        try:
            return self.behavior.talk()
        except Exception:
            return cb.over()

    def whisper(self):
        try:
            return self.behavior.whisper()
        except Exception:
            return cb.over()

    def vote(self):
        try:
            return self.behavior.vote()
        except Exception:
            return 1

    def attack(self):
        try:
            return self.behavior.attack()
        except Exception:
            return 1

    def divine(self):
        try:
            return self.behavior.divine()
        except Exception:
            return 1

    def guard(self):
        try:
            return self.behavior.guard()
        except Exception:
            return 1

    def finish(self):
        return self.behavior.finish()

if __name__ == '__main__':
    agent = MyAgent("otowolf")
    aiwolfpy.connect_parse(agent)