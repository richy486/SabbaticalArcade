extends Node2D

const BROWSER = "C:/Program Files/Google/Chrome/Application/chrome.exe"

enum GAME_TYPE {none, exe, web}

@export var title: String
@export var author: String
@export_multiline var description: String
@export var cover: Texture

@export_category("Game File")
@export var type: GAME_TYPE
@export var link: String

var process_id: int = -1
var selected: bool = false
var prepared: bool = false

func _ready():
	# Set cover image
	$Image.texture = cover

func play():
	# Check if we haven't already started
	if process_id != -1:
		kill()
		return
	
	match type:
		GAME_TYPE.exe:
			process_id = OS.create_process(link, [])
		GAME_TYPE.web:
			process_id = OS.create_process(BROWSER, ["--kiosk", link])
	
	if process_id == -1:
		#Global.fail()
		OS.alert("Failed to launch game. File is missing or path is incorrect.", link)
		Global.launch_fail.emit()
	else:
		Global.launch_success.emit()
		
	# NOTE: Since process_ids can't be killed/tracked as expected, I am resetting the id here
	# Otherwise we lose sync of whether a process is still running and this causes issues.
	process_id = -1

## NOTE: When testing, trying to kill process does not actually close the game.
## It looks like apps often spawn multiple processes, so this doesn't seem easy to track.
## Godot is limited here and recommends using external tools to track processes.
func kill():
	if process_id != -1:
		OS.kill(process_id)
		process_id = -1
