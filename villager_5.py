import random
from util import ActionType, RoleType
from textgenerator import TextGenerator
import emotion
import parse_content


class VillagerBehavior:
    def __init__(self, agent_name):
        self.myname = agent_name
        self.text_gen = TextGenerator()

    def getName(self):
        return self.myname

    def initialize(self, base_info, diff_data, game_setting):
        # set seed for this agent's behavior
        self.base_info = base_info
        random.seed(random.random() + self.base_info["agentIdx"])
        self.game_setting = game_setting
        self.player_size = len(self.base_info["remainTalkMap"].keys())

        self.myrole = base_info["myRole"]
        self.result_seer = []
        self.result_med = []
        self.talk_turn = 0
        self.honest = False
        self.divined_as_wolf = []
        self.divined_as_human = []
        self.wrong_divine = set()
        # white, black, grey
        self.white = set()
        self.black = set()
        self.greys = set()

        self.check_alive()

        self.seers = set()
        self.tryingPP = set()
        self.greys = set(self.alive) - {int(base_info["agentIdx"])}
        self.players = self.greys.copy()
        self.whisper_turn = 0
        self.attack_success = True
        self.attacked_who_lastnight = 0
        self.text_gen.gameInitialize(self.base_info["agentIdx"], self.player_size)
        # someone -> thinking -> me
        self.seer_divined_me_as_werewolf = set()
        self.estimated_me_as_werewolf = set()
        self.estimated_me_as_human = set()
        self.asked_why_divine = set()
        self.asked_why_doubt = set()
        # PP mode flag
        self.PPmode = False
        self.when_declare = random.randint(4, 8)

        # init emotion
        self.emo = emotion.Emotion(self.alive)
        self.stealth = True if random.random() > 0.25 else False
        self.who_said_black = {alive_player: [] for alive_player in self.alive}
        self.emo.myrole_appearance = base_info["myRole"]
        self.emo.myrole = base_info["myRole"]

        # coming out
        self.has_CO_seer = False

    def update(self, base_info, diff_data, request):
        self.base_info = base_info
        self.diff_data = diff_data

        self.check_alive()

        if self.base_info["day"] == 0:
            # skip first day
            return

        for player_id in range(diff_data.shape[0]):
            if diff_data.type[player_id] == "vote":
                who = diff_data.idx[player_id]
                target = diff_data.agent[player_id]
                if target == self.base_info["agentIdx"]:
                    self.emo.add(who, "voted_me")
                elif target not in self.vote_cand():
                    self.emo.add(who, "voted_who_i_love")
                else:
                    self.emo.add(who, "voted_who_i_hate")
            if diff_data.type[player_id] == "execute":
                for seer in self.who_said_black[diff_data.agent[player_id]]:
                    self.emo.add(seer, "you_said_black_but_not")

        for i in self.diff_data.iterrows():
            self.talk_recognize(i, request)

        if request == "DAILY_INITIALIZE":
            for player_id in range(diff_data.shape[0]):
                action_type = diff_data["type"][player_id]
                if action_type == "attack":
                    self.attacked_who_lastnight = diff_data["agent"][player_id]
                elif action_type == "identify":
                    self.result_med.append(diff_data["text"][player_id])
                elif action_type == "divine":
                    self.result_seer.append(diff_data["text"][player_id])
                    self.greys -= {int(diff_data["text"][player_id][14:16])}
                else:
                    continue

    def talk_recognize(self, i, request):
        to = 0
        raw = ""
        line = i[1]
        parsed_list = parse_content.parse_text(line["text"])
        who = line["agent"]
        stattype = line["type"]
        for interpreted in parsed_list:
            try:
                self.talk_recognize_update(i, to, raw, line, who, interpreted, stattype)
            except Exception:
                pass
            content = interpreted.split()
            if request == "DAILY_INITIALIZE" and content[0] == ActionType.DIVINED.value:
                if content[2] == RoleType.WEREWOLF.value:
                    self.divined_as_wolf.append(int(content[1][6:8]))
                    self.emo.add(int(content[1][6:8]), "divined_as_werewolf")
                elif content[2] == RoleType.HUMAN.value:
                    self.divined_as_human.append(int(content[1][6:8]))
                    self.emo.add(int(content[1][6:8]), "i_divined_as_human")

    def talk_recognize_update(self, i, to, raw, line, who, interpreted, stattype):
        if stattype == "talk":
            content = interpreted.split()
            if len(content) > 1:
                if not content[1].startswith("Agent"):
                    content = content[1:]
                to = int(content[1][6:8])
            if interpreted == "" or interpreted == "NONE":
                return
            if content[0] == ActionType.COMINGOUT.value:
                if self.talk_turn < 3:
                    if int(content[1][6:8]) > self.player_size:
                        return
                    if content[2] == RoleType.VILLAGER.value:
                        return
                    if content[2] in [
                        RoleType.POSSESSED.value,
                        RoleType.WEREWOLF.value,
                    ]:
                        self.tryingPP.add(int(i[1]["agent"]))
                    if content[2] == RoleType.SEER.value:
                        self.seers.add(int(i[1]["agent"]))
                    self.greys -= {int(content[1][6:8])}
            if content[0] == ActionType.DIVINED.value:
                if self.talk_turn < 3:
                    if int(content[1][6:8]) > self.player_size:
                        return
                    self.greys -= {int(content[1][6:8])}
                    if self.has_CO_seer:
                        self.emo.add(who, "seems_to_be_fake_seer")
                    if content[2] == RoleType.HUMAN.value:
                        if int(content[1][6:8]) == self.base_info["agentIdx"]:
                            self.emo.add(who, "divined_me_human")
                        self.white.add(int(content[1][6:8]))
                        if (
                            self.base_info["day"] == 1
                            and int(content[1][6:8]) == self.base_info["agentIdx"]
                            and self.myrole == RoleType.WEREWOLF.value
                        ):
                            self.wrong_divine.add(int(i[1]["agent"]))
                    else:
                        if int(content[1][6:8]) == self.base_info["agentIdx"]:
                            self.seer_divined_me_as_werewolf.add(who)
                            self.emo.add(who, "divined_me_werewolf")
                        self.black.add(int(content[1][6:8]))
                        self.emo.add(int(content[1][6:8]), "divined_as_werewolf")
                        self.who_said_black[int(content[1][6:8])].append(who)
                        if (
                            self.base_info["day"] == 1
                            and self.player_size == 5
                            and int(content[1][6:8]) != self.base_info["agentIdx"]
                            and self.myrole == RoleType.WEREWOLF.value
                        ):
                            self.wrong_divine.add(int(i[1]["agent"]))
                    if self.base_info["day"] == 1:
                        self.seers.add(int(i[1]["agent"]))
                        self.emo.add(who, "seems_to_be_true_seer")
            if who == self.base_info["agentIdx"]:
                return
            else:
                if (
                    content[0] == ActionType.ESTIMATE.value
                    and content[2] == RoleType.WEREWOLF.value
                ):
                    if int(content[1][6:8]) == self.base_info["agentIdx"]:
                        self.emo.add(who, "estimated_me_werewolf")
                        self.estimated_me_as_werewolf.add(who)
                if (
                    content[0] == ActionType.ESTIMATE.value
                    and content[2] == RoleType.HUMAN.value
                ):
                    if (
                        int(content[1][6:8]) == self.base_info["agentIdx"]
                        and self.base_info["day"] == 1
                    ):
                        self.emo.add(who, "estimated_me_human")
                        if random.random() < 0.8:
                            self.estimated_me_as_human.add(who)
                if to == self.base_info["agentIdx"]:
                    if content[0] == ActionType.ASK_WHY_DOUBT.value:
                        self.asked_why_doubt.add(
                            (int(i[1]["agent"]), int(content[1][6:8]))
                        )
                    if (
                        content[0] == ActionType.ASK_WHY_DEVINE.value
                        and self.has_CO_seer
                    ):
                        self.asked_why_divine.add(
                            (int(i[1]["agent"]), int(content[1][6:8]))
                        )
                    if content[0] == ActionType.REQUEST_VOTE.value:
                        if int(content[1][6:8]) in self.vote_cand():
                            self.emo.add(int(content[1][6:8]), "requested_vote")
                            self.emo.add(who, "sync_vote")
                        else:
                            if who == self.base_info["agentIdx"]:
                                pass
                            if int(content[1][6:8]) == self.base_info["agentIdx"]:
                                pass
                            else:
                                self.emo.add(who, "desync_vote")

    def dayStart(self):
        self.talk_turn = 0
        self.whisper_turn = 0
        self.day = self.base_info["day"]
        self.check_alive()
        return None

    def grey_random(self):
        if len(self.greys) == 0:
            return int(random.choice(list(self.alive_without_me)))
        t = int(random.choice(list(self.greys)))
        return t

    def check_alive(self):
        self.alive = []
        for i in self.base_info["remainTalkMap"].keys():
            if self.base_info["statusMap"][i] == "ALIVE":
                self.alive.append(int(i))
        self.alive_without_me = list(
            set(self.alive) - {int(self.base_info["agentIdx"])}
        )
        self.greys = self.greys & set(self.alive_without_me)
        self.text_gen.check_alive(self.alive)

    def talk(self):
        self.talk_turn += 1
        self.check_alive()
        if self.day == 1 and self.talk_turn < 7:
            return self.text_gen.generate("declare_VOTE", [self.vote()])
        if self.day == 2:
            if self.talk_turn == 1:
                if len(self.seers & set(self.alive)) > 0:
                    return self.text_gen.generate("comingout_POSSESSED")
                else:
                    return self.text_gen.generate("declare_VOTE", [self.vote()])
            elif self.talk_turn <= 3:
                return self.text_gen.generate("declare_VOTE", [self.vote()])
        return "Over"

    def vote(self):
        return self.emo.hateest(self.vote_cand())

    def vote_cand(self):
        COs = self.seers & set(self.alive_without_me)
        non_COs = set(self.alive_without_me) - self.seers - set(self.divined_as_human)
        if len(set(self.divined_as_wolf) & set(self.alive)) > 0:
            return set(self.divined_as_wolf) & set(self.alive)
        if self.myrole in [RoleType.VILLAGER.value, RoleType.SEER.value]:
            if len(self.seers) < 3:
                if len(self.black & set(self.alive_without_me)) == 1:
                    return self.black & set(self.alive_without_me)
                if len(non_COs) > 0:
                    return non_COs
            else:
                if len(COs) > 0:
                    return COs
        if self.myrole in [RoleType.POSSESSED.value, RoleType.WEREWOLF.value]:
            if self.day >= 2 and self.myrole in [
                RoleType.POSSESSED.value,
                RoleType.WEREWOLF.value,
            ]:
                if len(self.tryingPP - set([self.base_info["agentIdx"]])) > 0:
                    cand = set(self.alive) - self.tryingPP
                    if len(cand) > 0:
                        return cand
            if len(self.seers) == 3:
                if self.base_info["day"] == 2:
                    if self.myrole == RoleType.POSSESSED.value:
                        cand = set(self.alive) & set(self.seers) - set(
                            [self.base_info["agentIdx"]]
                        )
                        if len(cand) > 0:
                            return cand
            if len(self.seers) == 1:
                if self.myrole == RoleType.WEREWOLF.value and len(COs) > 0:
                    return COs
            if len(self.seers) < 3:
                if self.base_info["day"] == 1 and len(non_COs):
                    if self.myrole == RoleType.POSSESSED.value:
                        return non_COs
                    elif self.myrole == RoleType.WEREWOLF.value:
                        return non_COs
                if self.myrole == RoleType.POSSESSED.value and len(COs) > 0:
                    return COs
                elif self.myrole == RoleType.WEREWOLF.value and len(non_COs) > 0:
                    return non_COs
            else:
                if self.myrole == RoleType.POSSESSED.value and len(non_COs) > 0:
                    return non_COs
                elif (
                    self.myrole == RoleType.WEREWOLF.value
                    and len(non_COs) > 0
                    and self.seers <= set(self.alive)
                ):
                    return non_COs
                else:
                    return COs
        if self.myrole in [RoleType.WEREWOLF.value, RoleType.POSSESSED.value]:
            cand = set(self.alive_without_me) - self.wrong_divine
            if len(cand) > 0:
                return cand
            return self.alive_without_me
        cand = list(set(self.alive_without_me) - set(self.divined_as_human))
        if self.player_size == 15:
            return cand
        return cand

    def attack(self):
        non_COs = (
            set(self.alive_without_me) - self.seers - {self.attacked_who_lastnight}
        )
        if len(non_COs) > 0:
            return random.choice(list(non_COs))
        return self.grey_random()

    def divine(self):
        self.check_alive()
        return self.grey_random()

    def finish(self):
        return
