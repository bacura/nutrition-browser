#! /usr/bin/ruby
#encoding: utf-8
#Nutritoin browser note 0.2.1 (2025/05/18)


#==============================================================================
# STATIC
#==============================================================================
@debug = false
script = File.basename( $0, '.cgi' )


#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './body'

#==============================================================================
# DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		'pencil'	=> "<img src='bootstrap-dist/icons/pencil.svg' style='height:3em; width:3em;'>",\
		'trash'		=> "<img src='bootstrap-dist/icons/trash.svg' style='height:1.5em; width:1.2em;'>",\
		'camera'	=> "<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>"
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


#### Getting POST
command = @cgi['command']
note = @cgi['note']
note_code = @cgi['code']

if @debug
	puts "command: #{command}<br>"
	puts "<hr>"
end


aliasm = ''
if user.mid != nil
	r = db.query( "SELECT aliasu from #{$TB_USER} WHERE user='#{user.mom}';", false )
	if r.first
		aliasm = r.first['aliasu']
		aliasm = user.mom if aliasm == '' || aliasm == nil
	end
end

case command
when 'write'
	note_code = generate_code( user.name, 'n' )
	p @datetime, note_code, aliasm,note if @debug
	db.query( "INSERT INTO #{$TB_NOTE} SET code='#{note_code}', user='#{user.name}', aliasm='#{aliasm}', note='#{note}', datetime='#{@datetime}', status=1;", true )

when 'delete'
	p note_code if @debug
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
	target_photo.origin = note_code
	target_photo.type = 'jpg'
	target_photo.get_series()
	target_photo.delete_series( true )

	db.query( "DELETE FROM #{$TB_NOTE} WHERE code='#{note_code}';", true )

when 'photo_upload'
	puts 'photo_upload' if @debug
	note_code = generate_code( user.name, 'n' )
	new_photo = Media.new( user )
	new_photo.load_cgi( @cgi )
	new_photo.origin = note_code
	new_photo.save_photo( @cgi )
	new_photo.save_db()

	db.query( "INSERT INTO #{$TB_NOTE} SET code='#{note_code}', media='#{new_photo.code}', user='#{user.name}', aliasm='#{aliasm}', note='', datetime='#{@datetime}';", true )
end

photo = Media.new( user )
photo.base = 'bio'
photo.origin = user.name
photo_code = photo.get_series().first
if photo_code != nil
	profile_photo = "<img src='photo.cgi?iso=Q&code=#{photo_code}&tn=-tns' width='50px' class='img-thumbnail'>"
else
	profile_photo = "<img src='#{$PHOTO}/nobody.jpg' width='50px' class='img-thumbnail'>"
end

mom_photo = "<img src='#{$PHOTO}/mom.jpg' width='50px' class='img-thumbnail'>"
if user.mid != nil || user.mom != ''
	photo.origin = user.mom
	photo_code = photo.get_series().first
	mom_photo = "<img src='photo.cgi?iso=Q&code=#{photo_code}&tn=-tns' width='50px' class='img-thumbnail'>" if photo_code != nil
end

####
puts 'Extract note<br>' if @debug
daughter_delete = true
daughter_delete = false if user.mid != nil


note_html = ''
r = db.query( "SELECT * FROM #{$TB_NOTE} WHERE user='#{user.name}' ORDER BY datetime DESC;", false )
r.each do |e|
	note_date =  "#{e['datetime'].year}-#{e['datetime'].month}-#{e['datetime'].day} #{e['datetime'].hour}:#{e['datetime'].min}"
	note = e['note'].gsub( "\n", '<br>' )
	note_html << '<div class="row" style="padding:1rem;">'


	if e['aliasm'] == ''
		puts 'me' if @debug
		note_html << '<div class="col-3"></div>'

		if e['media'] == nil
			note_html << "<div class='col-7' >"
			note_html << "<div class='alert alert-light'>#{note}<br><br>"
			note_html << "<div align='right'>#{note_date}&nbsp;&nbsp;&nbsp;&nbsp;"
			if daughter_delete
				note_html << "<input type='checkbox' id='#{e['code']}'>&nbsp;"
				note_html << "<span onclick=\"deleteNote( '#{e['code']}' )\">#{l['trash']}</span>"
			end
			note_html << '</div></div></div>'
			note_html << "<div align='center' class='col-2'>#{profile_photo}<br>#{user.aliasu}</div>"
		else
			secure_photo = "<img src='photo.cgi?iso=Q&code=#{e['media']}&tn=-tn' class='img-thumbnail'>"

			note_html << "<div class='col-7' align='right'>"
			note_html << "<a href='#{$PHOTO}/#{e['code']}.jpg' target='photo'>#{secure_photo}</a>&nbsp;&nbsp;&nbsp;&nbsp;"
			note_html << "#{note_date}&nbsp;&nbsp;&nbsp;&nbsp;"
			if daughter_delete
				note_html << "<input type='checkbox' id='#{e['code']}'>&nbsp;"
				note_html << "<span onclick=\"deleteNote( '#{e['code']}', '#{e['media']}' )\">#{l['trash']}</span>"
			end
			note_html << '</div>'
		end
	else
		puts 'mom' if @debug
		note_html << "<div align='center' class='col-2'>#{mom_photo}<br>#{e['aliasm']}</div>"

		if e['media'] == nil
			note_html << "<div class='col-7'>"
			note_html << "	<div class='alert alert-success'>#{note}<br><br>"
			note_html << "		<div align='right'>#{note_date}&nbsp;&nbsp;&nbsp;&nbsp;"
			if user.mid != nil
				note_html << "	<input type='checkbox' id='#{e['code']}'>&nbsp;"
				note_html << "	<span onclick=\"deleteNote( '#{e['code']}' )\">#{l['trash']}</span>"
			end
			note_html << '</div></div></div>'
		else
			secure_photo = "<img src='photo.cgi?iso=Q&code=#{e['media']}&tn=-tn' class='img-thumbnail'>"

			note_html << "<div class='col-7' align='left'>"
			note_html << "<a href='#{$PHOTO}/#{e['code']}.jpg' target='photo'>#{secure_photo}</a>&nbsp;&nbsp;&nbsp;&nbsp;"
			note_html << "#{note_date}&nbsp;&nbsp;&nbsp;&nbsp;"
			if user.mid != nil
				note_html << "<input type='checkbox' id='#{e['code']}'>&nbsp;"
				note_html << "<span onclick=\"deleteNote( '#{e['code']}', '#{e['media']}' )\">#{l['trash']}</span>"
			end
			note_html << '</div>'

		end
	end
	note_html << '</div>'
end


#### HTML
html = <<-"HTML"
<div class='container-fluid'>
	<div class="row">
		<div class="col-2"></div>
		<div class="col-8">
			<div class="row">
				<textarea  class="form-control" id='note' value=''></textarea><br>
			</div>
			<br>
			<div class="row">
				<div class='col-5'>
					<form method='post' enctype='multipart/form-data' id='note_puf'>
						<div class="input-group input-group-sm">
							<label class='input-group-text'>#{l['camera']}</label>
							<input type='file' class='form-control' name='photo' onchange="PhotoUpload()">
						</div>
					</form>
				</div>
			</div>
			<br>
		</div>

		<div class="col-2">
			<button class='btn btn-sm btn-outline-light' onclick="writeNote()">#{l['pencil']}</button>
		</div>
		<hr>

		#{note_html}

	</div>
</div>
HTML

puts html


#==============================================================================
#FRONT SCRIPT
#==============================================================================

js = <<-"JS"
<script type='text/javascript'>

var PhotoUpload = function(){
	var now = new Date();
    var yyyy = now.getFullYear();
    var mm = now.getMonth() + 1;
    var dd = now.getDate();
    var hh = now.getHours();
    var m60 = now.getMinutes();
    var s60 = now.getSeconds();
    var origin = yyyy + "-" +  mm + "-" + dd + "-" + hh + "-" + m60 + "-" + s60

	form_data = new FormData( $( '#note_puf' )[0] );
	form_data.append( 'command', 'photo_upload' );
	form_data.append( 'origin', '' );
	form_data.append( 'base', 'note' );
	form_data.append( 'alt', 'Photo' );
	form_data.append( 'secure', '1' );

	$.ajax( "#{script}.cgi",
		{
			type: 'post',
			processData: false,
			contentType: false,
			data: form_data,
			dataype: 'html',
			success: function( data ){ $( '#L1' ).html( data ); }
		}
	);
};

</script>
JS

puts js
