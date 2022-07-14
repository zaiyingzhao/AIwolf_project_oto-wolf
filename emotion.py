from typing import List


class Emotion:
    def __init__(self, player_ids: List[int]):
        self.have_entered_ppmode = False
        self.reasons_default = {
            "i_divined_as_human": 99,
            "i_divined_as_human(fake)": 6,
            "divined_me_human": 5,
            "voted_who_i_hate": 1,
            "seems_to_be_true_seer": 2,
            "estimated_me_human": 5,
            "sync_vote": -3,
            "desync_vote": -1,
            "estimated_me_werewolf": -1,
            "requested_vote": -2,
            "divined_as_werewolf": 1,
            "seems_to_be_fake_seer": -4,
            "you_said_black_but_not": -10,
            "voted_me": -3,
            "voted_who_i_love": -8,
            "divined_me_werewolf": -5,
            "i_divined_as_werewolf(fake)": -29,
            "i_divined_as_werewolf": -99,
        }
        self.reasons_PP = {
            "i_divined_as_human": 99,
            "i_divined_as_human(fake)": 0,
            "divined_me_human": -1,
            "voted_who_i_hate": 3,
            "seems_to_be_true_seer": -7,
            "estimated_me_human": 3,
            "sync_vote": 1,
            "desync_vote": -1,
            "estimated_me_werewolf": -2,
            "requested_vote": -2,
            "divined_as_werewolf": 0,
            "seems_to_be_fake_seer": 0,
            "you_said_black_but_not": 30,
            "voted_me": -8,
            "voted_who_i_love": 0,
            "divined_me_werewolf": -6,
            "i_divined_as_werewolf(fake)": 0,
            "i_divined_as_werewolf": -99,
        }
        self.reasons = self.reasons_default
        self.emotion = {}
        self.myrole_appearance = "VILLAGER"
        self.myrole = "VILLAGER"
        for player_id in player_ids:
            self.emotion[player_id] = {key: 0 for key in self.reasons.keys()}
            self.emotion[player_id] = dict(
                zip(self.reasons.keys(), [0] * len(self.reasons))
            )

    def enter_ppmode(self):
        """
        self.reasons["seems_to_be_true_seer"] = -4
        self.reasons["seems_to_be_fake_seer"] = 2
        """
        print("entering PP mode")
        self.reasons = self.reasons_PP

    def leave_ppmode(self):
        print("leaving PP mode")
        self.reasons = self.reasons_default

    def add(self, player_id: int, reason):
        self.emotion[player_id][reason] += 1

    def loveest(self, candidates):
        # if in PP mode, then evaluation is reversed
        player2emotion = {player: 0 for player in candidates}
        for player in player2emotion.keys():
            for reason_key, reason_val in self.reasons.items():
                player2emotion[player] += self.emotion[player][reason_key] * reason_val
        max_emo = -1000000
        for player, emo_val in self.emotion.items():
            if max_emo < emo_val:
                # update
                max_emo = emo_val
                target_player = player
        return target_player

    def hateest(self, candidates):
        # if in PP mode, then evaluation is reversed
        player2emotion = {player: 0 for player in candidates}
        for player in player2emotion.keys():
            for reason_key, reason_val in self.reasons.items():
                if (
                    self.myrole in ["POSSESSED", "WEREWOLF"]
                    and reason_key == "divined_as_werewolf"
                ):
                    # skip for POSSESSED and WEREWOLF
                    continue
                player2emotion[player] += self.emotion[player][reason_key] * reason_val
        min_emo = 1000000
        target_player = 0
        for player, emo_val in player2emotion.items():
            if min_emo > emo_val:
                # update
                min_emo = emo_val
                target_player = player
        return target_player

    def hate_reason(self, who):
        reason2emotion = {
            reason_key: self.emotion[who][reason_key] * reason_val
            for reason_key, reason_val in self.reasons.items()
        }
        min_emo = 1000000
        target_reason = "none"
        for reason_key, reason_val in self.reasons.items():
            if reason_val > 0 or reason2emotion[reason_key] == 0:
                continue
            if min_emo > reason2emotion[reason_key]:
                # update
                min_emo = reason2emotion[reason_key]
                target_reason = reason_key
        return target_reason

    def love_reason(self, who):
        reason2emotion = {
            reason_key: self.emotion[who][reason_key] * reason_val
            for reason_key, reason_val in self.reasons.items()
        }
        max_emo = -1000000
        target_reason = "none"
        is_ok_to_be_honest = True
        # 嘘占い結果を出しているなら、本当の占い結果は無視しなければ
        for emo_key in self.emotion.keys():
            if self.emotion[emo_key]["i_divined_as_werewolf(fake)"] != 0:
                is_ok_to_be_honest = False
            if self.emotion[emo_key]["i_divined_as_human(fake)"] != 0:
                is_ok_to_be_honest = False

        for reason_key, reason_val in self.reasons.items():
            if reason_val < 0 or reason2emotion[reason_key] == 0:
                continue
            if is_ok_to_be_honest == False and reason_key == "i_divined_as_human":
                continue

            if self.myrole_appearance == "SEER" and reason_key in [
                "seems_to_be_true_seer",
                "divined_me_human",
            ]:
                continue

            if max_emo < reason2emotion[reason_key]:
                # update
                max_emo = reason2emotion[reason_key]
                target_reason = reason_key
        return target_reason


class EmotionWerewolf:
    def __init__(self, player_ids: List[int]):
        self.have_entered_ppmode = False
        self.reasons_default = {
            "i_divined_as_human": 99,
            "i_divined_as_human(fake)": 4,
            "divined_me_human": 4,
            "voted_who_i_hate": 5,
            "seems_to_be_true_seer": 0,
            "estimated_me_human": 1,
            "sync_vote": 1,
            "desync_vote": 1,
            "estimated_me_werewolf": -1,
            "requested_vote": -2,
            "divined_as_werewolf": -7,
            "seems_to_be_fake_seer": -4,
            "you_said_black_but_not": -4,
            "voted_me": -10,
            "voted_who_i_love": -11,
            "divined_me_werewolf": -8,
            "i_divined_as_werewolf(fake)": -28,
            "i_divined_as_werewolf": -99,
        }
        self.reasons_PP = {
            "i_divined_as_human": 99,
            "i_divined_as_human(fake)": 0,
            "divined_me_human": -1,
            "voted_who_i_hate": 3,
            "seems_to_be_true_seer": -7,
            "estimated_me_human": 3,
            "sync_vote": 1,
            "desync_vote": -1,
            "estimated_me_werewolf": -2,
            "requested_vote": -2,
            "divined_as_werewolf": 0,
            "seems_to_be_fake_seer": 0,
            "you_said_black_but_not": 30,
            "voted_me": -8,
            "voted_who_i_love": 0,
            "divined_me_werewolf": -6,
            "i_divined_as_werewolf(fake)": 0,
            "i_divined_as_werewolf": -99,
        }
        self.reasons = self.reasons_default
        self.emotion = {}
        self.myrole_appearance = "VILLAGER"
        self.myrole = "VILLAGER"
        for player_id in player_ids:
            self.emotion[player_id] = {key: 0 for key in self.reasons.keys()}
            self.emotion[player_id] = dict(
                zip(self.reasons.keys(), [0] * len(self.reasons))
            )

    def enter_ppmode(self):
        """
        self.reasons["seems_to_be_true_seer"] = -4
        self.reasons["seems_to_be_fake_seer"] = 2
        """
        print("entering PP mode")
        self.reasons = self.reasons_PP

    def leave_ppmode(self):
        print("leaving PP mode")
        self.reasons = self.reasons_default

    def add(self, player_id: int, reason):
        self.emotion[player_id][reason] += 1

    def loveest(self, candidates):
        # if in PP mode, then evaluation is reversed
        player2emotion = {player: 0 for player in candidates}
        for player in player2emotion.keys():
            for reason_key, reason_val in self.reasons.items():
                player2emotion[player] += self.emotion[player][reason_key] * reason_val
        max_emo = -1000000
        for player, emo_val in self.emotion.items():
            if max_emo < emo_val:
                # update
                max_emo = emo_val
                target_player = player
        return target_player

    def hateest(self, candidates):
        # if in PP mode, then evaluation is reversed
        player2emotion = {player: 0 for player in candidates}
        for player in player2emotion.keys():
            for reason_key, reason_val in self.reasons.items():
                # 役職によってはいくつかの理由をスルー
                if (
                    self.myrole in ["POSSESSED", "WEREWOLF"]
                    and reason_key == "divined_as_werewolf"
                ):
                    continue
                player2emotion[player] += self.emotion[player][reason_key] * reason_val
        min_emo = 1000000
        target_player = 0
        for player, emo_val in player2emotion.items():
            if min_emo > emo_val:
                # update
                min_emo = emo_val
                target_player = player
        return target_player

    def hate_reason(self, who):
        reason2emotion = {
            reason_key: self.emotion[who][reason_key] * reason_val
            for reason_key, reason_val in self.reasons.items()
        }
        min_emo = 1000000
        target_reason = "none"
        for reason_key, reason_val in self.reasons.items():
            if reason_val > 0 or reason2emotion[reason_key] == 0:
                continue
            if min_emo > reason2emotion[reason_key]:
                # update
                min_emo = reason2emotion[reason_key]
                target_reason = reason_key
        return target_reason

    def love_reason(self, who):
        reason2emotion = {
            reason_key: self.emotion[who][reason_key] * reason_val
            for reason_key, reason_val in self.reasons.items()
        }
        max_emo = -1000000
        target_reason = "none"
        is_ok_to_be_honest = True
        # 嘘占い結果を出しているなら、本当の占い結果は無視しなければ
        for emo_key in self.emotion.keys():
            if self.emotion[emo_key]["i_divined_as_werewolf(fake)"] != 0:
                is_ok_to_be_honest = False
            if self.emotion[emo_key]["i_divined_as_human(fake)"] != 0:
                is_ok_to_be_honest = False

        for reason_key, reason_val in self.reasons.items():
            if reason_val < 0 or reason2emotion[reason_key] == 0:
                continue
            # 嘘占い結果を出しているなら、本当の占い結果は無視しなければ
            if is_ok_to_be_honest == False and reason_key == "i_divined_as_human":
                continue

            # 占い師なら他を真占いだと思ってるわけがない
            if self.myrole_appearance == "SEER" and reason_key in [
                "seems_to_be_true_seer",
                "divined_me_human",
            ]:
                continue

            if max_emo < reason2emotion[reason_key]:
                # update
                max_emo = reason2emotion[reason_key]
                target_reason = reason_key
        return target_reason
