import praw, sys, re, time, datetime
NUM_COMMENTS = 1

#if len(sys.argv) < 3:
#	print("usage: python "+sys.argv[0]+" [num_posts_per_sub] [subreddits]")
#	print("we will read posts if they have at least "+str(NUM_COMMENTS)+" comments!")
#	sys.exit()

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

GOOD_ADJECTIVES = {"favorite","abundant","acceptable","accurate","adaptable","addicted","adorable","adventurous","amazing","ambitious","amused","amusing","astonishing","attractive","awesome","beautiful","beneficial","best","better","bright","cool","curious","cute","dazzling","distinct","elated","elegant","encouraging","entertaining","enthusiastic","excellent","excited","exciting","fabulous","fancy","fantastic","fascinated","flawless","funny","good","gorgeous","great","handy","happy","helpful","hilarious","important","incredible","inexpensive","interesting","likeable","lovely","lucky","magnificent","majestic","marvelous","necessary","new","nice","nifty","obtainable","outstanding","overjoyed","perfect","pleasant","powerful","precious","premium","pretty","proud","smart","special","spectacular","splendid","squealing","stimulating","strange","substantial","successful","superb","sweet","talented","tasteful","tasty","terrific","thankful","therapeutic","thoughtful","unique","upbeat","useful","valuable","wanting","well-made","wise","wonderful","worth","yielding","promising","yummy","fun","trustworthy","thankful","needed","cheap","consistent"}

NEUTRAL_ADJECTIVES = {"concerned","clever","crazy","creepy","different","difficult","early","efficient","enormous","fearful","fine","learned","massive","mysterious","needless","quick","shocked","shocking","sick","silent","weird","ubiquitous","unusual","wild",}

BAD_ADJECTIVES = {"abhorrent","abnormal","abrupt","afraid","aggressive","ambiguous","angry","annoyed","annoying","anxious","apathetic","ashamed","average","awful","bad","bitter","bizarre","boring","broken","cheaply","confused","damaging","dangerous","dark","dead","depressing","debunked","disastrous","disgusted","disgusting","disturbed","doubtful","dramatic","dry","dull","dumb","embarrassed","empty","envious","expensive","false","frightened","frightening","hateful","heartbreaking","hesitant","hideous","horrible","hurt","idiotic","ignorant","lacking","lame","late","laughable","lazy","ludicrous","naive","opposite","outrageous","painful","pathetic","plain","pointless","pricey","questionable","sad","salty","scary","spiteful","stupid","tacky","tasteless","terrible","thoughtless","threatening","tiresome","typical","ugliest","ugly","undesirable","unhealthy","uninterested","unnatural","unsuitable","unused","unwieldy","upset","uptight","useless","wasteful","well-off","worried","worthless","wrong",}

reddit = praw.Reddit(client_id='@@SET YOUR REDDIT APP ID@@',
           client_secret='@@SET YOUR REDDIT APP SECRET@@',
           user_agent='linux:com.athconnect.subeval (by /u/@@SET YOUR USERNAME@@)')
            
if reddit.read_only:
  print("Evaluating subreddits:")
else:
	print("..actually nah.")
	sys.exit()
	
global numGood
numGood = 0
global numBad
numBad = 0

def get_adjs(message):
  global numGood, numBad
  wordList = re.sub("[^\w]", " ", message).split()
  adjs = ["|"]
  prev_word = ""
  for word in wordList:
    if word.lower() in adjs:
      continue
    color = ""
    if word.lower() in GOOD_ADJECTIVES:
      color = bcolors.OKGREEN
      if prev_word.endswith(("not","n't")):
        color = bcolors.FAIL
      adjs.append(color + word.lower() + bcolors.ENDC)
    if word.lower() in NEUTRAL_ADJECTIVES:
      color = bcolors.WARNING
      adjs.append(color + word.lower() + bcolors.ENDC)
    if word.lower() in BAD_ADJECTIVES:
      color = bcolors.FAIL
      if prev_word.endswith(("not","n't")):
        color = bcolors.OKGREEN
      adjs.append(color + word.lower() + bcolors.ENDC)
    if (word.lower() != "the") | (word.lower() != "a"):
      prev_word = word.lower()
    if color == str(bcolors.OKGREEN):
      numGood = numGood + 1
    if color == str(bcolors.FAIL):
      numBad = numBad + 1
  adjs.append("\n")
  if len(adjs) == 2:
    adjs = []
  return adjs
    
while 1 == 1:
	try:
		print("\n"*80)
		print("updating subreddits...")
	
		# update subs to watch
		sublist = open("sublist.txt","r")
		subs = []
		for line in sublist.readlines():
			if not line.startswith("#"):
				subs.append(line.replace("\n",""))
		sublist.close()

		# print out scores
		sc = len(subs)
		for i in range(0,sc):
			b = 0.0
			g = 0.0
			# let's only care if they have at least NUM_COMMENTS comments
			for submission in reddit.subreddit(subs[i]).new(limit=int(sys.argv[1])):
				submission.comments.replace_more(limit=0)
				comments = list(submission.comments)
				if len(comments) >= NUM_COMMENTS:
					adjs = []
				for comment in comments:
					# extract adjectives and keep track of how many times each is used
					adjs.extend(get_adjs(comment.body))
					g += numGood
					b += numBad
					numGood = 0
					numBad = 0
					if len(adjs) > 0:
				    	#print("") # uncomment to print sub names
				    	#print("(" + str(len(comments)) + ") " + submission.title)
						adjstring = " "
						for a in adjs:
							adjstring = adjstring + a + " "
			        	#print(adjstring)
					
			# write to file
			color = bcolors.OKGREEN
			if b == 0:
				colors = bcolors.OKBLUE
			else:
				if g / (g+b) < 0.5:
					color = bcolors.FAIL
				elif g / (g+b) < 0.7:
					color = bcolors.WARNING
				elif g / (g+b) > 0.9:
					color = bcolors.OKBLUE
			print(subs[i]+": +"+str(int(g))+" -"+str(int(b))+" => "+color+str(int(g-b))+" point(s)"+bcolors.ENDC)
			today = datetime.datetime.now()
			with open(subs[i]+"_stats.csv","a") as file:
				# a bar for rating, a bar for comment volume
				rating = int(10*g/(g+b))
				if rating <= 0:
					bar = "[xxxxx     ]"
				if rating == 1:
					bar = "[ xxxx     ]"
				if rating == 2:
					bar = "[  xxx     ]"
				if rating == 3:
					bar = "[   xx     ]"
				if rating == 4:
					bar = "[    x     ]"
				if rating == 5:
					bar = "[     o    ]"
				if rating == 6:
					bar = "[     oo   ]"
				if rating == 7:
					bar = "[     ooo  ]"
				if rating == 8:
					bar = "[     oooo ]"
				if rating >= 9:
					bar = "[     ooooo]"
				# this really represents average num of comments in the last x # of posts
				volume = "["+"v"*(int((g+b)/8))
				file.write(today.strftime("%m/%d/%Y %H:%M")+","+str(int(g-b))+",  \t,"+bar+" "+volume+"\n")
		
		# end loop
		print("good luck have fun :)")
		time.sleep(1800)
	except Exception as e:
		print("error!")
		print(e)
		time.sleep(600)
		pass
	else:
		continue  
