using JSON

println(stderr, "Connect Four - Julia")

# This is fragile and relies on the fact that the driver always passes the
# command line arguments in the order --player <p> --width <w> --height <h>.
player = parse(Int8, ARGS[2])
width = parse(Int8, ARGS[4])
height = parse(Int8, ARGS[6])

println(stderr, "  player = $player")
println(stderr, "   width = $width")
println(stderr, "  height = $height")

"Returns the valid moves for the state as a list of integers."
function validmoves(state)
	grid = state["grid"]
	moves = Array{Int8}(undef, 0)
	for i = 1:width
		if grid[i][1] == 0
			push!(moves, i - 1) # Moves are zero based
		end
	end
	moves
end

# Loop reading the state from the driver and writing a random valid move.
for line in eachline(stdin)
	println(stderr, line)
	state = JSON.parse(line)
	action = Dict("move" => rand(validmoves(state)))
	msg = JSON.json(action)
	println(stderr, msg)
	println(stdout, msg)
	flush(stdout)
end

# Be a nice program and close the ports.
close(stdin)
close(stdout)
close(stderr)
