import vk_api, subprocess, sys, requests, os, json

with open('config.json') as json_data_file:
	data = json.load(json_data_file)

#log in
login, password = data['login'], data['password']
vk_session = vk_api.VkApi(login, password)
try:
	vk_session.auth()
except Exception as e:
	print(e)
	sys.exit(1)

# convert cookies to dict
cookies = vk_session.http.cookies.get_dict()

#extract user_id
user_id = cookies['l']

# cookies to string
s = '"'
for v in cookies:
	s += v + "=" + cookies[v] + ";"
s += '"'


#start node js script with params
i = 10
command = "node vk_music.js {} {}".format(user_id, s)
while i > 0:
	ans = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
	if ans.stderr == "":
		break
	else:
		print(ans.stderr)
		i -= 1
else:
	print("can't get list of music")
	sys.exit(1)

# split string to list
music_data_raw = ans.stdout.split('\n')
if music_data_raw[-1] == "":
	del music_data_raw[-1]

# check size
if len(music_data_raw) % 3 != 0:
	print("Error, len of list = " + str(music_data_raw))
	sys.exit(1)

# reshape to author - song - url
music_data = []
i = 0
while i < len(music_data_raw):
	line = (music_data_raw[i], music_data_raw[i + 1], music_data_raw[i + 2])
	music_data.append(line)
	i += 3

# filter empty or wrong elements
music_data = list(filter(lambda x: x[2][:5] == "https", music_data))

# Download and save music data
os.makedirs("music", exist_ok=True)
for elem in music_data:
	r = requests.get(elem[2])
	filename = "".join([x if x.isalnum() else "_" for x in "{} - {}".format(elem[0], elem[1][:30])])
	filename += ".mp3"
	with open("music/" + filename, "wb") as f:
		f.write(r.content)
