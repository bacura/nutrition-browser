#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 config 0.3.1 (2024/08/21)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )


#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'


#==============================================================================
#DEFINITION
#==============================================================================

# Renders the menu with no line
def menu( user )
	mods = Dir.glob( "#{$HTDOCS_PATH}/config_/mod_*" ).map do |x|
		File.basename( x ).sub( 'mod_', '' ).sub( '.rb', '' )
	end

	mods.delete( 'release' )
	mods.push( 'release' )

	html = mods.each_with_index.map do |e, i|
		require "#{$HTDOCS_PATH}/config_/mod_#{e}.rb"
		ml = module_lp( user.language )
		bclass = ( i == mods.size - 1 ) ? 'bg-danger' : 'ppill'
		puts "<span class='btn badge rounded-pill #{bclass}' onclick='configForm( \"#{e}\" )'>#{ml['mod_name']}</span>&nbsp;"
	end.join

	return html
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
db = Db.new( user, @debug, false )

# Getting POST data
mod = @cgi['mod']

# Driver logic
html = if mod == 'menu'
	puts 'MENU<br>' if @debug
	user.status == $ASTRAL ? "<span class='ref_error'>[config]Astral user limit!</span><br>" : menu( user )
else
	if mod.empty?
		"<div align='center'>Config</div>"
	else
		require "#{$HTDOCS_PATH}/config_/mod_#{mod}.rb"
		puts "MOD (#{mod})<br>" if @debug
		config_module( @cgi, db ) unless user.status == $ASTRAL
	end
end

puts html
