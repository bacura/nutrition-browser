#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 menu 0.0.0 (2024/12/21)


#==============================================================================
#STATIC
#==============================================================================
@debug = false
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
		menu: 		'献立編集',
		normal: 	'常食',
		delete: 	'削除',
		save: 		'保存',
		name: 		'献立名',
		savex: 		'展開保存',
		label: 		'ラベル',
		label_new: 	'新規ラベル',
		memo: 		'メモ',
		public: 	"<img src='bootstrap-dist/icons/globe.svg' style='height:1.0em; width:1.0em;'>公開",
		protect: 	"<img src='bootstrap-dist/icons/lock-fill.svg' style='height:1.0em; width:1.0em;'>保護",
		camera: 	"<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>",
		migi: 		"<img src='bootstrap-dist/icons/box-arrow-right.svg' style='height:2em; width:2em;'>"
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
if @debug
	puts "commnad:#{command}<br>"
	puts "code:#{code}<br>"
	puts "<hr>"
end


menu = Menu.new( user )
menu.debug if @debug

case command
when 'save'
	puts 'Saving menu<br>' if @debug
	menu.load_cgi( @cgi )
	menu.label = @cgi['new_label'] unless @cgi['new_label'].empty?
	mt = Tray.new( user )

	# Inserting new menu
	if mt.name.empty? || mt.name != menu.name || menu.protect == 1
		puts 'New saving<br>' if @debug
		menu.code = generate_code( user.name, 'm' )
		menu.meal = mt.meal
  		menu.insert_db

  		mt.name = menu.name
  		mt.code = menu.code
  		mt.protect = menu.protect
  		mt.update_db
	end

	# Updating menu
	menu.debug if @debug
	menu.update_db

when 'photo_upload'
	new_photo = Media.new( user )
	new_photo.load_cgi( @cgi )
	new_photo.save_photo( @cgi )
    new_photo.get_series()
    new_photo.save_db()

	code = @cgi['origin']
	menu.load_db( code, true )

when 'photo_mv'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
    target_photo.get_series()
    target_photo.move_series()
 
	code = @cgi['origin']
	menu.load_db( code, true )

when 'photo_del'
	target_photo = Media.new( user )
	target_photo.load_cgi( @cgi )
	target_photo.delete_photo( true )
	target_photo.delete_db( true )

	code = @cgi['origin']
	menu.load_db( code, true )
else
	puts 'Displaing menu<br>' if @debug
	menu.load_db( code, true ) unless code.empty?
end

puts 'Label HTML<br>' if @debug
r = db.query( "SELECT label from #{$TB_MENU} WHERE user=? AND name!='';", false, [user.name] )
label_list = []
r.each do |e| label_list << e['label'] end
label_list.uniq!

html_label = '<select class="form-select form-select-sm" id="label">'
html_label << "<option value='#{l[:normal]}' id='normal_label0' style='display:inline'>#{l[:normal]}</option>"

normal_label_c = 0
label_list.each do |e|
	unless e == l[:normal]
		normal_label_c += 1
		html_label << "<option value='#{e}' id='normal_label#{normal_label_c}' style='display:inline' #{$SELECT[e == menu.label]}>#{e}</option>"
	end
end


puts "Photo parts<br>" if @debug
photo = Media.new( user )
photo.origin = code
photo.base = 'menu'
photo.get_series()


puts 'HTML<br>' if @debug
html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-2'><h5>#{l[:menu]}</h5></div>
		<div class="col-4">
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="public" #{$CHECK[menu.public]}> #{l[:public]}
  				</label>
			</div>
			<div class="form-check form-check-inline">
  				<label class="form-check-label">
    				<input class="form-check-input" type="checkbox" id="protect" #{$CHECK[menu.protect]}> #{l[:protect]}
  				</label>
			</div>
		</div>
    </div>
    <br>
	<div class='row'>
		<div class="col-3">
			<div class="input-group input-group-sm">
				#{html_label}
			</div>
		</div>

		<div align='center' class="col-1">
			<span onclick="copyLabel()">#{l[:migi]}</span>
		</div>

		<div class="col-3">
			<div class="input-group input-group-sm">
				<label class="input-group-text" for="menu_name">#{l[:label_new]}</label>
      			<input type="text" class="form-control" id="new_label" value="">
	   		</div>
    	</div>

		<div class="col-5">
			<div class="input-group input-group-sm">
				<label class="input-group-text">#{l[:name]}</label>
      			<input type="text" class="form-control" id="menu_name" value="#{menu.name}" required>
      			<button class="btn btn-outline-primary" type="button" onclick="saveMenu( '#{menu.code}' )">#{l[:save]}</button>
    		</div>
    	</div>
	</div>
    <br>
	<div class='row'>
		<div class="col">
			<div class="form-group">
    			<label for='memo'>#{l[:memo]}</label>
				<textarea class="form-control" id='memo' rows="3">#{menu.memo}</textarea>
   			</div>
		</div>
	</div>
	<div class='row'>
		<div class='col-4'>#{photo.html_form_generic( menu&.code != nil )}</div>
	</div>

	<hr>
	#{photo.html_series( '-tn', 200, menu.protect )}

	<div class='row'>
		<div align='right' class='col-12 code'>#{menu.code}</div>
	</div>
</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
	js = <<-"JS"
<script type='text/javascript'>

var postReq = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
};

//
var saveMenu = ( code ) => {
	const menu_name = $( "#menu_name" ).val();
	if( menu_name != '' ){
		const public = $( "#public" ).is( ":checked" ) ? 1 : 0;
		const protect = $( "#protect" ).is( ":checked" ) ? 1 : 0;
		const label = $( "#label" ).val();
		const new_label = $( "#new_label" ).val();
		const memo = $( "#memo" ).val();

		postReq( 'save', { code, menu_name, public, protect, label, new_label, memo }, data => {
			$( "#L2" ).html( data );
			initMT( 'reload', code );
			displayVIDEO( menu_name );
		});
	}
	else{
		displayVIDEO( 'Menu name! (>_<)' );
	}
};


// Copying lebel to new label
var copyLabel = function(){
	$( "#new_label" ).val( $( "#label" ).val());
};


/////////////////////////////////////////////////////////////////////////////////////////////

var PhotoUpload = () => {
	const formData = new FormData( $( '#menu_puf' )[0] ); //#base + '_puf'
	formData.append( 'command', 'photo_upload' );
	formData.append( 'origin', '#{menu.code}' );
	formData.append( 'base', 'menu' );
	formData.append( 'alt', '#{menu.name}' );
	formData.append( 'secure', '0' );

	$.ajax( {
		url: "#{myself}",
		type: 'POST',
		processData: false,
		contentType: false,
		data: formData,
		dataType: 'html',
		success: ( data ) => $( '#L2' ).html( data )
	} );
}

var photoMove = ( code, zidx ) => {

	postReq( 'photo_mv', { origin:'#{menu.code}', code, zidx, base:'menu' }, data => {
		$( '#L2' ).html( data );
		displayVIDEO( code );
	});
}

var photoDel = ( code ) => {
	postReq( 'photo_del', { origin:'#{menu.code}', code, base:'menu' }, data => $( '#L2' ).html( data ));
}

</script>

JS

	puts js
end

puts '(^q^)' if @debug
