extends Control

const HALF_PI: float = PI / 2.0 # 1.57079632679

@export var carousel_scale := Vector2(400, 20)
@export var near_tint := Color.WHITE
@export var far_tint := Color.PURPLE # * Color.hex(0xffffff44)
@export var game_scale_min := 0.3
@export var game_scale_max := 1.0

@onready var ui_animator = $"../UI/AnimationPlayer"
@onready var game_title = $"../UI/CartInfo/GameTitle"
@onready var author = $"../UI/CartInfo/Author"

@onready var cart_details = $"../UI/Panel"
@onready var detail_cover = $"../UI/Panel/DetailBox/CartCover"
@onready var detail_description = $"../UI/Panel/DetailBox/CartDetails/Description"
@onready var detail_menu = $"../UI/Panel/DetailBox/CartDetails/Menu"
@onready var cart_play = $"../UI/Panel/DetailBox/CartDetails/Menu/Play"
@onready var cart_back = $"../UI/Panel/DetailBox/CartDetails/Menu/Back"

@onready var loading = $"../UI/LOADING"

var GameCart = preload("res://src/game_cart.tscn")

var carousel_angle: float = 0.0

var games: Array = []
var game_prepared: bool = false
var game_current: int = 0
var game_count: int = 0
var game_sector_size: float = TAU

var reader = preload("res://src/game_reader.gd").new()

func _ready():

	# This restarts the launcher if it is closed
	#OS.set_restart_on_exit(true)
	
	reader.collect_games()
	populate_carousel(reader.game_data)
	
	if game_count > 0:
		# Select random game
		game_current = randi() % game_count
		update_selection(game_current)
		game_sector_size = TAU / game_count

	cart_back.pressed.connect(unprepare_game)
	Global.launch_success.connect(_on_launch_success)

func _process(delta):
	update_carousel(delta)

func _input(event):
	if event is InputEventKey and event.pressed:
		if event.is_action_pressed(&"ui_left"):
			select_previous()
		if event.is_action_pressed(&"ui_right"):
			select_next()
		if event.is_action_pressed(&"ui_accept"):
			prepare_game()
		if event.is_action_pressed(&"ui_cancel"):
			unprepare_game()
			
		if event.is_action_pressed(&"restart"):
			get_tree().reload_current_scene()

func select_previous():
	unprepare_game()
	games[game_current].selected = false
	game_current = wrap(game_current + 1, 0, game_count)
	update_selection(game_current)

func select_next():
	unprepare_game()
	games[game_current].selected = false
	game_current = wrap(game_current - 1, 0, game_count)
	update_selection(game_current)

func prepare_game():
	if not game_prepared:
		ui_animator.play("show_details")
		cart_details.visible = true
		detail_cover.texture = games[game_current].cover
		detail_description.text = games[game_current].description

		# Connect Buttons
		cart_play.pressed.connect(games[game_current].play)
		game_prepared = true
	else:
		# Game is already prepared, so let's play
		games[game_current].play()

func unprepare_game():
	if not game_prepared:
		return
		
	ui_animator.play_backwards("show_details")
	
	# Disconnect Buttons
	cart_play.pressed.disconnect(games[game_current].play)
	game_prepared = false

func update_carousel(delta):
	var target_angle = game_sector_size * game_current - HALF_PI

	# If close, snap to target and exit early. Saves constantly iterating over the loop.
	if abs(carousel_angle - target_angle) < 0.01:
		carousel_angle = target_angle
		return
	else:
		carousel_angle = lerp_angle(carousel_angle, target_angle, delta * 10)

	for i in range(game_count):
		var _rad = game_sector_size * i - carousel_angle
		var _amount = sin(_rad) / 2.0 + 0.5 # Maps from 0..1
		games[i].position = Vector2(cos(_rad), sin(_rad)) * carousel_scale
		games[i].scale = Vector2.ONE * lerp(game_scale_min, game_scale_max, _amount)
		games[i].modulate = lerp(far_tint, near_tint, _amount)

func update_selection(index: int):
	game_current = index
	var game = games[game_current]
	game.selected = true
	
	# Update UI elements with game cart data
	game_title.text = game.title
	author.text = game.author

func populate_carousel(carts: Array):
	for cart in carts:
		var node = GameCart.instantiate()
		node.title = cart.name
		node.author = cart.author
		node.description = cart.description
		match cart.type:
			"exe":
				node.type = node.GAME_TYPE.exe
			"web":
				node.type = node.GAME_TYPE.web
		node.link = cart.link
		node.cover = cart.cover
		add_child(node)

	games = get_children()
	game_count = games.size()
	
func _on_launch_success():
	# Generate a fake loading screen!
	loading.visible = true
	await get_tree().create_timer(1.0).timeout
	loading.visible = false
