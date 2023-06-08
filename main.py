import sys
import openai
import config
import runner
from datetime import datetime


class chat:
    def __init__(self, debug, save):
        openai.organization = config.ORG_ID
        openai.api_key = config.API_KEY

        self.debug = debug
        self.save = save
        self.prompt = ""
        self.system_prompt = "You produce python scripts based on prompts without adding 'python' to the first line"

        self.msgs = [{"role": "system", "content": self.system_prompt}]
        self.history = []
        self.history.append(self.msgs[0]["content"])

        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.msgs
        )
        self.token_amnts = [res["usage"]["total_tokens"]]

    def saveConvo(self) -> None:
        if not self.save or len(self.msgs) == 1:
            return
        d = datetime.now()
        d_str = str(datetime.date(d)) + "_" + \
            str(datetime.time(d).hour) + "-" + str(datetime.time(d).minute)
        with open("convos/convo_" + d_str + ".txt", "w") as fout:
            for m in self.msgs:
                fout.write(m["role"])
                fout.write(": ")
                fout.write(m["content"])
                fout.write("\n")

    def updateSystemPrompt(self, prompt) -> bool:
        if len(prompt.split(" ")) < 2:
            return False
        p = prompt[prompt.find(" ")+1:]
        if p:
            self.system_prompt = p
            self.msgs.append({"role": "system", "content": p})
            print("System prompt successfully added")
            return True
        return False

    def processPrompt(self, prompt) -> bool:
        if prompt == ":q":
            return False
        elif prompt.split(" ")[0] == ":system":
            if not self.updateSystemPrompt(prompt):
                print("Invalid system prompt")
            print("\n")
            return True
        elif prompt == ":debug" or prompt == ":d":
            self.debug = not self.debug
            print("Debug on" if self.debug else "Debug off")
            return True
        elif prompt == ":save" or prompt == ":s":
            self.save = not self.save
            print("Saving on" if self.save else "Saving off")
            return True
        elif prompt == ":run" or prompt == ":r":
            runner.run(self.history[len(self.history)-1])
            return True
        else:
            print("Command not recognized\n\n")
            return True

    def sendChat(self, prompt):
        self.msgs.append({"role": "user", "content": prompt})
        print("\n")
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.msgs
        )
        self.history.append(res["choices"][0]["message"]["content"])
        self.token_amnts.append(res["usage"]["total_tokens"])

        return res

    def run(self) -> bool:
        try:
            if self.debug:
                print("DEBUG> tokens: " + str(sum(self.token_amnts)))
                print("DEBUG> system: " + self.system_prompt)

            prompt = input(">")
            if not prompt:
                print("\n")
                return True
            if prompt[0] == ":":
                return self.processPrompt(prompt)

            chat_res = self.sendChat(
                prompt)["choices"][0]["message"]["content"]

            # ensure the chat call doesn"t exceed max tokens
            while sum(self.token_amnts) > 2048:
                self.token_amnts.pop(0)
                self.msgs.pop(0)

            self.msgs.append({"role": "assistant", "content": chat_res})
            print(chat_res)
            print("\n")

            return True
        except KeyboardInterrupt:
            self.saveConvo()


def handleArgs(argv) -> dict:
    args = {"debug": False, "save": False}
    for a in argv:
        if a == "-d":
            args["debug"] = True
        elif a == "-s":
            args["save"] = True
    return args


if __name__ == "__main__":
    args = handleArgs(sys.argv)

    c = chat(args["debug"], args["save"])
    while c.run():
        pass
    c.saveConvo()
