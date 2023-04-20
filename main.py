import sys
import openai
import config
from datetime import datetime

openai.organization = config.ORG_ID
openai.api_key = config.API_KEY

def saveConvo():
  if len(msgs) == 1:
    return
  d = datetime.now()
  d_str = str(datetime.date(d)) + '_' + str(datetime.time(d).hour) + '-' + str(datetime.time(d).minute)
  with open("convos/convo_" + d_str + '.txt', "w") as fout:
    for m in msgs:
      fout.write(m['role'])
      fout.write(': ')
      fout.write(m['content'])
      fout.write('\n')

def run():
  try:
    if debug:
      print('DEBUG> tokens: ' + str(sum(token_amnts)))

    prompt = input(">")
    if prompt == 'q':
      return False
    
    msgs.append({"role":"user", "content":prompt})
    print("\n")

    res = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=msgs
    )

    chat_res = res['choices'][0]['message']['content']
    token_amnts.append(res['usage']['total_tokens'])

    # ensure the chat call doesn't exceed max tokens
    while sum(token_amnts) > 2048:
      token_amnts.pop(0)
      msgs.pop(0)

    msgs.append({'role':'assistant', 'content':chat_res})
    print(chat_res)
    print('\n')

    return True
  except KeyboardInterrupt:
    saveConvo()

if __name__ == "__main__":
  debug = False
  if len(sys.argv) > 1:
    debug = True if sys.argv[1] == '-d' else False

  prompt = ''
  msgs = [{'role':'system', 'content':'You are a friendly conversationalist'}]
  res = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
      messages=msgs
    )
  token_amnts = [res['usage']['total_tokens']]

  while run():
    pass

  saveConvo()
