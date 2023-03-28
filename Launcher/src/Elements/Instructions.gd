extends Label
var hidden = true



# changes the key function hint to tiny text and back  with the press of TAB
func _process(delta):
	if Input.is_action_just_pressed("ui_select"):
		$pop.play()
		hidden = !hidden
	if hidden:
		text = "Mixed-Media-Bundle-Launcher by Ash K - Developed, BB Tombo - Sounds, Homie Boon - Background music\nTab/(Y) to show controls"
	else:
		# i am very sorry, it won't let me add line breaks
		text = "Select game with:\nA D\nArrow keys\nD-pad\n\nOpen and launch game with:\nSpace\nEnter\n(A)\n\nGo back or quit launcher with:\nEsc\n(B)\n\nHide this information with:\nTab\n(Y)"
	pass
