import sys
import openai
import config
from datetime import datetime

class chat:
  def __init__(self, debug):
    openai.organization = config.ORG_ID
    openai.api_key = config.API_KEY

    self.debug = debug
    self.prompt = ''
    self.msgs = [{'role':'system', 'content':'You are a friendly conversationalist'}]
    res = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
      messages=self.msgs
    )
    self.token_amnts = [res['usage']['total_tokens']]

  def saveConvo(self):
    if len(self.msgs) == 1:
      return
    d = datetime.now()
    d_str = str(datetime.date(d)) + '_' + str(datetime.time(d).hour) + '-' + str(datetime.time(d).minute)
    with open("convos/convo_" + d_str + '.txt', "w") as fout:
      for m in self.msgs:
        fout.write(m['role'])
        fout.write(': ')
        fout.write(m['content'])
        fout.write('\n')

  def run(self):
    try:
      if self.debug:
        print('DEBUG> tokens: ' + str(sum(self.token_amnts)))

      prompt = input(">")
      if prompt == 'q':
        return False
      
      self.msgs.append({"role":"user", "content":prompt})
      print("\n")

      res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=self.msgs
      )

      chat_res = res['choices'][0]['message']['content']
      self.token_amnts.append(res['usage']['total_tokens'])

      # ensure the chat call doesn't exceed max tokens
      while sum(self.token_amnts) > 2048:
        self.token_amnts.pop(0)
        self.msgs.pop(0)

      self.msgs.append({'role':'assistant', 'content':chat_res})
      print(chat_res)
      print('\n')

      return True
    except KeyboardInterrupt:
      self.saveConvo()

if __name__ == "__main__":
  debug = False
  if len(sys.argv) > 1:
    debug = True if sys.argv[1] == '-d' else False

  c = chat(debug)

  while c.run():
    pass
  c.saveConvo()
