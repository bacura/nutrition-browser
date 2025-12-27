#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser meal tray monitor 0.0.1 (2024/12/21)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
script = 'mealm'

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'

#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
db = Db.new( user, @debug, false )

### User check
if user.name.nil?
	puts '-'
	exit
end

#### Getting POST data
recipe_code = @cgi['recipe_code']
mode = @cgi['mode']
p recipe_code, mode if @debug

mt = Tray.new( user )

if mode == 'add'
	mt.add_recipe( recipe_code )
	mt.update_db()

	# Updating history
	add_his( user, recipe_code )
end

puts mt.recipes.size
