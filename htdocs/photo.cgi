#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe photo 0.6.1 (2025/12/26)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
tmp_delete = false
myself = File.basename( __FILE__ )


#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './body'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		camera:		"<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>",\
		trash:		"<img src='bootstrap-dist/icons/trash-fill.svg' style='height:1.2em; width:1.2em;'>",\
		left_ca:	"<img src='bootstrap-dist/icons/arrow-left-circle.svg' style='height:1.2em; width:1.2em;'>",\
		right_ca:	"<img src='bootstrap-dist/icons/arrow-right-circle.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end


#==============================================================================
# Main
#==============================================================================

#### GET data
get_data = get_data()

iso  = get_data['iso']
code = get_data['code'].to_s.gsub( '/', '' )
tn   = get_data['tn'].to_s.gsub( '/', '' )

user = User.new( @cgi )
l = language_pack( user.language )
db = Db.new( user, @debug, false )
media = Media.new( user )

if iso == 'Q'
	iso_init( nil )
	media.code = code
	media.load_db()
	photo_file = media.get_path_code() + tn + ".jpg"

 	if File.exist?( photo_file ) && ( user.name == media.owner || user.mom == media.owner )
		File.open( photo_file, 'rb' ) do |f|
			f.each do |l| puts l end
		end
	else

	end
	exit
else
	html_init( nil )
end

user.debug if @debug

# POST
command = @cgi['command']
base = @cgi['base']
origin = @cgi['origin']
code = @cgi['code']
alt = @cgi['alt']
zidx = @cgi['zidx']
iso = @cgi['iso']

if @debug
	puts "command: #{command}<br>"
	puts "code: #{code}<br>"
	puts "base: #{base}<br>"
	puts "origin: #{origin}<br>"
	puts "zidx: #{zidx}<br>"
	puts "PHOTO_PATH: #{$PHOTO_PATH}<br>"
	puts "<hr>"
end


puts 'base origin<br>' if @debug
if origin == ''
	case base
	when 'menu'
		res = db.query( "SELECT code FROM #{$TB_MEAL} WHERE user=?", false, [user.name] )&.first
	when 'recipe'
		res = db.query( "SELECT code FROM #{$TB_SUM} WHERE user=?", false, [user.name] )&.first
	else
		res = nil
	end
	origin = res['code'] if res
end

media.origin = origin
media.base = base

case command
when 'upload'
	puts 'Upload<br>' if @debug
	unless user.barrier
		media.code = code
		media.alt = alt
		media.type = 'jpg'
		media.date = @datetime
		media.save_photo( @cgi )
		media.get_series()
		media.save_db
	end

when 'move'
	unless user.barrier
		puts 'Move<br>' if @debug
		media.code = code
		media.zidx = zidx

		puts "Update DB<br>" if @debug
		media.get_series()
		media.move_series()
	end

when 'delete'
	unless user.barrier
		puts "delete item DB<br>" if @debug
		media.code = code
		media.delete_db( true )
		media.delete_photo( true )
	end

when 'modal_body'
	puts 'body' if @debug
	media.code = code
	media.load_db()
	caption = media.alt == '' ? media.code : media.alt

	puts '<table width="100%"><tr>'
	puts "<td>#{caption}</td>"
    puts '<td align="right"><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></td>'
    puts '</tr></table>'

	if media.secure()
		puts "<img src='photo.cgi?iso=Q&code=#{code}' width='100%'>"
	else
		puts "<img src='#{$PHOTO}/#{code}.jpg' width='100%'>"
	end
	exit

when 'modal_label'
	puts 'label' if @debug
	media.code = code
	media.load_db()

	exit
end
