import openai
import config
from datetime import datetime

openai.organization = config.ORG_ID
openai.api_key = config.API_KEY

def saveConvo():
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
    msgs.append({"role":"assistant", "content":chat_res})

    print(chat_res + "\n")
    return True

  except KeyboardInterrupt:
    saveConvo()

if __name__ == "__main__":
  prompt = ""
  msgs = [{"role":"system", "content":"You are a friendly conversationalist"},]
  res = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=msgs
    )

  while run():
    pass

  saveConvo()
