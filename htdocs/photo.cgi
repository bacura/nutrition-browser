#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 recipe photo 0.6.1 (2025/03/15)

#==============================================================================
# STATIC
#==============================================================================
@debug = false
tmp_delete = false
#script = File.basename( $0, '.cgi' )

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
	l['jp'] = {
		camera:		"<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>",\
		trash:		"<img src='bootstrap-dist/icons/trash-fill.svg' style='height:1.2em; width:1.2em;'>",\
		left_ca:	"<img src='bootstrap-dist/icons/arrow-left-circle.svg' style='height:1.2em; width:1.2em;'>",\
		right_ca:	"<img src='bootstrap-dist/icons/arrow-right-circle.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end


def view_series( media, l, size )
	puts "view_series:#{},#{}" if @debug
	media.get_series()
	protect = true

	recipe = Recipe.new( media.user )
	recipe.load_db( media.origin, true ) if /\-r\-/ =~ media.origin

	if media.series.size > 0
		puts "<div class='row'>"
		media.series.each.with_index( 0 ) do |e, i|
			puts "<div class='col'>"
			if recipe.protect != 1 && media.muser == media.user.name
				puts "<span onclick=\"photoMove( '#{media.origin}', '#{e}', #{i - 1} )\">#{l[:left_ca]}</span>" if i != 0
				puts "&nbsp;&nbsp;<span onclick=\"photoMove( '#{media.origin}', '#{e}', #{i + 1} )\">#{l[:right_ca]}</span>" if i != media.series.size - 1
			end
			puts '<br>'


 			puts "<img src='#{$PHOTO}/#{e}-tn.jpg' width='#{size}px' class='img-thumbnail' id='iid_#{e}' onclick=\"modalPhoto( '#{e}' )\"><br>"


			puts "<span onclick=\"photoDel( '#{media.origin}', '#{e}', '#{media.base}' )\">#{l[:trash]}</span>" if recipe.protect != 1 && media.muser == media.user.name
			puts "</div>"
		end
		puts "</div>"
	else
		puts 'No photo'
	end
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
	query = ''
	case base
	when 'menu'
		query = "SELECT code FROM #{$MYSQL_TB_MEAL} WHERE user='#{user.name}';"
	when 'recipe'
		query = "SELECT code FROM #{$MYSQL_TB_SUM} WHERE user='#{user.name}';"
	end
	if query != ''
		r = db.query( query, false )
		origin = r.first['code']
	end
end

media.origin = origin
media.base = base

case command
when 'upload'
	puts 'Upload<br>' if @debug
	if user.status != 7
		media.code = code
		media.alt = alt
		media.type = 'jpg'
		media.date = @datetime

		tmp_file = @cgi['photo'].original_filename
		photo_type = @cgi['photo'].content_type
		photo_body = @cgi['photo'].read
		photo_size = photo_body.size.to_i
		if @debug
			puts "#{tmp_file}<br>"
			puts "#{photo_type}<br>"
			puts "#{photo_size}<br>"
			puts "<hr>"
		end

		if photo_size < $SIZE_MAX && ( photo_type == 'image/jpeg' || photo_type == 'image/jpg' )
			puts 'Image magick<br>' if @debug
			require 'nkf'
			require 'rmagick'

			puts "temporary file<br>" if @debug
			f = open( "#{$TMP_PATH}/#{tmp_file}", 'w' )
			f.puts photo_body
			f.close
			media.code = generate_code( user.name, 'p' )
			photo = Magick::ImageList.new( "#{$TMP_PATH}/#{tmp_file}" )

			puts "Resize<br>" if @debug
			photo_x = photo.columns.to_f
			photo_y = photo.rows.to_f
			photo_ratio = 1.0
			if photo_x >= photo_y
				tn_ratio = $TN_SIZE / photo_x
				tns_ratio = $TNS_SIZE / photo_x
				photo_ratio = $PHOTO_SIZE_MAX / photo_x if photo_x >= $PHOTO_SIZE_MAX
			else
				tn_ratio = $TN_SIZE / photo_y
				tns_ratio = $TNS_SIZE / photo_y
				photo_ratio = $PHOTO_SIZE_MAX / photo_y if photo_y >= $PHOTO_SIZE_MAX
			end

			puts "medium SN resize<br>" if @debug
			tn_file = photo.thumbnail( tn_ratio )
			tn_file.write( "#{$PHOTO_PATH}/#{media.code}-tn.jpg" )

			puts "small SN resize<br><br>" if @debug
			tns_file = photo.thumbnail( tns_ratio )
			tns_file.write( "#{$PHOTO_PATH}/#{media.code}-tns.jpg" )

			puts "resize 2k<br>" if @debug
			photo = photo.thumbnail( photo_ratio ) if photo_ratio != 1.0

#			puts "water mark<br>" if @debug
#			wm_text = "Nutrition Browser:#{media.code}"
#			wm_img = Magick::Image.new( photo.columns, photo.rows )
#			wm_drew = Magick::Draw.new
#			wm_drew.annotate( wm_img, 0, 0, 0, 0, wm_text ) do
#				self.gravity = Magick::SouthWestGravity
#				self.pointsize = 18
#				self.font_family = $WM_FONT
#				self.font_weight = Magick::BoldWeight
#				self.stroke = "none"
#			end
#			wm_img = wm_img.shade( true, 315 )
#			photo.composite!( wm_img, Magick::CenterGravity, Magick::HardLightCompositeOp )
			photo.write( "#{$PHOTO_PATH}/#{media.code}.jpg" )

			puts "insert DB<br>" if @debug
			media.get_series()
			media.save_db

			File.unlink "#{$TMP_PATH}/#{tmp_file}" if File.exist?( "#{$TMP_PATH}/#{tmp_file}" ) && tmp_delete
		end
	end

when 'move'
	if user.status != 7
		puts 'Move<br>' if @debug
		media.code = code
		media.zidx = zidx

		puts "Update DB<br>" if @debug
		media.get_series()
		media.move_series()
	end

when 'delete'
	if user.status != 7
		puts "delete item DB<br>" if @debug
		media.code = code
		if( media.delete_db )
			puts 'Delete<br>' if @debug
			File.unlink "#{$PHOTO_PATH}/#{code}-tns.jpg" if File.exist?( "#{$PHOTO_PATH}/#{code}-tns.jpg" )
			File.unlink "#{$PHOTO_PATH}/#{code}-tn.jpg" if File.exist?( "#{$PHOTO_PATH}/#{code}-tn.jpg" )
			File.unlink "#{$PHOTO_PATH}/#{code}.jpg" if File.exist?( "#{$PHOTO_PATH}/#{code}.jpg" )
		end
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

view_series( media, l, 200 )
puts "	<div align='right' class='code'>#{origin}</div>"
