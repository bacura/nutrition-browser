#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 Meal Tray 0.1.2 (2025/01/06)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		meal: 		"お膳",
		reset: 		"お片付け",
		command: 	"操作",
		photo:	 	"写真",
		name: 		"献立名",
		tag: 		"属性",
		edit: 		"献立編集",
		calc: 		"栄養計算",
		analysis: 	"基本解析",
		up: 		"<img src='bootstrap-dist/icons/chevron-up.svg' style='height:1.5em; width:1.5em;'>",
		down: 		"<img src='bootstrap-dist/icons/chevron-down.svg' style='height:1.5em; width:1.5em;'>",
		eraser: 	"<img src='bootstrap-dist/icons/eraser.svg' style='height:1.8em; width:1.8em;'>"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### Getting POST data
command = @cgi['command']
code = @cgi['code']
order = @cgi['order']
if @debug
	puts "command:#{command}<br>"
	puts "code:#{code}<br>"
	puts "order:#{order}<br>"
	puts "<hr>"
end


puts "Loading TRAY<br>" if @debug
mt = Tray.new( user )
mt.load_menu( code ) if command == 'load'
mt.debug if @debug


puts "Loading recipe<br>" if @debug
recipe_objs = []
mt.recipes.each do |e|
	recipe = Recipe.new( user )
	if recipe.load_db( e, true )
		recipe.load_media
		recipe_objs << recipe
	end
end


case command
# Deleting recipe from meal
when 'clear'
	# All
	if order == 'all'
		recipe_objs = []
		mt.name = ''
		mt.code = ''
	# One by one
	else
		recipe_objs.delete_at( order.to_i )
		update = '*'
	end

# 食品の順番を１つ上げる
when 'upper'
	if order.to_i == 0
		t = recipe_objs.shift
		recipe_objs << t
	else
		t = recipe_objs.delete_at( order.to_i )
		recipe_objs.insert( order.to_i - 1, t )
	end
	update = '*'

# 食品の順番を１つ下げる
when 'lower'
	if order.to_i == recipe_objs.size - 1
		t = recipe_objs.pop
		recipe_objs.unshift( t )
	else
		t = recipe_objs.delete_at( order.to_i )
		recipe_objs.insert( order.to_i + 1, t )
	end
	update = '*'
end

puts "HTML part<br>" if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-10'><h5>#{l[:meal]}: #{mt.name}</h5></div>
		<div class='col-2' align='right'>
			<input type='checkbox' id='meal_all_check'>&nbsp;
			<button type='button' class='btn btn-outline-danger btn-sm' onclick=\"clearMT( 'all', '#{mt.code}' )\">#{l[:reset]}</button>
		</div>
	</div>
	<hr>

	<div class='row'>
		<div class='col-1 meal_header'>#{l[:command]}</div>
		<div class='col-1 meal_header'>#{l[:photo]}</div>
		<div class='col-4 meal_header'>#{l[:name]}</div>
		<div class='col-2 meal_header'>#{l[:tag]}</div>
	</div>
	<br>
HTML

c = 0
recipe_objs.each do |e|
	html << "	<div class='row'>"
 	html << "		<div class='col-1'>"
 	html << "			<span onclick=\"upperMT( '#{c}', '#{e.code}' )\">#{l[:up]}</span>"
 	html << "			<span onclick=\"lowerMT( '#{c}', '#{e.code}' )\">#{l[:down]}</span>"
 	html << "		</div>"
	if e.media[0] != nil
  		html << "		<div class='col-1' align='center'><img src='#{$PHOTO}/#{e.media[0]}-tns.jpg'></div>"
  	else
  		html << "		<div class='col-1' align='center'>-</div>"
  	end
  	html << "		<div class='col-4' onclick=\"initCB( 'load', '#{e.code}' )\">#{e.name}</div>"
  	html << "		<div class='col-1'>"
  	html << "			#{@recipe_type[e.type]}&nbsp;" unless e.type == 0
  	html << "		</div>"
  	html << "		<div class='col-1'>"
  	html << "			#{@recipe_role[e.role]}&nbsp;" unless e.role == 0
  	html << "		</div>"
  	html << "		<div class='col-3'>"
  	html << "			#{@recipe_tech[e.tech]}&nbsp;" unless e.tech == 0
  	html << "		</div>"
  	html << "		<div class='col-1' align='right'><span onclick=\"clearMT( '#{c}', '#{e.code}' )\">#{l[:eraser]}</span></div>"
	html << "	</div>"
	c += 1
end

html << "	<br>"
html << "	<div class='row'>"
html << "		<div class='col-2'><button type='button' class='btn btn-primary btn-sm' onclick=\"initMenu( '#{mt.code}' )\">#{l[:edit]}</button></div>"
html << "		<div class='col-2'><button type='button' class='btn btn-primary btn-sm' onclick=\"initTMCalc( '#{mt.code}' )\">#{l[:calc]}</button></div>"
html << "		<div class='col-2'><button type='button' class='btn btn-primary btn-sm' onclick=\"initMTAnalysis( '#{mt.code}' )\">#{l[:analysis]}</button></div>"
html << "	</div>"
html << "	<div class='code'>#{mt.code}</div>"
html << "</div>"

puts html

#==============================================================================
# POST PROCESS
#==============================================================================
puts "Updating MT<br>" if @debug
mt.load_recipe_objs( recipe_objs )
mt.update_db

#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init' || command == 'load'
	js = <<~"JS"
<script type='text/javascript'>

//
var clearMT = ( order, code ) => {
	if( order == 'all'){
		if( document.getElementById( 'meal_all_check' ).checked ){
			postLayer( '#{myself}', 'clear', true, 'L1', { order:'all', code });
			addingMT( '' );

			displayVIDEO( 'Menu cleared' );
			flashBW();
			dl1 = true;
			displayBW();
		} else{
			displayVIDEO( 'Check! (>_<)' );
		}
	} else{
		postLayer( '#{myself}', 'clear', true, 'L1', { order, code });
		addingMT( '' );
	}
};

//
var upperMT = ( order, code ) => {
	postLayer( '#{myself}', 'upper', true, 'L1', { order, code });
};

//
var lowerMT = ( order, code ) => {
	postLayer( '#{myself}', 'lower', true, 'L1', { order, code });
};

</script>

JS

	puts js
end

puts '(^q^)' if @debug
