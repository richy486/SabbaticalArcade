extends ColorRect


const constant_progress : float = 1.0
const lerp_progress : float = 5.0
var progress = 0.0
var target_progress = 0.0

export (NodePath) var description_path_path;
onready var description_text = get_node(description_path_path);
var random=RandomNumberGenerator.new()

func _ready():
	random.randomize()

func _physics_process(delta):
	progress = lerp(progress, target_progress, delta * lerp_progress)
	var step = constant_progress * delta
	if abs(target_progress - progress) < step:
		progress = target_progress
	else:
		progress += sign(target_progress - progress) * step
	
	#percent_visible = progress
	modulate.a = progress# * 0.5
	description_text.percent_visible = progress
	pass

func update_description(description : String):
	#text = description
	description_text.text = description
	target_progress = 1.0
	color.h = random.randfn()
	color.s = 0.75
	color.v = 1.0
	pass

func hide_description():
	target_progress = 0.0
	pass
