import pandas as pd
import random


class TextGenerator(object):
    def __init__(self,):
        import os

        # load template
        base = os.path.dirname(os.path.abspath(__file__))
        name = os.path.normpath(os.path.join(base, "script_template.csv"))
        self.df = pd.read_csv(name, engine="python")
        self.df["used"] = 0

        # logging
        print(len(self.df), "scripts loaded")

    def gameInitialize(self, myID, player_size):
        """
        initialize game with specified player ID (myself)
        """
        self.me = myID
        self.player_size = player_size

    def check_alive(self, alive):
        self.alive = alive

    def generate(self, prot, args=[]):
        """
        generates text with prot.
        """
        # fill args with randomly selected agents
        while len(args) < 2:
            cand = set(self.alive) - set(args) - set([self.me])
            if not cand:
                return "SKIP"
            print(cand, args, self.me)
            args.append(random.choice(list(cand)))

        print(args)
        args = list(map(lambda x: "Agent[" + "{0:02d}".format(x) + "]", args))
        print(args)

        t = self.df[self.df.type == prot]
        s = t.sort_values("used")

        try:
            chosen = s.iloc[0]
        except Exception:
            return "SKIP"
        ans = chosen.text

        # count 'used'
        self.df.loc[chosen.name, "used"] += 1
        if pd.isnull(ans) or type(ans) is not str:
            return "SKIP"
        # replace [-1], [0], [1] with agents
        ans = (
            ans.replace("[-1]", "Agent[" + "{0:02d}".format(self.me) + "]")
            .replace("[0]", args[0])
            .replace("[1]", args[1])
        )

        print("RETURN::::", ans)

        return ans
