import parse_content
import re
from util import ActionType
from util import RoleType


def log_analytics_main(self, i, stattype):
    line = i[1]
    who = int(line["agent"])
    parsed_list = parse_content.parse_text(line["text"])
    raw = line["text"]
    for j in range(len(parsed_list)):
        try:
            log_analytics(self, i, raw, line, who, parsed_list[j], stattype, j)
        except Exception as e:
            print(e) 


def log_analytics(self, i, raw, line, who, uttr, stattype, j):
    if stattype == "talk":
        content = uttr.split()
        if self.agent_list[1] == 1:
            if "Skip" not in content and "Over" not in content:
                self.agent_list[3] -= {who}
        if re.search(ActionType.REQUEST.value, raw) == None:
            pass
        else:
            if re.search(ActionType.DIVINATION.value, raw) == None:
                pass
            else:
                self.request_divination_agent.add(who)
        if re.search(ActionType.REQUEST.value, raw) == None:
            pass
        else:
            if re.search(ActionType.COMINGOUT.value, raw) == None:
                pass
            else:
                if re.search(RoleType.SEER.value, raw) == None:
                    pass
                else:
                    self.request_comingout_seer_agent.add(who)
        if re.search(ActionType.REQUEST.value, raw) == None:
            pass
        else:
            if re.search(ActionType.GUARD.value, raw) == None:
                pass
            else:
                self.request_guard_agent.add(who)
        if re.search(ActionType.REQUEST.value, raw) == None:
            pass
        else:
            if re.search("ANY", raw) == None:
                pass
            else:
                if re.search(ActionType.VOTE.value, raw) == None:
                    pass
                else:
                    self.request_any_vote_agent.add(who)
                    if re.search("AND", raw) == None:
                        self.request_any_vote_non_and_agent.add(who)
        if content[0] == ActionType.ESTIMATE.value:
            if content[2] == RoleType.WEREWOLF.value:
                self.estimate_werewolf_agent.add(who)
            else:
                self.estimate_non_werewolf_agent.add(who)
        if content[0] == ActionType.ESTIMATE.value:
            if content[2] == RoleType.VILLAGER.value:
                self.estimate_villager_agent.add(who)
        if content[0] == ActionType.ESTIMATE.value:
            self.estimate_agent.add(who)
        if re.search("AND", raw) == None:
            pass
        else:
            if re.search("DAY", raw) == None:
                pass
            else:
                if re.search(ActionType.DIVINED.value, raw) == None:
                    pass
                else:
                    self.and_day_divined_agent.add(who)
        if re.search("DAY", raw) == None:
            pass
        else:
            self.day_agent.add(who)
            if re.search(ActionType.DIVINED.value, raw) == None:
                pass
            else:
                if not j and not re.search("BECAUSE", raw):
                    day_count = raw.count("DAY ")
                    day_start = []
                    start = 0
                    for _ in range(day_count):
                        start = raw.find("DAY ", start)
                        day_start.append(start)
                        start += 1
                    max_length = len(raw)
                    for i in day_start:
                        if i + 4 <= max_length:
                            tmp_day_num = str(raw[i + 4])
                        if re.match("[0-9]", raw[i + 5]):
                            if i + 5 <= max_length:
                                tmp_day_num = tmp_day_num + str(raw[i + 5])
                        self.divine_day[who].append(int(tmp_day_num))
        if re.search("DAY", raw) == None:
            pass
        else:
            self.day_agent.add(who)
            if re.search(ActionType.IDENTIFIED.value, raw) == None:
                pass
            else:
                if not j and not re.search("BECAUSE", raw):
                    day_count = raw.count("DAY ")
                    day_start = []
                    start = 0
                    for _ in range(day_count):
                        start = raw.find("DAY ", start)
                        day_start.append(start)
                        start += 1

                    max_length = len(raw)
                    for i in day_start:
                        if i + 4 <= max_length:
                            tmp_day_num = str(raw[i + 4])
                        if re.match("[0-9]", raw[i + 5]):
                            if i + 5 <= max_length:
                                tmp_day_num = tmp_day_num + str(raw[i + 5])
                        self.identify_day[who].append(int(tmp_day_num))
        if re.search("AND", raw) == None:
            pass
        else:
            self.and_agent.add(who)
        if re.search("XOR", raw) == None:
            pass
        else:
            self.xor_agent.add(who)
        if re.search("NOT", raw) == None:
            pass
        else:
            self.not_agent.add(who)
        if re.search("BECAUSE", raw) == None:
            pass
        else:
            if raw[:5] == "Agent":
                self.Camellia_because_agent.add(who)
            else:
                self.because_agent.add(who)
        if re.search(ActionType.REQUEST.value, raw) == None:
            pass
        else:
            self.request_agent.add(who)
        # TODO: Fix typo
        if re.search(ActionType.ESTIMATE.value, raw) == None:
            pass
        else:
            self.estimate_agent.add(who)
        if len(content) > 1:
            if not content[1].startswith("Agent"):
                return
            to = int(content[1][6:8])
        if uttr == "" or uttr == "NONE":
            return
        if content[0] == ActionType.COMINGOUT.value:
            if int(content[1][6:8]) > self.player_size:
                return

            if content[2] == RoleType.SEER.value:
                self.COs.add(who)
            elif content[2] == RoleType.MEDIUM.value and who not in self.COm:
                self.COm.append(who)
                self.result_all_mediums[who] = {"black": set(), "white": set()}
            elif content[2] == RoleType.VILLAGER.value:
                self.COv.add(who)
            elif content[2] == RoleType.POSSESSED.value:
                self.COp.add(who)
            elif content[2] == RoleType.BODYGUARD.value:
                self.COg.add(who)

        elif content[0] == ActionType.DIVINED.value:
            # DIVINED
            if self.talk_turn < 3:
                if int(content[1][6:8]) > self.player_size:
                    return
                if who in self.divineders:
                    if content[2] == RoleType.HUMAN.value:
                        self.result_all_divineders[who]["white"].add(to)
                        self.greys -= {to}
                    elif content[2] == RoleType.WEREWOLF.value:
                        self.result_all_divineders[who]["black"].add(to)
                        self.greys -= {to}
                else:
                    self.divineders.add(who)
                    self.result_all_divineders[who] = {"black": set(), "white": set()}
                    if content[2] == RoleType.HUMAN.value:
                        self.result_all_divineders[who]["white"].add(to)
                        self.greys -= {to}
                    elif content[2] == RoleType.WEREWOLF.value:
                        self.result_all_divineders[who]["black"].add(to)
                        self.greys -= {to}

        elif content[0] == ActionType.IDENTIFIED.value:
            # IDENTIFIED
            if self.talk_turn < 3:
                if int(content[1][6:8]) > self.player_size:
                    print("NOT WORKING!! ERRORCODE:TALKIDENTCONT")
                    return
                if who in self.COm:
                    if content[2] == RoleType.HUMAN.value:
                        self.result_all_mediums[who]["white"].add(to)
                    elif content[2] == RoleType.WEREWOLF.value:
                        self.result_all_mediums[who]["black"].add(to)
                else:
                    self.COm.append(who)
                    self.result_all_mediums[who] = {"black": set(), "white": set()}
                    if content[2] == RoleType.WEREWOLF.value:
                        self.result_all_mediums[who]["black"].add(to)
                    elif content[2] == RoleType.HUMAN.value:
                        self.result_all_mediums[who]["white"].add(to)

        elif content[0] == ActionType.VOTE.value:
            # VOTE
            if int(content[1][6:8]) > self.player_size:
                return
            if 1 <= who and who <= 15:
                if who == int(self.base_info["agentIdx"]):
                    return
                self.talk_vote_list[who - 1] = int(content[1][6:8])
            else:
                pass

        if who == self.base_info["agentIdx"]:
            return
    elif stattype == ActionType.VOTE.value:
        if line["idx"] in range(1, 16):
            if line["idx"] == int(self.base_info["agentIdx"]):
                return
            self.vote_list[line["idx"] - 1] = who
            return
    elif stattype == "execute":
        self.exed_players.append(who)
        self.alive -= {who}
        self.greys -= {who}
    elif stattype == "dead":
        self.attack_judge = 1
        self.ated_players.append(who)
        self.alive -= {who}
        self.greys -= {who}
    elif stattype == "whisper":
        content = uttr.split()
        if len(content) > 1:
            if not content[1].startswith("Agent"):
                return
            to = int(content[1][6:8])
        if uttr == "" or uttr == "NONE":
            return
        if content[0] == ActionType.COMINGOUT.value:
            if int(content[1][6:8]) > self.player_size:
                return
            if content[2] == RoleType.SEER.value:
                self.W_COs.add(who)
            if content[2] == RoleType.MEDIUM.value:
                self.W_COm.add(who)
            if content[2] == RoleType.BODYGUARD.value:
                self.W_COg.add(who)
        if content[0] == ActionType.VOTE.value:
            if int(content[1][6:8]) > self.player_size:
                return
            if 1 <= who and who <= 15:
                if who == int(self.base_info["agentIdx"]):
                    return
                self.W_vote_cand.add(int(content[1][6:8]))
            else:
                pass
        if content[0] == "ATTACK":
            if int(content[1][6:8]) > self.player_size:
                return
            if 1 <= who and who <= 15:
                if who == int(self.base_info["agentIdx"]):
                    return
                self.W_attack_cand.add(int(content[1][6:8]))
            else:
                pass
    elif stattype == "finish":
        content = uttr.split()
        if len(content) > 1:
            if not content[1].startswith("Agent"):
                return
            to = int(content[1][6:8])
        if uttr == "" or uttr == "NONE":
            return
        if content[0] == ActionType.COMINGOUT.value:
            if int(content[1][6:8]) > self.player_size:
                return
            if who == self.agent_list[2][0]:
                return
            if content[2] == RoleType.VILLAGER.value:
                return
            if content[2] == RoleType.SEER.value:
                return
            if content[2] == RoleType.MEDIUM.value:
                if not self.agent_list[2][8]:
                    if who in set(self.COm) & self.day2_alive:
                        if (
                            not self.result_all_mediums[who]["white"]
                            and not self.result_all_mediums[who]["black"]
                        ):
                            if who not in self.agent_list[2]:
                                self.agent_list[2][8] = who
                                self.agent_list[6] |= {self.agent_list[2][8]}
                                self.agent_list[7] |= {self.agent_list[2][8]}
            if content[2] == RoleType.BODYGUARD.value:
                return
            if content[2] == RoleType.POSSESSED.value:
                if who in self.COs | self.divineders:
                    self.agent_list[6] |= {who}
                    self.agent_list[4] -= {who}
            if content[2] == RoleType.WEREWOLF.value:
                if who in self.COs | self.divineders:
                    self.agent_list[7] |= {who}
                    self.agent_list[4] -= {who}
