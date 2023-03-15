#Addding NEW

from datetime import datetime
#сollecting tasks from site to dataframe
table = []
url = 'https://codeforces.com/problemset/page/1?order=BY_RATING_ASC&locale=ru'
page = requests.get(url)
maxindex = BeautifulSoup(page.text, "html.parser").findAll('span', class_='page-index')
maxpage = int(maxindex[-1].text)


for numpage in range(1, maxpage):
  url = 'https://codeforces.com/problemset/page/'+str(numpage)+'?order=BY_RATING_ASC&locale=ru'
  page = requests.get(url)
  allProblems = BeautifulSoup(page.text, "html.parser").findAll('tr')
  for problem in allProblems[1:-1]:
    entities = problem.text.split('\n')
    real_entities = []
    for entity in entities:
      if entity.strip()!='':
        real_entities.append(entity.strip())
    real_entities[2:-2] = [x.replace(',', '') for x in real_entities[2:-2]]
    if real_entities[-2].endswith('00'): #если 
      table.append(['https://codeforces.com/problemset/problem/'+real_entities[0][:-1]+'/'+real_entities[0][-1], real_entities[0], real_entities[1], real_entities[2:-2], int(real_entities[-2]), int(real_entities[-1][1:])])
    else:
      #print(real_entities) #we dropped special series of task 'labirint', which haven't statistics about users
      pass
df = pd.DataFrame(table, columns = ['link', 'num', 'name', 'themes', 'rating', 'solved'])

import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/code_forces')
except:
    print('Can`t establish connection to database')
if conn:
  cursor = conn.cursor() 
  added = 0
  updated = 0
  for i in df.index:
    cursor.execute("""SELECT id FROM task_table WHERE (id = '%s')""" % df.loc[i,'num'])
    z = cursor.fetchall()
    if len(z) == 0:
      added+=1
      cursor.execute("""insert into task_table (id, link, name, themes, rating, solved, main_theme, group_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (df.loc[i,'num'], df_.loc[i,'link'], df.loc[i,'name'], ' '.join(df.loc[i,'themes']), int(df.loc[i,'rating']), int(df.loc[i,'solved']), 'NAN', 'NAN'))
    else:
      cursor.execute("""SELECT solved FROM task_table WHERE (id = '%s')""" % df.loc[i,'num'])
      solved_old = cursor.fetchall()[0][0]
      if solved_old != df.loc[i, 'solved']:
        updated+=1
        cursor.execute("""UPDATE task_table SET solved = {} WHERE id = '{}'""".format(df.loc[i, 'solved'], df.loc[i, 'num'])) 
  with open("log.txt", 'a') as my_file:
    my_file.write('inserted %s'%str(added) + ' tasks at ' + str(datetime.now())+'\n')
    my_file.write('updated %s'%str(updated) + ' rows at ' + str(datetime.now())+'\n')
  conn.commit()
  conn.close()