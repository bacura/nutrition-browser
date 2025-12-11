#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 nutrition assessment tools 0.11b (2024/07/28)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
script = File.basename( $0, '.cgi' )
@mod_path = 'ginmi_'

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'
require './body'

#==============================================================================
#DEFINITION
#==============================================================================

#### Menu no line
def menu( user )
	mods = Dir.glob( "#{$HTDOCS_PATH}/#{@mod_path}/mod_*" )
	mods.map! do |x|
		x = File.basename( x )
		x = x.sub( 'mod_', '' )
		x = x.sub( '.rb', '' )
	end

	html = ''
	mods.each.with_index( 1 ) do |e, i|
		require "#{$HTDOCS_PATH}/#{@mod_path}/mod_#{e}.rb"

		ml = module_lp( user.language )
		html << "<span class='btn badge rounded-pill ppill' onclick='ginmiForm( \"#{e}\" )'>#{ml['mod_name']}</span>&nbsp;"
	end

	return html
end


#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
db = Db.new( user, @debug, false )


#### Getting POST
mod = @cgi['mod']

#### Driver
html = ''
if mod == 'menu'
	puts 'MENU<br>' if @debug
	unless user.status == 7
		html = menu( user )
	else
		html = "<span class='ref_error'>[ginmi]Astral user limit!</span><br>"
	end
else
	if mod == ''
		html =  "<div align='center'>Assessment tools</div>"
	else
		puts "MOD (#{mod})<br>" if @debug
		require "#{$HTDOCS_PATH}/#{@mod_path}/mod_#{mod}.rb"
		html = ginmi_module( @cgi, db ) unless user.status == 7
	end
end


puts 'HTML<br>' if @debug
puts html

#==============================================================================
#FRONT SCRIPT
#==============================================================================
if mod == 'menu'
	js = <<-"JS"
<script type='text/javascript'>

var ginmiForm = function( mod ){
	$.post( "ginmi.cgi", { mod:mod, command:'form' }, function( data ){ 
		$( "#L1" ).html( data );
	});
}

</script>
JS

	puts js 
end