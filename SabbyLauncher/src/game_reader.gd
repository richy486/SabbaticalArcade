extends Node

var DEBUG_GAMES_PATH := "D:/Projects/Godot Projects/SabbyLauncher/games"

var GAMES_PATH: String
var game_data := []

func _init():
	if OS.is_debug_build():
		#GAMES_PATH = DEBUG_GAMES_PATH
		GAMES_PATH = ProjectSettings.globalize_path("res://games/")
	else:
		GAMES_PATH = OS.get_executable_path() + "/games/"
	
func collect_games():
	var games_folder = DirAccess.open(GAMES_PATH)
	if not games_folder:
		OS.alert("Could not find games folder. Please create a /games/ folder next the EXE.")
		return
	
	# Iterate through root folders and look for a 'arcade.json' file - not recursive!
	var folder_names = games_folder.get_directories()
	for folder_name in folder_names:
		var folder = DirAccess.open(GAMES_PATH + "/" + folder_name)
		if not folder:
			continue
			
		if folder.file_exists("arcade.json"):
			parse_gamedata(folder.get_current_dir())
	
func parse_gamedata(path: String):
	# Read file
	var file_path = path + "/arcade.json"
	var file = FileAccess.open(file_path, FileAccess.READ)
	var json = JSON.parse_string(file.get_as_text())
	file.close()
	
	if json == null:
		OS.alert("Error reading arcade.json: ", file_path)
		return
	
	# Converting to absolute paths
	# NOTE: Probably a nicer way to do this (e.g. allow actual relative paths, e.g. "../")
	if "type" in json:
		if json.type == "exe":
			if "link" in json:
				json.link = path + "/" + json.link
				
	if "cover" in json:
		json.cover = path + "/" + json.cover
	elif FileAccess.file_exists(path + "/cover.png"):
		json["cover"] = path + "/cover.png"
		
	# Replace cover path with texture
	var tex = load(json.cover) as Texture
	json.cover = tex
		
	game_data.append(json)
